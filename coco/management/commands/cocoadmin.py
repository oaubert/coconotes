# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import urllib
import logging
import dateutil.parser

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.files import File
from django.utils.timezone import make_naive, is_aware

from coco.models import Activity, Course, Video, Module, Annotation, Newsitem, AnnotationType

logger = logging.getLogger(__name__)

def convert_date(d):
    if is_aware(d):
        d = make_naive(d)
    return d

class Command(BaseCommand):
    args = '[command] [param]'
    help = """Administration commands for COCo
"""
    def _import_info(self, cours, module, info):
        """Import video/module/course info from info.json files. Params: course_title module_title info.json
        """
        def get_user(username):
            if username == "":
                username = "anonyme"
            username = username.lower()
            user, created = User.objects.get_or_create(username=username)
            return user

        with open(info, 'r') as f:
            data = json.load(f)
        self.stdout.write("Saving %s\n" % data.get("title"))

        adminuser = get_user('admin')
        dirname = os.path.dirname(os.path.abspath(info))
        try:
            c = Course.objects.get(title=cours)
        except Course.DoesNotExist:
            c = Course(creator=adminuser, contributor=adminuser, title=cours, shorttitle=cours[:16])
            c.save()
        try:
            module = Module.objects.get(title=module, course=c)
        except Module.DoesNotExist:
            module = Module(creator=adminuser, contributor=adminuser, course=c, title=module, shorttitle=module[:16])
            module.save()

        activity_title = data.get("title", "Titre inconnu")
        descr = "%s - %s" % (data.get("date", "Date inconnue"),
                             data.get("author", "Auteur inconnu"))
        activity = Activity(creator=adminuser, contributor=adminuser,
                            title=activity_title, shorttitle=activity_title[:16],
                            module=module, description=descr)
        activity.save()

        url = data.get("url", "")
        if not url:
            # Default url
            url = "https://comin-ocw.org/contents/%s/camera.mp4" % dirname.split('/contents/')[-1]
        vid = Video(creator=adminuser, contributor=adminuser,
                    activity=activity,
                    title=activity_title,
                    shorttitle=activity_title[:16],
                    url=url)
        # Note: length is not initialized. We will get its duration
        # from the package just below.
        pic = os.path.join(dirname, 'imagecache', '00.png')
        if not os.path.exists(pic):
            pic = os.path.join(dirname, 'imagecache', '000.png')
        if os.path.exists(pic):
            with open(pic, 'rb') as f:
                vid.thumbnail.save(os.path.basename(pic), File(f))
        vid.save()

        # Read data.json if available
        packageurl = data.get('dataurl', os.path.join(dirname, 'data.json'))
        if packageurl.startswith('http') or os.path.exists(packageurl):
            self.stdout.write("Loading data from %s" % packageurl)
            f = urllib.urlopen(packageurl)
            package = json.loads("".join(f.readlines()))
            f.close()
            # Update video duration
            vid.duration = package['medias'][0]['meta']['dc:duration'] / 1000.0
            slug = package['medias'][0]['id']
            if re.match('^\d', slug):
                # id starting with a number. Add a "m" (media) prefix.
                slug = "m" + slug
            if Video.objects.filter(slug=slug).exists():
                self.stdout.write("Duplicate video slug: " + slug)
            else:
                vid.slug = slug
            vid.save()
            ats = {}
            for atjson in package['annotation-types']:
                try:
                    at = AnnotationType.objects.get(title=atjson['dc:title'])
                except AnnotationType.DoesNotExist:
                    # Create the AnnotationType matching dc:title
                    at = AnnotationType(creator=adminuser,
                                        created=convert_date(dateutil.parser.parse(atjson['dc:created'])),
                                        title=atjson['dc:title'],
                                        description=atjson['dc:description'])
                    at.save()
                ats[atjson['id']] = at
            self.stdout.write("Copying %d annotations" % len(package['annotations']))
            for a in package['annotations']:
                at = ats[a['meta']['id-ref']]
                self.stdout.write(".", ending="")
                self.stdout.flush()
                tags = []
                creator = a['meta']['dc:creator']
                contributor = a['meta']['dc:contributor']
                title = a['content']['title']
                m = re.match("^\[(\w+,)?(\w+)](.*)", title)
                if m:
                    creator = contributor = m.group(2)
                    if m.group(1) is not None:
                        tags.append(m.group(1).strip(',').strip())
                    title = m.group(3).strip()
                an = Annotation(creator=get_user(creator), contributor=get_user(contributor),
                                created=convert_date(dateutil.parser.parse(a['meta']['dc:created'])),
                                modified=convert_date(dateutil.parser.parse(a['meta']['dc:modified'])),
                                annotationtype=at,
                                video=vid,
                                begin=long(a['begin']) / 1000.0,
                                end=long(a['end']) / 1000.0,
                                title=title,
                                description=a['content']['description'])
                # FIXME: handle tags
                if 'data' in a['content']:
                    an.contenttype = a['content'].get('mimetype', 'text/plain')
                    an.contentdata = json.dumps(a['content']['data'])
                if 'img' in a['content']:
                    pic = os.path.join(dirname, a['content']['img']['src'])
                    if os.path.exists(pic):
                        with open(pic, 'rb') as f:
                            an.thumbnail.save(os.path.basename(pic), File(f))
                an.save()
                for t in tags:
                    an.tags.add(t)

    def _postnews(self, title, subtitle, data):
        """Post a newsitem message.
        """
        adminuser = User.objects.get(username='admin')
        n = Newsitem(creator=adminuser, title=title, subtitle=subtitle, description=data)
        n.save()

    def handle(self, *args, **options):
        dispatcher = {
            'info': self._import_info,
            'postnews': self._postnews,
            }
        self.help = self.help + "\n\n" + "\n".join("\t%s: %s" % (k, v.__doc__) for (k, v) in dispatcher.items())
        if not args:
            self.print_help(sys.argv[0], sys.argv[1])
            return
        command = args[0]
        args = args[1:]
        m = dispatcher.get(command)
        if m is not None:
            m(*args)
        else:
            raise CommandError("Unknown command")

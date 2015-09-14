# -*- coding: utf-8 -*-

import sys
import os
import json
import urllib
import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.files import File

from coco.models import Activity, Course, Video, Module, License, Annotation, Comment, Resource, Newsitem, AnnotationType

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '[command] [param]'
    help = """Administration commands for COCo
"""
    def _import_info(self, cours, module, info):
        """Import video/module/course info from info.json files. Params: course_title module_title info.json
        """
        with open(info, 'r') as f:
            data = json.load(f)
        self.stdout.write("Saving %s\n" % data.get("title"))
        user = User.objects.get(pk=1)
        dirname = os.path.dirname(os.path.abspath(info))
        try:
            c = Course.objects.get(title=cours)
        except Course.DoesNotExist:
            c = Course(creator=user, contributor=user, title=cours, shorttitle=cours[:16])
            c.save()
        try:
            module = Module.objects.get(title=module, course=c)
        except Module.DoesNotExist:
            module = Module(creator=user, contributor=user, course=c, title=module, shorttitle=module[:16])
            module.save()

        activity_title = data.get("title", "Titre inconnu")
        descr = "%s - %s" % (data.get("date", "Date inconnue"),
                             data.get("author", "Auteur inconnu"))
        activity = Activity(creator=user, contributor=user,
                            title=activity_title, shorttitle=activity_title[:16],
                            module=module, description=descr)
        activity.save()

        url = data.get("url", "")
        if not url:
            # Default url
            url = "https://comin-ocw.org/contents/%s/camera.mp4" % dirname.split('/contents/')[-1]
        vid = Video(creator=user, contributor=user,
                    activity=activity,
                    title=activity_title,
                    shorttitle=activity_title[:16],
                    url=url)
        # Note: length is not initialized. We will get its duration
        # from the package just below.
        pic = os.path.join(dirname, 'imagecache', '00.png')
        if not os.path.exists(pic):
            pic = os.path.join(dirname, 'imagecache', '000.png')
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
            # Update video length
            vid.length = package['medias'][0]['meta']['dc:duration'] / 1000.0
            vid.slug = package['medias'][0]['id']
            ats = {}
            for atjson in package['annotation-types']:
                try:
                    at = AnnotationType.objects.get(title=atjson['dc:title'])
                except AnnotationType.DoesNotExist:
                    # Create the AnnotationType matching dc:title
                    at = AnnotationType(creator=user,
                                        title=atjson['dc:title'],
                                        description=atjson['dc:description'])
                    at.save()
                ats[atjson['id']] = at
            self.stdout.write("Copying %d annotations" % len(package['annotations']))
            for a in package['annotations']:
                at = ats[a['meta']['id-ref']]
                self.stdout.write(".", ending="")
                self.stdout.flush()
                an = Annotation(creator=user, contributor=user,
                                annotationtype=at,
                                video=vid,
                                begin=a['begin'] / 1000.0,
                                end=a['end'] / 1000.0,
                                title=a['content']['title'],
                                description=a['content']['description'])
                if 'data' in a['content']:
                    an.contenttype = a['content'].get('mimetype', 'text/plain')
                    an.contentdata = json.dumps(a['content']['data'])
                if 'img' in a['content']:
                    pic = os.path.join(dirname, a['content']['img']['src'])
                    with open(pic, 'rb') as f:
                        an.thumbnail.save(os.path.basename(pic), File(f))
                an.save()

    def _postnews(self, title, subtitle, data):
        """Post a newsitem message.
        """
        user = User.objects.get(pk=1)
        n = Newsitem(creator=user, title=title, subtitle=subtitle, description=data)
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

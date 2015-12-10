# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import urllib
import logging
import dateutil.parser

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.core.files import File
from django.utils.timezone import make_naive, is_aware

from coco.models import Activity, Channel, Video, Chapter, Annotation, Newsitem, AnnotationType, License

logger = logging.getLogger(__name__)


def convert_date(d):
    if is_aware(d):
        d = make_naive(d)
    return d

REGISTERED = {}


def register(f):
    REGISTERED[f.__name__.strip('_')] = f
    return f


def get_group(annotationtype):
    """Return the group corresponding to a given annotation type
    """
    g = re.search("at_converted(\d+)", annotationtype)
    if g:
        group, created = Group.objects.get_or_create(name='Groupe ' + g.group(1))
    else:
        group = None
    return group


def get_user(username, context=None):
    if username == "":
        username = "anonyme"
    username = username.lower()
    user, created = User.objects.get_or_create(username=username)
    # Create groups matching at_converted\d+ annotation types
    if created and context is not None and username != 'anonyme':
        g = get_group(context)
        if g:
            g.user_set.add(user)
    return user


class Command(BaseCommand):
    args = '[command] [param]'
    help = """Administration commands for COCo
"""

    @register
    def _info(self, channel, info):
        """Import video/channel info from info.json files. Params: channel_title info.json
        """
        with open(info, 'r') as f:
            data = json.load(f)
        self.stdout.write("Saving %s\n" % data.get("title"))

        adminuser = get_user('admin')
        dirname = os.path.dirname(os.path.abspath(info))
        try:
            c = Channel.objects.get(title=channel)
        except Channel.DoesNotExist:
            c = Channel(creator=adminuser, contributor=adminuser, title=channel)
            c.save()

        title = data.get("title", "Titre inconnu")
        if title.startswith("Langage C -"):
            title = title.replace("Langage C -", "")

        try:
            chapter = Chapter.objects.get(title=title, channel=c)
        except Chapter.DoesNotExist:
            chapter = Chapter(creator=adminuser, contributor=adminuser, channel=c, title=title)
            chapter.save()

        descr = "%s - %s" % (data.get("date", "Date inconnue"),
                             data.get("author", "Auteur inconnu"))
        activity = Activity(creator=adminuser, contributor=adminuser,
                            title=title,
                            chapter=chapter, description=descr)
        activity.save()

        url = data.get("url", "")
        if not url:
            # Default url
            url = "https://comin-ocw.org/contents/%s/camera.mp4" % dirname.split('/contents/')[-1]
        vid = Video(creator=adminuser, contributor=adminuser,
                    activity=activity,
                    title=title,
                    url=url)
        # Note: length is not initialized. We will get its duration
        # from the package just below.

        # Migrate license info
        licenses = [license
                    for license in ('cc-by', 'cc-by-nc', 'cc-by-sa', 'cc-by-nc-sa')
                    if data.get(license)]
        if licenses:
            # Associate license
            vid.license = License.objects.get(slug=licenses[0])
        pic = os.path.join(dirname, 'imagecache', '00.png')
        if not os.path.exists(pic):
            pic = os.path.join(dirname, 'imagecache', '000.png')
        if os.path.exists(pic):
            with open(pic, 'rb') as f:
                vid.thumbnail.save(os.path.basename(pic), File(f))
            if not vid.activity.thumbnail:
                # Use same thumbnail
                with open(pic, 'rb') as f:
                    vid.activity.thumbnail.save(os.path.basename(pic), File(f))
                vid.activity.save()
            if not vid.activity.chapter.thumbnail:
                # Use same thumbnail
                with open(pic, 'rb') as f:
                    vid.activity.chapter.thumbnail.save(os.path.basename(pic), File(f))
                vid.activity.chapter.save()
            if not vid.activity.chapter.channel.thumbnail:
                # Use same thumbnail
                with open(pic, 'rb') as f:
                    vid.activity.chapter.channel.thumbnail.save(os.path.basename(pic), File(f))
                vid.activity.chapter.channel.save()
        vid.save()

        # Read data.json if available
        packageurl = data.get('dataurl', os.path.join(dirname, 'data.json'))
        if packageurl.startswith('http') or os.path.exists(packageurl):
            self.stdout.write("Loading data from %s" % packageurl)
            f = urllib.urlopen(packageurl)
            try:
                package = json.loads("".join(f.readlines()))
            except ValueError:
                package = {}
                f.close()
            if not package:
                print "************* Empty package: %s" % packageurl
                return
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
                an = Annotation(creator=get_user(creator, context=a['meta']['id-ref']),
                                contributor=get_user(contributor, context=a['meta']['id-ref']),
                                created=convert_date(dateutil.parser.parse(a['meta']['dc:created'])),
                                modified=convert_date(dateutil.parser.parse(a['meta']['dc:modified'])),
                                annotationtype=at,
                                video=vid,
                                begin=long(a['begin']) / 1000.0,
                                end=long(a['end']) / 1000.0,
                                title=title,
                                group=get_group(a['meta']['id-ref']),
                                description=a['content']['description'])
                # FIXME: handle tags
                if 'data' in a['content']:
                    an.contenttype = a['content'].get('mimetype', 'text/plain')
                    an.contentdata = json.dumps(a['content']['data'])
                elif 'level' in a['content']:
                    an.contenttype = 'application/json'
                    an.contentdata = json.dumps({'level': a['content']['level']})
                if 'img' in a['content']:
                    pic = os.path.join(dirname, a['content']['img']['src'])
                    if os.path.exists(pic):
                        with open(pic, 'rb') as f:
                            an.thumbnail.save(os.path.basename(pic), File(f))
                an.save()
                for t in tags:
                    an.tags.add(t)

    @register
    def _postnews(self, title, subtitle, data):
        """Post a newsitem message.
        """
        adminuser = User.objects.get(username='admin')
        n = Newsitem(creator=adminuser, title=title, subtitle=subtitle, description=data)
        n.save()

    @register
    def add_to_group(self, groupname, *names):
        """Add specified usernames to given groupname, creating items as necessary.
        """
        g, created = Group.objects.get_or_create(name=groupname)
        for username in names:
            u = get_user(username)
            g.user_set.add(u)

    def handle(self, *args, **options):
        self.help = self.help + "\n\n" + "\n\n".join("\t%s: %s" % (k, v.__doc__) for (k, v) in REGISTERED.items())
        if not args:
            self.print_help(sys.argv[0], sys.argv[1])
            return
        command = args[0]
        # We registered unbound methods, so put self as first parameter when calling
        args = [self] + list(args[1:])
        m = REGISTERED.get(command)
        if m is not None:
            m(*args)
        else:
            raise CommandError("Unknown command")

# -*- coding: utf-8 -*-

from argparse import RawDescriptionHelpFormatter
import dateutil.parser
import inspect
import json
import os
import logging
import re
import subprocess
import sys
import urllib

from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.core.files import File
from django.utils.timezone import make_naive, is_aware
from django.utils.text import slugify

from coco.models import Activity, Channel, Video, Chapter, Annotation, Newsitem, AnnotationType, License, UserMetadata
from coco.models import VISIBILITY_PUBLIC, VISIBILITY_GROUP, VISIBILITY_PRIVATE, TYPE_SLIDES

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
    g = re.search("at_converted(\d*)", annotationtype)
    if g:
        group, created = Group.objects.get_or_create(name='Groupe ' + (g.group(1) or "0"))
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

        adminuser = get_user('coco')
        dirname = os.path.dirname(os.path.abspath(info))
        try:
            c = Channel.objects.get(title=channel)
        except Channel.DoesNotExist:
            c = Channel(creator=adminuser, contributor=adminuser, title=channel, slug=slugify(channel))
            c.save()

        title = data.get("title", "Titre inconnu")
        if title.startswith("Langage C -"):
            title = title.replace("Langage C -", "")

        try:
            chapter = Chapter.objects.get(title=title, channel=c)
        except Chapter.DoesNotExist:
            chapter = Chapter(creator=adminuser, contributor=adminuser, channel=c, title=title, slug=slugify(title))
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
        pic = os.path.join(dirname, 'thumbnail.jpg')
        if not os.path.exists(pic):
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
            f = urllib.urlopen(packageurl.replace('https', 'http'))
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
                slug = slugify(title)
            else:
                vid.slug = slug
            vid.save()
            ats = {}
            for atjson in package['annotation-types']:
                sl = slugify(atjson['dc:title'])
                try:
                    at = AnnotationType.objects.get(slug=sl)
                except AnnotationType.DoesNotExist:
                    # Create the AnnotationType matching dc:title/slug
                    at = AnnotationType(creator=adminuser,
                                        created=convert_date(dateutil.parser.parse(atjson['dc:created'])),
                                        title=atjson['dc:title'],
                                        slug=sl,
                                        description=atjson['dc:description'])
                    at.save()
                ats[atjson['id']] = at

            if 'Notes' not in ats:
                at = AnnotationType.objects.get_or_create(title="Notes",
                                                          slug=slugify("Notes"),
                                                          defaults={
                                                              'creator': adminuser,
                                                              'description': "User note"
                                                          })[0]
                ats["Notes"] = at

            self.stdout.write("Copying %d annotations" % len(package['annotations']))
            for a in package['annotations']:
                if a['meta']['id-ref'] == "at_contributions":
                    at = ats['Notes']
                else:
                    at = ats[a['meta']['id-ref']]
                self.stdout.write(".", ending="")
                self.stdout.flush()
                tags = []
                creator = get_user(a['meta']['dc:creator'])
                contributor = get_user(a['meta']['dc:contributor'])
                title = a['content']['title']
                description = a['content']['description']
                group = get_group(a['meta']['id-ref'])
                visibility = VISIBILITY_PRIVATE
                if group is not None:
                    visibility = VISIBILITY_GROUP
                    # Use "Notes" type since we now have the group information
                    at = ats['Notes']
                if at.title not in ('Quiz', 'QuizPerso', TYPE_SLIDES, 'Partie'):
                    description = description or title
                    title = ""
                if at.title in ('Quiz', TYPE_SLIDES, 'Partie'):
                    visibility = VISIBILITY_PUBLIC
                    creator = contributor = get_user('coco')
                if 'public' in at.title.lower():
                    visibility = VISIBILITY_PUBLIC
                    at = ats['Notes']
                m = re.match("^\[([\w-]+,)?(\w+)](.*)", description)
                if m:
                    creator = contributor = get_user(m.group(2), context=a['meta']['id-ref'])
                    if m.group(1) is not None:
                        tags.append(m.group(1).strip(',').strip().lower())
                    description = m.group(3).strip()
                if group and not creator in group.user_set.all():
                    group.user_set.add(creator)
                an = Annotation(creator=creator,
                                contributor=contributor,
                                created=convert_date(dateutil.parser.parse(a['meta']['dc:created'])),
                                modified=convert_date(dateutil.parser.parse(a['meta']['dc:modified'])),
                                annotationtype=at,
                                video=vid,
                                begin=long(a['begin']) / 1000.0,
                                end=long(a['end']) / 1000.0,
                                title=title,
                                visibility=visibility,
                                group=group,
                                description=description)
                # FIXME: handle tags
                if 'data' in a['content']:
                    an.contenttype = a['content'].get('mimetype', 'text/plain')
                    an.contentdata = json.dumps(a['content']['data'])
                elif 'level' in a['content']:
                    an.contenttype = 'application/json'
                    an.contentdata = json.dumps({'level': a['content']['level']})
                elif at.title == TYPE_SLIDES:
                    # Enforce level 1
                    an.contenttype = 'application/json'
                    an.contentdata = json.dumps({'level': 1})

                if 'img' in a['content']:
                    img = a['content']['img']['src']
                    if ('note.png' not in img and 'contribution.svg' not in img):
                        pic = os.path.join(dirname, a['content']['img']['src'])
                        if os.path.exists(pic):
                            with open(pic, 'rb') as f:
                                an.thumbnail.save(os.path.basename(pic), File(f))
                an.save()
                for t in tags:
                    an.tags.add(t.lower())

    @register
    def _postnews(self, title, subtitle, data):
        """Post a newsitem message.
        """
        adminuser = User.objects.get(username='coco')
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

    @register
    def loremipsum(self):
        """Fill data with loremipsum gibberish
        """
        from loremipsum import Generator
        gen = Generator(dictionary=[ unicode(u.strip(), 'utf8') for u in open('/usr/share/dict/french').readlines() ])
        for g in Group.objects.filter(Q(metadata__description="") | Q(metadata__description__isnull=True)):
            g.metadata.description = gen.generate_sentence()[2]
            g.metadata.save()
        for o in Channel.objects.filter(Q(description="") | Q(description__isnull=True)):
        #for o in Video.objects.all():
            o.description = gen.generate_paragraph()[2]
            o.save()

    @register
    def check(self, fixup=False):
        """Check information consistency
        """
        # Check that all slides annotation are public
        private_slides = Annotation.objects.filter(annotationtype__title=TYPE_SLIDES).exclude(visibility=VISIBILITY_PUBLIC).values('video').distinct()
        if private_slides.count():
            self.stdout.write("There are non-public slides on the following videos:\n" +
                              "\n".join(unicode(v) for v in Video.objects.in_bulk(private_slides.values_list('video', flat=True)).values()))
            if fixup:
                private_slides.update(visibility=VISIBILITY_PUBLIC)

        # Check that all slides content is application/json type
        noncompliant_slides = Annotation.objects.filter(annotationtype__title=TYPE_SLIDES).exclude(contenttype='application/json')
        if noncompliant_slides.count():
            self.stdout.write("There are slides with non JSON content type:\n" +
                              "\n".join("[%s] %s" % (a.contenttype, a.contentdata) for a in noncompliant_slides))
            if fixup:
                # Fixup only slides with empty contentdata
                noncompliant_slides.filter(contentdata="").update(contenttype="application/json",
                                                                  contentdata="{}")

        anon = get_user('anonyme')
        # Check that users that created group annotations are present in groups
        for g in Group.objects.all():
            users = set( a.creator for a in g.annotation_set.all() ) - {anon}
            for u in users:
                if not u in g.user_set.all():
                    self.stdout.write("User %s not in group %s but created group annotations" % (u.username, g.name))
                if fixup:
                    g.user_set.add(u)

        def check_foreign_key(model, field):
            foreign_model = field.related.model
            def check_instance(instance):
                try:
                    getattr(instance, field.name)
                    return True
                except ObjectDoesNotExist:
                    print '%s with pk %s refers via field %s to nonexistent %s with pk %s' % \
                        (model.__class__, str(instance.pk), field.name, foreign_model.__class__, getattr(instance, field.attname))
            return check_instance

        # Data integrity check
        coco = models.get_app('coco')
        for model in models.get_models(coco):
            if hasattr(model, 'creator'):
                # Check creator
                missing = model.objects.filter(creator=None)
                if missing.count():
                    self.stdout.write("Missing creator for %s (%d)" % (model.__name__, missing.count()))
            for field in model._meta.local_fields + model._meta.local_many_to_many + model._meta.virtual_fields:
                if isinstance(field, models.ForeignKey):
                    check_foreign_key(model, field)

    @register
    def publish(self, channeltitle, url, title=""):
        """Publish the video (channeltitle, url, title)
        """
        adminuser = get_user('coco')
        try:
            channel = Channel.objects.get(Q(slug=channeltitle) | Q(title=channeltitle))
        except:
            channel = Channel(creator=adminuser, contributor=adminuser, title=channeltitle, slug=slugify(channeltitle))
            channel.save()

        if not title:
            title = os.path.basename(url)
        slug = slugify(title)
        try:
            chapter = Chapter.objects.get(title=title, channel=channel)
        except Chapter.DoesNotExist:
            chapter = Chapter(creator=adminuser, contributor=adminuser, channel=channel, title=title, slug=slug)
            chapter.save()

        activity = Activity(creator=adminuser, contributor=adminuser,
                            title=title,
                            slug=slug,
                            chapter=chapter)
        activity.save()

        # Get length
        duration = 0
        dur = subprocess.check_output('gst-discoverer-1.0 "%s" | grep Duration' % url, shell=True)
        if dur:
            info = re.search('(\d+):(\d+):(\d+.\d+)', dur)
            if info:
                duration = float(info.group(1)) * 24 * 60 + float(info.group(2)) * 60 + float(info.group(3))

        vid = Video(creator=adminuser, contributor=adminuser,
                    activity=activity,
                    title=title,
                    url=url,
                    slug=slug,
                    duration=duration)

        # Save anyway, so that we have a valid video even if thumbnailing fails
        vid.save()
        # Get thumbnail
        thumbnail_name = os.tmpnam() + ".jpg"
        # Low-dependency thumbnailer
        subprocess.call('gst-launch-1.0 gnlurisource "uri=%s" start=4000000 duration=2000000 ! videoconvert ! jpegenc ! filesink location=%s' % (url, thumbnail_name), shell=True)
        if os.path.exists(thumbnail_name):
            with open(thumbnail_name, 'rb') as f:
                vid.thumbnail.save(os.path.basename(thumbnail_name), File(f))
            for o in (vid.activity, vid.activity.chapter, vid.activity.chapter.channel):
                if not o.thumbnail:
                    # Use same thumbnail
                    with open(thumbnail_name, 'rb') as f:
                        o.thumbnail.save(os.path.basename(thumbnail_name), File(f))
                        o.save()
            os.unlink(thumbnail_name)
        vid.save()

    @register
    def fix_user_metadata(self):
        """Fix UserMetadata.config fields after a loaddata
        """
        for u in UserMetadata.objects.exclude(config=None):
            if isinstance(u.config, basestring):
                # Wrong field, probably bad serialization
                # Try to restore json data from python serialization
                try:
                    data = json.loads(u.config.lower().replace("u'", "'").replace("'", '"'))
                    print "Fixed config for %s" % u.user.username
                    u.config = data
                    u.save()
                except ValueError:
                    print "Impossible to fix config metadata for %s" % u.user.username

    @register
    def create_user(self, email, username="", fullname=""):
        """Create a new user.
        """
        if not username:
            username = email[:email.index('@')]
        if ' ' in fullname:
            first_name, last_name = fullname.split(" ", 1)
        elif '.' in fullname:
            first_name, last_name = fullname.split(".", 1)
        else:
            first_name = fullname
            last_name = ''
        username = username.lower()
        user, created = User.objects.get_or_create(username=username,
                                                   defaults={ 'email': email,
                                                              'first_name': first_name,
                                                              'last_name': last_name })
        if created:
            self.stdout.write("Created user %s (%s)" % (username, email))
        else:
            self.stdout.write("User %s already exists" % username)

    def add_arguments(self, parser):
        def arg_signature(f):
            spec = inspect.getargspec(f)
            if spec.varargs:
                args = spec.args[1:] + ['*' + spec.varargs]
            else:
                args = spec.args[1:] or ["[none]"]
            return ", ".join(args)

        self.help = self.help + "\n".join("%s - %s\n\tParameters: %s" % (k, v.__doc__.strip(), arg_signature(v)) for (k, v) in REGISTERED.items())
        parser.formatter_class = RawDescriptionHelpFormatter

    def handle(self, *args, **options):
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

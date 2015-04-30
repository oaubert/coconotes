# -*- coding: utf-8 -*-

import sys
import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import json

from coco.models import Activity, Course, Video, Module, License, Annotation, Comment, Resource, Newsitem

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
                    title=activity_title, shorttitle=activity_title[:16], url=url)
        vid.save()

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


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coco', '0004_add_group_info'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercontent',
            old_name='syllabus',
            new_name='contentdata',
        ),
        migrations.AddField(
            model_name='usercontent',
            name='contenttype',
            field=models.CharField(default=b'text/plain', max_length=127, verbose_name=b'Content-Type', blank=True),
        ),
    ]

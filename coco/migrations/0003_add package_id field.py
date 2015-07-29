# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coco', '0002_auto_20150430_0829'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='package_id',
            field=models.CharField(help_text=b'Package identifier', max_length=255, verbose_name=b'Package id', blank=True),
        ),
    ]

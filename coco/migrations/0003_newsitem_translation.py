# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coco', '0002_data_licenses'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsitem',
            name='description_en',
            field=models.TextField(verbose_name='Description (english)', blank=True),
        ),
        migrations.AddField(
            model_name='newsitem',
            name='title_en',
            field=models.CharField(max_length=250, verbose_name='Title (english)', blank=True),
        ),
    ]

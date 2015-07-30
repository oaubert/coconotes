# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('coco', '0003_add package_id field'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotation',
            name='group',
            field=models.ForeignKey(to='auth.Group', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='group',
            field=models.ForeignKey(to='auth.Group', null=True),
        ),
    ]

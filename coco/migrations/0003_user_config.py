# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('coco', '0002_data_licenses'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'activity', 'verbose_name_plural': 'activities'},
        ),
        migrations.AlterModelOptions(
            name='annotation',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'annotation', 'verbose_name_plural': 'annotations'},
        ),
        migrations.AlterModelOptions(
            name='annotationtype',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'annotation type', 'verbose_name_plural': 'annotation types', 'permissions': (('slide_update', 'Can update slide content'), ('slide_delete', 'Can delete slide content'), ('slide_add', 'Can add slide content'))},
        ),
        migrations.AlterModelOptions(
            name='channel',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'channel', 'verbose_name_plural': 'channels'},
        ),
        migrations.AlterModelOptions(
            name='chapter',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'chapter', 'verbose_name_plural': 'chapters'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'comment', 'verbose_name_plural': 'comments'},
        ),
        migrations.AlterModelOptions(
            name='groupmetadata',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'group metadata', 'verbose_name_plural': 'group metadata'},
        ),
        migrations.AlterModelOptions(
            name='newsitem',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'news item', 'verbose_name_plural': 'news items'},
        ),
        migrations.AlterModelOptions(
            name='resource',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify'},
        ),
        migrations.AlterModelOptions(
            name='usercontent',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify'},
        ),
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ('-promoted', '-modified', 'title'), 'get_latest_by': 'modify', 'verbose_name': 'video', 'verbose_name_plural': 'videos'},
        ),
        migrations.AddField(
            model_name='usermetadata',
            name='config',
            field=annoying.fields.JSONField(null=True, verbose_name='Configuration', blank=True),
        ),
    ]

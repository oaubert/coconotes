# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sorl.thumbnail.fields
import datetime
import taggit_autosuggest.managers
import coco.models
import coco.fields
from django.conf import settings
import annoying.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'activity',
                'verbose_name_plural': 'activities',
            },
        ),
        migrations.CreateModel(
            name='AnnotationType',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
                ('contributor', models.ForeignKey(related_name='modified_annotationtype', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_annotationtype', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'annotation type',
                'verbose_name_plural': 'annotation types',
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
                ('category', models.CharField(max_length=20, verbose_name='Category', blank=True)),
                ('syllabus', models.TextField(verbose_name='Syllabus', blank=True)),
                ('contributor', models.ForeignKey(related_name='modified_channel', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_channel', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'channel',
                'verbose_name_plural': 'channels',
            },
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
                ('channel', models.ForeignKey(to='coco.Channel')),
                ('contributor', models.ForeignKey(related_name='modified_chapter', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_chapter', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'chapter',
                'verbose_name_plural': 'chapters',
            },
        ),
        migrations.CreateModel(
            name='GroupMetadata',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
                ('contributor', models.ForeignKey(related_name='modified_groupmetadata', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_groupmetadata', to=settings.AUTH_USER_MODEL)),
                ('group', annoying.fields.AutoOneToOneField(to='auth.Group')),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=16, unique=True, null=True, blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('url', models.URLField(max_length=250, verbose_name='URL', blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(upload_to=b'thumbnails')),
            ],
        ),
        migrations.CreateModel(
            name='Newsitem',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
                ('category', models.CharField(default=b'', max_length=64, verbose_name='Category', blank=True)),
                ('published', models.DateTimeField(help_text='Publication date', null=True, verbose_name='Publication date')),
                ('contributor', models.ForeignKey(related_name='modified_newsitem', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_newsitem', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'news item',
                'verbose_name_plural': 'news items',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
                ('url', models.URLField(max_length=250, verbose_name='URL', blank=True)),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='coco.Activity')),
                ('tag', models.ForeignKey(related_name='coco_taggedactivity_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedAnnotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.ForeignKey(related_name='coco_taggedannotation_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='coco.Channel')),
                ('tag', models.ForeignKey(related_name='coco_taggedchannel_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedChapter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='coco.Chapter')),
                ('tag', models.ForeignKey(related_name='coco_taggedchapter_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.ForeignKey(related_name='coco_taggedcomment_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.ForeignKey(related_name='coco_taggedvideo_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserContent',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text='Element creation date', null=True, verbose_name='Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text='Element modification date', null=True, verbose_name='Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name='State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('slug', coco.fields.SlugOrNullField(max_length=128, unique=True, null=True, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('promoted', models.IntegerField(default=0, help_text='Promoted level - 0 by default', verbose_name='Promoted')),
                ('contentdata', models.TextField(verbose_name='Content', blank=True)),
                ('contenttype', models.CharField(default=b'text/plain', max_length=127, verbose_name='Content-Type', blank=True)),
                ('visibility', models.SmallIntegerField(default=1, help_text='Content visibility', verbose_name='Visibility', choices=[(1, 'Private'), (2, 'Group'), (3, 'Public')])),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250, verbose_name='Title', blank=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('user', annoying.fields.AutoOneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('usercontent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='coco.UserContent')),
                ('begin', models.FloatField(default=0, help_text='Annotation begin time (in seconds)', verbose_name='Begin')),
                ('end', models.FloatField(default=0, help_text='Annotation end time (in seconds)', verbose_name='End')),
                ('annotationtype', models.ForeignKey(to='coco.AnnotationType', null=True)),
                ('group', models.ForeignKey(blank=True, to='auth.Group', null=True)),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'annotation',
                'verbose_name_plural': 'annotations',
            },
            bases=('coco.usercontent',),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('usercontent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='coco.UserContent')),
                ('group', models.ForeignKey(blank=True, to='auth.Group', null=True)),
                ('parent_annotation', models.ForeignKey(blank=True, to='coco.Annotation', null=True)),
                ('parent_comment', models.ForeignKey(blank=True, to='coco.Comment', null=True)),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
            },
            bases=('coco.usercontent',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('resource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='coco.Resource')),
                ('duration', models.FloatField(default=0, help_text='Video duration in seconds', verbose_name='Duration')),
            ],
            options={
                'ordering': ('-promoted', '-modified', 'title'),
                'abstract': False,
                'verbose_name': 'video',
                'verbose_name_plural': 'videos',
            },
            bases=('coco.resource',),
        ),
        migrations.AddField(
            model_name='usercontent',
            name='contributor',
            field=models.ForeignKey(related_name='modified_usercontent', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='usercontent',
            name='creator',
            field=models.ForeignKey(related_name='created_usercontent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resource',
            name='contributor',
            field=models.ForeignKey(related_name='modified_resource', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='creator',
            field=models.ForeignKey(related_name='created_resource', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resource',
            name='license',
            field=models.ForeignKey(blank=True, to='coco.License', null=True),
        ),
        migrations.AddField(
            model_name='chapter',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='coco.TaggedChapter', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='teachers',
            field=models.ManyToManyField(related_name='teacher_for', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channel',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='coco.TaggedChannel', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='activity',
            name='chapter',
            field=models.ForeignKey(to='coco.Chapter'),
        ),
        migrations.AddField(
            model_name='activity',
            name='contributor',
            field=models.ForeignKey(related_name='modified_activity', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='creator',
            field=models.ForeignKey(related_name='created_activity', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='activity',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='coco.TaggedActivity', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='video',
            name='activity',
            field=models.ForeignKey(blank=True, to='coco.Activity', null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='slides',
            field=models.ForeignKey(related_name='source_video', blank=True, to='coco.Resource', null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='coco.TaggedVideo', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='taggedvideo',
            name='content_object',
            field=models.ForeignKey(to='coco.Video'),
        ),
        migrations.AddField(
            model_name='taggedcomment',
            name='content_object',
            field=models.ForeignKey(to='coco.Comment'),
        ),
        migrations.AddField(
            model_name='taggedannotation',
            name='content_object',
            field=models.ForeignKey(to='coco.Annotation'),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent_video',
            field=models.ForeignKey(blank=True, to='coco.Video', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='coco.TaggedComment', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='coco.TaggedAnnotation', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='video',
            field=models.ForeignKey(to='coco.Video'),
        ),
    ]

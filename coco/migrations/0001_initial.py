# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import datetime
import taggit_autosuggest.managers
import coco.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text=b'Element creation date', null=True, verbose_name=b'Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text=b'Element modification date', null=True, verbose_name=b'Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name=b'State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title', blank=True)),
                ('shorttitle', models.CharField(max_length=16, verbose_name=b'Shorttitle', blank=True)),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('contributor', models.ForeignKey(related_name='modified_activity', to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_activity', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text=b'Element creation date', null=True, verbose_name=b'Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text=b'Element modification date', null=True, verbose_name=b'Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name=b'State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title', blank=True)),
                ('shorttitle', models.CharField(max_length=16, verbose_name=b'Shorttitle', blank=True)),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('category', models.CharField(max_length=20, verbose_name=b'Category', blank=True)),
                ('syllabus', models.TextField(verbose_name=b'Syllabus', blank=True)),
                ('contributor', models.ForeignKey(related_name='modified_course', to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_course', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=16)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title', blank=True)),
                ('url', models.URLField(max_length=250, verbose_name=b'URL', blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(upload_to=b'thumbnails')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text=b'Element creation date', null=True, verbose_name=b'Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text=b'Element modification date', null=True, verbose_name=b'Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name=b'State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title', blank=True)),
                ('shorttitle', models.CharField(max_length=16, verbose_name=b'Shorttitle', blank=True)),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('contributor', models.ForeignKey(related_name='modified_module', to=settings.AUTH_USER_MODEL, null=True)),
                ('course', models.ForeignKey(to='coco.Course')),
                ('creator', models.ForeignKey(related_name='created_module', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Newsitem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text=b'Element creation date', null=True, verbose_name=b'Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text=b'Element modification date', null=True, verbose_name=b'Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name=b'State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title', blank=True)),
                ('shorttitle', models.CharField(max_length=16, verbose_name=b'Shorttitle', blank=True)),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('subtitle', models.CharField(default=b'', max_length=64, verbose_name=b'Category', blank=True)),
                ('published', models.DateTimeField(help_text=b'Publication date', null=True, verbose_name=b'Publication date')),
                ('contributor', models.ForeignKey(related_name='modified_newsitem', to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='created_newsitem', to=settings.AUTH_USER_MODEL)),
                ('tags', taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text=b'Element creation date', null=True, verbose_name=b'Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text=b'Element modification date', null=True, verbose_name=b'Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name=b'State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title', blank=True)),
                ('shorttitle', models.CharField(max_length=16, verbose_name=b'Shorttitle', blank=True)),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('url', models.URLField(max_length=250, verbose_name=b'URL', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now, help_text=b'Element creation date', null=True, verbose_name=b'Creation date')),
                ('modified', coco.models.AutoDateTimeField(help_text=b'Element modification date', null=True, verbose_name=b'Modification date')),
                ('state', models.CharField(default=b'draft', max_length=16, verbose_name=b'State', blank=True)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title', blank=True)),
                ('shorttitle', models.CharField(max_length=16, verbose_name=b'Shorttitle', blank=True)),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('thumbnail', sorl.thumbnail.fields.ImageField(null=True, upload_to=b'thumbnails', blank=True)),
                ('syllabus', models.TextField(verbose_name=b'Content', blank=True)),
                ('visibility', models.CharField(default=b'private', help_text=b'Visibility (private, group, public)', max_length=16, verbose_name=b'Visibility')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('usercontent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='coco.UserContent')),
                ('begin', models.FloatField(default=0, help_text=b'Annotation begin time (in seconds)', verbose_name=b'Begin')),
                ('end', models.FloatField(default=0, help_text=b'Annotation end time (in seconds)', verbose_name=b'End')),
                ('category', models.CharField(default=b'', help_text=b'Category (question, suggestion...)', max_length=64, verbose_name=b'Category', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('coco.usercontent',),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('usercontent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='coco.UserContent')),
                ('parent_annotation', models.ForeignKey(to='coco.Annotation', null=True)),
                ('parent_comment', models.ForeignKey(to='coco.Comment', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('coco.usercontent',),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('resource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='coco.Resource')),
                ('length', models.FloatField(default=0, help_text=b'Video length in seconds', verbose_name=b'Length')),
            ],
            options={
                'abstract': False,
            },
            bases=('coco.resource',),
        ),
        migrations.AddField(
            model_name='usercontent',
            name='contributor',
            field=models.ForeignKey(related_name='modified_usercontent', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='usercontent',
            name='creator',
            field=models.ForeignKey(related_name='created_usercontent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usercontent',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='resource',
            name='contributor',
            field=models.ForeignKey(related_name='modified_resource', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='creator',
            field=models.ForeignKey(related_name='created_resource', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resource',
            name='license',
            field=models.ForeignKey(to='coco.License', null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='activity',
            name='module',
            field=models.ForeignKey(to='coco.Module'),
        ),
        migrations.AddField(
            model_name='activity',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='video',
            name='activity',
            field=models.ForeignKey(to='coco.Activity', null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='slides',
            field=models.ForeignKey(related_name='source_video', to='coco.Resource', null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent_video',
            field=models.ForeignKey(to='coco.Video', null=True),
        ),
        migrations.AddField(
            model_name='annotation',
            name='video',
            field=models.ForeignKey(to='coco.Video'),
        ),
    ]

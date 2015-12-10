from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import Group

from rest_framework.routers import DefaultRouter
from ajax_select import urls as ajax_select_urls

import coco.views as views
from .models import Channel, Chapter, Activity, Video, Newsitem, Resource

uuid_regexp = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'resource', views.ResourceViewSet)
router.register(r'channel', views.ChannelViewSet)
router.register(r'chapter', views.ChapterViewSet)
router.register(r'activity', views.ActivityViewSet)
router.register(r'video', views.VideoViewSet)
router.register(r'annotation', views.AnnotationViewSet)
router.register(r'annotationtype', views.AnnotationTypeViewSet)
router.register(r'news', views.NewsitemViewSet)

urlpatterns = patterns('',
                       url(r'^$', views.home, name='root'),

                       url(r'^i18n/', include('django.conf.urls.i18n')),

                       url(r'^accounts/profile', views.profile, name='profile'),

                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

                       url(r'^search/$', views.search, name='search'),

                       url(r'^channel/$', ListView.as_view(model=Channel), name='view-channel-list'),
                       url(r'^channel/(?P<pk>%s)/$' % uuid_regexp,
                           DetailView.as_view(model=Channel, context_object_name='channel'),
                           name='view-channel-detail'),
                       url(r'^channel/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Channel, context_object_name='channel'), name='view-channel-detail'),
                       url(r'^chapter/$', ListView.as_view(model=Chapter), name='chapter-list'),
                       url(r'^chapter/(?P<pk>%s)/$' % uuid_regexp,
                           DetailView.as_view(model=Chapter, context_object_name='chapter'),
                           name='view-chapter-detail'),
                       url(r'^chapter/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Chapter, context_object_name='chapter'), name='view-chapter-detail'),
                       url(r'^activity/$', ListView.as_view(model=Activity), name='activity-list'),
                       url(r'^activity/(?P<pk>%s)/$' % uuid_regexp,
                           DetailView.as_view(model=Activity, context_object_name='activity'),
                           name='view-activity-detail'),
                       url(r'^activity/(?P<slug>[\w\d_-]+)/$',
                           DetailView.as_view(model=Activity, context_object_name='activity'),
                           name='view-activity-detail'),
                       url(r'^video/$', ListView.as_view(model=Video), name='view-video-list'),
                       url(r'^video/(?P<pk>%s)/$' % uuid_regexp, DetailView.as_view(model=Video, context_object_name='video'), name='view-video-detail'),
                       url(r'^video/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Video, context_object_name='video'), name='view-video-detail'),
                       url(r'^video/(?P<pk>%s)/cinelab$' % uuid_regexp, views.cinelab, name='video-cinelab'),
                       url(r'^video/(?P<slug>[\w\d_-]+)/cinelab$', views.cinelab, name='video-cinelab-slug'),

                       url(r'^video/(?P<pk>%s)/info/$' % uuid_regexp,
                           DetailView.as_view(model=Video, template_name='coco/video_info.html'),
                           name='video-info'),
                       url(r'^video/(?P<slug>[\w\d_-]+)/info/$',
                           DetailView.as_view(model=Video, template_name='coco/video_info.html'),
                           name='video-info-slug'),

                       url(r'^resource/$', ListView.as_view(model=Resource), name='resource-view-list'),
                       url(r'^resource/(?P<pk>%s)/$' % uuid_regexp,
                           DetailView.as_view(model=Resource, context_object_name='resource'),
                           name='view-resource-detail'),
                       url(r'^resource/(?P<slug>[\w\d_-]+)/$',
                           DetailView.as_view(model=Resource, context_object_name='resource'),
                           name='view-resource-detail'),

                       url(r'^news/$', ListView.as_view(model=Newsitem), name='view-newsitem-list'),
                       url(r'^news/(?P<pk>%s)/$' % uuid_regexp,
                           DetailView.as_view(model=Newsitem, context_object_name='item'),
                           name='view-newsitem-detail'),
                       url(r'^news/(?P<slug>[\w\d_-]+)/$',
                           DetailView.as_view(model=Newsitem, context_object_name='item'),
                           name='view-newsitem-detail'),

                       url(r'^group/$', ListView.as_view(model=Group, template_name='group_list.html'), name='group-list'),
                       url(r'^group/(?P<pk>\d+)/$', DetailView.as_view(model=Group, template_name='group_detail.html'), name='group-detail'),

                       url(r'^annotation/add$', views.AnnotationCreateView.as_view(), name='view-annotation-create'),
                       url(r'^annotation/(?P<pk>[\w\d_-]+)/$', views.AnnotationDetailView.as_view(), name='view-annotation-detail'),
                       url(r'^annotation/(?P<pk>[\w\d_-]+)/edit/$', views.annotation_edit, name='view-annotation-update'),
                       url(r'^annotation/(?P<pk>[\w\d_-]+)/delete/$', views.AnnotationDeleteView.as_view(), name='view-annotation-delete'),

                       # REST API
                       url(r'^api/v1/annotation_add$', views.annotation_add, name='api-annotation-add'),
                       url(r'^api/v1/', include(router.urls)),

                       url(r'^ajax_select/', include(ajax_select_urls)),
                       )

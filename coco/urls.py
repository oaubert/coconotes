from django.conf.urls import url, include
from django.conf import settings
from django.views.generic import ListView, DetailView, TemplateView
import django.views.static
from django.views.defaults import page_not_found
from django.contrib.admin.views.decorators import staff_member_required

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

urlpatterns = [
    url(r'^$', views.home, name='root'),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^about/', TemplateView.as_view(template_name="about.html"), name='about'),
    url(r'^accounts/profile/log$', views.log_action, name='profile-log'),
    url(r'^accounts/profile/edit/?$', views.UpdateProfile.as_view(), name='profile-update'),
    url(r'^accounts/profile/(?P<name>.+)/form$', views.UserSettingForm.as_view(), name='profile-setting-form'),
    url(r'^accounts/profile/(?P<name>.+)$', views.UserSetting.as_view(), name='profile-setting'),
    url(r'^accounts/profile', views.profile, name='profile'),
    url(r'^user/(?P<username>.*)$', views.userprofile, name='profile-named'),

    url(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),

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
    url(r'^video/(?P<pk>%s)/$' % uuid_regexp, views.VideoDetailView.as_view(), name='view-video-detail'),
    url(r'^video/(?P<slug>[\w\d_-]+)/$', views.VideoDetailView.as_view(), name='view-video-detail'),
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

    url(r'^group/$', views.GroupListView.as_view(), name='group-list'),
    url(r'^group/(?P<pk>\d+)/$', views.GroupDetailView.as_view(), name='view-group-detail'),
    url(r'^group/(?P<pk>\d+)/activity$', views.GroupActivityView.as_view(), name='view-group-activity'),

    url(r'^annotation/add$', views.AnnotationCreateView.as_view(), name='view-annotation-create'),
    url(r'^annotation/(?P<pk>[\w\d_-]+)/$', views.AnnotationDetailView.as_view(), name='view-annotation-detail'),
    url(r'^annotation/(?P<pk>[\w\d_-]+)/edit/$', views.annotation_edit, name='view-annotation-update'),
    url(r'^annotation/(?P<pk>[\w\d_-]+)/delete/$', views.AnnotationDeleteView.as_view(), name='view-annotation-delete'),
    url(r'^annotation/(?P<pk>[\w\d_-]+)/level/$', views.slide_level, name='view-slide-level'),
    url(r'^annotation/(?P<pk>[\w\d_-]+)/toggle/(?P<prop>public|featured)/$', views.toggle_annotation, name='view-annotation-toggle'),
    url(r'^annotation/(?P<pk>[\w\d_-]+)/comment/$', views.annotation_comment, name='view-annotation-comment'),

    url(r'^comment/(?P<pk>[\w\d_-]+)/$', views.CommentDetailView.as_view(), name='view-comment-detail'),
    url(r'^comment/(?P<pk>[\w\d_-]+)/edit/$', views.comment_edit, name='view-comment-update'),

    url(r'^actions/dashboard$', staff_member_required(TemplateView.as_view(template_name="actstream/dashboard.html")), name='access-log'),

    # REST API
    url(r'^api/v1/annotation_add$', views.annotation_add, name='api-annotation-add'),
    url(r'^api/v1/access_log(.json)?$', views.access_log, name='api-access-log'),
    url(r'^api/v1/', include(router.urls)),

    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^404/$', page_not_found, ),
]

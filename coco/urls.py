from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic import ListView, DetailView
import coco.views as views
from .models import Course, Module, Activity, Video, Newsitem, Resource
from rest_framework.routers import DefaultRouter

uuid_regexp = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'resource', views.ResourceViewSet)
router.register(r'course', views.CourseViewSet)
router.register(r'module', views.ModuleViewSet)
router.register(r'activity', views.ActivityViewSet)
router.register(r'video', views.VideoViewSet)
router.register(r'annotation', views.AnnotationViewSet)
router.register(r'annotationtype', views.AnnotationTypeViewSet)
router.register(r'news', views.NewsitemViewSet)

urlpatterns = patterns('',
                       url(r'^$', views.home, name='root'),

                       url(r'^accounts/profile', views.profile, name='profile'),

                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

                       url(r'^search/$', views.search, name='search'),

                       url(r'^course/$', ListView.as_view(model=Course), name='course-list'),
                       url(r'^course/(?P<pk>%s)/$' % uuid_regexp, DetailView.as_view(model=Course, context_object_name='course'), name='course-detail'),
                       url(r'^course/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Course, context_object_name='course'), name='course-detail'),
                       url(r'^module/$', ListView.as_view(model=Module), name='module-list'),
                       url(r'^module/(?P<pk>%s)/$' % uuid_regexp, DetailView.as_view(model=Module, context_object_name='module'), name='module-detail'),
                       url(r'^module/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Module, context_object_name='module'), name='module-detail'),
                       url(r'^activity/$', ListView.as_view(model=Activity), name='activity-list'),
                       url(r'^activity/(?P<pk>%s)/$' % uuid_regexp, DetailView.as_view(model=Activity, context_object_name='activity'), name='activity-detail'),
                       url(r'^activity/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Activity, context_object_name='activity'), name='activity-detail'),
                       url(r'^video/$', ListView.as_view(model=Video), name='video-list'),
                       url(r'^video/(?P<pk>%s)/$' % uuid_regexp, DetailView.as_view(model=Video, context_object_name='video'), name='video-detail'),
                       url(r'^video/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Video, context_object_name='video'), name='video-detail'),
                       url(r'^video/(?P<pk>%s)/cinelab$' % uuid_regexp, views.cinelab, name='video-cinelab'),
                       url(r'^video/(?P<slug>[\w\d_-]+)/cinelab$', views.cinelab, name='video-cinelab'),

                       url(r'^resource/$', ListView.as_view(model=Resource), name='resource-list'),
                       url(r'^resource/(?P<pk>%s)/$' % uuid_regexp, DetailView.as_view(model=Resource, context_object_name='resource'), name='resource-detail'),
                       url(r'^resource/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Resource, context_object_name='resource'), name='resource-detail'),

                       url(r'^news/$', ListView.as_view(model=Newsitem), name='newsitem-list'),
                       url(r'^news/(?P<pk>%s)/$' % uuid_regexp, DetailView.as_view(model=Newsitem, context_object_name='item'), name='newsitem-detail'),
                       url(r'^news/(?P<slug>[\w\d_-]+)/$', DetailView.as_view(model=Newsitem, context_object_name='item'), name='newsitem-detail'),

                       url(r'^annotation/add$', views.AnnotationCreateView.as_view(), name='annotation-create'),
                       url(r'^annotation/(?P<pk>[\w\d_-]+)/$', views.AnnotationDetailView.as_view(), name='annotation-detail'),
                       url(r'^annotation/(?P<pk>[\w\d_-]+)/edit/$', views.AnnotationUpdateView.as_view(), name='annotation-update'),
                       url(r'^annotation/(?P<pk>[\w\d_-]+)/delete/$', views.AnnotationDeleteView.as_view(), name='annotation-delete'),

                       # REST API
                       url(r'^api/', include(router.urls))
)

from django.conf.urls import patterns, url, include
from django.conf import settings
from django.views.generic import TemplateView, ListView, DetailView
import coco.views as views
from .models import Course, Module, Activity, Video, Newsitem

urlpatterns = patterns('',
                       url(r'^$', views.home, name='root'),

                       url(r'^accounts/profile', views.profile, name='profile'),

                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

                       url(r'^search/$', views.search, name='search'),

                       url(r'^course/$', ListView.as_view(model=Course), name='course-list'),
                       url(r'^course/(?P<pk>[\w\d_-]+)/$', DetailView.as_view(model=Course, context_object_name='course'), name='course-detail'),
                       url(r'^module/$', ListView.as_view(model=Module), name='module-list'),
                       url(r'^module/(?P<pk>[\w\d_-]+)/$', DetailView.as_view(model=Module, context_object_name='module'), name='module-detail'),
                       url(r'^activity/$', ListView.as_view(model=Activity), name='activity-list'),
                       url(r'^activity/(?P<pk>[\w\d_-]+)/$', DetailView.as_view(model=Activity, context_object_name='activity'), name='activity-detail'),
                       url(r'^video/$', ListView.as_view(model=Video), name='video-list'),
                       url(r'^video/(?P<pk>[\w\d_-]+)/$', DetailView.as_view(model=Video, context_object_name='video'), name='video-detail'),
                       url(r'^video/(?P<video>[\w\d_-]+)/cinelab$', views.cinelab, name='video-cinelab'),

                       url(r'^news/$', ListView.as_view(model=Newsitem), name='newsitem-list'),
                       url(r'^news/(?P<pk>[\w\d_-]+)/$', DetailView.as_view(model=Newsitem, context_object_name='item'), name='newsitem-detail'),

                       # REST API
                       url(r'^api/', include(patterns('',
                                                      url(r'^course/$',
                                                          views.CourseList.as_view(),
                                                          name='api-course-list'),
                                                      url(r'^course/(?P<pk>[\d\w]+)/$',
                                                          views.CourseDetail.as_view(),
                                                          name='api-course-detail'),
                                                      url(r'^video/$',
                                                          views.VideoList.as_view(),
                                                          name='api-video-list'),
                                                      url(r'^video/(?P<pk>[\d\w]+)/$',
                                                          views.VideoDetail.as_view(),
                                                          name='api-video-detail'),
                                                      )))
                       )

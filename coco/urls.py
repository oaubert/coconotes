from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView, ListView, DetailView
import coco.views as views
from .models import Course

urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='root.html'), name='root'),
                       url(r'^course/$', ListView.as_view(model=Course), name='course-list'),
                       url(r'^course/(?P<pk>[\w\d_]+)/$', DetailView.as_view(model=Course, context_object_name='course'), name='course-detail'),
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

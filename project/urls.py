from django.conf.urls import include, url
from django.contrib import admin
import django_cas_ng.views as cas

admin.autodiscover()

urlpatterns = [
    url(r'', include('coco.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^actions/', include('actstream.urls')),
    url(r'^accounts/login/?$', cas.login, name='cas_ng_login'),
    url(r'^accounts/logout/?$', cas.logout, name='cas_ng_logout'),
    url(r'^accounts/callback/?$', cas.callback, name='cas_ng_proxy_callback'),
]

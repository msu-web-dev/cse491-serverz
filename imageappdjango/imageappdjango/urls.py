from django.conf.urls import patterns, include, url

from django.contrib import admin
import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'imageappdjango.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'image.views.index', name='index'),
    url(r'^upload/$', 'image.views.upload', name='upload'),
    url(r'^upload_receive/$', 'image.views.upload_receive', name='upload_receive'),
    url(r'^image_raw/$', 'image.views.image_raw', name='image_raw'),
    url(r'^image/$', 'image.views.image', name='image'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT
        }),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT
        })
)

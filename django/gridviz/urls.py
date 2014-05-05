# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.conf.urls import patterns, include, url
from django.contrib import admin
from registration.backends.default import urls as registration_urls

from gridviz import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(registration_urls)),
    url(r'^drawings/$', views.drawing_list),
    url(r'^drawings/create$', views.drawing_create),
    url(r'^drawings/(?P<pk>\d*)$', views.drawing_update),
    url(r'^drawings/(?P<pk>\d*)/delete$', views.drawing_confirm_delete),
    url(r'^drawings/(?P<pk>\d*)/edit', views.drawing_edit)
)

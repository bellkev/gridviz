# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from registration.backends.default import urls as registration_urls

from gridviz import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include(registration_urls)),
    url(r'^drawings/$', views.DrawingList.as_view(), name='gridviz_drawing_list'),
    url(r'^drawings/create$', views.DrawingCreate.as_view(), name='gridviz_drawing_create'),
    url(r'^drawings/(?P<pk>\d*)$', views.DrawingUpdate.as_view(), name='gridviz_drawing_update'),
    url(r'^drawings/(?P<pk>\d*)/delete$', views.DrawingDelete.as_view(), name='gridviz_drawing_delete'),
    url(r'^drawings/(?P<pk>\d*)/edit', views.DrawingEdit.as_view(), name='gridviz_drawing_edit')
)

from django.conf.urls import patterns, include, url
from django.contrib import admin

from gridviz import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^drawings/$', views.drawing_list),
    url(r'^drawings/create$', views.drawing_create),
    url(r'^drawings/(?P<pk>\d*)$', views.drawing_update),
    url(r'^drawings/(?P<pk>\d*)/delete$', views.drawing_confirm_delete),
    url(r'^drawings/(?P<pk>\d*)/edit', views.drawing_edit)
)

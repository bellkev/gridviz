from django.conf.urls import patterns, include, url
from django.contrib import admin

from gridviz import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^drawings/$', views.drawings),
    url(r'^drawings/create$', views.create_drawing),
    url(r'^drawings/(?P<pk>\d*)$', views.drawing_detail)
)

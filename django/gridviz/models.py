# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import Prefetch
from model_utils.managers import InheritanceManager
from gridviz import svg_data_types


class Drawing(models.Model):
    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('gridviz_drawing_update', kwargs={'pk': self.pk})

    def get_elements(self):
        qs = self.elements.select_related('type')
        pre_qs = SvgDatumBase.objects.select_related('attribute').select_subclasses()

        def attr_dict(data):
            return dict([(datum.attribute.name, datum.value) for datum in data])

        return [{'id': el.pk, 'tagName': el.type.name, 'attrs': attr_dict(el.data.all())} for el in
                qs.prefetch_related(Prefetch('data', queryset=pre_qs))]


class SvgElementType(models.Model):
    name = models.CharField(max_length=20)


class SvgElement(models.Model):
    type = models.ForeignKey(SvgElementType)
    drawing = models.ForeignKey(Drawing, related_name='elements')

    def get_attrs(self):
        # TODO: Investigate why the explicit field name reference is needed here
        data = self.data.select_related('attribute').select_subclasses()
        return dict([(datum.attribute.name, datum.value) for datum in data])


class SvgAttribute(models.Model):
    name = models.CharField(max_length=20)
    data_type = models.PositiveSmallIntegerField()


class SvgDatumBase(models.Model):
    element = models.ForeignKey(SvgElement, related_name='data')
    attribute = models.ForeignKey(SvgAttribute)
    objects = InheritanceManager()


class SvgFloatDatum(SvgDatumBase):
    data_type = svg_data_types.FLOAT_TYPE
    value = models.FloatField()


class SvgCharDatum(SvgDatumBase):
    data_type = svg_data_types.CHAR_TYPE
    value = models.CharField(max_length=255)
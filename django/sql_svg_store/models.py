# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.db import models
from model_utils.managers import InheritanceManager

import svg_data_types


class SvgElementType(models.Model):
    name = models.CharField(max_length=20)


class SvgElement(models.Model):
    type = models.ForeignKey(SvgElementType)
    drawing = models.ForeignKey('drawings.Drawing', related_name='elements')

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
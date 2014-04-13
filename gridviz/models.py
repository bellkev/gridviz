from django.db import models
from django.core.urlresolvers import reverse


class Drawing(models.Model):
    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('gridviz.views.drawing_update', kwargs={'pk': self.pk})


class SvgElementType(models.Model):
    name = models.CharField(max_length=20)


class SvgElement(models.Model):
    type = models.ForeignKey(SvgElementType)


class SvgAttributeType(models.Model):
    name = models.CharField(max_length=20)
    data_type = models.PositiveSmallIntegerField()


class Data(models.Model):
    element = models.ForeignKey(SvgElement)
    attribute_type = models.ForeignKey(SvgAttributeType)
    data_type = models.PositiveSmallIntegerField()


class LengthData(Data):
    value = models.FloatField()
from django.db import models
from django.core.urlresolvers import reverse
from model_utils.managers import InheritanceManager


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
    drawing = models.ForeignKey(Drawing)


class SvgAttribute(models.Model):
    name = models.CharField(max_length=20)


class SvgDatumBase(models.Model):
    element = models.ForeignKey(SvgElement, related_name='data')
    attribute = models.ForeignKey(SvgAttribute)
    objects = InheritanceManager()


class SvgLengthDatum(SvgDatumBase):
    value = models.FloatField()
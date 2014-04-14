from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import Prefetch
from model_utils.managers import InheritanceManager


class Drawing(models.Model):
    title = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('gridviz.views.drawing_update', kwargs={'pk': self.pk})

    def get_elements(self):
        qs = self.svgelement_set.select_related('type')
        pre_qs = SvgDatumBase.objects.select_related('attribute').select_subclasses()

        def attr_dict(data):
            return dict([(datum.attribute.name, datum.value) for datum in data])

        return [{el.type.name: attr_dict(el.data.all())} for el in
                qs.prefetch_related(Prefetch('data', queryset=pre_qs))]


class SvgElementType(models.Model):
    name = models.CharField(max_length=20)


class SvgElement(models.Model):
    type = models.ForeignKey(SvgElementType)
    drawing = models.ForeignKey(Drawing)

    def get_attrs(self):
        # TODO: Investigate why the explicit field name reference is needed here
        data = self.data.select_related('attribute').select_subclasses()
        return dict([(datum.attribute.name, datum.value) for datum in data])


class SvgAttribute(models.Model):
    name = models.CharField(max_length=20)


class SvgDatumBase(models.Model):
    element = models.ForeignKey(SvgElement, related_name='data')
    attribute = models.ForeignKey(SvgAttribute)
    objects = InheritanceManager()


class SvgLengthDatum(SvgDatumBase):
    value = models.FloatField()
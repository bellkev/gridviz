# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Prefetch

from sql_svg_store.models import SvgDatumBase


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
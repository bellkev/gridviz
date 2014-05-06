# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.forms import ModelForm

from .models import Drawing


class CreateDrawingForm(ModelForm):
    class Meta:
        model = Drawing
        fields = ('title',)
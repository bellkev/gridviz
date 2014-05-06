# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.urlresolvers import reverse_lazy

from .models import Drawing


class DrawingList(ListView):
    model = Drawing

    def get_queryset(self):
        return Drawing.objects.filter(created_by=self.request.user)


class DrawingCreate(CreateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_create'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class DrawingDelete(DeleteView):
    model = Drawing
    success_url = reverse_lazy('gridviz_drawing_list')


class DrawingUpdate(UpdateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_update'

    def get_queryset(self):
        return Drawing.objects.filter(created_by_id=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        drawing = self.get_object()
        if request.is_ajax():
            return JsonResponse({'title': drawing.title, 'elements': drawing.get_elements()})
        else:
            return super(DrawingUpdate, self).get(request, *args, **kwargs)


class DrawingEdit(DetailView):
    model = Drawing
    template_name_suffix = '_edit'
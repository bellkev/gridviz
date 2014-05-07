# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.urlresolvers import reverse_lazy
from braces.views import LoginRequiredMixin

from .models import Drawing


class FilterByUserMixin(LoginRequiredMixin):
    # SingleObjectMixin filters by pk after this
    def get_queryset(self):
        return Drawing.objects.filter(created_by=self.request.user)


class DrawingList(FilterByUserMixin, ListView):
    model = Drawing


class DrawingCreate(LoginRequiredMixin, CreateView):
    model = Drawing
    fields = ('title',)
    template_name_suffix = '_create'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class DrawingDelete(FilterByUserMixin, DeleteView):
    model = Drawing
    success_url = reverse_lazy('gridviz_drawing_list')


class DrawingUpdate(FilterByUserMixin, UpdateView):
    model = Drawing
    fields = ('title',)
    template_name_suffix = '_update'

    def get_queryset(self):
        return Drawing.objects.filter(created_by_id=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        drawing = self.get_object()
        if request.is_ajax():
            return JsonResponse({'title': drawing.title, 'elements': drawing.get_elements()})
        else:
            return super(DrawingUpdate, self).get(request, *args, **kwargs)


class DrawingEdit(FilterByUserMixin, DetailView):
    model = Drawing
    template_name_suffix = '_edit'
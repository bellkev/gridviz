from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.core.urlresolvers import reverse_lazy

from .models import Drawing


class DrawingList(ListView):
    model = Drawing

drawing_list = DrawingList.as_view()


class DrawingCreate(CreateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_create'

drawing_create = DrawingCreate.as_view()


class DrawingDelete(DeleteView):
    model = Drawing
    success_url = reverse_lazy('gridviz.views.drawing_list')

drawing_confirm_delete = DrawingDelete.as_view()


class DrawingUpdate(UpdateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_update'

    def get(self, request, *args, **kwargs):
        drawing = self.get_object()
        if request.is_ajax():
            return JsonResponse({'title': drawing.title})
        else:
            return super(DrawingUpdate, self).get(request, *args, **kwargs)

drawing_update = DrawingUpdate.as_view()


class DrawingEdit(DetailView):
    model = Drawing
    template_name_suffix = '_edit'

drawing_edit = DrawingEdit.as_view()
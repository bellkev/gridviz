from django.views.generic import ListView, CreateView, UpdateView

from .models import Drawing


class DrawingList(ListView):
    model = Drawing

drawing_list = DrawingList.as_view()


class DrawingCreate(CreateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_create'

drawing_create = DrawingCreate.as_view()


class DrawingUpdate(UpdateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_update'

drawing_update = DrawingUpdate.as_view()
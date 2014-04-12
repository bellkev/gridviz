from django.views.generic import ListView, CreateView, UpdateView

from .models import Drawing


class DrawingList(ListView):
    model = Drawing

drawings = DrawingList.as_view()


class DrawingCreate(CreateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_create'

create_drawing = DrawingCreate.as_view()


class DrawingUpdate(UpdateView):
    model = Drawing
    fields = ['title']
    template_name_suffix = '_update'

drawing_detail = DrawingUpdate.as_view()
from django.views.generic import ListView, DetailView, CreateView
from django.forms.models import modelform_factory

from .models import Drawing


class Drawings(ListView):
    template_name = 'drawings.html'
    queryset = Drawing.objects.order_by('-created_at')

drawings = Drawings.as_view()


class CreateDrawing(CreateView):
    template_name = 'create_drawing.html'
    form_class = modelform_factory(Drawing, fields=['title'])

create_drawing = CreateDrawing.as_view()


class DrawingDetail(DetailView):
    template_name = 'drawing_detail.html'
    model = Drawing

drawing_detail = DrawingDetail.as_view()
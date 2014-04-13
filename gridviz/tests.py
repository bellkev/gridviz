from django.test import TestCase

from .models import Drawing, SvgElementType, SvgElement, SvgAttribute, SvgLengthDatum


class DrawingModelTest(TestCase):

    def test_unicode_representation(self):
        drawing = Drawing(title='My drawing title')
        self.assertEqual(unicode(drawing), drawing.title)

    def test_get_absolute_url(self):
        drawing = Drawing.objects.create(title='My drawing title',)
        self.assertEqual(drawing.get_absolute_url(), '/drawings/' + str(drawing.pk))


class SvgDatumModelTestBase(TestCase):

    def setUp(self):
        self.test_drawing = Drawing.objects.create(title='test_drawing')
        self.test_type = SvgElementType.objects.create(name='test_type')
        self.test_attr = SvgAttribute.objects.create(name='test_attr')
        self.test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)


class SvgLengthDatumModelTest(SvgDatumModelTestBase):

    def test_length(self):
        SvgLengthDatum.objects.create(element=self.test_element, attribute=self.test_attr, value=12.5)
        self.assertEqual(SvgElement.objects.first().data.first().svglengthdatum.value, 12.5)


class ProjectTests(TestCase):

    def test_drawings(self):
        response = self.client.get('/drawings/')
        self.assertEqual(response.status_code, 200)

    def test_drawing_update(self):
        drawing = Drawing.objects.create(title='drawing title')
        response = self.client.get('/drawings/' + str(drawing.pk))
        self.assertEqual(response.status_code, 200)

    def test_not_found_drawing(self):
        drawing = Drawing.objects.create(title='drawing title')
        response = self.client.get('/drawings/' + str(drawing.pk + 1))
        self.assertEqual(response.status_code, 404)

    def test_create_drawing(self):
        response = self.client.get('/drawings/create')
        self.assertEqual(response.status_code, 200)

    def test_delete_drawing(self):
        drawing = Drawing.objects.create(title='drawing title')
        response = self.client.get(drawing.get_absolute_url() + '/delete')
        self.assertEqual(response.status_code, 200)

    def test_drawgin_edit(self):
        drawing = Drawing.objects.create(title='drawing title')
        response = self.client.get(drawing.get_absolute_url() + '/edit')
        self.assertEqual(response.status_code, 200)


class DrawingListTests(TestCase):
    """Test that drawings show up"""
    def test_one_drawing(self):
        Drawing.objects.create(title='1-title')
        response = self.client.get('/drawings/')
        self.assertContains(response, '1-title')

    def test_two_drawings(self):
        Drawing.objects.create(title='1-title')
        Drawing.objects.create(title='2-title')
        response = self.client.get('/drawings/')
        self.assertContains(response, '1-title')
        self.assertContains(response, '2-title')

    def test_no_drawings(self):
        response = self.client.get('/drawings/')
        self.assertContains(response, 'You haven\'t made any drawings yet')


class DrawingCreateTests(TestCase):

    def test_create(self):
        self.client.post('/drawings/create', {'title': 'a'})
        new_drawing = Drawing.objects.first()
        self.assertEqual(new_drawing.title, 'a')

    def test_no_title(self):
        response = self.client.post('/drawings/create', {'title': ''})
        self.assertContains(response, 'This field is required.')


class DrawingUpdateTests(TestCase):

    def test_rename(self):
        new_drawing = Drawing.objects.create(title='abc')
        self.client.post('/drawings/' + str(new_drawing.pk), {'title': 'def'})
        self.assertEqual(Drawing.objects.get(pk=new_drawing.pk).title, 'def')


class DrawingDeleteTests(TestCase):

    def test_delete(self):
        new_drawing = Drawing.objects.create(title='abc')
        self.client.post(new_drawing.get_absolute_url() + '/delete')
        self.assertRaises(Drawing.DoesNotExist, Drawing.objects.get, pk=new_drawing.pk)
import json

from django.test import TestCase
from gridviz import svg_data_types

from .models import Drawing, SvgElementType, SvgElement, SvgAttribute, SvgLengthDatum
from .messages import process_message


class SvgTest(TestCase):
    def setUp(self):
        self.test_drawing = Drawing.objects.create(title='test_drawing')
        self.test_type = SvgElementType.objects.create(name='test_type')
        self.test_attr = SvgAttribute.objects.create(name='test_attr', data_type=svg_data_types.LENGTH_TYPE)
        self.test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)


class DrawingModelTest(SvgTest):
    def test_unicode_representation(self):
        drawing = Drawing(title='My drawing title')
        self.assertEqual(unicode(drawing), drawing.title)

    def test_get_absolute_url(self):
        drawing = Drawing.objects.create(title='My drawing title', )
        self.assertEqual(drawing.get_absolute_url(), '/drawings/' + str(drawing.pk))

    def test_get_elements(self):
        el1 = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        el2 = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        el3 = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        attr_1 = SvgAttribute.objects.create(name='attr_1', data_type=svg_data_types.LENGTH_TYPE)
        attr_2 = SvgAttribute.objects.create(name='attr_2', data_type=svg_data_types.LENGTH_TYPE)
        SvgLengthDatum.objects.create(element=el1, attribute=self.test_attr, value=1)
        SvgLengthDatum.objects.create(element=el2, attribute=self.test_attr, value=2)
        SvgLengthDatum.objects.create(element=el3, attribute=attr_1, value=3)
        SvgLengthDatum.objects.create(element=el3, attribute=attr_2, value=4)

        with self.assertNumQueries(2):
            self.assertEqual(self.test_drawing.get_elements(),
                             [{'id': self.test_element.pk, 'tagName': 'test_type', 'attrs': {}},
                              {'id': el1.pk, 'tagName': 'test_type', 'attrs': {'test_attr': 1}},
                              {'id': el2.pk, 'tagName': 'test_type', 'attrs': {'test_attr': 2}},
                              {'id': el3.pk, 'tagName': 'test_type', 'attrs': {'attr_2': 4, 'attr_1': 3}}])


class SvgElementModelTest(SvgTest):
    def test_get_attrs(self):
        attr_1 = SvgAttribute.objects.create(name='attr_1', data_type=svg_data_types.LENGTH_TYPE)
        attr_2 = SvgAttribute.objects.create(name='attr_2', data_type=svg_data_types.LENGTH_TYPE)
        SvgLengthDatum.objects.create(element=self.test_element, attribute=attr_1, value=1)
        SvgLengthDatum.objects.create(element=self.test_element, attribute=attr_2, value=2)
        with self.assertNumQueries(1):
            self.assertEqual(self.test_element.get_attrs(), {'attr_1': 1, 'attr_2': 2})


class SvgLengthDatumModelTest(SvgTest):
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

    def test_drawing_edit(self):
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
    def setUp(self):
        self.new_drawing = Drawing.objects.create(title='abc')

    def test_rename(self):
        self.client.post('/drawings/' + str(self.new_drawing.pk), {'title': 'def'})
        self.assertEqual(Drawing.objects.get(pk=self.new_drawing.pk).title, 'def')

    def test_html(self):
        response = self.client.get('/drawings/' + str(self.new_drawing.pk))
        self.assertContains(response, "Edit Drawing")

    def test_json(self):
        response = self.client.get('/drawings/' + str(self.new_drawing.pk),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertJSONEqual(response.content, json.dumps({'title': 'abc', 'elements': []}))


class DrawingDeleteTests(TestCase):
    def test_delete(self):
        new_drawing = Drawing.objects.create(title='abc')
        self.client.post(new_drawing.get_absolute_url() + '/delete')
        self.assertRaises(Drawing.DoesNotExist, Drawing.objects.get, pk=new_drawing.pk)


class MessageQueries(SvgTest):
    def setUp(self):
        super(MessageQueries, self).setUp()
        self.test_message = json.dumps({'action': 'add_attr', 'element_id': self.test_element.pk,
                                        'temp_id': 123, 'attr_name': 'test_attr', 'attr_value': 25})

    def test_create(self):
        result = process_message(self.test_drawing, self.test_message)
        datum = SvgLengthDatum.objects.first()
        expected = json.dumps({'action': 'add_attr', 'element_id': self.test_element.pk, 'temp_id': 123,
                               'id': datum.pk, 'attr_name': 'test_attr', 'attr_value': 25})
        self.assertEqual(SvgLengthDatum.objects.first().value, 25)
        self.assertEqual(expected, result)

    def test_drawing_filter(self):
        with self.assertRaises(SvgElement.DoesNotExist):
            process_message(Drawing.objects.create(title='foo'), self.test_message)
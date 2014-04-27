# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json

from django.test import TestCase
from gridviz import svg_data_types

from .models import Drawing, SvgElementType, SvgElement, SvgAttribute, SvgFloatDatum, SvgCharDatum
from .messages import process_message


class SvgTest(TestCase):
    def setUp(self):
        self.test_drawing = Drawing.objects.create(title='test_drawing')
        self.test_type = SvgElementType.objects.create(name='test_type')
        self.test_attr = SvgAttribute.objects.create(name='test_attr', data_type=svg_data_types.FLOAT_TYPE)


class DrawingModelTest(SvgTest):
    def test_unicode_representation(self):
        drawing = Drawing(title='My drawing title')
        self.assertEqual(unicode(drawing), drawing.title)

    def test_get_absolute_url(self):
        drawing = Drawing.objects.create(title='My drawing title', )
        self.assertEqual(drawing.get_absolute_url(), '/drawings/' + str(drawing.pk))

    def test_get_elements(self):
        test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        el1 = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        el2 = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        el3 = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        attr_1 = SvgAttribute.objects.create(name='attr_1', data_type=svg_data_types.FLOAT_TYPE)
        attr_2 = SvgAttribute.objects.create(name='attr_2', data_type=svg_data_types.FLOAT_TYPE)
        SvgFloatDatum.objects.create(element=el1, attribute=self.test_attr, value=1)
        SvgFloatDatum.objects.create(element=el2, attribute=self.test_attr, value=2)
        SvgFloatDatum.objects.create(element=el3, attribute=attr_1, value=3)
        SvgFloatDatum.objects.create(element=el3, attribute=attr_2, value=4)

        with self.assertNumQueries(2):
            self.assertEqual(self.test_drawing.get_elements(),
                             [{'id': test_element.pk, 'tagName': 'test_type', 'attrs': {}},
                              {'id': el1.pk, 'tagName': 'test_type', 'attrs': {'test_attr': 1}},
                              {'id': el2.pk, 'tagName': 'test_type', 'attrs': {'test_attr': 2}},
                              {'id': el3.pk, 'tagName': 'test_type', 'attrs': {'attr_2': 4, 'attr_1': 3}}])


class SvgElementModelTest(SvgTest):
    def test_get_attrs(self):
        test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        attr_1 = SvgAttribute.objects.create(name='attr_1', data_type=svg_data_types.FLOAT_TYPE)
        attr_2 = SvgAttribute.objects.create(name='attr_2', data_type=svg_data_types.FLOAT_TYPE)
        SvgFloatDatum.objects.create(element=test_element, attribute=attr_1, value=1)
        SvgFloatDatum.objects.create(element=test_element, attribute=attr_2, value=2)
        with self.assertNumQueries(1):
            self.assertEqual(test_element.get_attrs(), {'attr_1': 1, 'attr_2': 2})


class SvgFloatDatumModelTest(SvgTest):
    def test_length(self):
        test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        SvgFloatDatum.objects.create(element=test_element, attribute=self.test_attr, value=12.5)
        self.assertEqual(SvgElement.objects.first().data.first().svgfloatdatum.value, 12.5)


class SvgCharDatumModelTest(SvgTest):
    def test_length(self):
        test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        SvgCharDatum.objects.create(element=test_element, attribute=self.test_attr, value='abc')
        self.assertEqual(SvgElement.objects.first().data.first().svgchardatum.value, 'abc')


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

    def test_create_element(self):
        SvgElementType.objects.create(name='rect')
        SvgAttribute.objects.bulk_create([
            SvgAttribute(name='x', data_type=svg_data_types.FLOAT_TYPE),
            SvgAttribute(name='y', data_type=svg_data_types.FLOAT_TYPE),
            SvgAttribute(name='width', data_type=svg_data_types.FLOAT_TYPE),
            SvgAttribute(name='height', data_type=svg_data_types.FLOAT_TYPE)
        ])
        create_element_message = json.dumps({'action': 'create_element', 'tagName': 'rect',
                                             'attrs': {'x': 10, 'y': 10, 'width': 10, 'height': 10},
                                             'messageType': 'persistent', 'clientId': 'abc',
                                             'tempId': 'temp_123'})
        result = process_message(self.test_drawing, create_element_message)
        el = SvgElement.objects.first()
        expected = json.dumps({'action': 'create_element', 'tagName': 'rect',
                               'attrs': {'x': 10, 'y': 10, 'width': 10, 'height': 10},
                               'messageType': 'persistent', 'clientId': 'abc', 'id': el.pk,
                               'tempId': 'temp_123'})
        self.assertJSONEqual(result, expected)

    def test_delete_element(self):
        el = SvgElement.objects.create(drawing=self.test_drawing, type=self.test_type)
        delete_element_message = json.dumps({'action': 'delete_element', 'id': el.pk, 'messageType': 'persistent'})
        result = process_message(self.test_drawing, delete_element_message)
        with self.assertRaises(SvgElement.DoesNotExist):
            SvgElement.objects.get(pk=el.pk)
            self.assertJSONEqual(result, delete_element_message)


    # TODO: Reimplement below but for update_element when written
    # def test_drawing_filter(self):
    #     test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
    #     test_message = json.dumps({'action': 'add_attr', 'element_id': test_element.pk,
    #                                'temp_id': 123, 'attr_name': 'test_attr', 'attr_value': 25})
    #     with self.assertRaises(SvgElement.DoesNotExist):
    #         process_message(Drawing.objects.create(title='foo'), test_message)
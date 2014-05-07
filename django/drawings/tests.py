# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json

from django.conf import settings
from django.test import TestCase

from drawings.models import Drawing
from drawings.test_helpers import UserDataMixin, DrawingDataMixin, LoggedInMixin
from sql_svg_store import svg_data_types
from sql_svg_store.models import SvgElement, SvgAttribute, SvgFloatDatum
from sql_svg_store.test_helpers import SvgDataMixin


class DrawingModelTest(UserDataMixin, DrawingDataMixin, SvgDataMixin, TestCase):
    def test_unicode_representation(self):
        self.assertEqual(unicode(self.test_drawing), self.test_drawing.title)

    def test_get_absolute_url(self):
        self.assertEqual(self.test_drawing.get_absolute_url(), '/drawings/' + str(self.test_drawing.pk))

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


class TestLoginRequired(UserDataMixin, DrawingDataMixin, TestCase):
    def assertRedirectsToLogin(self, response, next):
        self.assertRedirects(response, '{}?next={}'.format(settings.LOGIN_URL, next))

    def test_drawings(self):
        drawings_url = '/drawings/'
        response = self.client.get(drawings_url)
        self.assertRedirectsToLogin(response, drawings_url)

    def test_update_drawing(self):
        update_url = self.test_drawing.get_absolute_url()
        response = self.client.get(update_url)
        self.assertRedirectsToLogin(response, update_url)

    def test_create_drawing(self):
        create_url = '/drawings/create'
        response = self.client.get(create_url)
        self.assertRedirectsToLogin(response, create_url)

    def test_delete_drawing(self):
        delete_url = self.test_drawing.get_absolute_url() + '/delete'
        response = self.client.get(delete_url)
        self.assertRedirectsToLogin(response, delete_url)

    def test_drawing_edit(self):
        edit_url = self.test_drawing.get_absolute_url() + '/edit'
        response = self.client.get(edit_url)
        self.assertRedirectsToLogin(response, edit_url)


class TestDrawingList(LoggedInMixin, TestCase):
    def test_one_drawing(self):
        Drawing.objects.create(title='1-title', created_by=self.test_user)
        response = self.client.get('/drawings/')
        self.assertContains(response, '1-title')

    def test_two_drawings(self):
        Drawing.objects.create(title='1-title', created_by=self.test_user)
        Drawing.objects.create(title='2-title', created_by=self.test_user)
        response = self.client.get('/drawings/')
        self.assertContains(response, '1-title')
        self.assertContains(response, '2-title')

    def test_no_drawings(self):
        response = self.client.get('/drawings/')
        self.assertContains(response, 'You haven\'t made any drawings yet')

    def test_user_filtering(self):
        Drawing.objects.create(title='1-title', created_by=self.other_user)
        response = self.client.get('/drawings/')
        self.assertContains(response, 'You haven\'t made any drawings yet')


class TestDrawingCreate(LoggedInMixin, TestCase):
    def test_html(self):
        response = self.client.get('/drawings/create')
        self.assertContains(response, 'New Drawing')

    def test_create(self):
        self.client.post('/drawings/create', {'title': 'a'})
        new_drawing = Drawing.objects.first()
        self.assertEqual(new_drawing.created_by, self.test_user)
        self.assertEqual(new_drawing.title, 'a')

    def test_no_title(self):
        response = self.client.post('/drawings/create', {'title': ''})
        self.assertContains(response, 'This field is required.')


class TestDrawingUpdate(LoggedInMixin, DrawingDataMixin, TestCase):
    def test_rename(self):
        self.client.post(self.test_drawing.get_absolute_url(), {'title': 'def'})
        self.assertEqual(Drawing.objects.get(pk=self.test_drawing.pk).title, 'def')

    def test_html(self):
        response = self.client.get(self.test_drawing.get_absolute_url())
        self.assertContains(response, 'Edit Drawing')

    def test_json(self):
        response = self.client.get(self.test_drawing.get_absolute_url(),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertJSONEqual(response.content, json.dumps({'title': 'abc', 'elements': []}))

    def test_unauthorized(self):
        self.client.login(**self.other_login_kwargs)
        response = self.client.get(self.test_drawing.get_absolute_url())
        self.assertEqual(response.status_code, 404)


class TestDrawingDelete(LoggedInMixin, DrawingDataMixin, TestCase):
    def test_html(self):
        response = self.client.get(self.test_drawing.get_absolute_url() + '/delete')
        self.assertContains(response, 'Delete Confirmation')

    def test_delete(self):
        self.client.post(self.test_drawing.get_absolute_url() + '/delete')
        with self.assertRaises(Drawing.DoesNotExist):
            Drawing.objects.get(pk=self.test_drawing.pk)
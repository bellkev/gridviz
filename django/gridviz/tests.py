# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.
from collections import defaultdict
from importlib import import_module

import json
from django.conf import settings
from django.contrib.auth import get_user_model
import gevent

from django.test import TestCase, TransactionTestCase, RequestFactory
from gridviz import svg_data_types
from gridviz.subscriber import DatabaseSubscriber

from .models import Drawing, SvgElementType, SvgElement, SvgAttribute, SvgFloatDatum, SvgCharDatum
from .messages import process_message


class UserDataMixin(object):
    def setUp(self):
        self.login_kwargs = {'username': 'joe', 'password': 'abc'}
        self.other_login_kwargs = {'username': 'jane', 'password': 'abc'}
        self.test_user = get_user_model().objects.create_user(**self.login_kwargs)
        self.other_user = get_user_model().objects.create_user(**self.other_login_kwargs)
        super(UserDataMixin, self).setUp()


class LoggedInMixin(UserDataMixin):
    def setUp(self):
        super(LoggedInMixin, self).setUp()
        self.client.login(**self.login_kwargs)


class DrawingDataMixin(object):
    def setUp(self):
        self.test_drawing = Drawing.objects.create(title='abc', created_by=self.test_user)
        self.other_drawing = Drawing.objects.create(title='def', created_by=self.other_user)
        super(DrawingDataMixin, self).setUp()


class SvgDataMixin(object):
    def setUp(self):
        self.test_type = SvgElementType.objects.create(name='test_type')
        self.test_attr = SvgAttribute.objects.create(name='test_attr', data_type=svg_data_types.FLOAT_TYPE)
        super(SvgDataMixin, self).setUp()


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


class SvgElementModelTest(UserDataMixin, DrawingDataMixin, SvgDataMixin, TestCase):
    def test_get_attrs(self):
        test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        attr_1 = SvgAttribute.objects.create(name='attr_1', data_type=svg_data_types.FLOAT_TYPE)
        attr_2 = SvgAttribute.objects.create(name='attr_2', data_type=svg_data_types.FLOAT_TYPE)
        SvgFloatDatum.objects.create(element=test_element, attribute=attr_1, value=1)
        SvgFloatDatum.objects.create(element=test_element, attribute=attr_2, value=2)
        with self.assertNumQueries(1):
            self.assertEqual(test_element.get_attrs(), {'attr_1': 1, 'attr_2': 2})


class SvgFloatDatumModelTest(UserDataMixin, DrawingDataMixin, SvgDataMixin, TestCase):
    def test_length(self):
        test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        SvgFloatDatum.objects.create(element=test_element, attribute=self.test_attr, value=12.5)
        self.assertEqual(SvgElement.objects.first().data.first().svgfloatdatum.value, 12.5)


class SvgCharDatumModelTest(UserDataMixin, DrawingDataMixin, SvgDataMixin, TestCase):
    def test_length(self):
        test_element = SvgElement.objects.create(type=self.test_type, drawing=self.test_drawing)
        SvgCharDatum.objects.create(element=test_element, attribute=self.test_attr, value='abc')
        self.assertEqual(SvgElement.objects.first().data.first().svgchardatum.value, 'abc')


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


class MessageTestCase(UserDataMixin, DrawingDataMixin, TransactionTestCase):
    def setUp(self):
        super(MessageTestCase, self).setUp()
        self.rect_type = SvgElementType.objects.create(name='rect')
        SvgAttribute.objects.bulk_create([
            SvgAttribute(name='x', data_type=svg_data_types.FLOAT_TYPE),
            SvgAttribute(name='y', data_type=svg_data_types.FLOAT_TYPE),
            SvgAttribute(name='width', data_type=svg_data_types.FLOAT_TYPE),
            SvgAttribute(name='height', data_type=svg_data_types.FLOAT_TYPE)
        ])
        self.test_create_message = {'action': 'create_element', 'tagName': 'rect',
                                    'attrs': {'x': 10, 'y': 10, 'width': 10, 'height': 10},
                                    'messageType': 'persistent', 'clientId': 'abc',
                                    'tempId': 'temp_123'}


class EditMessageTestCase(MessageTestCase):
    def setUp(self):
        super(EditMessageTestCase, self).setUp()
        result = process_message(self.test_drawing.pk, json.dumps(self.test_create_message))
        self.test_element = SvgElement.objects.get(pk=json.loads(result)['id'])
        self.test_update_message = self.test_create_message.copy()
        self.test_update_message['attrs'] = {'x': 20, 'y': 20, 'width': 10, 'height': 10}
        self.test_update_message['action'] = 'update_element'
        self.test_update_message['id'] = self.test_element.pk
        self.test_delete_message = {'action': 'delete_element', 'id': self.test_element.pk,
                                    'messageType': 'persistent'}
        self.test_ui_message = self.test_update_message.copy()
        self.test_ui_message['messageType'] = 'ui'


class CreateMessages(MessageTestCase):
    def test_create_element(self):
        result = process_message(self.test_drawing.pk, json.dumps(self.test_create_message))
        self.test_create_message['id'] = SvgElement.objects.first().pk
        expected = json.dumps(self.test_create_message)
        self.assertJSONEqual(result, expected)


class UpdateMessages(EditMessageTestCase):
    # TODO: Test that attrs get added, deleted, or preserved on update as appropriate
    def test_update_element(self):
        result = process_message(self.test_drawing, json.dumps(self.test_update_message))
        self.assertJSONEqual(result, json.dumps(self.test_update_message))
        self.assertEqual(self.test_update_message['attrs'], self.test_element.get_attrs())

    def test_update_drawing_filter(self):
        with self.assertRaises(SvgElement.DoesNotExist):
            process_message(self.other_drawing, json.dumps(self.test_update_message))

    def test_ui_message(self):
        result = process_message(self.test_drawing, json.dumps(self.test_ui_message))
        self.assertJSONEqual(result, json.dumps(self.test_ui_message))


class DeleteMessages(EditMessageTestCase):
    def setUp(self):
        super(DeleteMessages, self).setUp()

    def test_delete_element(self):
        result = process_message(self.test_drawing, json.dumps(self.test_delete_message))
        self.assertJSONEqual(result, json.dumps(self.test_delete_message))
        with self.assertRaises(SvgElement.DoesNotExist):
            SvgElement.objects.get(pk=self.test_element.pk)

    def test_delete_drawing_filter(self):
        with self.assertRaises(SvgElement.DoesNotExist):
            process_message(self.other_drawing, json.dumps(self.test_delete_message))


class MockPubSub(object):
    def __init__(self):
        self.subscribed_channels = []

    def subscribe(self, channel):
        self.subscribed_channels.append(channel)


class MockRedis(object):
    def __init__(self):
        self.published_messages = defaultdict(list)
        self.pubsubs = []

    def pubsub(self):
        ps = MockPubSub()
        self.pubsubs.append(ps)
        return ps

    def publish(self, channel, message):
        self.published_messages[channel].append(message)


def blowup(e):
    raise e


class SubscriberTests(TestCase):
    def setUp(self):
        #TODO: Use override_settings decorator instead
        settings.SVG_STORE = 'gridviz.test_svg_store'
        self.message_module = import_module('{}.messages'.format(settings.SVG_STORE))
        channels = ['subscribe-broadcast', 'publish-broadcast']
        self.drawing_id = 1
        self.factory = RequestFactory()
        request = self.factory.get(settings.WEBSOCKET_URL + str(self.drawing_id), dict((key, None) for key in channels))
        self.connection = MockRedis()
        self.subscriber = DatabaseSubscriber(self.connection)
        self.subscriber.greenlet_error_handler = blowup
        self.subscriber.set_pubsub_channels(request, channels)
        self.subscribed_channel = self.connection.pubsubs[0].subscribed_channels[0]

    def test_set_pubsub_channels(self):
        # This is only overridden to preserve the drawing_id from the original http request that is upgraded
        self.assertEqual(self.subscriber.drawing_id, self.drawing_id)

    def test_publish_message(self):
        client_message = 'Hello, from the client,'
        self.message_module.process_fn = lambda s: s + ' and from the server!'
        server_message = self.message_module.process_fn(client_message)

        self.subscriber.publish_message(client_message)
        gevent.wait()
        # Should process message through SVG store
        self.assertEqual(self.message_module.processed_messages[0], client_message)
        # And send the result to redis
        self.assertEqual(self.connection.published_messages[self.subscribed_channel][0], server_message)

    def test_empty_message(self):
        # Should ignore empty messages (uwsgi produces these periodically)
        self.subscriber.publish_message('')
        self.assertFalse(self.message_module.processed_messages)
        self.assertFalse(self.connection.published_messages[self.subscribed_channel])

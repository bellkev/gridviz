# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from collections import defaultdict
from importlib import import_module
import json

from django.conf import settings
from django.test import TestCase, TransactionTestCase, RequestFactory
import gevent

from drawings.tests import UserDataMixin, DrawingDataMixin
from sql_svg_store import svg_data_types
from sql_svg_store.models import SvgElementType, SvgAttribute, SvgElement, SvgFloatDatum, SvgCharDatum
from sql_svg_store.subscriber import DatabaseSubscriber
from sql_svg_store.test_helpers import SvgDataMixin
from sql_svg_store.messages import process_message


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
        settings.SVG_STORE = 'test_svg_store'
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

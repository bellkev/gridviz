# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from importlib import import_module
from django.conf import settings
import gevent
from ws4redis.subscriber import RedisSubscriber


class DatabaseSubscriber(RedisSubscriber):
    def __init__(self, connection):
        self.drawing_id = None
        self.greenlet_error_handler = lambda x: x
        super(DatabaseSubscriber, self).__init__(connection)

    def set_pubsub_channels(self, request, channels):
        self.drawing_id = int(request.path_info.replace(settings.WEBSOCKET_URL, '', 1))
        super(DatabaseSubscriber, self).set_pubsub_channels(request, channels)

    def do_publish_message(self, client_message, expire=None):
        message_module = import_module('{}.messages'.format(settings.SVG_STORE))
        server_message = message_module.process_message(self.drawing_id, client_message)
        super(DatabaseSubscriber, self).publish_message(server_message, expire=expire)

    def publish_message(self, client_message, expire=None):
        if client_message:
            greenlet = gevent.spawn(self.do_publish_message, client_message, expire=expire)
            greenlet.link_exception(self.greenlet_error_handler)
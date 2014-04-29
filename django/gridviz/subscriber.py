# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.
import json
from django.conf import settings
import gevent
from ws4redis.subscriber import RedisSubscriber

from gridviz.messages import process_message


class DatabaseSubscriber(RedisSubscriber):
    def __init__(self, connection):
        self.drawing_id = None
        super(DatabaseSubscriber, self).__init__(connection)

    def set_pubsub_channels(self, request, channels):
        self.drawing_id = int(request.path_info.replace(settings.WEBSOCKET_URL, '', 1))
        super(DatabaseSubscriber, self).set_pubsub_channels(request, channels)

    def do_publish_message(self, client_message, expire=None):
        server_message = process_message(self.drawing_id, client_message)
        super(DatabaseSubscriber, self).publish_message(server_message, expire=expire)
        server_message = json.loads(server_message)
        if server_message['action'] == 'create_element':
            print 'Responded to create message for element with tempId:', server_message['tempId'], 'With id:', server_message['id']

    def publish_message(self, client_message, expire=None):
        if client_message:
            message_dict = json.loads(client_message)
            if message_dict['action'] == 'create_element':
                print 'Recieved create message for element with tempId:', message_dict['tempId']
            gevent.spawn(self.do_publish_message, client_message, expire=expire)
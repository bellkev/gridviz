# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.
from django.conf import settings
from ws4redis.subscriber import RedisSubscriber

from gridviz.messages import process_message
from gridviz.models import Drawing


class DatabaseSubscriber(RedisSubscriber):
    def __init__(self, connection):
        self.drawing_id = None
        super(DatabaseSubscriber, self).__init__(connection)

    def set_pubsub_channels(self, request, channels):
        self.drawing_id = int(request.path_info.replace(settings.WEBSOCKET_URL, '', 1))
        super(DatabaseSubscriber, self).set_pubsub_channels(request, channels)

    def publish_message(self, client_message, expire=None):
        drawing = Drawing.objects.get(pk=self.drawing_id)
        server_message = process_message(drawing, client_message)
        super(RedisSubscriber, self).publish_message(server_message, expire=expire)
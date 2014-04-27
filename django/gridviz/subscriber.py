# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.
from ws4redis.subscriber import RedisSubscriber

from gridviz.messages import process_message
from gridviz.models import Drawing


class DatabaseSubscriber(RedisSubscriber):
    def publish_message(self, client_message, expire=None):
        drawing = Drawing.objects.get(pk=5)
        server_message = process_message(drawing, client_message)
        super(RedisSubscriber, self).publish_message(server_message, expire=expire)
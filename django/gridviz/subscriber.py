# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.
from ws4redis.subscriber import RedisSubscriber


class DatabaseSubscriber(RedisSubscriber):
    def publish_message(self, message, expire=None):
        super(RedisSubscriber, self).publish_message(message, expire=expire)
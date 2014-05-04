# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json
import time

from django.db import connection
from gevent.pool import Pool

from .messages import process_message
from .tests import EditMessageTestCase


def process_and_cleanup(*args):
    result = process_message(*args)
    connection.close()
    return result


def benchmark(fn):
    def inner(*args):
        start = time.time()
        results = fn(*args)
        duration = time.time() - start
        print 'Benchmarked', fn.__name__, ':'
        print '\tProcessed {} transactions in {} seconds = {} tps'.format(len(results),
                                                                          duration, len(results) / duration)
        return results

    return inner


class BulkCreateTests(EditMessageTestCase):
    def setUp(self):
        super(BulkCreateTests, self).setUp()
        self.pool = Pool(10)

    def gen_create_message(self, count):
        new_message = self.test_create_message.copy()
        new_message['tempId'] = str(count)
        return json.dumps(new_message)

    def gen_delete_message(self, id):
        new_message = self.test_delete_message.copy()
        new_message['id'] = id
        return json.dumps(new_message)

    def gen_update_message(self, id):
        new_message = self.test_update_message.copy()
        new_message['id'] = id
        return json.dumps(new_message)

    @benchmark
    def process_create_messages(self):
        results = [self.pool.spawn(process_and_cleanup, self.test_drawing.pk, self.gen_create_message(count))
                   for count in range(10)]
        self.pool.join()
        return results

    @benchmark
    def process_update_messages(self, update_id):
        results = [self.pool.spawn(process_and_cleanup, self.test_drawing.pk, self.gen_update_message(update_id))
                   for _ in range(10)]
        self.pool.join()
        return results

    @benchmark
    def process_delete_messages(self, to_delete):
        results = [self.pool.spawn(process_and_cleanup, self.test_drawing.pk, self.gen_delete_message(delete_id))
                   for delete_id in to_delete]
        self.pool.join()
        return results

    def test_message_processing(self):
        create_results = self.process_create_messages()
        update_id = json.loads(create_results[0].value)['id']
        self.process_update_messages(update_id)
        to_delete = [json.loads(result.value)['id'] for result in create_results]
        self.process_delete_messages(to_delete)

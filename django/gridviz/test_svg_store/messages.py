# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

processed_messages = []

server_suffix = ''

process_fn = lambda x: x


def process_message(drawing_id, client_message):
    server_message = process_fn(client_message)
    processed_messages.append(client_message)
    return server_message
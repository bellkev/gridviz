# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json
import time

from .models import SvgDatumBase, SvgElement, SvgAttribute, SvgElementType


def datum_class_for_attr(attr):
    return [c for c in SvgDatumBase.__subclasses__() if c.data_type == attr.data_type][0]


def save_attrs(el, attr_dict):
    for key in attr_dict:
        attr = SvgAttribute.objects.get(name=key)
        datum = datum_class_for_attr(attr)(element=el, attribute=attr, value=attr_dict[key])
        datum.save()


def create_element(drawing, message):
    el_type = SvgElementType.objects.get(name=message['tagName'])
    el = SvgElement(type=el_type, drawing=drawing)
    el.save()
    save_attrs(el, message['attrs'])
    return dict(message.items() + [('id', el.pk)])


def update_element(drawing, message):
    el = SvgElement.objects.get(drawing=drawing, pk=message['id'])
    save_attrs(el, message['attrs'])
    return message


def delete_element(drawing, message):
    el = SvgElement.objects.get(drawing=drawing, pk=message['id'])
    el.delete()
    return message


def process_message(drawing, message):
    allowed_actions = [create_element, update_element, delete_element]
    actions_dict = dict((action.__name__, action) for action in allowed_actions)
    message_dict = json.loads(message)
    if message_dict['messageType'] == 'persistent':
        result_dict = actions_dict[message_dict['action']](drawing, message_dict)
        result = json.dumps(result_dict)
    else:
        result = message
    return result
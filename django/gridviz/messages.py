# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json
from django.db import transaction

from .models import SvgDatumBase, SvgElement, SvgAttribute, SvgElementType


def datum_class_for_attr(attr):
    return [c for c in SvgDatumBase.__subclasses__() if c.data_type == attr.data_type][0]


def save_attrs(el, attr_dict):
    current_attrs = [datum.attribute for datum in el.data.all()]
    for key, value in attr_dict.iteritems():
        attr = SvgAttribute.objects.get(name=key)
        datum_class = datum_class_for_attr(attr)
        if attr in current_attrs:
            datum_class.objects.filter(element=el, attribute=attr).update(value=value)
        else:
            datum_class.objects.create(element=el, attribute=attr, value=value)


def create_element(drawing_id, message):
    el_type = SvgElementType.objects.get(name=message['tagName'])
    el = SvgElement(type=el_type, drawing_id=drawing_id)
    el.save()
    save_attrs(el, message['attrs'])
    return dict(message.items() + [('id', el.pk)])


def update_element(drawing_id, message):
    el = SvgElement.objects.get(drawing_id=drawing_id, pk=message['id'])
    save_attrs(el, message['attrs'])
    return message


def delete_element(drawing_id, message):
    el = SvgElement.objects.get(drawing_id=drawing_id, pk=message['id'])
    el.delete()
    return message


@transaction.atomic
def process_message(drawing_id, message):
    allowed_actions = [create_element, update_element, delete_element]
    actions_dict = dict((action.__name__, action) for action in allowed_actions)
    message_dict = json.loads(message)
    if message_dict['messageType'] == 'persistent':
        result_dict = actions_dict[message_dict['action']](drawing_id, message_dict)
        result = json.dumps(result_dict)
    else:
        result = message
    return result
# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json

from .models import SvgDatumBase, SvgElement, SvgAttribute, SvgElementType


def create_element(drawing, message):
    el_type = SvgElementType.objects.get(name=message['tagName'])
    el = SvgElement(type=el_type, drawing=drawing)
    attr_dict = message['attrs']
    el.save()
    for key in attr_dict:
        attr = SvgAttribute.objects.get(name=key)
        datum_class = [c for c in SvgDatumBase.__subclasses__() if c.data_type is attr.data_type][0]
        datum = datum_class(element=el, attribute=attr, value=attr_dict[key])
        datum.save()
    return {'action': 'create_element',
            'tagName': el.type.name,
            'id': el.pk,
            'attrs': el.get_attrs(),
            'messageType': 'persistent',
            'clientId': message['clientId']}


def process_message(drawing, message):
    allowed_actions = [create_element]
    actions_dict = dict((action.__name__, action) for action in allowed_actions)
    message_dict = json.loads(message)
    result_dict = actions_dict[message_dict['action']](drawing, message_dict)
    return json.dumps(result_dict)
# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json

from .models import SvgDatumBase, SvgElement, SvgAttribute


def create_datum(drawing, message):
    el = SvgElement.objects.get(pk=message['element_id'], drawing=drawing)
    attr = SvgAttribute.objects.get(name=message['attr_name'])
    datum_class = [c for c in SvgDatumBase.__subclasses__() if c.data_type is attr.data_type][0]
    datum = datum_class.objects.create(element=el, attribute=attr, value=message['attr_value'])
    message['id'] = datum.pk
    return message


def process_message(drawing, message):
    actions_dict = {'add_attr': create_datum}
    message_dict = json.loads(message)
    result_dict = actions_dict[message_dict['action']](drawing, message_dict)
    return json.dumps(result_dict)
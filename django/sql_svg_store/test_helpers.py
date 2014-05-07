# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from sql_svg_store import svg_data_types
from sql_svg_store.models import SvgElementType, SvgAttribute


class SvgDataMixin(object):
    def setUp(self):
        self.test_type = SvgElementType.objects.create(name='test_type')
        self.test_attr = SvgAttribute.objects.create(name='test_attr', data_type=svg_data_types.FLOAT_TYPE)
        super(SvgDataMixin, self).setUp()
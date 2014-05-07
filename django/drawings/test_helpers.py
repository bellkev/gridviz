# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from django.contrib.auth import get_user_model

from drawings.models import Drawing


class UserDataMixin(object):
    def setUp(self):
        self.login_kwargs = {'username': 'joe', 'password': 'abc'}
        self.other_login_kwargs = {'username': 'jane', 'password': 'abc'}
        self.test_user = get_user_model().objects.create_user(**self.login_kwargs)
        self.other_user = get_user_model().objects.create_user(**self.other_login_kwargs)
        super(UserDataMixin, self).setUp()


class LoggedInMixin(UserDataMixin):
    def setUp(self):
        super(LoggedInMixin, self).setUp()
        self.client.login(**self.login_kwargs)


class DrawingDataMixin(object):
    def setUp(self):
        self.test_drawing = Drawing.objects.create(title='abc', created_by=self.test_user)
        self.other_drawing = Drawing.objects.create(title='def', created_by=self.other_user)
        super(DrawingDataMixin, self).setUp()
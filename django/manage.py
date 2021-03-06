#!/usr/bin/env python

# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

from gevent import monkey
monkey.patch_all()
import pymysql
pymysql.install_as_MySQLdb()

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gridviz.settings.dev_runserver")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
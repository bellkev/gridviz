# Copyright (c) 2014 Kevin Bell. All rights reserved.
# See the file LICENSE.txt for copying permission.

import json
import sys

from coveralls.api import Coveralls


class MergeCoveralls(Coveralls):
    def __init__(self, merge_file, **kwargs):
        super(MergeCoveralls, self).__init__(**kwargs)
        with open(merge_file, 'rb') as mf:
            self.external_data = json.loads(mf.read())

    def create_data(self):
        merge_data = super(MergeCoveralls, self).create_data()
        merge_data['source_files'] += self.external_data['source_files']
        return merge_data

try:
    external_file = sys.argv[1]
except IndexError:
    print "ERROR: You must specify an external file to merge"
    exit(1)
coveralls = MergeCoveralls(external_file)
print "Submitting coverage to coveralls.io..."
result = coveralls.wear()
print "Coverage submitted!"
print result['message']
print result['url']
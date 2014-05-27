/*
 * Copyright (c) 2014 Kevin Bell. All rights reserved.
 * See the file LICENSE.txt for copying permission.
 */

// Blow up on errors
casper.on('resource.received', function (resource) {
    if (resource.status !== 200) {
        casper.test.fail('Failed to load resource at ' + resource.url);
    }
});
casper.on('page.error', function (e) {
    casper.test.fail(e);
});

// Test
casper.test.begin('Run smoke tests on production-style site', function (test) {
    casper.start(casper.cli.options.start + '/accounts/login/', function () {
        test.assertHttpStatus(200, 'make sure login page loads');
    }).run(function () {
        test.done();
    });
});


/*
 * Copyright (c) 2014 Kevin Bell. All rights reserved.
 * See the file LICENSE.txt for copying permission.
 */

// Blow up on errors
casper.on('resource.received', function (resource) {
    if (resource.status >= 400) {
        this.test.fail('Failed to load resource at ' + resource.url);
    }
});
casper.on('page.error', function (e) {
    this.test.fail(e);
});

// Test
casper.test.begin('Run smoke tests on production-style site', function (test) {
    casper.start(casper.cli.options.start + '/accounts/login/');
    casper.then(function () {
        test.assertHttpStatus(200, 'make sure login page loads');
    });
    casper.then(function () {
        this.fill('#login form', {
            'username': casper.cli.options.testUser,
            'password': casper.cli.options.testPass
        }, true);
    });
    casper.then(function () {
        test.assertUrlMatch(/drawings/, 'make sure we can login');
    });
    casper.run(function () {
        test.done();
    });
});


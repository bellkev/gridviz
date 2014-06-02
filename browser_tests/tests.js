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

// Include client scripts
casper.options.clientScripts.push('bower_components/jquery/dist/jquery.min.js');

// Test
casper.test.begin('Run smoke tests on production-style site', function (test) {
    casper.start(casper.cli.options.start + '/accounts/login/');

    // Load site
    casper.then(function () {
        test.assertHttpStatus(200, 'make sure login page loads');
    });
    casper.then(function () {
        this.fill('#login form', {
            'username': casper.cli.options.testUser,
            'password': casper.cli.options.testPass
        }, true);
    });

    // Login
    casper.then(function () {
        test.assertUrlMatch(/drawings/, 'make sure we can login');
    });

    // Make a drawing
    casper.then(function () {
        this.click('#new-drawing');
    });
    casper.then(function () {
        this.fill('#drawing-create form', {
            'title': 'My Drawing'
        }, true);
    });
    casper.then(function () {
        test.assertSelectorHasText('#drawing-update .content-title', 'My Drawing', 'make sure we can make a drawing');
    });

    // Edit the drawing
    casper.run(function () {
        test.done();
    });
});


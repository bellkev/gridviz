'use strict';

/*
 * Copyright (c) 2014 Kevin Bell. All rights reserved.
 * See the file LICENSE.txt for copying permission.
 */

var sharedConfig = require('./karma-shared.conf');

module.exports = function (config) {
    sharedConfig(config);
    config.set({
        browsers: ['PhantomJS'],
        preprocessors: {
            'angular/app.js': ['coverage']
        },
        reporters: ['coverage', 'dots'],
        coverageReporter: {
            type : 'lcovonly',
            dir : 'coverage/'
        }
    });
};
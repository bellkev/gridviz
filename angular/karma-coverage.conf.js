var sharedConfig = require('./karma-shared.conf');

module.exports = function (config) {
    sharedConfig(config);
    config.set({
        browsers: ['PhantomJS'],
        preprocessors: {
            'app.js': ['coverage']
        },
        reporters: ['coverage']
    });
};
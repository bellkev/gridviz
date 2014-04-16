//noinspection JSUnresolvedVariable
module.exports = function (config) {
    config.set({
        browsers: ['PhantomJS'],
        files: ['../bower_components/angular/angular.js',
                '../bower_components/angular-mocks/angular-mocks.js',
                'app.js', 'app.spec.js'],
        frameworks: ['jasmine'],
        preprocessors: {
            'app.js': ['coverage']
        },
        reporters: ['coverage']
    });
};
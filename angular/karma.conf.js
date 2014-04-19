//noinspection JSUnresolvedVariable
module.exports = function (config) {
    config.set({
        browsers: ['Chrome'],
        files: ['../bower_components/jquery/dist/jquery.js',
                '../bower_components/jquery.threedubmedia/event.drag/jquery.event.drag.js',
                '../bower_components/angular/angular.js',
                '../bower_components/angular-mocks/angular-mocks.js',
                'app.js', 'app.spec.js'],
        frameworks: ['jasmine'],
        reporters: ['progress']
//        preprocessors: {
//            'app.js': ['coverage']
//        },
//        reporters: ['coverage']
    });
};
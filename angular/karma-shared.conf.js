module.exports = function (config) {
    config.set({
        files: ['../bower_components/jquery/dist/jquery.js',
                '../bower_components/jquery.threedubmedia/event.drag/jquery.event.drag.js',
                '../bower_components/angular/angular.js',
                '../bower_components/lodash/dist/lodash.js',
                '../bower_components/angular-mocks/angular-mocks.js',
                '../bower_components/jquery-simulate/jquery.simulate.js',
                'app.js', 'app.spec.js'],
        frameworks: ['jasmine']
    });
};
describe('GridvizController', function(){

    beforeEach(module('GridvizEditor'));

    it('should set initial message to be "Hello!"', inject(function($controller) {
        var scope = {},
        ctrl = $controller('GridvizController', {$scope:scope});
        expect(scope.message).toBe('Hello!');
    }));

});

describe('SvgElement', function(){

    var scope, el;

    beforeEach(module('GridvizEditor'));
    beforeEach(inject(function($compile, $rootScope) {
        scope = $rootScope;
        scope.el =  { tagName: 'rect', attrs: { width: 10 } };
        el = angular.element('<div><svg-element element="el"></svg-element></div>');
        $compile(el)(scope);
        scope.$apply();
    }));

    it('should set correct tag name', function () {
        expect(el.children()[0].localName).toBe('rect');
    });

    it('should bind attributes', function () {
        expect(el.children().attr('width')).toBe('10');
        scope.el.attrs.width = 5;
        scope.$apply();
        expect(el.children().attr('width')).toBe('5');
    });

});
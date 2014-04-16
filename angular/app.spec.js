describe('GridvizController', function(){

    beforeEach(module('GridvizEditor'));

    it('should set initial message to be "Hello!"', inject(function($controller) {
        var scope = {},
        ctrl = $controller('GridvizController', {$scope:scope});
        expect(scope.message).toBe('Hello!');
    }));

});
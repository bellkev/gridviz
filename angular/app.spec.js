describe('gridvizEditor', function () {

    beforeEach(module(function ($provide) {
        $provide.value('$window', {
            WebSocket: function (url) {
                this.send = function (message) {};
            }
        });
    }));

    describe('GridvizController', function () {
        var scope, backend, loc, createController;

        beforeEach(module('gridvizEditor'));
        beforeEach(inject(function ($httpBackend, $controller) {
            backend = $httpBackend;
            loc = { absUrl: function () {
                return  "http://www.gridviz.com/drawings/5/edit"
            }};
            scope = {};
            createController = function() {
                return $controller('GridvizController', {'$scope': scope, '$location': loc});
            };
        }));

        afterEach(function () {
            backend.verifyNoOutstandingExpectation();
            backend.verifyNoOutstandingRequest();
        });

        it('should get initial drawing dump', function () {
            var drawing = {
                "elements": [
                    {"attrs": {"y": 200.0, "x": 200.0, "height": 200.0, "width": 200.0}, "tagName": "rect"}
                ],
                "title": "asdf"};
            backend.expectGET('http://www.gridviz.com/drawings/5').respond(drawing);
            createController();
            backend.flush();
            expect(scope.drawing.elements[0].attrs.y).toBe(200.0);
        });
    });

    describe('svgElement', function () {
        var scope, el;

        beforeEach(module('gridvizEditor'));
        beforeEach(inject(function ($compile, $rootScope) {
            scope = $rootScope;
            scope.el =  { tagName: 'rect', attrs: { width: 10 } };
            el = angular.element('<div><svg-element element="el"></svg-element></div>');
            $compile(el)(scope);
            scope.$apply();
        }));

        it('should set correct tag name', function () {
            expect(el.children()[0].localName).toBe('rect');
        });

        it('should use the svg namespace', function () {
            expect(el.children()[0].namespaceURI).toBe('http://www.w3.org/2000/svg');
        });

        it('should bind attributes', function () {
            expect(el.children().attr('width')).toBe('10');
            scope.el.attrs.width = 5;
            scope.$apply();
            expect(el.children().attr('width')).toBe('5');
        });

    });

    describe('editorService', function () {
        var es, scope;

        beforeEach(module(function ($provide) {
            $provide.value('messageService', {
                sendMessage: function () {}
            });
        }));
        beforeEach(module('gridvizEditor'));
        beforeEach(inject(function (editorService, $rootScope) {
            es = editorService;
            scope = $rootScope;
        }));

        it('should change element coordinates by grid increments', function () {
            var el =  { tagName: 'rect', attrs: {x: 20, y: 20, width: 20, height: 20} };
            es.drag(el, {offsetX: 22, offsetY: 22});
            expect(el.attrs.x).toBe(20);
            es.drag(el, {offsetX: 32, offsetY: 32});
            expect(el.attrs.x).toBe(40);
        });

        it('should handle circle attrs', function () {
            var el =  { tagName: 'circle', attrs: {cx: 30, cy: 30, r: 10} };
            es.drag(el, {offsetX: 32, offsetY: 32});
            expect(el.attrs.cx).toBe(50);
        });
    });
});
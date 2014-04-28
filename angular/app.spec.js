'use strict';

/*
 * Copyright (c) 2014 Kevin Bell. All rights reserved.
 * See the file LICENSE.txt for copying permission.
 */

describe('gridvizEditor', function () {

    beforeEach(module({
        $window: {
            WebSocket: function (url) {
                this.send = _.noop;
            }},
        $location: {
            absUrl: function () {
                return  "http://www.gridviz.com/drawings/5/edit"
            },
            port: _.constant(8000),
            host: _.constant('localhost')
        }
    }));

    describe('GridvizController', function () {
        var scope, backend, createController;

        beforeEach(module('gridvizEditor'));
        beforeEach(inject(function ($httpBackend, $controller) {
            backend = $httpBackend;
            scope = {};
            createController = function () {
                return $controller('GridvizController', {'$scope': scope});
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
        var scope, el, lastDragOpts;

        beforeEach(module('gridvizEditor'));
        beforeEach(module(function ($provide) {
            $provide.value('editorService', {
                drag: function (el, opts) {
                    lastDragOpts = opts;
                }
            });
        }));
        beforeEach(inject(function ($compile, $rootScope) {
            scope = $rootScope;
            scope.el = { tagName: 'rect', attrs: { x: 10, y: 10, width: 10, height: 10 } };
            el = angular.element('<svg><svg-element element="el"></svg-element></svg>');
            angular.element('body').append(el);
            $compile(el)(scope);
            scope.$apply();
        }));

        afterEach(function () {
            angular.element('svg').remove();
        });

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

        it('should be draggable', function () {
            var initialX = el.children().offset().left;
            var initialY = el.children().offset().top;
            el.children().simulate("drag", {
                moves: 1,
                dx: 5,
                dy: 5
            });
            expect(lastDragOpts).toEqual({offsetX: initialX + 5, offsetY: initialY + 5});
        })

    });

    describe('editorService', function () {
        var es, scope, lastMessage, rect, circle;

        beforeEach(module('gridvizEditor'));
        beforeEach(module(function ($provide) {
            $provide.value('messageService', {
                sendUiMessage: function (message) {
                    lastMessage = message;
                }
            });
        }));
        beforeEach(inject(function (editorService, $rootScope) {
            es = editorService;
            scope = $rootScope;
            rect = { id: 1, tagName: 'rect', attrs: {x: 20, y: 20, width: 20, height: 20} };
            circle = { id: 2, tagName: 'circle', attrs: {cx: 30, cy: 30, r: 10} };
            lastMessage = null;
        }));

        describe('drag', function () {
            it('should not change attrs or send a message if moved less than a grid space', function () {
                es.drag(rect, {offsetX: 22, offsetY: 22});
                expect(rect.attrs.x).toBe(20);
                expect(lastMessage).toBeNull();
            });

            it('should send a message if moved a grid space', function () {
                es.drag(rect, {offsetX: 32, offsetY: 32});
                expect(lastMessage).toEqual({
                    action: 'update_el',
                    id: 1,
                    attrs: { x: 40, y: 40, width: 20, height: 20 }
                });
            });

            it('should handle circle attrs', function () {
                es.drag(circle, {offsetX: 32, offsetY: 32});
                expect(lastMessage).toEqual({
                    action: 'update_el',
                    id: 2,
                    attrs: { cx: 50, cy: 50, r: 10 }
                });
            });
        });
    });

    describe('messageService', function () {
        var ms, ws, lastWsMessage;

        beforeEach(module('gridvizEditor'));
        beforeEach(module(function ($provide) {
            $provide.value('$window', {
                WebSocket: function (uri) {
                    this.send = function (message) {
                        lastWsMessage = message;
                    };
                    ws = this;
                }
            });
        }));
        beforeEach(inject(function (messageService) {
            ms = messageService;
            lastWsMessage = undefined;
        }));

        describe('ui messages', function () {
            var ownServerData, otherServerData, clientData, lastCallbackData;

            beforeEach(function () {
                lastCallbackData = null;
                ms.onUiMessage(function (data) {
                    lastCallbackData = data;
                });
                ownServerData = {
                    foo: 'bar',
                    clientId: ms.clientId,
                    messageType: 'ui'
                };
                otherServerData = {
                    foo: 'bar',
                    clientId: 'abc',
                    messageType: 'ui'
                };
                clientData = {
                    foo: 'bar'
                };
            });

            it('should add id, stringify, tag as ui message, and send ws messages', function () {
                ms.sendUiMessage(clientData);
                expect(JSON.parse(lastWsMessage)).toEqual(ownServerData);
            });

            it('should broadcast local ui messages', function () {
                ms.sendUiMessage(clientData);
                expect(lastCallbackData).toEqual(ownServerData);
            });

            it('should parse and broadcast messages from server to listeners', function () {
                ws.onmessage({data: JSON.stringify(otherServerData)});
                expect(lastCallbackData).toEqual(otherServerData);
            });

            it('should not re-broadcast its own ui messages', function () {
                ws.onmessage({data: JSON.stringify(ownServerData)});
                expect(lastCallbackData).toBeNull();
            });
        });

        describe('persistent messages', function () {
            var ownServerData, otherServerData, clientData, lastPersistentCallbackData, lastUiCallbackData;

            beforeEach(function () {
                lastPersistentCallbackData = null;
                lastUiCallbackData = null;
                ms.onPersistentMessage(function (data) {
                    lastPersistentCallbackData = data;
                });
                ms.onUiMessage(function (data) {
                    lastUiCallbackData = data;
                });
                ownServerData = {
                    foo: 'bar',
                    clientId: ms.clientId,
                    messageType: 'persistent'
                };
                otherServerData = {
                    foo: 'bar',
                    clientId: 'abc',
                    messageType: 'persistent'
                };
                clientData = {
                    foo: 'bar'
                };
            });

            it('should add id, stringify, tag as persistent message, and send ws messages', function () {
                ms.sendPersistentMessage(clientData);
                expect(JSON.parse(lastWsMessage)).toEqual(ownServerData);
            });

            it('should locally broadcast persistent messages for the ui but not for the persistent cache', function () {
                ms.sendPersistentMessage(clientData);
                expect(lastUiCallbackData).toEqual(ownServerData);
                expect(lastPersistentCallbackData).toBeNull();
            });

            it('should parse and broadcast messages from server to listeners', function () {
                ws.onmessage({data: JSON.stringify(otherServerData)});
                expect(lastPersistentCallbackData).toEqual(otherServerData);
            });

            it('should re-broadcast its own persistent messages once received from the server', function () {
                ws.onmessage({data: JSON.stringify(ownServerData)});
                expect(lastPersistentCallbackData).toEqual(ownServerData);
            });
        });

    });
});
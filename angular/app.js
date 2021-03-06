'use strict';

/*
 * Copyright (c) 2014 Kevin Bell. All rights reserved.
 * See the file LICENSE.txt for copying permission.
 */

angular.module('gridvizEditor', [])
    .controller('GridvizController', function ($scope, $http, $location, messageService, $document) {
        var url = $location.absUrl().replace(/\/edit.*/, '');
        $http.get(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}}).then(function (response) {
            $scope.drawing = response.data;
        });

        var getElementById = function (id) {
            return _.find($scope.drawing.elements, {id: id});
        };

        var deleteSelected = function () {
            _.forEach($scope.drawing.elements, function (el) {
                if (el.selected) {
                    messageService.sendPersistentMessage({
                        action: 'delete_element',
                        id: el.id
                    })
                }
            });
        };

        var deleteById = function (id) {
            _.remove($scope.drawing.elements, {id: id})
        };

        var updateId = function (oldId, newId) {
            _.find($scope.drawing.elements, {id: oldId}).id = newId;
        };

        messageService.onUiMessage(function (data) {
            if (data.action === 'update_element') {
                getElementById(data.id).attrs = data.attrs;
            }
            else if (data.action === 'create_element') {
                $scope.drawing.elements.push({
                    id: data.id || data.tempId,
                    tagName: data.tagName,
                    attrs: _.clone(data.attrs)
                })
            }
            else if (data.action === 'delete_element') {
                deleteById(data.id);
            }
            else if (data.action === 'update_id') {
                updateId(data.tempId, data.id);
                console.log("Updated element with tempId:", data.tempId, "To:", data.id);
            }
            // Apply if an apply isn't already in progress
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        });

        $scope.createRect = function () {
            var message = {
                action: 'create_element',
                tagName: 'rect',
                tempId: messageService.tempId(),
                attrs: {
                    x: 300,
                    y: 100,
                    width: 40,
                    height: 40
                }
            };
            console.log("Created element with tempId:", message.tempId);
            messageService.sendPersistentMessage(message);
        };

        $scope.deselectAll = function (ev) {
            if (!ev || ev.target === ev.currentTarget) {
                _.forEach($scope.drawing.elements, function (el) {
                    el.selected = false;
                });
            }
        };

        $document.keydown( function (ev) {
            if (ev.keyCode === 8) {
                deleteSelected();
            }
        });
    }).directive('panel', function ($window) {
        return {
            templateUrl: $window.serverData.templatePrefix + 'ngtemplates/panel.html',
            restrict: 'E',
            transclude: true,
            scope: {},
            link: function (scope, el, attrs) {
                scope.panelClasses = {
                    closed: true
                };
                scope.panelClasses[attrs.dock] = true;
            }
        }
    }).directive('svgElement', function ($compile, $document, editorService) {
        var postLink = function (scope, el) {
            var html, newEl, lastValues = {};

            // Set tag name
            html = document.createElementNS('http://www.w3.org/2000/svg', scope.element.tagName);
            newEl = $(html);
            el.replaceWith(newEl);
            $compile(newEl)(scope);

            // Make selectable
            newEl.mousedown(function (ev) {
                scope.deselect();
                scope.element.selected = true;
                scope.$apply();
            });

            var corners = _.times(4, _.constant('<div class="select-corner"/>')).map($);
            $document.find('#drawing-edit').append(corners);

            var updateCorners = function () {
                var pos = newEl.offset();
                _.merge(pos, {
                    bottom: pos.top + newEl[0].getBoundingClientRect().height,
                    right: pos.left + newEl[0].getBoundingClientRect().width
                });

                var mappings = [
                    {top: 'top', left: 'left'},
                    {top: 'top', left: 'right'},
                    {top: 'bottom', left: 'left'},
                    {top: 'bottom', left: 'right'}
                ];
                _.forEach(corners, function (corner, index) {
                    // TODO: Make this more efficient (e.g. don't update attrs when hidden) and test
                    corner.css({
                        display: scope.element.selected ? 'block' : 'none',
                        top: pos[mappings[index]['top']],
                        left: pos[mappings[index]['left']]
                    });
                });
            };

            // Bind attrs
            scope.$watch(function () {
                var gridvizAttrs = scope.element.attrs;
                _.forOwn(gridvizAttrs, function (val, key) {
                    if (lastValues[key] !== val) {
                        newEl.attr(key, val);
                        lastValues[key] = val;
                    }
                });
                updateCorners();
            });

            // Make draggable
            newEl.drag(function (ev, dd) {
                editorService.drag(scope.element, {offsetX: dd.offsetX, offsetY: dd.offsetY}, false);
                scope.$apply();
            });

            newEl.drag('end', function (ev, dd) {
                editorService.drag(scope.element, {offsetX: dd.offsetX, offsetY: dd.offsetY}, true);
                scope.$apply();
            });

            // Clean up
            scope.$on('$destroy', function () {
                _.invoke(corners, 'remove');
                newEl.remove();
            });
        };
        return {
            link: postLink,
            restrict: 'E',
            scope: {
                element: '=',
                deselect: '&'
            }
        }
    }).service('editorService', function (messageService) {
        this.drag = function (el, dd, persistent) {
            var xGrid = Math.round(dd.offsetX / 20) * 20;
            var yGrid = Math.round(dd.offsetY / 20) * 20;

            var toUpdate = {};

            if (el.tagName === 'circle') {
                toUpdate.cx = xGrid + el.attrs.r;
                toUpdate.cy = yGrid + el.attrs.r;
            }

            else {
                toUpdate.x = xGrid;
                toUpdate.y = yGrid;
            }

            var diff = _.pick(toUpdate, function (val, key) {
                return val !== el.attrs[key];
            });
            var newAttrs = _.merge(_.clone(el.attrs), diff);
            var message = {action: 'update_element', id: el.id, attrs: newAttrs};

            if (persistent) {
                messageService.sendPersistentMessage(message)
            } else if (!_.isEmpty(diff)) {
                messageService.sendUiMessage(message);
            }
        };
    }).service('messageService', function ($location, $window, $rootScope) {
        var self = this;
        var port = $location.port();
        var drawingId = $location.absUrl().match(/\/drawings\/(\d*)\//)[1];
        var uri = 'ws://' + $location.host() + (port ? ':' + port : '')
            + '/ws/' + drawingId + '?subscribe-broadcast&publish-broadcast';
        var ws = new $window.WebSocket(uri);
        var uiOnlyMessageName = 'gridviz.ui';
        var persistentMessageName = 'gridviz.persistent';
        var uiOnlyType = 'ui';
        var persistentType = 'persistent';

        var randomHex = function () {
            return _.random(Math.pow(2, 32)).toString(16);
        };
        self.clientId = randomHex() + randomHex();

        var tempPrefix = 'temp_';
        var isTempId = function (id) {
            return _.isString(id) && id.indexOf(tempPrefix) >= 0;
        };
        self.tempId = _.wrap(tempPrefix, _.uniqueId);

        ws.onmessage = function (message) {
            var messageData = JSON.parse(message.data);
            if (messageData.clientId !== self.clientId) {
                $rootScope.$emit(uiOnlyMessageName, messageData);
            }
            else if (messageData.action === 'create_element') {
                // A special action performed only on the client
                // to upgrade a tempId to a permanent one
                $rootScope.$emit(uiOnlyMessageName, {
                    action: 'update_id',
                    tempId: messageData.tempId,
                    id: messageData.id
                })
            }
            if (messageData.messageType === persistentType) {
                $rootScope.$emit(persistentMessageName, messageData);
            }
        };

        var wsTime;
        ws.onopen = function () {
            wsTime = Date.now();
            console.log('Websocket open');
        };

        ws.onclose = function () {
            console.log('Websocket closed after', Date.now() - wsTime, 'ms');
        };

        var onMessage = function (name, handler) {
            $rootScope.$on(name, function (e, data) {
                handler(data);
            });
        };

        self.onUiMessage = function (handler) {
            onMessage(uiOnlyMessageName, handler);
        };

        self.onPersistentMessage = function (handler) {
            onMessage(persistentMessageName, handler);
        };

        var sendMessage = function (name, data) {
            if (isTempId(data.id)) {
                // The tempId/permanent id pair can be cached on the server is this becomes too limiting
                // (e.g. to allow a rapid-fire create/delete)
                throw new Error("A tempId can only be used to create elements");
            }
            else {
                data.clientId = self.clientId;
                $rootScope.$emit(uiOnlyMessageName, data);
                ws.send(JSON.stringify(data));
            }
        };

        self.sendUiMessage = function (data) {
            data.messageType = uiOnlyType;
            sendMessage(uiOnlyMessageName, data);
        };

        self.sendPersistentMessage = function (data) {
            data.messageType = persistentType;
            sendMessage(persistentMessageName, data);
        };
    });
angular.module('gridvizEditor', [])
    .controller('GridvizController',function ($scope, $http, $location, messageService) {
        var url = $location.absUrl().replace(/\/edit.*/, '');
        $http.get(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}}).then(function (response) {
            $scope.drawing = response.data;
        });

        var getElementById = function (id) {
            var els = $scope.drawing.elements;
            for (var index = 0; index < els.length; index++) {
                if (els[index].id === id) {
                    return els[index];
                }
            }
        };

        messageService.onMessage(function (data) {
            if (data.action = 'update_el') {
                getElementById(data.id).attrs = data.attrs;
                $scope.$apply();
            }
        });


    }).directive('svgElement',function ($compile, $document, editorService) {
        var postLink = function (scope, el) {
            var html, newEl, lastValues = {};

            // Set tag name
            html = document.createElementNS('http://www.w3.org/2000/svg', scope.element.tagName);
            newEl = angular.element(html);
            el.replaceWith(newEl);
            $compile(newEl)(scope);

            // Bind attrs
            scope.$watch(function () {
                var gridvizAttrs = scope.element.attrs;
                _.forOwn(gridvizAttrs, function (val, key) {
                    if (lastValues[key] !== val) {
                        newEl.attr(key, val);
                        lastValues[key] = val;
                    }
                });
            });

            // Make draggable
            newEl.drag(function (ev, dd) {
                editorService.drag(scope.element, {offsetX: dd.offsetX, offsetY: dd.offsetY});
                scope.$apply();
            });
        };
        return {
            link: postLink,
            restrict: 'E',
            scope: {
                element: '='
            }
        }
    }).service('editorService', function (messageService) {
        this.drag = function (el, dd) {
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

            if (!_.isEmpty(diff)) {
                _.merge(el.attrs, diff);
                var message = {action: 'update_el', id: el.id};
                message.attrs = el.attrs;
                messageService.sendMessage(message);
            }
        };
    }).service('messageService', function ($location, $window, $rootScope) {
        var port = $location.port();
        var uri = 'ws://' + $location.host() + (port ? ':' + port : '')
                    + '/ws/foobar?subscribe-broadcast&publish-broadcast';
        var ws = new $window.WebSocket(uri);
        // A random 32-bit int as hex
        var randomHex = function () { return Math.floor(Math.random() * Math.pow(2, 32)).toString(16); };
        var clientId = randomHex() + randomHex();

        var uiMessageName = 'gridviz.ui.message';

        ws.onmessage = function (message) {
            $rootScope.$emit(uiMessageName, JSON.parse(message.data));
        };

        this.onMessage = function (handler) {
            $rootScope.$on(uiMessageName, function (e, data) {
                if (data.clientId !== clientId) {
                    handler(data);
                }
            });
        };

        this.sendMessage = function (data) {
            data.clientId = clientId;
            ws.send(JSON.stringify(data));
        };
    });
angular.module('gridvizEditor', [])
    .controller('GridvizController', function ($scope) {

        $scope.elements = [
            {
                tagName: 'rect',
                attrs: {
                    x: 100,
                    y: 100,
                    width: 100,
                    height: 100
                }
            },
            {
                tagName: 'circle',
                attrs: {
                    cx: 250,
                    cy: 250,
                    r: 50
                }
            }
        ];

    }).directive('svgElement', function ($compile, $document, editorService) {
        var postLink = function (scope, el, attrs) {
            var html, newEl, lastValues = {};

            // Set tag name
            html = $document[0].createElementNS('http://www.w3.org/2000/svg', scope.element.tagName);
            newEl = angular.element(html);
            el.replaceWith(newEl);
            $compile(newEl)(scope);

            // Bind attrs
            scope.$watch(function () {
                var gridvizAttrs = scope.element.attrs;
                for (var key in gridvizAttrs) {
                    var value = gridvizAttrs[key];
                    if (lastValues[key] !== value) {
                        newEl.attr(key, value);
                        lastValues[key] = value;
                    }
                }
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
    }).service('editorService', function () {
        this.drag = function (el, dd) {
            var xGrid = Math.round( dd.offsetX / 20 ) * 20;
            var yGrid = Math.round( dd.offsetY / 20 ) * 20;

            if (el.tagName === 'circle') {
                el.attrs.cx = xGrid + el.attrs.r;
                el.attrs.cy = yGrid + el.attrs.r;
            }

            else  {
                el.attrs.x = xGrid;
                el.attrs.y = yGrid;
            }
        };
    });
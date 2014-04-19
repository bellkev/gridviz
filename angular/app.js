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
            {tagName: 'circle'}
        ]
    })
    .directive('svgElement', function ($compile, $document) {
        var postLink = function (scope, el, attrs) {
            var html = $document[0].createElementNS('http://www.w3.org/2000/svg', scope.element.tagName);
            var newEl = angular.element(html);
            var lastValues = {};

            // Set tag name
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
        };
        return {
            link: postLink,
            restrict: 'E',
            scope: {
                element: '='
            }
        }
    });
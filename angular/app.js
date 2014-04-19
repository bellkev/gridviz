angular.module('gridvizEditor', [])
    .controller('GridvizController', function ($scope) {
        $scope.message = 'Hello!';
        $scope.el = {'tagName': 'rect'};
    })
    .directive('svgElement', function ($compile, $document) {
        var postLink = function (scope, el, attrs) {
            var html = $document[0].createElement(scope.element.tagName);
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
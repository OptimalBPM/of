/// <reference path="../../typings/angularjs/angular.d.ts" />
/// <reference path="../../typings/jquery/jquery.d.ts" />

console.log("Before schemaTree definition");
import "angular";
import "jquery";
import "angular-ui-tree";
import "angular-ui-tree/angular-ui-tree.min.css!"
import "../controllers/schemaTreeController"
import {TreeScope} from "../types/schemaTreeTypes"

export function schemaTree():ng.IDirective {
    return {
        restrict: 'E',
        scope: {
            itemRenderer: "@",
            newNodeObjectId: "@",
            nodeManager : "=",
            expanderPosition: "@",
            treeOptions : "="
        },
        controller: "SchemaTreeController",
        link: ($scope:TreeScope, element:JQuery) => {
            console.log("link function in schemaTree directive called ");

            if (!($scope.expanderPosition))
            {
                $scope.expanderPosition = "left";
            }
            $scope.$watch('onInit', function (value) {
                if ($scope.nodeManager) {
                    console.log("Before tree.doInit");
                    $scope.tree.doInit($scope);
                }
                else
                {
                    console.log("Initiating schemaTree $scope.nodeManager not set!")
                }

            })

        },
        templateUrl: 'views/schematree.html'
    }

}



console.log("After schemaTree definition");
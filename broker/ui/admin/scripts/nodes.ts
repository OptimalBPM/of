// The references looks like this so that they'll work in the output /dist folder
/// <reference path="../typings/tsd.d.ts" />


import "jquery";
import "angular";
import "angular-route";
import "angular-strap";
import "angular-strap/angular-strap.tpl";
import {SchemaTreeController} from "../controllers/schemaTreeController";
import {schemaTree} from "../directives/schemaTree";
import {NodesController} from "../controllers/nodesController";
import {nodes} from "../directives/nodes";


export function initNodes() {
    angular.module("schemaTreeModule", [])
        .controller("SchemaTreeController", ["$scope", "$q", "$timeout", SchemaTreeController])
        .directive("schemaTree", schemaTree)
        .directive("ngRightClick", function ($parse) {
            return function (scope, element, attrs) {
                let fn: any = $parse(attrs.ngRightClick);
                element.bind("contextmenu", function (event) {
                    scope.$apply(function () {
                        event.preventDefault();
                        fn(scope, {$event: event});
                    });
                });
            };
        });


    angular.module("nodesModule", ["ngRoute", "mgcrea.ngStrap", "ui.tree", "ui.ace", "schemaForm", "ui.layout", "ngAnimate", "schemaTreeModule"])
        .controller("NodesController", ["$scope", "$http", "$q", NodesController])
        .directive("nodes", nodes)
        // TOOD: Remove this route? It should certainly not be here
        .config(["$routeProvider", function ($routeProvider) {
            $routeProvider.when("/nodes", {
                templateUrl: "views/nodes/nodes.html"
            });
        }]);

    // nodes template cache
    // {nodesTemplateCache}

}

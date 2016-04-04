/// <reference path="../typings/angularjs/angular.d.ts" />
/// <reference path="../typings/jquery/jquery.d.ts" />


import "angular";

import "jquery";
import "angular-ui-select";
import {NodesScope} from  "../types/schemaTreeTypes";


export function nodes(): ng.IDirective {
    return {
        restrict: "E",
        scope: {},
        controller: "NodesController",
        link: ($scope: NodesScope, element: JQuery) => {
            console.log("link function in nodes directive called ");
        },
        templateUrl: "views/nodes.html"
    };

}



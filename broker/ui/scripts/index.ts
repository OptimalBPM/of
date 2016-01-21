///<reference path="../typings/angularjs/angular.d.ts" />

'use strict';

/**
 * @ngdoc overview
 * @name mainApp
 * @description
 * # Optimal Framework
 *
 * Main module of the application.
 */
//sourceMappingUrl=main.js.map


console.log("Before app defines");
import "jquery";


import "bootstrap";
import "bootstrap/css/bootstrap.css!"

import "angular";
import "angular-route";
import "angular-cookies";
import "angular-touch";
import "angular-sanitize";
import "angular-animate";
import "angular-schema-form";
import "angular-ui-layout";
import "angular-ui-layout/ui-layout.css!";
import "font-awesome"

import "bootstrap3-dialog";

import {initNodes} from "./nodes";
import {initPlugins, initRoutes} from "../plugins/init";



import {AboutController} from "../controllers/about";
import {AdminController} from "../controllers/admin";
import {MainController} from "../controllers/main";
import {CustomRootScope} from "../types/schemaTreeTypes";
import {VerticalDraggableMenuController} from "../controllers/verticalDraggableMenuController";


// BootstrapDialog ambient declaration as there is no type definition
declare var BootstrapDialog: any;

function initApp() {


    // First initialize mbefe
    initNodes();
    var app = angular
        .module('mainApp',
        [
            'ngAnimate',
            'ngRoute',
            'ngSanitize',
            'ngTouch',
            'nodesModule',
            'ngCookies'
            //"ngRoute", "mgcrea.ngStrap", "ui.tree", "ui.ace", "schemaForm", "ui.layout", "ngAnimate", "schemaTreeModule"
        ]);

    // Register all controllers
    app.controller('AdminController', ["$scope", "$timeout", AdminController]);
    app.controller('MainController', ["$scope", "$http", "$route", MainController]);

    app.controller("AboutController", ["$scope", "$http", AboutController]);


    initPlugins(app);


    app.directive('afterRepeat', function () {
        // Do what is specified in "after-repeat" after a repeat is done.
        return function (scope, element, attrs) {
            if (scope.$last) {
                angular.element(element).scope().$eval(attrs.afterRepeat);
            }
        };
    });
    // Configure all routes
    app.config(($routeProvider) => {
        initRoutes($routeProvider)
            .when('/analysis', {
                templateUrl: 'views/analysis.html',

            })
            .when('/admin', {
                templateUrl: 'views/admin.html',
                // This is the mbe-nodes external directive, it needs an associated controller
                controller: "AdminController"
            })
            .when('/about', {
                templateUrl: 'views/about.html',
                controller: "AboutController"
            })
            .otherwise({
                redirectTo: '/about'
            });

    });

    // Find the html angular element.
    var $html = angular.element(document.getElementsByTagName('html')[0]);

    angular.element().ready(() => {
        // bootstrap the app manually
        console.log("Bootstrap the application.");

        angular.bootstrap($html, ['mainApp']);

        var $scope:CustomRootScope = <CustomRootScope>angular.element($html).scope();
        declare var BootstrapDialog:any;
        $scope.BootstrapDialog = BootstrapDialog;


    });

}

// Initialize
initApp();
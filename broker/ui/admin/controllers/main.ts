///<reference path="../typings/angularjs/angular.d.ts" />
interface MainScope extends ng.IScope {
    controller: MainController;
}


interface AdminSettings {
    theme: string;
}

export class MainController {

    $http: ng.IHttpService;
    $route: angular.route.IRouteService;
    $scope: MainScope;
    username: string;

    menus: any[];

    settings: AdminSettings;

    password: string;
    login_status: string = "Logging in...";


    /* Make menu items look nice when their associated view is navigated to */
    menu_item_class = (routeName) => {
        return this.button_controller_selected_look(
            routeName,
            "bpm_menu_item",
            "bpm_menu_item bpm_menu_item_selected");
    };

    menu_item_class_look = (routeName) => {
        return this.button_controller_selected_look(
            routeName,
            "bpm_menu_item_look",
            "bpm_menu_item_look bpm_menu_item_look_selected");
    };
    /* Return one class when selected and another when not */
    button_controller_selected_look = (routeName, unselected, selected) => {
        if (this.$route.current && (this.$route.current.$$route.originalPath === routeName)) {
            return selected;
        }
        return unselected;
    };

    loadMenus = () => {
        return this.$http.get("/plugins/admin_menus.json")
            .success((data): any => {
                this.menus = data;
                console.log("loaded menus");
            })
            .error((data, status, headers, config): any => {

                this.bootstrapAlert("Loading menus failed: " + status);
            });
    };

    constructor(private $scope: MainScope, $http: ng.IHttpService, $route: angular.route.IRouteService) {

        console.log("Initiating MainController" + $scope.toString());
        this.$route = $route;
        this.$scope = $scope;
        this.$http = $http;

        this.$scope.controller = this;
        this.loadMenus();

        console.log("Initiated MainController");

    }
}
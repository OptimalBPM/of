///<reference path="../typings/angularjs/angular.d.ts" />


interface AboutScope extends ng.IScope {
    broker_environment: string;
}

export class AboutController {

    $http:ng.IHttpService;
    $scope:AboutScope;

    get_about_data = () => {
            this.$scope.broker_environment = "";
            this.$http.get('/get_broker_environment').
                success((data, status, headers, config) => {
                    this.$scope.broker_environment = data;

                }).
                error((data, status, headers, config) => {
                    this.$scope.broker_environment = "Failed to retrieve broker environment: " + status;
                });
        };
    get_datatype = (value) => {
        if (angular.isObject(value)) {
            return "dict";
        } else
        if (angular.isArray(value)) {
            return "array";
        } else
        if (angular.isString(value)) {
            return "string"
        } else {
            return null;
        }
    };




    constructor(private $scope:AboutScope, $http:ng.IHttpService) {

        console.log("Initiating AboutController" + $scope.toString());


        this.$scope = $scope;

        this.$http = $http;
        this.get_about_data();
        console.log("Initiated AboutController");

    }
}
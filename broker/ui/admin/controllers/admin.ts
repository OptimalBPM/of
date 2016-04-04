///<reference path="../typings/angularjs/angular.d.ts" />

export class AdminController {

    $timeout: ng.ITimeoutService;


    resizeNodes = () => {
        $("#nodesContainer").height($(window).height() - $("#footerDiv").height() - $("#menuDiv").height() - 20);
    };

    constructor(private $scope: ng.IScope, $timeout: ng.ITimeoutService) {

        console.log("Initiating AdminController" + $scope.toString());
        this.$timeout = $timeout;

        $timeout(() => {
            // Set height
            this.resizeNodes();
            $(window).resize(() => {
                this.resizeNodes();
            });
        });
        console.log("Initiated AdminController");

    }
}
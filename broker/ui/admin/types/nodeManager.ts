/// <reference path="../typings/tsd.d.ts" />
import {SchemaTreeController} from "../controllers/schemaTreeController";
import {TreeNode, NodesScope, Dict} from "schemaTreeTypes";

export interface NodeManagement {

    /**
     * Synchronous. If assigned, called to init the tree. *Must* have the treeScope parameter(exact name),
     * exposes the scope of the tree and is the only way to set the rest of the callback and settings.
     * @param treeScope - The scope of the tree
     */

    // Only initiated if not already initiated.
    onInit(schemaTreeController: SchemaTreeController): void;


    /*The following callbacks should be set in the onInit callback, as the tree scope is available there */

    /** Synchronous. Called when a node is selected
     * @param treeNode
     */
    onSelectNode(treeNode: TreeNode): void;


    /**
     * Async. Called when a node is removed. Typically contains code to remove from backend, Must return a promise.
     * @param {string} id - The ObjectId of the node to remove
     * @returns {ng.IPromise}
     */
    onAsyncRemoveNode?(id: string): ng.IHttpPromise<any>;


    /**
     * Async. Called when a children should be loaded. Typically contains code to load from backend, Must return a promise.
     * @param {string} parentId - an Id of a parent node, can be null
     * @returns {ng.IPromise}
     */
    onAsyncLoadChildren?(parentId: string): ng.IHttpPromise<any>;


    /**
     * Async. Called when a children should be loaded. Typically contains code to load from backend, Must return a promise.
     * @returns {ng.IPromise}
     */
    onAsyncInitTree(): ng.IPromise<any>;


    /**
     * Should return a CSS base class given a tree item. Typically matches the shortname of the schema with a CSS class name.
     * @param {string} node - the tree item.
     * @returns {string}
     */
    getClassFromItem(node: TreeNode): string;


    /**
     * Should return a CSS base class given a tree node type,.
     * @param {string} nodeType - the tree item.
     * @returns {string}
     */
    getIconClass(nodeType: string): string;


}
/* Everyone inheriting from this class must implement the NodeManagement interface */

export class NodeManager implements NodeManagement {
    $q: ng.IQService;
    $http: ng.IHttpService;

    /* An instance of the nodeScope */
    nodeScope: NodesScope;

    /* The forms that are used for each schema id*/
    forms: Dict;

    /* The schema tree controller */
    tree: SchemaTreeController;

    getClassname = (): string => {
        return this.constructor.toString().match(/\w+/g)[1];
    };

    doSubmit = (submit_data: any) => {

        // First we broadcast an event so all fields validate themselves
        let result: any = this.nodeScope.$broadcast("schemaFormValidate");

        this.tree.log(result.toString());
        if (this.nodeScope.ngform.$valid) {
            // The form checked out, save data
            this.onSubmit(submit_data);

        }
        else {
            this.nodeScope.$root.BootstrapDialog.alert("The input didn't match validation!");
        }
    };

    onSubmit = (submit_data: any): void => {
        console.log("onSubmit not implemented in " + this.getClassname + " base class!");
    };
    onInit = (schemaTreeController: SchemaTreeController) => {
        console.log("onInit not implemented in " + this.getClassname() + " base class!");
    };
    onSelectNode = (treeNode: TreeNode): void => {
        console.log("onSelectNode not implemented in " + this.getClassname() + " base class!");
    };
    getClassFromItem = (node: TreeNode): string => {
        console.log("onSelectNode not implemented in " + this.getClassname() + " base class!");
        return "";
    };
    getIconClass = (nodeType: string): string => {
        console.log("getIconClass not implemented in " + this.getClassname() + " base class!");
        return "";
    };
    onAsyncInitTree = (): ng.IPromise<any> => {
        console.log("onAsyncInitTree not implemented in " + this.getClassname() + " base class!");
        return null;
    };

    constructor(private $scope: NodesScope, $http: ng.IHttpService, $q: ng.IQService) {

        console.log("Initiating the nodes manager base class" + $scope.toString());
        $scope.nodeManager = this;
        this.nodeScope = $scope;
        this.$q = $q;
        this.$http = $http;
        console.log("Initiated the nodes manager base class");
    }
}

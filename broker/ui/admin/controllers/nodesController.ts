/// <reference path="../typings/angularjs/angular.d.ts" />

/**
 * Module that implements a tree using MBE, a schema validated form and ui layout

 * @module nodes
 * @service Nodes
 * @author Nicklas Börjesson
 * @link https://www.github.com/optimalbpm/mbe
 */
'use strict';
import "angular";
import "angular-strap";
import "angular-schema-form";
import "angular-ui-layout";
import "angular-ui-layout/ui-layout.css!";
import "angular-animate";

import "ace";
import "ace/theme-monokai";
import "ace/mode-json";
import "angular-ui/ui-ace";
import "networknt/angular-schema-form-ui-ace";

import "angular-schema-form-dynamic-select";

import "bootstrap3-dialog";
import "bootstrap3-dialog/dist/css/bootstrap-dialog.min.css!"
import {NodeManager, NodeManagement} from "../types/nodeManager"
import {TreeNode} from "../types/schemaTreeTypes"



/* The SchemaTreeControl class is instantiated as a controller class in the typescript model */
export class NodesController extends NodeManager implements NodeManagement {

    // The history data
    history: any[];

    /** The groups variable holds a list of all the groups. */
    groups: any[];


    /* TODO: Unresolved bug, sometimes nodes aren't initialized correctly (undefined arrays) \n Possible to add nodes twice */
    /* TODO: Add proper($timeout-based) animation delay to tree */
    /* TODO: Follow-up so that angular-strap select dropdown positioning on scroll is rectified */

    // *********************** Web service calls ******************************

    /**
     * Returns a promise for all nodes under the node with parent_id
     * @param {string} parentId - an objectId of a parent node, can be null
     * @returns {IHttpPromise}
     */
    onAsyncLoadChildren = (parentId: string): ng.IHttpPromise<any> => {
        if (parentId != null) {
            parentId = "ObjectId(" + parentId.toString() + ")"
        }
        return this.$http.post('node/find', {"parent_id": parentId});
    };

    /**
     * Removes the given node from the database
     * @param {string} nodeId - The ObjectId of the node to remove
     * @returns {IHttpPromise}
     */
    onAsyncRemoveNode = (nodeId: string): ng.IHttpPromise<any> => {
        return this.$http.post('node/remove', {"_id": nodeId});
    };

    /**
     * Returns a list of history items for the node
     * @param {string} historyId - The ObjectId of the node to list history for
     * @returns {IHttpPromise}
     */
    loadHistory = (historyId: string): ng.IHttpPromise<any> => {
        return this.$http.post('node/history', {"_id": historyId})
    };

    /**
     * Is called when the schema form save-button is clicked
     * @param {object} submitData - The data to be submitted
     */
    onSubmit = (submitData: any): void => {
        this.saveNode(submitData);
    };


    /**
     * Returns a promise to save the provided data to the database
     * @param {object} saveData - to save, must comply with the relevant mbe schema
     * @returns {IHttpPromise}
     */
    saveNode = (saveData): ng.IHttpPromise<any> => {

        var id = saveData["_id"];
        var _curr_child;

        _curr_child = this.tree.findChild(this.tree.children, id);

        if (id == this.tree.treeScope.newNodeObjectId) {
            // Delete the id so that a new item is saved.
            delete saveData["_id"];
        }

        return this.$http.post('node/save', saveData)
            .success((_id) => {
                var strId: string = _id.toString();
                saveData["_id"] = strId;
                this.tree.data[strId] = saveData;
                _curr_child.id = saveData["_id"];
                _curr_child.title = saveData["name"];
                _curr_child.type = saveData["schemaRef"];
                _curr_child.allowedChildTypes = saveData["allowedChildTypes"];
                console.log("Data saved, _id: " + strId)
            })
            .error((data: any, status: number, headers: ng.IHttpHeadersGetter, config: ng.IRequestConfig) => {
                this.nodeScope.$root.BootstrapDialog.alert("Saving node failed: " + status);
            });
    };

    /**
     * Returns a CSS base class given a tree item
     * @param {TreeNode} node - the tree item.
     * @returns {string}
     */
    getClassFromItem = (node: TreeNode): string => {
        return "node";
    };
    /**
     * Returns a CSS icon base class given a node type
     * @param {string} nodeType - the node type.
     * @returns {string}
     */
    getIconClass = (nodeType: string): string => {
        return "";
    };

    /**
     *********************** Refresh functions ******************************
     */

    /**
     * Initialize groups
     */
    onInitGroups = function () {
        return this.onAsyncLoadChildren("000000010000010001e64c24")
            .success((_data)  => {
                this.groups = this.tree.dataToLookups(_data);

            })
            .error((data, status) => {
                this.nodeScope.$root.BootstrapDialog.alert("Loading groups failed: " + status);
            });
    };

    /**
     * Load all schemas
     */
    onInitSchemas = (): ng.IHttpPromise<any> => {
        return this.$http.get('node/get_schemas')
            .success((data: any) => {
                this.tree.schemas = data;
            })
            .error((data: any, status: number, headers: ng.IHttpHeadersGetter, config: ng.IRequestConfig) => {
                this.nodeScope.$root.BootstrapDialog.alert("Loading schemas failed: " + status);
            });
    };

    /**
     * Load all UI forms
     */
    onInitForms = (): ng.IHttpPromise<any> => {

        return this.$http.get('views/nodes/node_forms.js')
            .success((data: any) => {
                var _nodeSchemaRef = 'of://node.json';
                this.forms = {};
                // Import the data, pass the tree scope to the function
                var _data = new Function("scope", data.toString()).call(this, this.tree);
                var _nodeForm = _data[_nodeSchemaRef];

                Object.keys(_data).forEach(
                    (_currSchemaRef) => {

                        if (_currSchemaRef == _nodeSchemaRef) {
                            // Do not concatenate with itself
                            var _newForm = _nodeForm.slice(0)
                        }
                        else {
                            // Insert form after nodename and description in base node form
                            var _newForm = _nodeForm.slice(0);
                            _newForm.splice.apply(_newForm, [2, 0].concat(_data[_currSchemaRef]))
                        }
                        // Add submit and store the finished form.
                        this.forms[_currSchemaRef] = _newForm.concat(
                            [
                                {
                                    type: "submit",
                                    title: "Save"
                                }
                            ]);
                    }
                );
                // TODO: Is AnyOf implemented? https://github.com/Textalk/angular-schema-form/issues/163me
                // TODO: Are $refs implemented? https://github.com/Textalk/angular-schema-form/issues/69
                // TODO: Is populating implemented? https://github.com/Textalk/angular-schema-form/issues/205

            })
            .error((data: any, status: number, headers: ng.IHttpHeadersGetter, config: ng.IRequestConfig) => {
                this.nodeScope.$root.BootstrapDialog.alert("Loading forms failed: " + status);
            });
    };


    /**
     * Set the currently edited schema form
     * @param node
     */
    set_details = (node):void => {
        var schemaRef = "";
        this.nodeScope.selected_schema = null;
        if ("schemaRef" in node) {
            schemaRef = node["schemaRef"];
            this.nodeScope.selected_schema = this.tree.schemas[schemaRef];
            // Set form and add save/submit button
            this.nodeScope.selected_form = this.forms[schemaRef];
        }

        this.nodeScope.selected_data = node;
        console.log("schemaRef: " + schemaRef);

    };


    show_history = (id): ng.IHttpPromise<any> => {

        if (id != this.tree.treeScope.newNodeObjectId) {
            return this.loadHistory(id)
                .success((data: any) => {
                    this.history = data;
                })
                .error((data: any, status: number, headers: ng.IHttpHeadersGetter, config: ng.IRequestConfig) => {
                    this.nodeScope.$root.BootstrapDialog.alert("Loading history failed: " + status);
                });
        }

    };

    /**
     * Select the provided node
     * @param treeNode
     */
    onSelectNode = (treeNode): void => {

        this.set_details(this.tree.data[treeNode.id]);
        this.show_history(treeNode.id);
        this.tree.selectedItem = treeNode;
    };

    /**
     * Initialize the node controller
     * @param schemaTreeController
     */
    onInit = (schemaTreeController): void => {
        console.log("In NodesController.onInit");
        this.tree = schemaTreeController;
        this.tree.treeScope.nodeManager = this;
    };

    // *********************** Initialization *************************

    onAsyncInitTree = (): ng.IPromise<any> => {
        return new this.$q((resolve, reject) => {
            // Initialize all metadata
            this.onInitGroups().then(() => {
                this.onInitForms().then(() => {
                    this.onInitSchemas().then(() => {
                        resolve();
                    });
                });
            });
        });
    };


}

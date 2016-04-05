/// <reference path="../typings/tsd.d.ts" />

import {SchemaTreeController} from "../controllers/schemaTreeController";
import {NodeManager} from "nodeManager";

export interface CustomRootScope extends ng.IRootScopeService {
    /* This is injected during the application initialization */
    BootstrapDialog: any;
}

interface CustomMBEScope extends ng.IScope {
    $root: CustomRootScope;
}
/* This interface is to add typing to the scope */
export interface TreeScope extends CustomMBEScope {
    /* The url of the angular html template that render each node(not including decoration and expander*/
    itemRenderer: string;

    /* The top level of the tree will be children of the node with _id = topNodeId */
    topNodeId: string;

    /* The ObjectId given to a new node, that cannot collide with a another id */
    newNodeObjectId: string;

    /* An array of the allowed child types of the top node, a angular expression */
    topAllowedChildTypes: string[];

    /* The tree controller */
    tree: SchemaTreeController;

    /* The node manager instance  */
    nodeManager: NodeManager;

    /* The position of the +-sign that is used to expand/collapse the tree */
    expanderPosition: string;

    /* The angular-ui-tree settings that are passed on to the tree */
    treeOptions: any;

}


export interface NodesScope extends CustomMBEScope {
    $root: CustomRootScope;
    ngform: any;
    nodeManager: any;
    forms: any;
    selected_schema: any;
    selected_form: any;
    selected_data: any;

}

export interface NodeViewScope extends CustomMBEScope {
    collapsed: boolean;
    remove(): void;
    toggle(): void;
}
export interface Dict {
    [index: string]: any;
}

export class UISettings {
    showAddBars: boolean;
    downAddSiblingAfter: boolean;
    downAddChildAfter: boolean;
    strAllowedChildTypes: string;
}

export class TreeNode {
    id: string;
    name: string;
    title: string;
    type: string;
    children: TreeNode[];
    allowedChildTypes: string[];
    expanded: boolean;
    parentItem: TreeNode;
    ui: UISettings;
    nodeViewScope: NodeViewScope;

    constructor() {
        this.ui = new UISettings();
    }

}

///<reference path="../typings/tsd.d.ts"/>
///<reference path="responses.ts"/>
console.log("In test-main.spec.ts");

import {initNodes} from "../scripts/nodes";
import 'test/responses';
import "bootstrap";

import "angular";
import 'angular-mocks';
import 'angular-schema-form';
import "angular-strap";

import 'angular-schema-form-dynamic-select';

initNodes();

console.log("Initializeed Nodes.");
var expect = chai.expect;

chai.should();

function initNodesDirective($rootScope, $httpBackend, $compile) {

    // Init a local scope
    var scope = $rootScope.$new();
    // Create a template
    var tmpl = angular.element('<nodes></nodes>');

    // Add http mocks

    $httpBackend.whenPOST("node/find", {parent_id: "ObjectId(000000010000010001e64c24)"}).respond(200, get_groups());
    $httpBackend.whenGET("views/nodes/node_forms.js").respond(200, get_node_forms());
    $httpBackend.whenGET("node/get_schemas").respond(200, get_schemas());
    $httpBackend.whenPOST("node/find", {parent_id: null}).respond(200, get_top());
    $httpBackend.whenPOST("node/find", {parent_id: "ObjectId(000000010000010001e64c00)"}).respond(200, get_administration());
    $httpBackend.whenGET("views/nodes/node_renderer.html").respond(200, get_node_renderer());
    $httpBackend.whenPOST("node/lookup", {conditions: {parent_id: "ObjectId(000000010000010001e64c24)"}, collection: "node"}).respond(200, get_groups_lookup());
    $httpBackend.whenPOST("node/history", {_id: "000000010000010001e64c23"}).respond(200, get_administration_history());
    $httpBackend.whenGET("views/nodes.html").respond(200, get_views_nodes());
    $httpBackend.whenGET("views/schematree.html").respond(200, get_views_schematree());

    // Compile the template
    $compile(tmpl)(scope);

    // Do an update, this triggers all items to be loaded
    $rootScope.$apply();

    // Attempt to click one of the selects, doesn't work as Karma seem to not work that way
    //tmpl.children().eq(7).children().eq(0).children().eq(1).click();

    // Tell the mock to respond to requests
    $httpBackend.flush();
    return tmpl;
}

describe("Test the Nodes directive", ():void => {

    beforeEach(module('nodesModule'));
    it('initialize the nodes tree properly against mockup backend', function () {
        inject(function ($compile, $rootScope, $http, $httpBackend, $timeout, $document) {
            var tmpl = initNodesDirective($rootScope, $httpBackend, $compile);
            // Load example data


            // Wait for all getting done before checking.
            $timeout(function () {

                // Find HTML elements in the response, find its scope, and then deep compare with known results.
                var schemaTreeNode = tmpl.children().eq(0).children().eq(0).children().eq(1);
                expect(schemaTreeNode[0].nodeName).to.equal("SCHEMA-TREE", "Schema tree not found.");
                console.log("Schema tree found");
                var schemaTreeRoot = schemaTreeNode.children().eq(0).children().eq(1);
                var administrationLabel = schemaTreeRoot.children().eq(0).children().eq(0).children().eq(1).children().eq(0).children().eq(0).children().eq(3).children().eq(0)
                expect(administrationLabel[0].innerHTML)
                    .to.equal("Administration", "Administration tree node not found.");
                console.log("Administration tree node found")

                // Click the Administration label
                administrationLabel.click();

                $httpBackend.flush();

                // Wait for all actions being done
                $timeout(function () {

                    console.log("Administration tree node found");
                    var asfInputs = tmpl.children().eq(0).children().eq(2).children().eq(1);
                    expect((<HTMLInputElement>asfInputs.children().eq(0).children().eq(0).children().eq(1)[0]).value)
                        .to.equal("Administration", "Administration ASF value not found or wrong.");
                    console.log("Administration ASF value found");
                    var accessTab = asfInputs.children().eq(2).children().eq(0).children().eq(2).children().eq(0).children().eq(1).children().eq(0);
                    var writeRightButton = accessTab.children().eq(0).children().eq(0).children().eq(1).children().eq(0);
                    expect((writeRightButton != undefined))
                        .to.equal(true, "Right drop down doesn't exist.");

                    // Click the Write rights drop down (i.e. invoke the ASDFS callback)
                    writeRightButton.children().eq(0).click();
                    // TODO: Make the click above work. For some reason the <ul> that should appear between the button and the span doesn't during testing. Losing focus, perhaps?

                    $timeout(function () {

                        console.log((<any>tmpl.children().eq(0).children().eq(4).children().eq(1).children().eq(6).children().eq(0).html()));

                        // Check to that history is loaded,
                        expect((<any>tmpl.children().eq(0).children().eq(4).children().eq(1).children().eq(6).children().eq(0).html()))
                            .to.equal("add");
                    });
                });


            });

            // Angular doesn't like async unit tests, tell it to call the checks above
            $timeout.flush()

        });
    });
});


var a = {
    "a9ca8030-6ea4-11e4-9803-0800200c9a66": [
        {
            key: "name",
            type: "text",
            title: "Name",
            readonly: false
        },
        {
            key: "description",
            type: "textarea",
            title: "Description",
            readonly: false
        },
        {
            type: "fieldset",
            title: "",
            items: [
                {
                    type: "tabs",
                    tabs: [
                        {
                            title: "Access",
                            items: [
                                {
                                    key: "canWrite",
                                    title: "Write",
                                    type: "strapselect",
                                    description: "The groups that have write access.",
                                    placeholder: "No groups selected",
                                    startEmpty: false,
                                    options: {
                                        multiple: "true",
                                        httpPost: {
                                            url: "node/lookup",
                                            parameter: {
                                                "conditions": {"parent_id": "ObjectId(000000010000010001e64c24)"},
                                                "collection": "node"
                                            }
                                        }
                                    }
                                },
                                {
                                    key: "canRead",
                                    title: "Read",
                                    type: "strapselect",
                                    description: "The groups that have read access.",
                                    placeholder: "No groups selected",
                                    startEmpty: false,
                                    options: {
                                        multiple: "true",
                                        httpPost: {
                                            url: "node/lookup",
                                            parameter: {
                                                "conditions": {"parent_id": "ObjectId(000000010000010001e64c24)"},
                                                "collection": "node"
                                            }
                                        }
                                    }
                                },
                                {
                                    key: "allowedChildTypes",
                                    title: "Allowed child type",
                                    type: "strapselect",
                                    description: "The child types that can be added to this node.",
                                    placeholder: "No child types selected",
                                    startEmpty: true,
                                    options: {
                                        multiple: "true",
                                        callback: scope.lookupChildNodeTypes
                                    }
                                }
                            ]
                        },
                        {
                            title: "Metadata",
                            items: [
                                {
                                    key: "_id",
                                    title: "Id",
                                    description: "The Id of the node. A <a href=\"http://docs.mongodb.org/manual/reference/object-id/\" target='_blank'>MongoDB objectId</a>.",
                                    type: "text",
                                    readonly: true
                                },
                                {
                                    key: "parent_id",
                                    title: "Parent Id",
                                    description: "The Id of the parent node. A <a href=\"http://docs.mongodb.org/manual/reference/object-id/\" target='_blank'>MongoDB objectId</a>.",
                                    type: "text",
                                    readonly: true
                                },
                                {
                                    key: "schemaId",
                                    type: "text",
                                    title: "Schema Id",
                                    description: "The Id of the schema. A <a href=\"http://http://en.wikipedia.org/wiki/Universally_unique_identifier/\" target='_blank'>UUID(GUID)</a>.",
                                    readonly: true
                                },
                                {
                                    key: "createdWhen",
                                    type: "text",
                                    title: "Created when",
                                    description: "The date and time the node was created.",
                                    readonly: true
                                }
                            ]
                        }

                    ]
                }
            ]
        }
    ],
    "5d3b8e21-adf3-4005-b73c-1fb63a46f399": [
        {
            key: "rights",
            title: "Rights",
            type: "strapselect",
            description: "The rights the group has.",
            placeholder: "No rights selected",
            startEmpty: false,
            options: {
                multiple: "true",
                httpPost: {
                    url: "node/lookup",
                    parameter: {"conditions": {"parent_id": "ObjectId(000000010000010001e64c26)"}, "collection": "node"}
                }
            }
        }

    ],
    "4288fc06-d615-4f1c-ac10-8328153f2c54": [],
    "2fb3b2c9-a29c-4fc0-b29d-6eed738b6dab": [
        {
            title: "Credentials",
            type: "fieldset",
            items: [
                {
                    type: "tabs",
                    tabs: [
                        {
                            title: "Username/Password",
                            items: [
                                {
                                    key: "credentials['usernamePassword']['username']",
                                    title: "Username",
                                    description: "The username.",
                                    type: "text",
                                    readonly: false
                                },
                                {
                                    key: "credentials['usernamePassword']['password']",
                                    type: "password",
                                    title: "Password",
                                    description: "The password.",
                                    readonly: false
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            key: "groups",
            title: "Groups",
            description: "The groups the user belongs to.",
            placeholder: "No groups selected",
            startEmpty: false,
            type: "strapselect",
            options: {
                httpPost: {
                    url: "node/lookup",
                    parameter: {"conditions": {"parent_id": "ObjectId(000000010000010001e64c24)"}, "collection": "node"}
                }
            }
        }
    ],
    "688a51b8-c8e7-465f-8ec9-9ad132245143": [
    ],

    "b8f7b679-bb6c-4ef9-af30-c50962dd8a54": [
        {
            key: "pipPackages",
            type: "array",
            title:"Pip packages",
            description: "The Pip-packages that the process depends on",
            readonly: false,
            items: [
                {
                    key: "pipPackages[]",
                    type: "string",
                    title:"Package name"
                }
                ]
        },
        {
            key: "entryPoint",
            title: "Entry point",
            description: "The entry point of the process",
            items: [
                {
                    key: "entryPoint.moduleName",
                    type: "string",
                    title: "Module name",
                    description: "The module to enter",
                    readonly: false
                },
                {
                    key: "entryPoint.functionName",
                    type: "string",
                    title: "Function name",
                    description: "The name of the function to be called",
                    readonly: false
                }

            ]
        },
        {
            key: "folder",
            type: "text",
            title:"Folder",
            description: "The folder where the process source code is located",
            readonly: false
        },
        {
            key: "canStart",
            title: "Start",
            type: "strapselect",
            description: "The groups that can start the process.",
            placeholder: "No groups selected",
            startEmpty: false,
            options: {
                multiple: "true",
                httpPost: {
                    url: "node/lookup",
                    parameter: {
                        "conditions": {"parent_id": "ObjectId(000000010000010001e64c24)"},
                        "collection": "node"
                    }
                }
            }
        },
        {
            key: "canStop",
            title: "Stop",
            type: "strapselect",
            description: "The groups that can stop the process.",
            placeholder: "No groups selected",
            startEmpty: false,
            options: {
                multiple: "true",
                httpPost: {
                    url: "node/lookup",
                    parameter: {
                        "conditions": {"parent_id": "ObjectId(000000010000010001e64c24)"},
                        "collection": "node"
                    }
                }
            }
        },
        {
            key: "runAs",
            title: "Run as",
            type: "strapselect",
            description: "The user to run as.",
            placeholder: "No users selected",
            startEmpty: false,
            options: {
                multiple: "false",
                httpPost: {
                    url: "node/lookup",
                    parameter: {
                        "conditions": {"parent_id": "ObjectId(000000010000010001e64c25)"},
                        "collection": "node"
                    }
                }
            }
        },

        {
            key: "globals",
            type: "ace",
            aceOptions: {
                mode: 'json'
            },
            validationMessage: {
              'noGlobals': 'Globals contains invalid JSON'
            },
            $validators: {
              noGlobals: function(value) {
                  try {
                      value = JSON.parse(value);
                      return true;
                  }
                  catch (err) {
                      return false;
                  }
              }
            },
            title:"Global variables",
            description: "The global variables that is provided as input to the process"
        },
    ],
    "27b27a7bf-a686-4415-9a35-0ec3d3189d82": [
        {
            key: "repositoriesLocation",
            type: "text",
            title:"Repositories location",
            description: "Where repositories are located",
            readonly: false
        }
    ],
    "daf49a9d-b6e7-43f5-81c7-e5a76a2f1bb9": [
        {
            key: "repositoriesLocation",
            type: "text",
            title:"Repositories location",
            description: "Where repositories are located",
            readonly: false
        },
        {
            key: "numberOfWorkers",
            type: "text",
            title:"Number of workers",
            description: "The number of worker processes the agent will start to handle requests.",
            readonly: false
        }
    ],
    "3fc3bc67-a26d-41c7-bc6e-02e9ad92c8bb": [
        {
            key: "theme",
            type: "text",
            title:"Theme",
            description: "The name of the theme of the admin application",
            readonly: false
        }
    ]
};

return a;


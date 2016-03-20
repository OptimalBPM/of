"""
Created on Mar 6, 2015

@author: Nicklas Boerjesson
@note: The schema tools

"""
from copy import deepcopy
import os
import json


from jsonschema.validators import RefResolver
from jsonschema.exceptions import SchemaError



# strict-rfc3339


from of.broker.lib.schema_mongodb import MongodbValidator
from of.common.logging import EC_NOTIFICATION, SEV_INFO, SEV_DEBUG, write_to_log


class SchemaTools():
    """
        The schema tools class does all the handling, validation and transformation of schemas in the optimal framework.
    """
    # The json_schema_objects keeps the parsed and instantiated schema objects.
    json_schema_objects = None
    # json_schema_folder is the folder of where the json schemas are kept
    json_schema_folders = None

    # The resolve is responsible for resolving URI prefixes referencing other schemas,
    resolver = None
    # The URI-handlers are a dict of callbacks, used when resolving URI:s.
    uri_handlers = None

    # An instance of the mongodb JSON validator.
    mongodb_validator = None


    # noinspection PyDefaultArgument
    def __init__(self, _json_schema_folders=[], _uri_handlers=None):
        """
        Initiate the SchemaTools class

        :param _json_schema_folders: A list of folders where schema files are stored
        :param : _uri_handlers: A dict of uri_handlers, resolves a URI prefix to a actual schema.

        """

        if not _json_schema_folders:
            _json_schema_folders = []

        if not _uri_handlers:
            self.uri_handlers = {}
        else:
            self.uri_handlers = _uri_handlers

        self.resolver = RefResolver(base_uri="",
                                handlers=self.uri_handlers, referrer=None, cache_remote=True)

        self.mongodb_validator = MongodbValidator(resolver= self.resolver)

        self.json_schema_objects = {}

        # Load application specific schemas
        for _curr_folder in _json_schema_folders:
            self.load_schemas_from_directory(os.path.abspath(_curr_folder))

        # Resolve all the schemas
        for curr_schemaRef, curr_schema in self.json_schema_objects.items():
            self.json_schema_objects[curr_schemaRef] = self.resolveSchema(curr_schema)

        write_to_log("Schemas loaded and resolved: " +
                     str.join(", ",  ["\"" +_curr_schema["title"] + "\""  for _curr_schema in self.json_schema_objects.values()])
                     , _category=EC_NOTIFICATION, _severity=SEV_DEBUG)


    @staticmethod
    def check_schema_fields(_curr_schema_obj, _curr_file):
        """ Check so all mandatory fields are in the schema
        :param _curr_schema_obj: Schema to check
        :param _curr_file: File name use in error message

        """

        def raise_field_error(_collection):
            raise Exception("MongoBackend.load_schemas_from_directory: The \"" + _collection + "\"" +
                            " field is not in the schema-\"" + _curr_file + "\"")

        if "version" not in _curr_schema_obj:
            raise_field_error("version")
        if "namespace" not in _curr_schema_obj:
            raise_field_error("namespace")

    def load_schema_from_file(self, _file_name):
        """
        Loads a specified schema from a file, checks it and stores it in the schema cache.

        :param _file_name: The name of the schema file

        """
        try:
            _curr_file = open(_file_name, "r")
        except Exception as e:
            raise Exception("load_schema_from_file: Error loading \"" + _file_name +
                            "\": " + str(e))
        try:
            _json_schema_obj = json.load(_curr_file)

        except Exception as e:
            raise Exception("load_schema_from_file: Error parsing \"" + _file_name +
                            "\"" + str(e))

        _curr_file.close()

        try:
            self.check_schema_fields(_json_schema_obj, _file_name)
        except SchemaError as scherr:
            raise Exception("load_schema_from_file: SchemaError in " + _file_name + " at path:" + str(
                scherr.path) + "\nMessage:\n" + str(scherr.message))
        except Exception as e:
            raise Exception("load_schema_from_file: schema validation in " + _file_name + ", error :" + str(e))
        _schemaRef = _json_schema_obj["namespace"] + "://" + os.path.split(_file_name)[1]
        self.json_schema_objects[_schemaRef] = _json_schema_obj

    def load_schemas_from_directory(self, _schema_folder):
        """
        Load and validate all schemas in a folder, add to json_schema_objects

        :param _schema_folder: Where to look

        """
        _only_files = [f for f in os.listdir(_schema_folder) if
                       os.path.isfile(os.path.join(_schema_folder, f)) and f[-5:].lower() == ".json"]
        for _file in _only_files:
            self.load_schema_from_file(os.path.join(_schema_folder, _file))

    def apply(self, _data, _schema_ref=None):
        """
        Validate the JSON in _data against a JSON schema.

        :param _data: The JSON data to validate
        :param _schema_ref: If set, validate against the specified schema, and not the one in the data.
        :return: the schema object that was validated against.

        """
        if _schema_ref is not None:
            _json_schema_obj = self.json_schema_objects[_schema_ref]
        else:
            if "schemaRef" in _data:
                try:
                    _json_schema_obj = self.json_schema_objects[_data["schemaRef"]]
                except KeyError as e:
                    raise Exception("SchemaTools.apply, invalid schemaRef: " + _data["schemaRef"])
            else:
                raise Exception("SchemaTools.apply, data must have a schemaRef attribute")

        self.mongodb_validator.apply(_data, _json_schema_obj)
        return _data, _json_schema_obj

    def validate(self, _data, _schema_ref=None):
        """
        Validate the JSON in _data against a JSON schema.

        :param _data: The JSON data to validate
        :param _schema_ref: If set, validate against the specified schema, and not the one in the data.
        :return: the schema object that was validated against.

        """
        if _schema_ref is not None:
            _json_schema_obj = self.json_schema_objects[_schema_ref]
        else:
            _json_schema_obj = self.json_schema_objects[_data["schemaRef"]]

        self.mongodb_validator.validate(_data, _json_schema_obj)
        return _data, _json_schema_obj


    def non_base_type(self, _type):
        if _type not in ["array", "string", "integer", "object"]:
            return [_type]
        else:
            return []

    def resolveSchema(self, _schema):
        """
        Recursively resolve all I{$ref} JSON references in a JSON Schema.
        :param _schema: A L{dict} with a JSON Schema.
        :return: The resolved JSON Schema, a L{dict}.
        """
        _result = deepcopy(_schema)



        def local_resolve(_obj, _ref_history):
            """
            Recurse the JSON-tree and see where there are unresolved remote references.
            :param _obj: The node to resolve
            :param _ref_history: The previously resolved remote references, for cyclical check
            """

            if isinstance(_obj, list):
                # Loop any list
                for item in _obj:
                    local_resolve(item, _ref_history)
                return

            if isinstance(_obj, dict):

                if "$ref" in _obj:
                    _curr_ref = _obj["$ref"]

                    # Do not resolve local references
                    if _curr_ref[0] == "#":
                        return

                    # Check for cyclical references
                    if _curr_ref in _ref_history:
                        raise Exception("Error, cyclical remote reference: " + str(_curr_ref) + ":  Formers " + str(_ref_history))

                    with self.resolver.resolving(_curr_ref) as resolved:
                        # Resolve the resolved schema
                        local_resolve(resolved, _ref_history + [_curr_ref])
                        # Remove the reference
                        del _obj["$ref"]
                        # Add the resolved fragment to the schema
                        _obj.update(resolved)


                else:
                    # Loop all properties
                    for _key, _value in _obj.items():
                        if isinstance(_value, dict) and "type" in _value:
                            local_resolve(_value, _ref_history)

                        else:
                            local_resolve(_value, _ref_history)
        try:
            local_resolve(_result, [])
        except Exception as e:
            raise Exception("schemaTools.resolveSchema: Error resolving schema:" + str(e) + "Schema " + json.dumps(_schema, indent=4))

        # Make top allOf into properties
        if "allOf" in _result:
            _new_properties = {}
            for _curr_properties in _result["allOf"]:
                _new_properties.update(_curr_properties["properties"])

            _result["properties"] = _new_properties
            del _result["allOf"]

        _result["$schema"] = "http://json-schema.org/draft-04/schema#"

        try:
            self.mongodb_validator.check_schema(_result)
        except Exception as e:
            raise Exception("schemaTools.resolveSchema: error validating resolved schema:" + str(e) + "Schema " + json.dumps(_result, indent=4))

        return _result
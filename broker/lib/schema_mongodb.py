"""
This module serves as an extension for the JSON schema library.
It is made in a similar extension-vein as seep (https://github.com/Julian/Seep)

Created on Mar 18, 2016

@author: Nicklas Boerjesson

"""

from bson.objectid import ObjectId
# noinspection PyProtectedMember
from jsonschema import _utils
from jsonschema.exceptions import ValidationError
import jsonschema.validators


def of_object_id(value):
    """
    Converts a string value to a MongoDB object value.

    Instead of generating a new value, which is the default behaviour of ObjectId(), it returns None if provided None,
    :param value: A string value. Can be empty.
    :return: None or a corresponding ObjectId-instance.

    """
    if value is not None:
        return ObjectId(value)
    else:
        return None


class MongodbValidator():
    """
    The MongodbValidator class is a plug-in for JSON schema that converts objectId-formatted strings into
    actual ObjectId instances if the objectId property is present in the schema,

    """
    """The main validator class, a descendent of the jsonschema validator"""
    validator_class = None
    """The object setter is called to change the value"""
    object_setter = None

    def __init__(self, resolver=None):
        """Initializes MongodbValidator by initializing  and setting the resolver"""
        self.init_classes()
        self.resolver = resolver

    def init_classes(self):
        """Initialize all dynamically defined classes"""
        self.object_setter = jsonschema.validators.create(
            meta_schema={}, validators={"properties": self._set_object_ids},
        )

        # noinspection PyAttributeOutsideInit
        self.base_validator = jsonschema.validators.Draft4Validator
        self.validator_class = jsonschema.validators.extend(
            self.base_validator, {
                "properties": self._properties_with_objectids,
                "type": self._type_except_objectid,
            }
        )

    def apply(self, data, mongodb_schema):
        """
        Apply the MBE schema to the data.

        :param data: A mongo schema
        :param mongodb_schema: mongodb_schema: a mongodb_schema (JSON Schema with Seep properties)
        :return: the affected data

        """
        self.validator_class(schema=mongodb_schema, resolver=self.resolver).validate(data)
        return data

    def validate(self, data, mongodb_schema):
        """
        Validate the data with the MBE schema.

        :param data: A mongo schema
        :param mongodb_schema: mongodb_schema: a mongodb_schema (JSON Schema with Seep properties)
        :return: the affected data

        """
        self.base_validator(schema=mongodb_schema, resolver=self.resolver).validate(data)


    def check_schema(self, schema):
        """
        Check a schema, raises ValidationError if validation failed and RefResolutionError if it can't find a
        referenced file.

        :param schema: The schema to check.

        """
        # TODO: Check, should this really be like this?
        jsonschema.validators.Draft4Validator({}, resolver=self.resolver).check_schema(schema)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _type_except_objectid(self, validator, types, instance, schema):
        """
        Had to override the internal type checker to avoid it stopping at ObjectId.
        There is no other way for ObjectIds to be set in JSON data except for here.
        """
        types = _utils.ensure_list(types)

        if not any(validator.is_type(instance, _type) for _type in types):
            if not isinstance(instance, ObjectId):
                yield ValidationError(_utils.types_msg(instance, types))

    def _properties_with_objectids(self, validator, properties, instance, schema):
        """
        Responsible for looping properties.
        """
        for error in self.base_validator.VALIDATORS["properties"](
                validator, properties, instance, schema
        ):
            yield error
        subschemas = [(instance, schema)]
        while subschemas:
            subinstance, subschema = subschemas.pop()
            self.object_setter(subschema).validate(subinstance)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def _set_object_ids(self, validator, properties, instance, schema):
        """
        Translates objectIds in the current scope.
        """
        for _property, subschema in properties.items():
            if _property in instance:
                if "objectId" in subschema:
                    # print("setting property - " + _property)
                    curr_instance = instance[_property]
                    if curr_instance is not None and curr_instance != "":
                        instance[_property] = of_object_id(curr_instance)

                elif "type" in subschema and subschema["type"] == "array":
                    if "objectId" in subschema["items"]:
                        # print("found array - " + _property)
                        for curr_idx in range(0, len(instance[_property])):
                            curr_item = instance[_property][curr_idx]
                            if type(curr_item) is str and curr_item is not None and curr_item != "":
                                # print("setting array item - " + curr_item)
                                instance[_property][curr_idx] = of_object_id(curr_item)



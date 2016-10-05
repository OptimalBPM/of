
def set_dict_if_set(_dest, _attribute, _value, _default_value):
    """Set a dict attribute if value is set"""
    if _value is not None:
        _dest[_attribute] = _value
    elif _default_value is not None:
        _dest[_attribute] = _default_value

def set_property_if_in_dict(_dest_obj, _property_name, _dict, _default_value = None, _error_msg = None):
    """Set an object property is the same attribute exists in the dict. If _error is set, raise exception if missing."""
    if _property_name in _dict:
        _dest_obj.__dict__[_property_name] = _dict[_property_name]
    elif _default_value is not None:
        _dest_obj.__dict__[_property_name] = _default_value
    elif _error_msg is not None:
        raise Exception(_error_msg + " Attribute missing: " + _property_name)
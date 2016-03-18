"""
    The permission module handles permissions for nodes.
"""


from of.broker.lib.schema_mongodb import mbe_object_id

__author__ = 'nibo'


def filter_by_group(_nodes, _permission, _user, _database_access, _error_prefix_if_not_allowed=None,
                    _use_object_id=False):
    """This function filters a list of nodes based on what groups a user belong to and its right

    :param _nodes: A list of node
    :param _permission: The permission to check. For example "canRead" or "canWrite".
    :param _user: The user to check
    :param  _database_access: A database access instance.
    :param _error_prefix_if_not_allowed: If set, the supplied error message is raised. Normally used when testing for\
        write access.
    :param _use_object_id: If true, the node has ObjectId instances and not strings.
    :return: A list of nodes any of the users' groups have the permission defined in _permission for

    """
    _result = []
    _groups = _user["groups"]
    # Loop nodes
    for _curr_row in _nodes:
        _has_permission = False
        # Check if any of the group the user belongs to..
        for _curr_group in _groups:
            # ..is among those the node has listed having the requested permission
            if _use_object_id:
                if mbe_object_id(_curr_group) in _curr_row[_permission]:
                    _has_permission = True
                    break
            elif _curr_group in _curr_row[_permission]:
                _has_permission = True
                break
        if _has_permission:
            _result.append(_curr_row)
        elif _error_prefix_if_not_allowed:
            # Raise an error if a user lacks the _permission for.
            _error = _error_prefix_if_not_allowed + ":" + _user["name"] + " doesn't have the " + _permission + \
                " for the " + _curr_row["name"] + "(" + str(_curr_row["_id"]) + ")-node."

            _database_access.logging.log_security("permission",
                                                  _error,
                                                  _user["_id"], str(_curr_row["_id"]))
            raise PermissionError(_error)

    return _result

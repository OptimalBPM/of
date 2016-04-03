"""
Created on Mar 6, 2015

The groups module contains functionality for checking group level rights.

@author: Nicklas Boerjesson


"""

from decorator import getfullargspec

__author__ = 'nibo'

_groups = None


def init_groups(_database_access):
    """
    Initiate the global groups object, load all groups from the provided database

    :param _database_access: A database access object
    :return: The global group object

    """

    global _groups
    _groups = Groups(_database_access)


def has_right(_right, _user):
    """

    Global convenience function, see Groups.has_right

    :param _right:

    """
    global _groups
    if _groups:
        _groups.has_right(_right, _user)


def user_in_any_of_groups(_user, _groups):
    """
    Check if a user belongs to any of the groups
    :param _user: A user instance
    :param _groups: A list of groups to check
    :return: True if in any of the groups
    """
    _user_groups = _user["groups"]
    for _group in _groups:
        if _group in _user_groups:
            return True
    return False

def aop_has_right(_rights):
    """

    A decorator to supply the has_right functionality. Takes a function pointer.
    It is necessary to make it able to get the data in runtime.
    TODO: That is quite ugly.

    :param _rights_function: A a list with rights or a pointer to a function that returns the right to check for
    :return: returns a decorator function.


    """

    def wrapper(func):
        def wrapped_f(*args, **kwargs):
            # Get a list of the names of the non-keyword arguments
            if "_user" in kwargs:
                _user = kwargs["_user"]
            else:

                # TODO: Add support for keyword arguments, can be convenient in cases where code is called from python
                _argument_specifications = getfullargspec(func)
                try:
                    # Try and find _session_id
                    user_idx = _argument_specifications.args.index("_user")
                except:
                    raise Exception("Has right aspect for \"" + func.__name__ + "\": No _user parameter in function, internal error.")

                if user_idx > len(args) - 1:
                    raise Exception(
                        "Has right aspect for \"" + func.__name__ + "\": The _user parameter isn't supplied.")


                _user = args[user_idx]

            if isinstance(_rights, list):
                has_right(_rights, _user)
            elif callable(_rights):
                has_right(_rights(), _user)




            return func(*args, **kwargs)

        return wrapped_f

    return wrapper


class RightCheckError(Exception):
    """Exception class for Rights errors"""
    pass


class Groups():
    """
    The Groups class is the central location for group management in MBE and holds the group cache.

    """
    _groups = {}

    def __init__(self, _database_access):
        """
        The class initiates by loading all groups from the database.

        :param _database_access: A database access object instance


        """
        self._groups = {}
        self._database_access = _database_access
        self.reload_all()

    def reload_all(self):
        """
        Reload all groups from database
        """
        self._groups.clear()
        _cursor = self._database_access.find(
            {"collection": "node", "conditions": {"schemaRef": "of://group.json"}})
        for _curr_group in _cursor:
            self._groups[_curr_group["_id"]] = _curr_group

    def has_right(self, _right, _user):
        """
        Check if a certain user, through group membership, holds a certain right.
        Raises a RightCheckError if npt

        :param _right: The right in question
        :param _user: A user object

        """

        if type(_right) is list:
            for _curr_group in _user["groups"]:
                for _curr_right in _right:
                    if _curr_right in self._groups[_curr_group]["rights"]:
                        return _curr_group
        else:
            for _curr_group in _user["groups"]:
                if _right in self._groups[_curr_group]["rights"]:
                    return _curr_group

        # TODO: Add nice-looking alert for all errors in UI
        _error = "The user \"" + _user["name"] + "\" doesn't have the " + str(_right) + " right."
        self._database_access.logging.log_security("right",
                                                   _error,
                                                   _user["_id"], None)

        raise RightCheckError("The user \"" + _user["name"] + "\" doesn't have the " + str(_right) + " right.")

    def __iter__(self):
        """Access function for making the class iterable."""
        return self._groups

    def __getitem__(self, item):
        """Access function for making the class iterable."""
        return self._groups[item]

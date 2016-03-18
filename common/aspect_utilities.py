"""
Created on Nov 6, 2012

@author: Nicklas Börjesson
@node: Utilities to help creating aspects in AOP.
"""
from inspect import getfullargspec


def alter_function_parameter_and_call(function_object, args, kwargs, name, value, err_if_not_set=None):
    """Changes or sets the value of an argument, if present, and calls the function.

    :param function_object: An instance of the called function
    :param args: A list of arguments
    :param kwargs: A dict of keyword arguments
    :param name: Name of the parameter that should be set
    :param value: Value to set that parameter to
    :param err_if_not_set: If is set, raise as error if the argument isn't present.
    :return: The return value of the called function

    """
    argspec = getfullargspec(function_object)

    if name in argspec.args:
        arg_idx = argspec.args.index(name)
        largs = list(args)
        largs.pop(arg_idx)
        largs.insert(arg_idx, value)
        new_args = tuple(largs)
        return function_object(*new_args, **kwargs)
    elif err_if_not_set is not None:
        raise Exception(err_if_not_set)

    return function_object(args, kwargs)




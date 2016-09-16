"""
CherryPy-specific login and session management

Created on Jun 17, 2016

@author: Nicklas Boerjesson
"""



import cherrypy
from http.cookies import SimpleCookie
from decorator import decorator

from of.common.security.authentication import check_session, login, AuthenticationError, logout

def _check_session_aspect(func, *args, **kwargs):
    """CherryPy-specific check_session aspect code, checks if there is a valid cookie"""

    try:
        # Try and find _session_id
        _session_id = cherrypy.request.cookie["session_id"].value
    except:
        raise AuthenticationError("Authentication aspect for \"" + func.__name__ + "\": No session_id cookie")

    # Set user variable and execute function.
    kwargs["_user"] = check_session(_session_id)
    kwargs["_session_id"] = _session_id
    return func(*args, **kwargs)


def aop_check_session(f):
    """
    CherryPy-specific session checking decorator.

    :param f: the function

    """
    return decorator(_check_session_aspect, f)


def _login_json_aspect(func, *args, **kwargs):
    """
    CherryPy-specific session login aspect.

    """
    _message = cherrypy.request.json

    if _message is not None and isinstance(_message, dict):
        # TODO: Add a hook for custom login

        if "credentials" not in _message:
            raise AuthenticationError("_login_json_aspect for \"" + func.__name__ + "\": No credentials in request")

        # Already logged in, log out old session
        if "session_id" in cherrypy.request.cookie and cherrypy.request.cookie["session_id"].value != "":
            print("_login_json_aspect: Logging out old session: " + cherrypy.request.cookie["session_id"].value)
            logout(cherrypy.request.cookie["session_id"].value)


        _session_id, _user = login(_message["credentials"])
        _session_cookie = cherrypy.response.cookie
        _session_cookie["session_id"] = _session_id
        _session_cookie["session_id"]["secure"] = True
        _session_cookie["session_id"]["path"] = "/"

        kwargs["_message"] = _message
        kwargs["_session_id"] = _session_id
        kwargs["_user"] = _user
        return func(*args, **kwargs)
    else:
        raise AuthenticationError("Authentication aspect for \"" + func.__name__ + "\": No message structure")


def aop_login_json(f):
    """
    CherryPy-specific session login decorator.

    """
    return decorator(_login_json_aspect, f)

def cherrypy_logout(_session_id):
    """
    CherryPy-specific logout

    :param _session_id: The session id of the session that is to be logged out
    :return:
    """
    logout(_session_id)

    _new_cookie = SimpleCookie()
    _new_cookie["session_id"] = ""
    _new_cookie["session_id"]['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    return _new_cookie
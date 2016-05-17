"""
    A test server in CherryPy that demonstrates how to use MBE from CherryPy.
"""
from of.broker.cherrypy_api.authentication import aop_login_json, aop_check_session, cherrypy_logout
from of.broker.lib.auth_backend import MongoDBAuthBackend
from of.common.security.authentication import init_authentication
from of.schemas.validation import of_uri_handler

__author__ = 'Nicklas Boerjesson'

import sys
import os

# Add MBE path
script_dir = os.path.dirname(__file__)


import cherrypy

from of.broker.cherrypy_api.node import CherryPyNode
from of.broker.testing.init import init_database


class Server(object):
    """
        The server object.
    """
    node = None
    database_access = None

    def __init__(self):
        self._reset_database()
        init_authentication(MongoDBAuthBackend(self._database_access))
        self.node = CherryPyNode(self._database_access)

    def _reset_database(self):
        self._database_access = init_database("test_skeleton_of",
                                              _data_files=[os.path.join(script_dir, "../../testing/data_struct.json")],
                                              _json_schema_folders=[os.path.join(script_dir, "../../../schemas")],
                                              _uri_handlers={"of": of_uri_handler})

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_login_json
    def login(self, **kwargs):
        return {}


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def logout(self, **kwargs):
        cherrypy.response.cookie = cherrypy_logout(kwargs["_session_id"])
        return {}



    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json')
    def reset_database(self, **kwargs):
        self._reset_database()
        return {"result": "OK"}


def start_server():
    """
        Initialize and start the server.
    """
    if hasattr(cherrypy.engine, 'subscribe'):  # CherryPy >= 3.1
        pass
    else:
        raise Exception("This application requires CherryPy >= 3.1 or higher.")
        # cherrypy.engine.on_stop_engine_list.append(_save_data)

    # Some global configuration

    cherrypy.config.update({"server.ssl_certificate": os.path.join(os.path.dirname(__file__), "../cert.pem"),
                            "server.ssl_private_key": os.path.join(os.path.dirname(__file__), "../privkey.pem")})

    # cherrypy.config.update(config=os.path.join(script_dir, "config.ini"))
    app = cherrypy.tree.mount(Server(), '/',
                              {'/':
                                  {
                                      "tools.staticdir.root": os.path.abspath(
                                          os.path.join(os.path.dirname(__file__), "static")),
                                      "tools.decode.on": True,
                                      "tools.trailing_slash.on": True,
                                      "tools.staticdir.on": True,
                                      "tools.staticdir.index": "index.html",
                                      "tools.staticdir.dir": ""
                                  }
                              })

    if hasattr(cherrypy.engine, "signal_handler"):
        cherrypy.engine.signal_handler.subscribe()
    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    start_server()
else:
    cherrypy.config.update({"server.ssl_certificate": os.path.join(os.path.dirname(__file__), "../cert.pem"),
                            "server.ssl_private_key": os.path.join(os.path.dirname(__file__), "../privkey.pem"),
                            "tools.staticdir.root": os.path.abspath(script_dir)})
    app = cherrypy.tree.mount(Server())
    print("Running")

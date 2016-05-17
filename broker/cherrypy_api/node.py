"""
    The CherryPy-module provides a web server plugin for CherryPy.
"""



import cherrypy

from of.broker.cherrypy_api.authentication import aop_check_session
from of.broker.lib.node import Node


__author__ = 'Nicklas Borjesson'




class CherryPyNode(object):
    """
    The CherryPyNode class is a plugin for CherryPy to expose the MBE node-functionality.
    Each function maps to counterparts in the node class.

    """
    # A local instance of the MBE Node API
    _node = None

    def __init__(self, _database_access):
        self._node = Node(_database_access)




    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def save(self, **kwargs):
        return self._node.save(cherrypy.request.json, kwargs["_user"])

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def find(self, **kwargs):
        return self._node.find(cherrypy.request.json, kwargs["_user"])

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def lookup(self, **kwargs):
        return self._node.lookup(cherrypy.request.json, kwargs["_user"])

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def remove(self, **kwargs):
        return self._node.remove(cherrypy.request.json, kwargs["_user"])

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def load_node(self, **kwargs):
        return self._node.load_node(cherrypy.request.json, kwargs["_user"])

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def load_children(self, **kwargs):
        return self._node.load_children(cherrypy.request.json, kwargs["_user"])

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def history(self, **kwargs):
        return self._node.history(cherrypy.request.json, kwargs["_user"])



    @cherrypy.expose
    @cherrypy.tools.json_out(content_type='application/json')
    @aop_check_session
    def get_schemas(self, **kwargs):
        return self._node.get_schemas(kwargs["_user"])
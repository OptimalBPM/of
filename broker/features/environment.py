"""
    Initialization for MBE tests.
"""
import os
import queue
import time

from bson.objectid import ObjectId
import cherrypy

from mbe.node import Node

from of.broker.lib.messaging.handler import BrokerWebSocketHandler
from of.common.queue.monitor import Monitor
import of.common.messaging.websocket
from of.common.testing.init_env import init_env
from of.broker.lib.messaging.websocket import MockupWebSocket

__author__ = 'Nicklas Borjesson'

# Test users uuids
object_id_user_root = "000000010000010001e64c30"
object_id_user_test = "000000010000010001e64c31"


object_id_right_admin_nodes = "000000010000010001e64d01"

script_dir = os.path.dirname(__file__)

def before_all(context):

    os.environ["OPTIMAL_FW_CFG"] = os.path.join(script_dir, "steps", "config.json")
    init_env(context)


def init_broker_cycles(context, feature):
    print("\nRunning Broker startup and shutdown scenarios\n=========================================================\n")


def before_feature(context, feature):
    """
    Initialisation for all features.

    :param context:
    :param feature:
    :return:

    """

    if feature.name in ["Broker startup and shutdown scenarios"]:
        init_broker_cycles(context, feature)

def after_feature(context, feature):
    pass

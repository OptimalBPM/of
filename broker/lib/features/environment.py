"""
    Initialization for MBE tests.
"""
import queue
import time

from bson.objectid import ObjectId
import cherrypy
from multiprocessing import Queue

from mbe.node import Node

from of.broker.lib.messaging.handler import BrokerWebSocketHandler
from of.common.messaging.constants import GOING_AWAY
from of.common.queue.monitor import Monitor
import of.common.messaging.websocket

from of.broker.lib.messaging.websocket import MockupWebSocket
from optimalbpm.testing.init_env import init_env

__author__ = 'nibo'

# Test users uuids
object_id_user_root = "000000010000010001e64c30"
object_id_user_test = "000000010000010001e64c31"

object_id_right_admin_nodes = "000000010000010001e64d01"


def before_all(context):
    init_env(context)


def init_low_level(context, feature):

    # Fake session registration
    _peers = {
        "sender":
            {
                "address": "source_peer",
                "user": context.user,
                "queue": Queue()
            },
        "receiver":
            {
                "address": "destination_peer",
                "user": context.user,
                "queue": Queue()
            }
    }

    context.monitor = Monitor(
        _handler=BrokerWebSocketHandler(_process_id=context.peer_process_id, _peers=_peers,
                                        _schema_tools=context.db_access.schema_tools, _address="broker",
                                        _database_access=context.db_access), _logging_function=cherrypy.log.error)

    of.common.messaging.websocket.monitor = context.monitor

    # Register mockup WebSockets
    context.sender = MockupWebSocket(session_id="sender", context=context)
    context.receiver = MockupWebSocket(session_id="receiver", context=context)

    def _stop_broker():
        pass



def before_feature(context, feature):
    """
    Initialisation for all features.

    :param context:
    :param feature:
    :return:

    """
    if feature.name in ["Process Management", "Process definition management API", "Message broker"]:
        init_low_level(context, feature)



def after_feature(context, feature):
    print("After feature " + feature.name + ", stopping broker.")
    context.sender.close(code=GOING_AWAY, reason="Close sender")
    context.receiver.close(code=GOING_AWAY, reason="Close receiver")
    if feature.name in ["Process Management", "Process definition management API", "Message broker"]:
        context.monitor.stop()
        time.sleep(.1)

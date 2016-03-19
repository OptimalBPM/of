"""
    Initialization for MBE tests.
"""
import os

from of.broker.testing.init_env import init_env

__author__ = 'Nicklas Borjesson'

# Test users uuids
id_user_root = "000000010000010001e64c30"
id_user_test = "000000010000010001e64c31"


id_right_admin_nodes = "000000010000010001e64d01"

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

"""
The constants module holds constants for all the schemas defined in Optimal Framework

Created on Jan 22, 2016

@author: Nicklas Boerjesson
"""
__author__ = 'Nicklas Borjesson'

"""
Constants for _ids in the Optimal Framework database
TODO: These are only constant for this instance of the database (perhaps XOR-them together with environment Id?)
"""
# Hard coded locations of always present nodes

id_administration = "000000010000010001e64c23"
id_groups = "000000010000010001e64c24"
id_users = "000000010000010001e64c25"
id_rights = "000000010000010001e64c26"
id_right_admin_everything = "000000010000010001e64c27"
id_group_administrators = "000000010000010001e64c28"
id_group_users = "000000010000010001e64c29"

id_peers = "000000010000010002e64d03"
id_templates = "000000010000010002e64d04"
# Shorthand for a valid 24-digit zero object id
zero_object_id = "000000000000000000000000"

"""
Schema definition constants

Note: A new schema must be both given schemaRef and be added to category
"""



# Schema category map. Used by handlers.
schema_categories = {
    # Message category - Messages between peers - forwarded by the broker to the destination if not itself
    "ref://of.message.message": "message",
    "ref://of.message.error": "message",
    # Node category - Nodes in the node tree, cannot be messages
    "ref://of.node.broker": "node",
    "ref://of.node.admin": "node",
    "ref://of.node.peer": "node",
    # Log category - Log messages - written to the log collection by the broker
    "ref://of.log.progression": "log",
    "ref://of.log.process_state": "log",
    "ref://of.event": "log",
    # Process category - Process instance data - written to the process collection by the broker
    "ref://of.process.system": "process"
    # Control category - Control messages for runtime entities
    # None for broker yet.
}

# These messages should are intercepted and stored by the broker
intercept_schema_ids = []

peer_type__schema_id = {

    "broker": "ref://of.node.broker",
    "admin": "ref://of.node.admin",
    "peer": "ref://of.node.peer"
}


def peer_type_to_schema_id(_peer_type):
    if _peer_type in peer_type__schema_id:
        return peer_type__schema_id[_peer_type]
    else:
        raise Exception("Invalid peer type:" + _peer_type)

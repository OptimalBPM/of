"""
The constants module holds constants for all the schemas defined in Optimal Framework
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

id_users = "000000010000010001e64c25"
id_peers = "000000010000010002e64d03"

# Shorthand for a valid 24-digit zero object id
zero_object_id = "000000000000000000000000"

"""
Schema definition constants

Note: A new schema must be both given schemaRef and be added to category
"""



# Schema category map. Used by handlers.
schema_categories = {
    # Message category - Messages between peers - forwarded by the broker to the destination if not itself
    "of://message.json": "message",
    "of://message_error.json": "message",
    # Node category - Nodes in the node tree, cannot be messages
    "of://node_broker.json": "node",
    "of://node_admin.json": "node",
    "of://node_peer.json": "node",
    # Log category - Log messages - written to the log collection by the broker
    "of://log_progression.json": "log",
    "of://log_process_state.json": "log",
    "of://event.json": "log",
    # Process category - Process instance data - written to the process collection by the broker
    "of://process_system.json": "process"
    # Control category - Control messages for runtime entities
    # None for broker yet.
}

# These messages should are intercepted and stored by the broker
intercept_schema_ids = []

peer_type__schema_id = {

    "broker": "of://node_broker.json",
    "admin": "of://node_admin.json",
    "peer": "of://node_peer.json"
}


def peer_type_to_schema_id(_peer_type):
    if _peer_type in peer_type__schema_id:
        return peer_type__schema_id[_peer_type]
    else:
        raise Exception("Invalid peer type:" + _peer_type)

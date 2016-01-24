"""
The constants module holds constants for all the schemas defined in Optimal BPM
"""
__author__ = 'Nicklas Borjesson'

"""
Constants for _ids in the Optimal BPM database
TODO: These are only constant for this instance of the database (perhaps XOR-them together with environment Id?)
"""

# The users node
id_users = "000000010000010001e64c25"

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
    # Log category - Log messages - written to the log collection by the broker
    "of://log_progression.json": "log",
    "of://log_process_state.json": "log",
    # Process category - Process instance data - written to the process collection by the broker
    "of://process_system.json": "process"
    # Control category - Control messages for runtime entities
    # None for broker yet.
}

# These messages should are intercepted and stored by the broker
intercept_schema_ids = []

peer_type__schema_id = {

    "broker": "of://node_broker.json",
    "admin": "of://node_admin.json"
}


def peer_type_to_schema_id(_peer_type):
    if _peer_type in peer_type__schema_id:
        return peer_type__schema_id[_peer_type]
    else:
        raise Exception("Invalid peer type:" + _peer_type)

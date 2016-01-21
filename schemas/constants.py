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

Note: A new schema must be both given schemaId and be added to category
"""

# Fragment category - Fragments used by other schemas


# Message category - Messages between peers - forwarded by the broker to the destination if not itself
schema_id_message = "a31426b4-8b42-4d98-b7b8-05e8bc8f6869"
schema_id_message_error = "656d3644-3c05-4cd6-ba58-2a11953a43bf"

# Node category - Nodes in the node tree, cannot be messages
schema_id_node_broker = "27b27a7bf-a686-4415-9a35-0ec3d3189d82"
schema_id_node_admin = "3fc3bc67-a26d-41c7-bc6e-02e9ad92c8bb"

# Log category - Log messages - written to the log collection by the broker
schema_id_log_progression = "88925f4c-5e2f-4e12-8606-586021ac5e53"
schema_id_log_process_state = "edcfd97b-a292-4d9e-8436-0466900b1991"

# Process category - Process instance data - written to the process collection by the broker
schema_id_system_process = "9523e937-1efc-438d-b54c-fb9bb9843a87"

# Control category - Control messages for runtime entities

# Schema category dict. Used by handlers.
schema_categories = {

    schema_id_node_broker: "node",

    schema_id_log_progression: "log",

    schema_id_message: "message",
    schema_id_message_error: "message",
    schema_id_log_process_state: "log",
    schema_id_system_process: "process"
}

# These messages should are intercepted and stored by the broker
intercept_schema_ids = []

peer_type__schema_id = {

    "broker": schema_id_node_broker,
    "admin": schema_id_node_admin
}


def peer_type_to_schema_id(_peer_type):
    if _peer_type in peer_type__schema_id:
        return peer_type__schema_id[_peer_type]
    else:
        raise Exception("Invalid peer type:" + _peer_type)

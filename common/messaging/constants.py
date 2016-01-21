"""
This process holds constants for the web socket error-codes
"""
__author__ = 'Nicklas Börjesson'

# Web socket error codes: http://tools.ietf.org/html/rfc6455#section-7.4.1

#: 1000 indicates a normal closure, meaning that the purpose for which the connection was established has been fulfilled.
WS_NORMAL_CLOSURE = 1000
#: 1001 indicates that an endpoint is "going away", such as a server going down or a browser having navigated away from a page.
GOING_AWAY = 1001
#: 1002 indicates that an endpoint is terminating the connection due to a protocol error.
PROTOCOL_ERROR = 1002
#: 1003 indicates that an endpoint is terminating the connection because it has received a type of data it cannot accept (e.g., an endpoint that understands only text data MAY send this if it receives a binary message).
UNACCEPTABLE_DATA = 1003
#: 1008 indicates that an endpoint is terminating the connection because it has received a message that violates its policy.  This is a generic status code that can be returned when there is no other more suitable status code (e.g., 1003 or 1009) or if there is a need to hide specific details about the policy.
POLICY_VALIDATION = 1008
#: 1009 indicates that an endpoint is terminating the connection because it has received a message that is too big for it to process.
TOO_BIG = 1009
#: 1010 indicates that an endpoint (client) is terminating the connection because it has expected the server to negotiate one or more extension, but the server didn't return them in the response message of the WebSocket handshake.  The list of extensions that are needed SHOULD appear in the /reason/ part of the Close frame. Note that this status code is not used by the server, because it can fail the WebSocket handshake instead.
BAD_SERVER_RESPONSE = 1010
#: 1011 indicates that a server is terminating the connection because it encountered an unexpected condition that prevented it from fulfilling the request.
UNEXPECTED_CONDITION = 1011
#: 1015 is a reserved value and MUST NOT be set as a status code in a Close control frame by an endpoint. It is designated for use in applications expecting a status code to indicate that the connection was closed due to a failure to perform a TLS handshake (e.g., the server certificate can't be verified).
TLS_FAILURE = 1015

#: 4011 is a private value that indicates that a socket is closed because the broker is restarting, this to tell the agents to wait a short while and re-register and reconnect
BROKER_RESTARTING = 4011
#: 4012 is a private value that indicates that a socket is closed because the broker is shutting down, this to tell agents to wait a longer and periodically reconnect
BROKER_SHUTTING_DOWN = 4012



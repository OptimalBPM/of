# CherryPy API

This is the CherryPy interface definitions for the APIs presented by the broker.
These provide the implementations of the Broker API.

`authentication.py` contains a general decorator for session and authentication in the interfaces implemented by the broker. 
It is used by all plugins that extend the backend.

`node.py` implements the node API, the entity tree of the optimal framework.

`broker.py` implement the brokers own little API, two functions deserve mentioning:
* register/unregister, handles peer registration
* socket - called when a peer wants to upgrade its connection to a websocket connection
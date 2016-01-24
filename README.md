# Optimal Framework

THIS SOFTWARE IS STILL UNRELEASED. IT IS UNDER HEAVY DEVELOPMENT AND NOT RECOMMENDED FOR PRODUCTION, ONLY RESEARCH

The Optimal Framework is a modern, and running, multi-user system.
What differs it from many other frameworks is that it comes with a runnable server as-is.
The goal is to create something that not only provides the framework for solving, but actually has already implemented the most common problems in systems programming.
A typical implementation would someone moving desktop client-based system to web based clients.
As the client side of Optimal Framework is Typescript, and the server side is Python, there are no restriction on what can be done.
The backend is a MongoDB database, which covers a surprising range of usage scenarios, but there is no problems with additionally using a RDBMS backend.

# Features

* Messaging (messaging between different components in a multi-user system is not only a chat function)
* Settings and resource management - There is a 
* Users and groups
* Permissions
* Rights
* Authentication and session management
* Logging, auditing
* Locking
* Installers
* User interface 
* Dependency-aware plug-in framework

More features, commercial and non-commercial, ranging from  to actual commercial extensive systems like Optimal BPM and will be available through the plug-in network.

# Support

Outside github issues, there will be commercial support o

# History

It was first built as a base for the [Optimal BPM process management system](http://www.optimalbpm.se). 
However, as development moved on, it became clear that:
a. as that system needed to have a plug-in structure, and 
b. that one would have in some way treat parts of Optimal BPM as plug-ins, 
..there was no reason to not write Optimal BPM itself as a plug-in.

And as answer to the question "a plug-in to what?", the Optimal Framework was born.

It is not primarily thought of as something to build a web site, but rather for creating applicatoin systems, like a  



# Source

The structure of the Optimal Framework source:
/broker - The Optimal Framework broker
/common - Libraries used by the broker and those interacting with it
/schema - The JSON schemas, and functionality to resolve the of:// scheme

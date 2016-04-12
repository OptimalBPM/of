# Optimal Framework

***THIS SOFTWARE IS STILL UNRELEASED. IT IS UNDER HEAVY DEVELOPMENT AND NOT RECOMMENDED FOR PRODUCTION, ONLY RESEARCH!***

The Optimal Framework is a modern, and running, multi-user system.
What differs it from many other frameworks is that it comes with a runnable server as-is.
The goal is to create something that not only provides the framework for solving, but actually has already implemented the most common problems in systems programming.
A typical implementation would someone moving a traditional desktop client-based system to web based clients or apps.
As the client side of Optimal Framework is Typescript, and the server side is Python, there are no restriction on what can be done.
The backend is a MongoDB database, which covers a surprising range of usage scenarios, but there are no problems with additionally using an RDBMS backend.
It is like a CMS for systems development. One could call it a Function Management System. And FMS.

# Features

* Messaging (messaging between different components in a multi-user system is not merely a chat function)
* Settings and resource management - Central tree structure
* JSON Schema based integrity control
* Centralized schema and input form management using [JSON Schema](http://json-schema.org/) and [Angular Schema Form](https://github.com/json-schema-form/angular-schema-form)
* Users and groups
* Permissions
* Rights
* Authentication and session management
* Logging, auditing (categories, severities, local, remote)
* Locking
* Installers
* Administrative User interface 
* Dependency-aware plug-in framework

More features, commercial and non-commercial, ranging from  to actual extensive commercial systems like Optimal BPM and will be available through a plug-in ecosystem.

# How does it work?

The most important concepts of the Optimal Framework are the broker, plugins and schemas.

## Broker
In the conceptual middle of the system is the broker. 

It is responsible for most cross-cutting concerns like messaging, security logging and keeping persistent data.

## Schemas
JSON Schema is used to define [all data structures](https://github.com/OptimalBPM/of/tree/master/schemas) in the system. 

It is not only used to validate and define the data in the MongoDB database backend, but also used in front end interfaces like the [administrative interface](https://github.com/OptimalBPM/of-admin), and to [handle messages](https://github.com/OptimalBPM/of/blob/master/common/messaging/handler.py#L115).

All data in OF are required to have a valid schema reference that it adheres to, and are dictionaries that is turned back and forth into JSON when transmitted.


## Plugins
All functionality is added via plugins. 

In OF, a plugin is almost able to change everything about how the system operates.
Developing plugins is simple and intuitive, they are simple GIT repositories that have a [definitions file](https://github.com/OptimalBPM/optimalbpm/blob/master/definitions.json) that describes them.

Plugins add:
* functionality to the backend by defining [CherryPy-exposed classes](https://github.com/OptimalBPM/optimalbpm/blob/master/broker/cherrypy/process.py) that are mounted by the built-in web server and dynamically
 incorporated into the backend via [hooks](https://github.com/OptimalBPM/optimalbpm/blob/master/hooks_broker.py). Hooks are run at [different points of the broker initialisation](https://github.com/OptimalBPM/of/blob/master/broker/broker.py#L185), which allow for extensive control. Implementing a hook is simply to define a function in a module.
* namespaces and definitions by simply placing the schemas in the [/schema folder](https://github.com/OptimalBPM/optimalbpm/tree/master/schemas), they are automatically imported into the system, to be used in the messaging and data validation.
* functionality to the admin frontend by [listing the angular directives, controllers, menu items and routes](https://github.com/OptimalBPM/optimalbpm/tree/master/admin-ui) that one wished to include. 



# Support

Outside Github issues, there will be commercial support available.

# History

It was first built as a base for the [Optimal BPM process management system](http://www.optimalbpm.se). 
However, as development moved on, it became clear that:

a. as that system needed to have a plug-in structure, and 

b. that one would have in some way treat parts of Optimal BPM as plug-ins,
 
..there was no reason to not write Optimal BPM itself as a plug-in.

And as an answer to the question "a plug-in to what?", the Optimal Framework was born.

It is not primarily thought of as something to build a web site, but rather for creating sector-specific computing systems.



# Source

The structure of the Optimal Framework source:
* /broker - The Optimal Framework broker
* /broker/ui - The ui:s of the broker
* /common - Libraries used by the broker and those interacting with it
* /schemas - The JSON schemas, and functionality to resolve the of:// scheme

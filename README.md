# Optimal Framework

***THIS SOFTWARE IS STILL UNRELEASED. IT IS IN ITS FINAL PHASES OF DEVELOPMENT AND NOT YET RECOMMENDED FOR PRODUCTION, ONLY RESEARCH!***

The Optimal Framework is a modern, and running, multi-user system, it differs from many other frameworks because it comes with a runnable server as-is.
The goal is to create something that not only provides the framework for solving, but actually has already implemented the most common problems in systems programming.

As the client side of Optimal Framework is Typescript, and the server side is Python, there are no restrictions on what can be done.
The backend is a MongoDB database, which covers a surprising range of usage scenarios, but there are no problems with additionally using an RDBMS backend.

A typical implementation would someone moving a traditional desktop client-based system to web based clients or apps.
It is like a CMS for systems development. One could call it a Function Management System. An FMS.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
# Table of Contents

- [Features](#features)
- [Help](#help)
  - [Support](#support)
- [Documentation](#documentation)
  - [Concepts](#concepts)
  - [Examples](#examples)
  - [API](#api)
  - [Installing](#installing)
  - [Developers](#developers)
  - [Source](#source)
- [History](#history)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


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
* Administrative User interface 
* Dependency-aware plug-in framework

Upcoming:

* Locking
* Installers

More features, commercial and non-commercial, ranging from  to actual extensive commercial systems like Optimal BPM and will be available through a plug-in ecosystem.

# Help

If you have questions or problems, please create an issue.

If you just wan't to reach out and discuss, please check out the gitter room.

## Support

Outside the Github community, there will be commercial grade support packages available.

# Documentation

## Concepts
There are three major concepts in the Optimal Framework: [broker, nodes, plugins and schemas](https://github.com/OptimalBPM/of/wiki/Concepts).

## Examples

There will be a repository with an example plugin shortly, meanwhile, look at [Optimal BPM](https://github.com/OptimalBPM/optimalbpm).

## API

Currently, there is no real API documentation, however the code is pretty well commented. 

## Installing

Installation is currently a little bit cumbersome, will become scripted later.    
But this is how it is done on unix flavors.   
If it is on windows, do not use sudo and change the commands appropriately.

System requirements:

* install mongodb
* install python3.4 or newer
* install python3-pip


Install the framework:

* ```sudo pip3 install of``` (of is the Optimal Framework pypi package)


The configuration folder optimalbpm of the framework is by default located in the home folder of the user running the system.

Install the :

* ```cd ~``` go to your home directory
* ```git clone https://github.com/OptimalBPM/of-config.git optimalframework```
* ```cd optimalframework```
* ```cd plugins```
* ```git clone https://github.com/OptimalBPM/of-admin admin``` - install the admin interface plugin
* ```cd admin/ui```
* ```npm install```   (add --production if you want to install without dev stuff, may need sudo)
* ```node_modules/jspm/jspm.js install```  (installs the web dependencies, may need sudo)
* ```cd ../../```
* ```sh initdb.sh```  - initialize the database (or python3 initdb.py)
* ```sh broker.sh```  - run the system (or python3 broker.py)

The admin interface should now be reachable on:
https://127.0.0.1:8080/admin/#/process

Which is sort of the point. You now have a running system that already have all these features from the get go.  
Now just add your own functionality in a [plugin](https://github.com/OptimalBPM/of/wiki/Concepts#plugins) that you simply add next to the admin interface plugin.
If there is a folder there, and a definitions.json-file, it is a plugin and will be loaded by the framework.


## Developers
For those wanting to contribute to OF itself, feel free to make pull requests.  
However, please try and not include too much in each, and work against the development branch unless it is a brief and non-breaking bug fix.

OF strictly follows semantic versioning.

## Source structure

The structure of the Optimal Framework source:

* /broker - The Optimal Framework broker
* /broker/ui - The ui of the broker, by default just a holding page, easily replaced by plugins. 
* /common - Libraries used by the broker and those interacting with it
* /schemas - The JSON schemas, and functionality to resolve the of:// scheme



# History

It was first built as a base for the [Optimal BPM process management system](http://www.optimalbpm.se). 
However, as development moved on, it became clear that:

a. as that system needed to have a plug-in structure, and 

b. that one would have in some way treat parts of Optimal BPM as plug-ins,
 
..there was no reason to not write Optimal BPM itself as a plug-in.

And as an answer to the question "a plug-in to what?", the Optimal Framework was born.

It is not primarily thought of as something to build a web site, but rather for creating sector-specific computing systems.





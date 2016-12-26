# Optimal Framework

The Optimal Framework is the equivalent of a Content Management System for systems development.
One could call it a Function Management System. An FMS.

The fastest route to building a system is to start out halfway there.

It is a modern, plugin-based, multi-user system, and it differs from many other frameworks because it is a runnable server as-is.
The goal is to create something that not only provides the framework for solving, but actually has already implemented the most common problems in systems programming.
Adding functionality to the Python backend is just to add classes and properties to the system, it is a highly intuitive approach.

There is also an optional [administrative UI-plugin](https://github.com/OptimalBPM/of-admin), written in Typescript and Angular and easily extensible.
If one want to add an application UI, any client-side framework that can work against the backend will work.

Behind the backend resides a MongoDB database, which covers a surprising range of usage scenarios, but there are no problems with additionally using an RDBMS backend.

A typical usage scenario would be someone moving a traditional desktop client-based system to web based clients or apps.


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
  - [Linuxes:](#linuxes)
    - [Debian/Ubuntu:](#debianubuntu)
    - [OSX(using brew):](#osxusing-brew)
  - [Windows:](#windows)
    - [MongoDB](#mongodb)
    - [Python](#python)
  - [Installing the framework/system/application](#installing-the-frameworksystemapplication)
- [Running](#running)
- [Developers](#developers)
- [Source structure](#source-structure)
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
* Installer

Upcoming:

* Locking

More features, commercial and non-commercial, ranging from  to actual extensive commercial systems like Optimal BPM and will be available through a plug-in ecosystem.

# Help

If you have questions or problems, please create an issue.

If you just wan't to reach out and discuss, please check out the gitter room.

## Support

Outside the Github community, there will be commercial grade support packages available.

# Documentation

## Concepts
There are four major concepts in the Optimal Framework: [broker, nodes, plugins and schemas](https://github.com/OptimalBPM/of/wiki/Concepts).

## Examples

There will be a repository with an example plugin shortly, meanwhile, look at [Optimal BPM](https://github.com/OptimalBPM/optimalbpm).

## API

The general API is documented in the [wiki](https://github.com/OptimalBPM/of/wiki/API).

Also, try and visually browse the github source tree, there are README:s for most packages.

# Installing

Installation is done using an installation program, optimalsetup. 
This is useful, because it can download an instruction of what to install.
So applications using the framework will only need to provide a JSON-file to make an installation.

These are the prerequisites:

* MongoDB
* Python3.4 or newer.

``To install them...``

## Linuxes:

These versions comes with Python 3.4 or newer: 
* Debian Jessie (v8.0)
* Ubuntu Trusty (v14.04)
* OpenSuSE 13.2
* Fedora 22
* RHEL/Centos(manual install)

### Debian/Ubuntu:
```sudo apt-get install mongodb python3 python3-pip```

_Pip is for some reason not included in some distributions_
### OSX(using brew):
```brew install mongodb python3```


## Windows:
### MongoDB
Download and install https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/

### Python
Download and install Python https://www.python.org/downloads/windows/
_Remember to click "add to path", or you will have to write the full path to the Python executable_


## Installing the framework/system/application

Download the installer:
https://github.com/OptimalBPM/of/raw/master/tools/setup/optimalsetup.py

The installer uses setup files to define what to install, it also installs the pip of-package and its dependencies.
It should be run with administrative/sudo priviliges, because when run, the installer makes sure that its dependencies are installed.
The dependencies are distlib, dulwich and on windows win32api. On some debian distributions python3-tk needs to be installed, and if so it does.

But to just install the basic installation of the Optimal Framework, run the setup with the `--default_of_install` option:
`python optimalsetup.py --default_of_install' simply installs a bare installation of the framework in the "of" folder of the users' home folder.

# Running

In the install folder, the scripts for starting the initializing the database and the broker is located, .sh- and .bat-files for the respective platforms.
* initdb - initiates the database
* broker - starts the broker.

So first, run the initdb script, and then the broker script. The admin interface should now be reachable on:
https://127.0.0.1:8080/admin/#/process

Login using with the root user and then use "root" as the password. You are now logged in.

Which is sort of the point. You now have a running system that already have all these features from the get go.  

Now just add your own functionality in a [plugin](https://github.com/OptimalBPM/of/wiki/Concepts#plugins) that you simply add next to the admin interface plugin.
If there is a folder there, and a definitions.json-file, it is a plugin and will be loaded by the framework.


# Developers
For those wanting to contribute to OF itself, feel free to make pull requests.  
However, please try and not include too much in each, and work against the development branch unless it is a brief and non-breaking bug fix.

OF strictly follows semantic versioning.

# Source structure

The structure of the Optimal Framework source:

* /broker - The Optimal Framework broker
* /common - Libraries used by the broker and those interacting with it
* /schemas - The JSON schemas, and functionality to resolve the of:// scheme
* /forms - JSF forms used by any user interfaces.


# History

It was first built as a base for the [Optimal BPM process management system](http://www.optimalbpm.se). 
However, as development moved on, it became clear that:

a. as that system needed to have a plug-in structure, and 

b. that one would have in some way treat parts of Optimal BPM as plug-ins,
 
..there was no reason to not write Optimal BPM itself as a plug-in.

And as an answer to the question "a plug-in to what?", the Optimal Framework was born.

It is not primarily thought of as something to build a web site, but rather for creating sector-specific computing systems.





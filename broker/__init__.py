"""
This package holds the Optimal Framework broker, its libraries and UI
"""
__author__ = 'Nicklas Borjesson'

import runpy
def run_broker():
    runpy.run_module(mod_name="of.broker.broker", run_name="__main__")

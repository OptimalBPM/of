"""
This package contains all broker-level BDD tests for the Optimal BPM broker script
"""
__author__ = 'Nicklas Borjesson'
import runpy
def run_broker_testing():
    runpy.run_module(mod_name="of.broker.broker", run_name="__main__")


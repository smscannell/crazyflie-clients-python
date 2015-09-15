# Connect to Crazyflie
# Start logging baro and accZ
# Send via UDP to simulink model
# Receive commands from simulink

from __future__ import print_function

from threading import Thread
import signal
import time
import sys

try:
    import zmq
except ImportError as e:
    raise Exception("ZMQ library probably not installed ({})".format(e))


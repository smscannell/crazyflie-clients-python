# Connect to Crazyflie
# Start logging baro and accZ
# Send via UDP to simulink model
# Receive commands from simulink
# C:\python34\python C:\users\sam\documents\github\crazyflie-clients-python\bin\cfzmq

from __future__ import print_function

from threading import Thread
import signal
import time
import sys
from array import array
import numpy as np
import pylab as pl


try:
    import zmq
except ImportError as e:
    raise Exception("ZMQ library probably not installed ({})".format(e))

class _LogThread(Thread):
    def __init__(self, socket, *args):
        super(_LogThread, self).__init__(*args)
        self._socket = socket

    def run(self):
        while True:
            log = self._socket.recv_json()
            if log["event"] == "data":
                print(log)
                X.append(log["timestamp"])
                Y.append(log["variables"]["baro.asl"])
            if log["event"] == "created":
                print("Created block {}".format(log["name"]))
            if log["event"] == "started":
                print("Started block {}".format(log["name"]))
            if log["event"] == "stopped":
                print("Stopped block {}".format(log["name"]))
            if log["event"] == "deleted":
                print("Deleted block {}".format(log["name"]))


SRV_ADDR = "tcp://127.0.0.1"
CF_URI = "radio://0/22/1M"
X = array('d')
Y = array('d')

context = zmq.Context()
client_conn = context.socket(zmq.REQ)
client_conn.connect("{}:2000".format(SRV_ADDR))

log_conn = context.socket(zmq.SUB)
log_conn.connect("{}:2001".format(SRV_ADDR))
log_conn.setsockopt_string(zmq.SUBSCRIBE, u"")

log_thread = _LogThread(log_conn)
log_thread.start()

print("Scanning for Crazyflies ...", end=' ')
scan_cmd = {
    "version": 1,
    "cmd": "scan"
}
client_conn.send_json(scan_cmd)
resp = client_conn.recv_json()
print("done!")
for i in resp["interfaces"]:
    print("\t{} - {}".format(i["uri"], i["info"]))

connect_cmd = {
    "version": 1,
    "cmd": "connect",
    "uri": "{}".format(CF_URI)
}
print("Connecting to {} ...".format(connect_cmd["uri"]), end=' ')
client_conn.send_json(connect_cmd)
resp = client_conn.recv_json()
if resp["status"] != 0:
    print("fail! {}".format(resp["msg"]))
    sys.exit(1)
print("done!")

# Do logging
print("Loggable variables")
for group in resp["log"]:
    print("\t{}".format(group))
    for name in resp["log"][group]:
        print("\t  {} ({})".format(name,
                                   resp["log"][group][name]["type"]))

log_cmd = {
    "version": 1,
    "cmd": "log",
    "action": "create",
    "name": "Test log block",
    "period": 1000,
    "variables": [
        "baro.temp",
        "baro.asl",
        "acc.z"
    ]
}
print("Creating logging {} ...".format(log_cmd["name"]), end = ' ')
client_conn.send_json(log_cmd)
resp = client_conn.recv_json()
if resp["status"] ==0:
    print("done!")
else:
    print("fail! {}".format(resp["msg"]))

log_cmd = {
    "version": 1,
    "cmd": "log",
    "action": "start",
    "name": "Test log block"
}
print("Starting logging {} ...".format(log_cmd["name"]), end=' ')
client_conn.send_json(log_cmd)
resp = client_conn.recv_json()
if resp["status"] == 0:
    print("done!")
else:
    print("fail!")

time.sleep(20)

log_cmd = {
    "version": 1,
    "cmd": "log",
    "action": "stop",
    "name": "Test log block",
}
print("Stopping logging {} ...".format(log_cmd["name"]), end=' ')
client_conn.send_json(log_cmd)
resp = client_conn.recv_json()
if resp["status"] == 0:
    print("done!")
else:
    print("fail!")

time.sleep(5)


connect_cmd = {
    "version": 1,
    "cmd": "disconnect",
    "uri": "{}".format(CF_URI)
}
print("Disconnecting from {} ...".format(connect_cmd["uri"]), end=' ')
client_conn.send_json(connect_cmd)
resp = client_conn.recv_json()
if resp["status"] != 0:
    print("fail! {}".format(resp["msg"]))
    sys.exit(1)
print("done!")

pl.plot(X,Y)
pl.show()

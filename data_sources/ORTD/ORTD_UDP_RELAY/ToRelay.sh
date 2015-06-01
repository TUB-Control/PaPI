#!/bin/sh

# Commandline Args:

# 1: Port FROM ORTD
# 2: Port TO ORTD

# 3: Port TO Recv
# 4: Port FROM Recv


node Relay.js 20000 20001 21000 21001


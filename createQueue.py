#!/usr/bin/python -u
#
# Retrieves all user queues
#

##### Main program 
import pysqs

queues=[]

sqs=pysqs.init()
queues=sqs.listqueues()

print queues
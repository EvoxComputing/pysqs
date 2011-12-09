#!/usr/bin/python -u
#
# Retrieves all user queues
#

##### Main program 

import lib.pysqs,sys

queues=[]

try:
	sqs=lib.pysqs.sqs()
	sqs.loadconfig("/root/dev/pysqs/config/aws.conf")
	sqs.testnet()
	sqs.loadregions()
	sqs.listqueues()

except:
	print "Error::listQueues::ExceptionOccured"
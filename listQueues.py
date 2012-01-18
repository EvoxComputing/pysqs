#!/usr/bin/python -u
#
# Retrieves all user queues
#

##### Main program 

import lib.pysqs,sys

try:
	sqs=lib.pysqs.SQS()
	## Loads AWS credentials from config file
	sqs.loadconfig("config/aws.conf")
	
	print
	print "Available Regions"
	print "-------------------"
	for queuename in lib.pysqs.AWS_REGIONS.iterkeys():
		print queuename, lib.pysqs.AWS_REGIONS[queuename]
	print
	
	# Region name
	region="eu-west-1.queue" 
	# Only POST methos supported currently
	method="POST" 
	#1 is SSL ON and 0 is SSL OFF
	ssl_flag=1 
	# Queue name
	prefix=""
	# Make the AWS call
	sqs.list_queues(region,method,ssl_flag,prefix)
	#List queue names
	for qname in sqs.queues:
		print "Queue found: %s" % (qname)
	
	print "Result: %s " % (sqs.get_responsemsg())
	
	

except:
	print "Error::listQueue::ExceptionOccured"
	print "Exception::", sys.exc_info()[0]
	print "Exception::", sys.exc_info()[1]

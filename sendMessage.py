#!/usr/bin/python -u
#
# Sends a message to a queue
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
	ssl_flag=0 
	# Message
	message="My First Message"
	# Queue name
	queue_name="myqueue1"
	
	# Make the AWS call
	sqs.send_msg(region,method,ssl_flag,message,queue_name)
	
	print "Result: %s " % (sqs.get_responsemsg())
	print "Message ID: %s " % (sqs.get_msgid())
	

except:
	print "Error::listQueue::ExceptionOccured"
	print "Exception::", sys.exc_info()[0]
	print "Exception::", sys.exc_info()[1]

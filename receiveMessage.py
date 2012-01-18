#!/usr/bin/python -u
#
# Receives a message from a queue
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
	message="My Second Message"
	# Queue name
	queue_name="myqueue1"
	#Max Number of msgs
	max=2
	#Visibility timeout
	vis_timeout=""
	# Attributes to return
	attributes=[]
	all_attributes=["All"]
	
	# Make the AWS call
	sqs.receive_msg(region,method,ssl_flag,queue_name,max,vis_timeout,all_attributes)
	
	print "Result: %s " % (sqs.get_responsemsg())
	
	aws_msg=lib.pysqs.AWSmessage()
	
	aws_msg = sqs.get_msgs()
	
	print "Received: %d messages" % (len(aws_msg.aws_messages))
	
	for message in aws_msg.aws_messages:
		print "Message body: %s " % (message.body)
		
	## delete the retrieved messages
	
	#for message in aws_msg.aws_messages:
	#	sqs.delete_msg(region,method,ssl_flag,queue_name,message.receipthandle) 
	
	
	

except:
	print "Error::listQueue::ExceptionOccured"
	print "Exception::", sys.exc_info()[0]
	print "Exception::", sys.exc_info()[1]

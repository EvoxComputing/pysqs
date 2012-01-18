#!/usr/bin/python -u
#
# Create SQS queue
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
	queue_name="myqueue1"
	# Make the AWS call
	sqs.create_queue(region,method,ssl_flag,queue_name)
	print "Result: %s " % (sqs.get_responsemsg())
	
	## Queue Attributes
	attributes=["ApproximateNumberOfMessages",
				"MessageRetentionPeriod"]
	all_attributes=["All"]
	
	sqs.get_queueattr(region,method,ssl_flag,queue_name,all_attributes)
	print "Result: %s " % (sqs.get_responsemsg())
	# Print attributes requested
	for att_name in sqs.get_queue_attributes().iterkeys():
		print att_name, sqs.queue_attributes[att_name]
	
	# Get queue URL
	sqs.queueurl(region,method,ssl_flag,queue_name)
	print "Queue URL: %s " % (sqs.get_queue_url())
	
	# Delete the queue. Note: takes up to 60 sec to actually delete the queue
	#sqs.delete_queue(region,method,ssl_flag,queue_name)
	#print "Result: %s " % (sqs.get_responsemsg())
	
	
				
except:
	print "Error::createQueue::ExceptionOccured"
	print "Exception::", sys.exc_info()[0]
	print "Exception::", sys.exc_info()[1]
		
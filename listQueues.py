#!/usr/bin/python -u
#
# Retrieves all user queues
#

##### Main program 

import lib.pysqs,sys,time

try:
	sqs=lib.pysqs.sqs()
	## Loads AWS credentials from config file
	sqs.loadconfig("/home/dlam/working/devel/pysqs/config/aws.conf")
	## Tests connectivity to amazon
	#sqs.testnet()
	## Tests connectivity to all regions
	#sqs.testregions()
	
	
	sqs.list_queues("sqs.eu-west-1","GET",1,"")

except:
	print "Error::listQueues::ExceptionOccured"
	print "Exception::", sys.exc_info()[0]
	print "Exception::", sys.exc_info()[1]

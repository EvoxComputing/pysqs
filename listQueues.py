#!/usr/bin/python -u
#
# Retrieves all user queues
#

##### Main program 

import lib.pysqs,sys,time
from timeit import Timer

def sendmessage(sqs,times):
		for i in range(1,times):
			sqs.send_msg("eu-west-1.queue","POST",1,"message","test4")	
			
			
t = Timer('sendmessage(sqs,times)', "from __main__ import sendmessage,sqs,times")
try:
	sqs=lib.pysqs.sqs()
	## Loads AWS credentials from config file
	sqs.loadconfig("config/aws.conf")
	## Tests connectivity to amazon
	#sqs.testnet()
	## Tests connectivity to all regions
	#sqs.testregions()
	
	#sqs.create_queue("eu-west-1.queue","POST",1,"test1")
	sqs.list_queues("eu-west-1.queue","POST",1,"")
	for qname in sqs.queues:
		print "Queue found: %s" % (qname)
	
	### Insert 100 messages in queue
	times=1

	print 'Sent %d messages in %.3f seconds' % (times,t.timeit(1))
	

except:
	print "Error::listQueues::ExceptionOccured"
	print "Exception::", sys.exc_info()[0]
	print "Exception::", sys.exc_info()[1]

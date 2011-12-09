# Amazon Simple Queue Service
# API Reference (API Version 2011-10-01)
# pysqs.py


import os,sys, httplib

class sqs:
	
	def __init__(self,action="null",queueNamePrefix="null",expires="",aWSAccessKeyId="",signature="",config=""):
	
		self.action=action
		self.queueNamePrefix=queueNamePrefix
		self.expires=expires
		self.aWSAccessKeyId=aWSAccessKeyId
		self.signature=signature
		self.config=config
		  
		self.version="2011-10-01"
		self.signatureMethod="HmacSHA256"
		self.signatureVersion="2"
		self.awsregions={'us-east-1': 'sqs.us-east-1.amazonaws.com'}

	def init(self):
		## Load the AWS config file
		loadconfig()

		## Test internet connectivity
		testnet()
		
		## Test HMAC sign
		signrequest()
		
		## Load available AWS regions
		loadregions()

	def testnet(self):
		## Test Internet connection via HTTP
		uri="www.python.org"
		try:
			conn = httplib.HTTPConnection(uri)
			conn.request("GET", "/index.html")
			r1 = conn.getresponse()
			if r1.status == 200:
				print "Internet Connection [OK]"
			
			else:
				print "Error::testnet:No valid response from python.org %s" % (r1.status)
				raise Exception('Something wrong with python.org?')
				
					
		except:
			print "Error::testnet:Connecting to python", sys.exc_info()[0]
			raise Exception()
	
	def loadregions(self):
		## Test connection to AWS regions
		for region,regionuri in self.awsregions.iteritems():
			try:
				conn = httplib.HTTPConnection(regionuri)
				conn.request("GET", "/index.html")
				r1 = conn.getresponse()
				if r1.status == 200:
					print "Region %s [OK]" % (region)
				
				
				else:
					print "Error::loadregions:No valid response [%s] from region %s" % (r1.reason,region)
					
			except:
				print "Error::loadregions:Connecting to AWS", sys.exc_info()[0]
				raise Exception()
		
	def listqueues(self):		
		## Retrieve queus
		print "Retrieving queues"
			
	def loadconfig(self,config):
		## Set config path
		self.config=config
		## Load AWS credentials from config file
		
		splitchar="="
		count=0
		mapfile=self.config
		### Try to load the mapfile
		try:
			if mapfile == "":
				print "Error::loadconfig:No config file set"
				raise Exception('No valid mappings found')
				
			print "Trying to load file map : %s" %(mapfile)
			infile = open(mapfile,"r")
						
			for line in infile:
				entry=line.strip()
				n=entry.split(splitchar)
				
				if len(n) != 2:
					print "Error::loadconfig:No valid mappings found"
					raise Exception('No valid mappings found')
			
			
		except:
			print "Error::loadconfig:Reading file", sys.exc_info()[0]
			raise Exception()

	
	def createlistquery(self):
		## Test connection to AWS regions
		print "createlistquery"
	
		
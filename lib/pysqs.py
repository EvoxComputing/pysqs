# Amazon Simple Queue Service
# API Reference (API Version 2011-10-01)
# pysqs.py


import os
import sys
import httplib2
import httplib
import urlparse
import urllib
import time
import base64
import hmac
import hashlib

class SQSError(Exception): pass

## Defs
AWS_REGIONS = {
    'sqs.us-east-1': 'US East (Northern Virginia)',
    'sqs.us-west-2': 'US West (Oregon)',
    'sqs.us-west-1': 'US West (Northern California)', 
    'sqs.eu-west-1': 'EU (Ireland)', 
    'sqs.ap-northeast-1': 'Asia Pacific (Singapore)',
	'sqs.ap-northeast-1': 'Asia Pacific (Tokyo)'
}

WS_URI = "amazonaws.com"

SQS_ACTIONS = ('ListQueues', 'DeleteQueue', 'AddPermission','ChangeMessageVisibility')

## Helper functions

def generate_timestamp():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def _utf8_str(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')
    else:
        return str(s)


class SignatureMethod(object):

    @property
    def name(self):
        raise NotImplementedError

    def build_signature_base_string(self, request):
        sig = '\n'.join((
            request.get_normalized_http_method(),
            request.get_normalized_http_host(),
            request.get_normalized_http_path(),
            request.get_normalized_parameters()
        ))
        return sig

    def build_signature(self, request, aws_secret):
        raise NotImplementedError
		


class SignatureMethod_HMAC_SHA256(SignatureMethod):
    name = 'HmacSHA256'
    version = '2'
	
    def build_signature(self, request, aws_secret):
		print "Doing SHA256 ..."
		base = self.build_signature_base_string(request)
		print "\n\nBASE %s" % (base)
		hashed = hmac.new(aws_secret, base, hashlib.sha256)
		
		return base64.b64encode(hashed.digest())
		
##AWS request
# 1. Sort the parameters of the query in natural byte order
# 2. URL encode the query
# 3. Calculate HMAC of the query string 
# 4. Convert to base64

class awsrequest:
	def __init__(self,region,method,url,parms):
		
		self.method=method
		self.parms=parms
		self.region=region
		self.url=url
		
			
	def set_parameter(self, name, value):
		self.parms[name] = value

	def get_parameter(self, parameter):
		try:
			return self.parms[parameter]
		except KeyError:
			raise SQSError('Parameter not found: %s' % parameter)

		
	def get_normalized_parameters(self):
		return urllib.urlencode([(_utf8_str(k), _utf8_str(v)) for (k, v) in sorted(self.parms.iteritems()) if k != 'Signature'])	
		
		
	def get_normalized_http_method(self):
		return self.method.upper()
	
	def get_normalized_http_path(self):
		parts = urlparse.urlparse(self.url)
		if not parts[2]:
			return '/'
		else:
			return parts[2]

	def to_postdata(self):
		return urllib.urlencode([(_utf8_str(k), _utf8_str(v)) for (k, v) in self.parms.iteritems()])	
        
	def get_normalized_http_host(self):
		parts = urlparse.urlparse(self.url)
		return parts[1].lower()

	def sign_request(self, signature_method, aws_key, aws_secret):
		
		self.set_parameter('AWSAccessKeyId', aws_key)
		self.set_parameter('SignatureVersion', signature_method.version)
		self.set_parameter('SignatureMethod', signature_method.name)
		self.set_parameter('Timestamp', generate_timestamp())
		self.set_parameter('Signature', signature_method.build_signature(self, aws_secret))

class sqs:
	
	def __init__(self,action="null",queueNamePrefix="null",expires="",aWSAccessKeyId="",aWSSecretKey="",signature="",config=""):
	
		self.action=action
		self.queueNamePrefix=queueNamePrefix
		self.expires=expires
		self.aWSAccessKeyId=aWSAccessKeyId
		self.aWSSecretKey=aWSSecretKey
		self.signature=signature
		self.config=config
		  
		self.uri=""  
		self.host=""
		self.scheme=""
		self.version="2011-10-01"
		self.signatureMethod="HmacSHA256"
		self.signatureVersion="2"
		self.http = httplib2.Http()
		
		try:
			import hashlib # 2.5+
			self.signature_method = SignatureMethod_HMAC_SHA256()
		except ImportError:
			self.signature_method = SignatureMethod_HMAC_SHA1()
		
		
		
	def testnet(self):
		## Test Internet connection via HTTP
		uri="aws.amazon.com"
		try:
			conn = httplib.HTTPConnection(uri)
			conn.request("GET", "/index.html")
			r1 = conn.getresponse()
			if r1.status == 200:
				print "[OK] Connection to %s" % (uri)
			
			else:
				print "Error::testnet:No valid response from aws.amazon.com %s" % (r1.status)
				raise Exception('Something wrong with your internet connection?')
				
					
		except:
			print "Error::testnet:Connecting to amazon", sys.exc_info()[0]
			raise Exception()
	
	def testregions(self):
		## Test connection to AWS regions
		for region,regioname in AWS_REGIONS.iteritems():
			try:
				
				conn = httplib.HTTPConnection(region+"."+WS_URI)
				conn.request("GET", "/index.html")
				r1 = conn.getresponse()
				if r1.status == 200 or r1.status == 403:
					print "[OK] Region %s " % (regioname)
				
				else:
					print "Error::loadregions:No valid response [%s] from region %s" % (r1.reason,region)
					
			except:
				print "Error::loadregions:Connecting to AWS", sys.exc_info()[0]
				raise Exception()
		

			
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
				print n[0],n[1]
				if n[0] == "AWS_ACCESS_KEY_ID":
					self.aWSAccessKeyId=n[1]
				if n[0] == "AWS_SECRET_ACCESS_KEY":
					self.aWSSecretKey=n[1]
				
		except:
			print "Error::loadconfig:Reading file", sys.exc_info()[0]
			raise Exception()

	def prepare_qdstinfo(self,region,ssl):
		uri=""
		if ssl == 1:
			scheme="https"
		if ssl == 0:
			scheme="http"
		
		
		self.uri    = scheme+"://"+region+"."+WS_URI
		self.host   = region+"."+WS_URI
		self.scheme = scheme
	
		
		
	def _make_request(self,request):
		headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                   'host': self.host}
				   
		## Set common query parameters	
		print "Connecting to host %s" % (self.host)
		
		request.set_parameter("Version",self.version)
		
		request.sign_request(self.signature_method, self.aWSAccessKeyId, self.aWSSecretKey)
		response, content = self.http.request(request.url, request.method, headers=headers, body=request.to_postdata())
		print content
		
		
	
	def list_queues(self,region,method,ssl,prefix):		
		## Retrieve queues
		print "Retrieving queues"		
		self.prepare_qdstinfo(region,ssl)
				
		## Request parms
		parms ={
			'Action': 'ListQueues',
			'QueueNamePrefix': prefix
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)

	





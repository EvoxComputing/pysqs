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
from xml.dom.minidom import parse, parseString
from Crypto.Cipher import AES

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
		base = self.build_signature_base_string(request)
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
		
		
class AWSmessage:
	rec=0
	messageid=""
	receipthandle=""
	md5=""
	body=""
	requestid=""
	
	base64_decode=1
	
	aws_messages=[]
	
	def parse_response(self,dom):
		
		message_num = 0
		handle_num  = 0
		md_num      = 0
		body_num    = 0
		
		message_id_list  = []
		handle_list      = []
		md5_hash_list    = []
		msg_body_list    = []
		
		#Retrieve message IDs
		for name in dom.getElementsByTagName("MessageId"):
			msgid=name.toxml().replace('<MessageId>','').replace('</MessageId>','')
			message_id_list.insert(message_num,msgid)
			message_num+=1
			
		#Retrieve message Handles
		for name in dom.getElementsByTagName("ReceiptHandle"):
			handle=name.toxml().replace('<ReceiptHandle>','').replace('</ReceiptHandle>','')
			handle_list.insert(handle_num,handle)
			handle_num+=1
		
		#Retrieve message md5s
		for name in dom.getElementsByTagName("MD5OfBody"):
			md5=name.toxml().replace('<MD5OfBody>','').replace('</MD5OfBody>','')
			md5_hash_list.insert(md_num,md5)
			md_num+=1	
		
		#Retrieve message md5s
		for name in dom.getElementsByTagName("Body"):
			body=name.toxml().replace('<Body>','').replace('</Body>','')
			msg_body_list.insert(body_num,body)
			body_num+=1	
		
		for i in range(0,body_num):
			sqs_message=AWSmessage()
			sqs_message.rec=i
			sqs_message.messageid=message_id_list[i]
			sqs_message.receipthandle=handle_list[i]
			sqs_message.md5=md5_hash_list[i]
			
			try:
				if self.base64_decode == 1:
					sqs_message.body=base64.b64decode(msg_body_list[i])
				else:
					sqs_message.body=msg_body_list[i]
			except:
				sqs_message.body=msg_body_list[i]
				
			self.aws_messages.append(sqs_message)
			
			#print "Msg id %s" % (message_id_list[i])
			#print "Handle %s" % (handle_list[i])
			#print "MD5 %s " % (md5_hash_list[i])
			#print "Body %s" % (msg_body_list[i])
		
			
	
class SQS:
	
	def __init__(self,action="null",queueNamePrefix="null",expires="",aWSAccessKeyId="",aWSSecretKey="",signature="",config=""):
	
		self.action=action
		self.queueNamePrefix=queueNamePrefix
		self.expires=expires
		self.aWSAccessKeyId=aWSAccessKeyId
		self.aWSSecretKey=aWSSecretKey
		self.AESKey=""
		self.signature=signature
		self.config=config
		
		self.encryptionsupport = 1
		self.encrypt_flag = 0
		  
		self.uri=""  
		self.host=""
		self.scheme=""
		self.path=""
		self.version="2011-10-01"
		self.signatureMethod="HmacSHA256"
		self.signatureVersion="2"
		self.http = httplib2.Http()
		self.MAX_MSG_SIZE=1024*64
		
		self.queues=[]
		self.queue_url=""
		self.queue_attributes={}
		self.responsemessage=""
		self.messageid=""
		self.awsmsg=""
		
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
				
				if len(n) < 2:
					print "Error::loadconfig:No valid mappings found"
					raise Exception('No valid mappings found')
				
				if n[0] == "AWS_ACCESS_KEY_ID":
					self.aWSAccessKeyId=n[1]
				if n[0] == "AWS_SECRET_ACCESS_KEY":
					self.aWSSecretKey=n[1]
				if n[0] == "AES_KEY":
					self.AESKey=n[1]	
			
			
		except:
			print "Error::loadconfig:Reading file", sys.exc_info()[0]
			raise Exception()

	def prepare_qdstinfo(self,region,ssl):
		uri=""
		if ssl == 1:
			scheme="https"
		if ssl == 0:
			scheme="http"
		
		if self.path == "":
			self.uri    = scheme+"://"+region+"."+WS_URI
		else:
			self.uri    = scheme+"://"+region+"."+WS_URI+"/"+self.path
		self.host   = region+"."+WS_URI
		self.scheme = scheme
	
		
		
	def _make_request(self,request):
		headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                   'host': self.host}
				   
		## Set common query parameters	
		#print "Connecting to host %s" % (self.host)
		
		request.set_parameter("Version",self.version)
		
		request.sign_request(self.signature_method, self.aWSAccessKeyId, self.aWSSecretKey)
		response, content = self.http.request(request.url, request.method, headers=headers, body=request.to_postdata())
		
		#print content
		dom = parseString(content)
		if dom.getElementsByTagName("Error"):
			self.responsemessage="AWS Error"
			raise SQSError(self.showawserror(dom))
		
		if dom.getElementsByTagName("ListQueuesResult"):
			self.savequeues(dom)
			self.set_responsemsg("Queue list succesfully retrieved")
		
		if dom.getElementsByTagName("CreateQueueResult"):
			self.set_responsemsg("Create queue command succesfully executed")
			
		if dom.getElementsByTagName("GetQueueUrlResult"):
			self.set_responsemsg("URL Id retrieved succesfully")
			self.set_queue_url(dom)	

		if dom.getElementsByTagName("DeleteQueueResponse"):
			self.set_responsemsg("Queue deleted succesfully")

		if dom.getElementsByTagName("GetQueueAttributesResult"):
			self.set_responsemsg("Attributes retrieved succesfully")
			self.set_queue_attributes(dom)
		
		if dom.getElementsByTagName("SendMessageResult"):
			self.set_responsemsg("Message sent succesfully")	
			self.set_msgid(dom)

		if dom.getElementsByTagName("ReceiveMessageResult"):
			self.set_responsemsg("Message received succesfully")	
			self.set_msgs(dom)			


								
			
	def set_responsemsg(self,msg):
		self.responsemessage=msg
		
		
	def get_responsemsg(self):
		return self.responsemessage

	def set_msgid(self,dom):
		for name in dom.getElementsByTagName("MessageId"):
			self.messageid=name.toxml().replace('<MessageId>','').replace('</MessageId>','')
			
	def get_msgid(self):
		return self.messageid
			
	def savequeues(self,dom):
		for name in dom.getElementsByTagName("QueueUrl"):
			parts=urlparse.urlparse(name.toxml().replace('<QueueUrl>','').replace('</QueueUrl>',''))
			self.queues.append(parts[2].split("/")[2])

	def set_queue_url(self,dom):
		for name in dom.getElementsByTagName("QueueUrl"):
			self.queue_url=name.toxml().replace('<QueueUrl>','').replace('</QueueUrl>','')
			
	def get_queue_url(self):		
		return self.queue_url

	def set_queue_attributes(self,dom):
		self.queue_attributes={}
		attribute_names=[]
		att_n=0
		
		for name in dom.getElementsByTagName("Name"):
			att_name=name.toxml().replace('<Name>','').replace('</Name>','')
			attribute_names.insert(att_n,att_name)
			att_n+=1
		
		val_n=0
		for value in dom.getElementsByTagName("Value"):
			att_value=value.toxml().replace('<Value>','').replace('</Value>','')
			self.queue_attributes[attribute_names[val_n]] = att_value
			val_n+=1

	def set_msgs(self,dom):
		self.awsmsg=AWSmessage()
		self.awsmsg.parse_response(dom)

	def get_msgs(self):
		if self.encryptionsupport == 1:
			## Check if we have AES support
			try:
				from Crypto.Cipher import AES
				self.encrypt_flag=1
			except:
				pass
		if self.encrypt_flag == 1:
			obj = AES.new(self.AESKey, AES.MODE_ECB)
			#Decrypt message body
			aws_msg=AWSmessage()
			
			for message in aws_msg.aws_messages:
				#print "Message body: %s " % (message.body)
				plaintext= obj.decrypt(message.body)
				aws_msg.aws_messages[message.rec].body =plaintext
			
			
		return self.awsmsg
		
		
	def get_queue_attributes(self):
		return self.queue_attributes
	
	def showawserror(self,dom):
		return dom.getElementsByTagName("Message")[0].toxml().replace('<Message>','').replace('</Message>','')
		
	
	def list_queues(self,region,method,ssl,prefix):		
				
		self.prepare_qdstinfo(region,ssl)
				
		## Request parms
		parms ={
			'Action': 'ListQueues',
			'QueueNamePrefix': prefix
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)

	def create_queue(self,region,method,ssl,name):		
				
		self.prepare_qdstinfo(region,ssl)
				
		## Request parms
		parms ={
			'Action': 'CreateQueue',
			'QueueName': name
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)	

	def delete_queue(self,region,method,ssl,queuename):		
		self.path=queuename				
		self.prepare_qdstinfo(region,ssl)
				
		## Request parms
		parms ={
			'Action': 'DeleteQueue'
			
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)			
		
	def queueurl(self,region,method,ssl,name):	
		
		self.prepare_qdstinfo(region,ssl)
				
		## Request parms
		parms ={
			'Action': 'GetQueueUrl',
			'QueueName': name
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)	

	def get_queueattr(self,region,method,ssl,queuename,attributes):
		self.path=queuename	
		self.prepare_qdstinfo(region,ssl)
		
		x=1
		parms={}
		for att in attributes:
			att_name = "AttributeName."+str(x)
			parms[att_name] = att
			x+=1
		
		## Request parms
		parms['Action'] = 'GetQueueAttributes'
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)
			
	def send_msg(self,region,method,ssl,message,queuename):		
		
		if self.encryptionsupport == 1:
			## Check if we have AES support
			try:
				from Crypto.Cipher import AES
				self.encrypt_flag=1
			except:
				pass
		if self.encrypt_flag == 1:
			obj = AES.new(self.AESKey, AES.MODE_ECB)
			#Encrypt
			message = obj.encrypt(message)
		
			
		
		self.path=queuename		
		self.prepare_qdstinfo(region,ssl)
		
		#Convert message to base64 here. URL encoding of spaces in message body 
		# is not accepted by aws for some reason (based on this implementation)
		# We convert all messages to base64
		
		message_norm=base64.b64encode(message)
		
		
			
		#Max allowd size
		if sys.getsizeof(message_norm) > self.MAX_MSG_SIZE:
			raise SQSError("Message maximum size limit exceeded")
		
		## Request parms
		## Message gets normalized later
		parms ={
			'Action': 'SendMessage',
			'MessageBody': message_norm
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)	


	def receive_msg(self,region,method,ssl,queuename,max,vis_timeout,attributes):		
				
		self.path=queuename		
		self.prepare_qdstinfo(region,ssl)
		
		if vis_timeout == "":
			vis_timeout = 30
		if attributes == "":
			attributes = "All"
			
		## Request parms
		parms ={
			'Action': 'ReceiveMessage',
			'MaxNumberOfMessages': max,
			'VisibilityTimeout': vis_timeout,
			'AttributeName': attributes
			
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)	

	def delete_msg(self,region,method,ssl,queuename,handle):		
				
		self.path=queuename		
		self.prepare_qdstinfo(region,ssl)
		
		## Request parms
		parms ={
			'Action': 'DeleteMessage',
			'ReceiptHandle': handle
						
		}
		
		
		request=awsrequest(region,method,self.uri,parms)
		self._make_request(request)	
		
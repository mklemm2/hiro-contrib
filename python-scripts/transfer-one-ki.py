#!/usr/bin/env python2
from StringIO import StringIO
from urllib import quote_plus
import subprocess as sp, time, json, socket, urlparse, pycurl, shlex, sys, os, xml.etree.ElementTree as et

__RETRY__ = 100

ki_list=shlex.split("${KnowledgeItemIDs}")

config = {
	"SourceEnvironment": {
		"EngineHost":"${SYSTEM:KI_Deployment#SourceEnvironment['EngineHost']}",
		"GraphitURL":"${SYSTEM:KI_Deployment#SourceEnvironment['GraphitURL']}",
		"WSO2ISURL":"${SYSTEM:KI_Deployment#SourceEnvironment['WSO2ISURL']}",
		"ClientID":"${SYSTEM:KI_Deployment#SourceEnvironment['ClientID']}",
		"ClientSecret":"${SYSTEM:KI_Deployment#SourceEnvironment['ClientSecret']}",
		"DryRunWhitelistPath":"${SYSTEM:KI_Deployment#SourceEnvironment['DryRunWhitelistPath']}",
		"SSHOptions":"${SYSTEM:KI_Deployment#SourceEnvironment['SSHOptions']}",
		"SSHUser":"${SYSTEM:KI_Deployment#SourceEnvironment['SSHUser']}"
	},
	"TargetEnvironment": {
		"EngineHost":"${SYSTEM:KI_Deployment#TargetEnvironment['EngineHost']}",
		"GraphitURL":"${SYSTEM:KI_Deployment#TargetEnvironment['GraphitURL']}",
		"WSO2ISURL":"${SYSTEM:KI_Deployment#TargetEnvironment['WSO2ISURL']}",
		"ClientID":"${SYSTEM:KI_Deployment#TargetEnvironment['ClientID']}",
		"ClientSecret":"${SYSTEM:KI_Deployment#TargetEnvironment['ClientSecret']}",
		"DryRunWhitelistPath":"${SYSTEM:KI_Deployment#TargetEnvironment['DryRunWhitelistPath']}"
	}
}

# Classes
class TunnelError(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class Tunnel(object):
	def __init__(self, host, usr='arago', opts=[], fwd={}):
		def fport():
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(('localhost', 0)); addr, port = s.getsockname(); s.close()
			return port
		self.host=host; self.usr=usr; self.opts=opts; self.fwd={}
		for tname, tdata in fwd.items():
			rh, rp = tdata.split(':')
			self.fwd[tname] = {'lh':'localhost', 'lp':str(fport()), 'rh':rh, 'rp':rp}
	def __enter__(self):
		self.p = sp.Popen(['ssh', '-l', self.usr, self.host,'-N'] + self.opts +
						  ['-L{lh}:{lp}:{rh}:{rp}'.format(**d) for d in self.fwd.values()], stderr=sp.PIPE)
		#time.sleep(20)
		return self

	def __exit__(self, exc_type=None, exc_value=None, traceback=None): self.p.terminate()

class WSO2Error(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class WSO2Auth(object):
	def __init__(self, wso2_url, creds):
		self.wso2_url=wso2_url; self.creds = creds;
		self.errormsg='Could not retrieve token, check WSO2 URL, ClientID and ClientSecret in aae.yaml and Service Provider in WSO2.'
		self.renew()
	def renew(self):
		buf = StringIO()
		con = pycurl.Curl()
		con.setopt(pycurl.URL, '%s/oauth2/token' % self.wso2_url)
		con.setopt(pycurl.HTTPHEADER, ['Content-Type:application/x-www-form-urlencoded'])
		con.setopt(pycurl.POSTFIELDS, 'grant_type=client_credentials&scope=openid')
		con.setopt(pycurl.USERPWD, "%s:%s" % self.creds)
		con.setopt(pycurl.SSL_VERIFYPEER, 0)
		con.setopt(pycurl.WRITEFUNCTION, buf.write)
		for retry in range(1,__RETRY__+1):
			try:
				con.perform()
				if con.getinfo(pycurl.HTTP_CODE)!=200: raise WSO2Error(self.errormsg)
				self.token = json.loads(buf.getvalue())['access_token']
			except pycurl.error:
				time.sleep(0.5)
				if retry>=__RETRY__: raise WSO2Error(self.errormsg)
				else: continue
			except ValueError as e:
				raise WSO2Error(self.errormsg)
			else:
				break
		con.close()

class RESTError(Exception):
	def __init__(self, message, code):
		Exception.__init__(self, message)
		self.http_code=code


class GraphAPI(object):
	def __init__(self, baseurl, auth, host=None):
		self.baseurl=baseurl; self.auth=auth; self.host=host if host else baseurl
		for retry in range(1,__RETRY__+1):
			try:
				self.get('/info')
			except RESTError as e:
				time.sleep(0.5)
				if retry>=__RETRY__: raise
				else: continue
			except pycurl.error as e:
				time.sleep(0.5)
				if retry>=__RETRY__: raise RESTError(e, -1)
				else: continue
			else:
				break
	def get(self, ressource):
		buf = StringIO()
		con = pycurl.Curl()
		con.setopt(pycurl.URL, self.baseurl + ressource)
		con.setopt(pycurl.HTTPHEADER, ["_TOKEN: {0.token}".format(self.auth), 'Host: %s' % self.host])
		con.setopt(pycurl.SSL_VERIFYPEER, 0)
		con.setopt(pycurl.WRITEFUNCTION, buf.write)
		con.perform()
		if con.getinfo(pycurl.HTTP_CODE)!=200: raise RESTError(json.loads(buf.getvalue())['error']['message'], con.getinfo(pycurl.HTTP_CODE))
		con.close()
		return json.loads(buf.getvalue())
	def update(self, ressource, data=None, replace=False):
		buf = StringIO()
		con = pycurl.Curl()
		con.setopt(pycurl.URL, self.baseurl + ressource)
		con.setopt(pycurl.HTTPHEADER, ["_TOKEN: {0.token}".format(self.auth),
									   'Content-Type: application/json',
									   'Host: %s' % self.host])
		con.setopt(pycurl.SSL_VERIFYPEER, 0)
		con.setopt(pycurl.WRITEFUNCTION, buf.write)
		if replace:
			con.setopt(pycurl.PUT, 1)
		else:
			con.setopt(pycurl.POST, 1)
		if data:
			data = json.dumps(data)
			data_io = StringIO(data)
			content_length = len(data)
			con.setopt(pycurl.READFUNCTION, data_io.read)
			con.setopt(pycurl.INFILESIZE, content_length)
			con.setopt(pycurl.POSTFIELDSIZE, content_length)
		else:
			con.setopt(pycurl.INFILESIZE, 0)
		con.perform()
		if con.getinfo(pycurl.HTTP_CODE)!=200: raise RESTError(json.loads(buf.getvalue())['error']['message'], con.getinfo(pycurl.HTTP_CODE))
		con.close()
		return json.loads(buf.getvalue())
	def replace(self, ressource, data=None):
		return self.update(ressource, data, replace=True)
	def delete(self, ressource):
		raise NotImplementedError
	def create(self, ogit_type, data=None):
		buf = StringIO()
		con = pycurl.Curl()
		con.setopt(pycurl.URL, self.baseurl + '/new/' + quote_plus(ogit_type))
		con.setopt(pycurl.HTTPHEADER, ["_TOKEN: {0.token}".format(self.auth),
									   'Content-Type: application/json',
									   'Host: %s' % self.host])
		con.setopt(pycurl.SSL_VERIFYPEER, 0)
		con.setopt(pycurl.WRITEFUNCTION, buf.write)
		con.setopt(pycurl.POST, 1)
		if data:
			data = json.dumps(data)
			data_io = StringIO(data)
			content_length = len(data)
			con.setopt(pycurl.READFUNCTION, data_io.read)
			con.setopt(pycurl.INFILESIZE, content_length)
			con.setopt(pycurl.POSTFIELDSIZE, content_length)
		else:
			con.setopt(pycurl.INFILESIZE, 0)
		con.perform()
		if con.getinfo(pycurl.HTTP_CODE)!=200: raise RESTError(json.loads(buf.getvalue())['error']['message'], con.getinfo(pycurl.HTTP_CODE))
		con.close()
		return json.loads(buf.getvalue())
	def query(self, query, query_type="vertices", limit=-1, offset=0, fields=None):
		buf = StringIO()
		con = pycurl.Curl()
		con.setopt(pycurl.URL, self.baseurl + '/query/' + query_type)
		con.setopt(pycurl.HTTPHEADER, ["_TOKEN: {0.token}".format(self.auth),
									   'Content-Type: application/json',
									   'Host: %s' % self.host])
		con.setopt(pycurl.SSL_VERIFYPEER, 0)
		con.setopt(pycurl.WRITEFUNCTION, buf.write)
		con.setopt(pycurl.POST, 1)
		data = {"query":query, "limit":limit, "offset":offset}
		if fields:
			data['fields']=', '.join(fields)
		if data:
			data = json.dumps(data)
			data_io = StringIO(data)
			content_length = len(data)
			con.setopt(pycurl.READFUNCTION, data_io.read)
			con.setopt(pycurl.INFILESIZE, content_length)
			con.setopt(pycurl.POSTFIELDSIZE, content_length)
		else:
			con.setopt(pycurl.INFILESIZE, 0)
		con.perform()
		con.close()
		return json.loads(buf.getvalue())['items']

class Whitelist(object):
	def __init__(self, path, host=None, usr='arago', opts=[]):
		self.kiids = sp.Popen(['ssh', '-l', usr, host] + opts + ['cat', path], stdout=sp.PIPE).communicate()[0].splitlines()

# Functions
def has_action(ki):
	e = et.parse(StringIO(ki['ogit/Automation/knowledgeItemFormalRepresentation'])).getroot()
	targets=[".//{https://graphit.co/schemas/v2/KiSchema}Action", ".//{https://graphit.co/schemas/v2/KiSchema}Execute"]
	for target in targets:
		if e.findall(target): return True
	return False

def get_vars(ki):
	e = et.parse(StringIO(ki['ogit/Automation/knowledgeItemFormalRepresentation'])).getroot()
	var_names=[]
	for ki_var in e.findall(".//{https://graphit.co/schemas/v2/KiSchema}Var") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}VarAdd") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}VarSet") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}VarDelete"):
		var_names.append(ki_var.attrib['Name'])
	for ki_elem in e.findall(".//{https://graphit.co/schemas/v2/KiSchema}Action") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}DatePrint") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}Execute") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}JavaScript") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}Regex") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}CreateVertex") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}ReadVertex") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}UpdateVertex") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}DeleteVertex") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}Connect") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}Disconnect") + e.findall(".//{https://graphit.co/schemas/v2/KiSchema}Query"):
		for ki_elem_attrib in ['Output', 'Error', 'SystemRC', 'StoreTo', 'StoreError', 'StoreStatus']:
			if ki_elem_attrib in ki_elem.attrib:
				var_names.append(ki_elem.attrib[ki_elem_attrib])
	for var_name in var_names:
		print >>sys.stderr, var_name
	return var_names

def transform_var(var_body):
	if var_body['ogit/subType'] == "mars":
		var_body['ogit/name'] = "NODE:" + var_body['ogit/name'][var_body['ogit/name'].find(":")+1:]
	elif var_body['ogit/subType'] == "local":
		var_body['ogit/name'] = "LOCAL:" + var_body['ogit/name'][var_body['ogit/name'].find(":")+1:]
	elif var_body['ogit/subType'] == "issue":
		var_body['ogit/name'] = "ISSUE:" + var_body['ogit/name'][var_body['ogit/name'].find(":")+1:]
	return var_body

def transfer_var(var_name, source_graph, target_graph):
	var_body=source_graph.get('/_variables/define?name={var_name}'.format(var_name=var_name))
	var_body=transform_var(var_body)
	try: target_graph.replace('/_variables/', data=var_body)
	except RESTError as e:
			if e.http_code==409: print >>sys.stderr, "{t} Variable \"{var_name}\" already exists!".format(
					t=time.strftime("[%Y-%m-%d %H:%M:S]"),
					var_name=var_name)
	for retry in range(1,30):
		try: target_graph.get('/_variables/define?name={var_name}'.format(var_name=var_name))
		except RESTError as e: time.sleep(0.5); continue
		else: return
	raise RESTError('Variable \"{var_name}\" could not be created: unknown error'.format(var_name=var_name), 500)

def transfer_ki(ki, source_graph, target_graph):
	new_ki = {
		'ogit/Automation/deployToEngine': True, 'ogit/Automation/deployStatus': None, 'ogit/Automation/isDeployed': None,
		'ogit/Automation/knowledgeItemFormalRepresentation':ki['ogit/Automation/knowledgeItemFormalRepresentation'],
		'ogit/name':ki['ogit/name'], 'ogit/description':ki['ogit/description'],
		'ogit/_id':ki['ogit/_id'], 'ogit/changeLog':ki['ogit/changeLog'] if 'ogit/changeLog' in ki else None
		}
	try:
		for var_name in get_vars(new_ki): transfer_var(var_name, source_graph, target_graph)
	except RESTError as e:
		if e.http_code==500:
			print >>sys.stderr, e
	else:
		try:
			target_graph.create('ogit/Automation/KnowledgeItem', new_ki)
		except RESTError as e:
			if e.http_code==409:
				print >>sys.stderr, "{t} KI with ID {kiid} and title \"{kititle}\" already exists!".format(
					t=time.strftime("[%Y-%m-%d %H:%M:S]"),
					kiid=new_ki['ogit/_id'], kititle=new_ki['ogit/name'])


# MAIN

try:
	sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
	tee = sp.Popen(["tee", "-a", "/var/log/autopilot/engine/transfer-one-ki.log"], stdin=sp.PIPE)
	os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
	os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
	print >>sys.stderr, "{t} Opening tunnel connection to {host}".format(
		t=time.strftime("[%Y-%m-%d %H:%M:S]"),
		host=config['SourceEnvironment']['EngineHost'])
	with Tunnel(config['SourceEnvironment']['EngineHost'], usr=config['SourceEnvironment']['SSHUser'],
				opts=shlex.split(config['SourceEnvironment']['SSHOptions']),
				fwd={'graphit':urlparse.urlparse(config['SourceEnvironment']['GraphitURL']).netloc,
					 'wso2':urlparse.urlparse(config['SourceEnvironment']['WSO2ISURL']).netloc}) as tun:
		try:
			print >>sys.stderr, "{t} Connecting to target GraphIT at {url}".format(
				t=time.strftime("[%Y-%m-%d %H:%M:S]"),
				url=config['TargetEnvironment']['GraphitURL'])
			target_graph = GraphAPI(config['TargetEnvironment']['GraphitURL'],
									WSO2Auth(config['TargetEnvironment']['WSO2ISURL'], (
										config['TargetEnvironment']['ClientID'],
										config['TargetEnvironment']['ClientSecret'])))
		except WSO2Error as e:
			print >>sys.stderr, "{t} Error connecting to {url}: {msg}".format(
				t=time.strftime("[%Y-%m-%d %H:%M:S]"),
				url=config['TargetEnvironment']['WSO2ISURL'],
				msg=e)
			sys.exit(5)
		except RESTError as e:
			print >>sys.stderr, "{t} Error connecting to {url}: {msg}".format(
				t=time.strftime("[%Y-%m-%d %H:%M:S]"),
				url=config['TargetEnvironment']['GraphitURL'],
				msg=e)
			sys.exit(5)
		try:
			print >>sys.stderr, "{t} Connecting to source GraphIT at {url}".format(
				t=time.strftime("[%Y-%m-%d %H:%M:S]"),
				url=config['SourceEnvironment']['GraphitURL'])
			source_graph = GraphAPI("https://{lh}:{lp}".format(**tun.fwd['graphit']),
									WSO2Auth("https://{lh}:{lp}".format(**tun.fwd['wso2']), (
										config['SourceEnvironment']['ClientID'],
										config['SourceEnvironment']['ClientSecret'])),
									host=config['SourceEnvironment']['WSO2ISURL'])
		except WSO2Error as e:
			print >>sys.stderr, "{t} Error connecting to {url} (through ssh tunnel): {msg}".format(
				t=time.strftime("[%Y-%m-%d %H:%M:S]"),
				url=config['SourceEnvironment']['WSO2ISURL'], msg=e)
			sys.exit(5)
		except RESTError as e:
			print >>sys.stderr, "{t} Error connecting to {url} (through ssh tunnel): {msg}".format(
				t=time.strftime("[%Y-%m-%d %H:%M:S]"),
				url=config['SourceEnvironment']['GraphitURL'], msg=e)
			sys.exit(5)
		query_string = "+ogit\/_type:\"ogit/Automation/KnowledgeItem\" +ogit\/isValid:\"true\" +ogit\/_id:" + "(\"" + "\" \"".join(ki_list) + "\")"
		try:
			for ki in source_graph.query(query_string):
				print >>sys.stderr, "{t} KI {ki} will be transferred to PROD".format(
						t=time.strftime("[%Y-%m-%d %H:%M:S]"), ki=ki['ogit/_id'])
				transfer_ki(ki, source_graph, target_graph)
		except RESTError as e:
			print >>sys.stderr, "{t} Error connecting to {url}: {msg}".format(
				t=time.strftime("[%Y-%m-%d %H:%M:S]"),
				url=config['TargetEnvironment']['GraphitURL'],
				msg=e)
			sys.exit(5)
except TunnelError as e:
	print >>sys.stderr, "{t} Error opening tunnel: {e}".format(
		t=time.strftime("[%Y-%m-%d %H:%M:S]"), e=e)

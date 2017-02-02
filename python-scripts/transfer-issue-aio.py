#!/usr/bin/env python2
from StringIO import StringIO
from urllib import quote_plus
import subprocess as sp, time, json, sys, socket, urlparse, pycurl, shlex, xml.etree.ElementTree as et

__RETRY__ = 60

# MAIN
iid="${IID}"

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
		"DryRunWhitelistPath":"${SYSTEM:KI_Deployment#TargetEnvironment['DryRunWhitelistPath']}",
	},
	"Options": {"ResolveIssues":"${SYSTEM:KI_Deployment#Options['ResolveIssues']}"}
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
		if con.getinfo(pycurl.HTTP_CODE)!=200: raise RESTError(json.loads(buf.getvalue())['error']['message'], con.getinfo(pycurl.HTTP_CODE))
		con.close()
		return json.loads(buf.getvalue())['items']

def cleanup_issue(issue, del_attribs=[], set_attribs={}, rename_attribs=[]):
	inbuf = StringIO(issue['ogit/Automation/issueFormalRepresentation'])
	outbuf = StringIO()
	t = et.parse(inbuf)
	it = t.getiterator()
	for el in it:
		if '}' in el.tag:
			el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
	for i in t.findall("."):
		for attr in del_attribs:
			if attr in i.attrib: del i.attrib[attr]
		for attr, val in set_attribs.items():
			i.set(attr, val)
		for attr in rename_attribs:
			old, new = attr
			if old in i.attrib:
				i.set(new, i.get(old))
				del i.attrib[old]
		i.set('xmlns', 'https://graphit.co/schemas/v2/IssueSchema')
	t.write(outbuf)
	issue['ogit/Automation/issueFormalRepresentation']=outbuf.getvalue()
	return issue

class Whitelist(object):
	def __init__(self, path, host=None, usr='arago', opts=[]):
		self.kiids = sp.Popen(['ssh', '-l', usr, host] + opts + ['cat', path], stdout=sp.PIPE).communicate()[0].splitlines()

with Tunnel(
		config['SourceEnvironment']['EngineHost'],
		usr=config['SourceEnvironment']['SSHUser'],
		opts=shlex.split(config['SourceEnvironment']['SSHOptions']),
		fwd={'graphit':urlparse.urlparse(config['SourceEnvironment']['GraphitURL']).netloc,
			 'wso2':urlparse.urlparse(config['SourceEnvironment']['WSO2ISURL']).netloc}
) as tun:
	try:
		source_graph = GraphAPI(
			config['TargetEnvironment']['GraphitURL'],
			WSO2Auth(
				config['TargetEnvironment']['WSO2ISURL'],
				(config['TargetEnvironment']['ClientID'], config['TargetEnvironment']['ClientSecret'])
			)
		)
	except WSO2Error as e:
		print >>sys.stderr, "Error connecting to {url}: {msg}".format(
			url=config['TargetEnvironment']['WSO2ISURL'],
			msg=e)
		sys.exit(5)
	except RESTError as e:
		print >>sys.stderr, "Error connecting to {url}: {msg}".format(
			url=config['TargetEnvironment']['GraphitURL'],
			msg=e)
		sys.exit(5)
	try:
		target_graph = GraphAPI(
			"https://{lh}:{lp}".format(**tun.fwd['graphit']),
			WSO2Auth(
				"https://{lh}:{lp}".format(**tun.fwd['wso2']),
				(config['SourceEnvironment']['ClientID'], config['SourceEnvironment']['ClientSecret'])
			), host=config['SourceEnvironment']['WSO2ISURL']
		)
	except WSO2Error as e:
		print >>sys.stderr, "Error connecting to {url} (through ssh tunnel): {msg}".format(
			url=config['SourceEnvironment']['WSO2ISURL'], msg=e)
		sys.exit(5)
	except RESTError as e:
		print >>sys.stderr, "Error connecting to {url} (through ssh tunnel): {msg}".format(
			url=config['SourceEnvironment']['GraphitURL'], msg=e)
		sys.exit(5)
	issue = source_graph.get('/{iid}'.format(iid=iid))
	issue = cleanup_issue(issue, del_attribs=['IID', 'UID', 'CTIME', 'ETIME', 'MTIME', 'LastCommand', 'LastMessage', 'LastMoved', 'LastProcessingKI', 'LastStatusChange', 'ProcessingTime', 'State'], set_attribs={'ExecIdle':'0'}, rename_attribs=[('CurrentNodeID', 'NodeID')])
	new_issue= {
		'ogit/Automation/deployStatus': None, 'ogit/Automation/isDeployed': None,
		'ogit/Automation/issueFormalRepresentation': issue['ogit/Automation/issueFormalRepresentation'],
		'/ExecIdle':0,
	}
	target_graph.create('ogit/Automation/AutomationIssue', new_issue)
	if config['Options']['ResolveIssues']:
		try:
			source_graph.update('/{iid}'.format(iid=iid), {
				'ogit/status':'RESOLVED_EXTERNAL',
				'/State':'RESOLVED_EXTERNAL',
				'ogit/Automation/deployStatus': None,
				'ogit/Automation/isDeployed': None})
		except RESTError as e:
			print >>sys.stderr, "Error updating issue state in {url}: {msg}".format(
				url=config['SourceEnvironment']['GraphitURL'], msg=e)

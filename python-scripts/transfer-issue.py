#!/usr/bin/env python2
import sys; sys.path.append("/vagrant/includes.zip"); import graphit, shlex, urlparse, simpleyaml

# MAIN
iid="0838e286-fab7-465f-9405-b308dc2561ba"

with open("/opt/autopilot/conf/aae.yaml") as aae_yaml:
	try:
		config = simpleyaml.load([entry['Value'] for entry in simpleyaml.load(aae_yaml)['SystemGlobalVariables'] if entry['Name']=="KI_Deployment"][0])
	except IndexError:
		print >>sys.stderr, "Config not found in aae.yaml"
		sys.exit(5)

with graphit.Tunnel(
		config['SourceEnvironment']['EngineHost'],
		usr=config['SourceEnvironment']['SSHUser'],
		opts=shlex.split(config['SourceEnvironment']['SSHOptions']),
		fwd={'graphit':urlparse.urlparse(config['SourceEnvironment']['GraphitURL']).netloc,
			 'wso2':urlparse.urlparse(config['SourceEnvironment']['WSO2ISURL']).netloc}
) as tun:
	try:
		source_graph = graphit.GraphAPI(
			config['TargetEnvironment']['GraphitURL'],
			graphit.WSO2Auth(
				config['TargetEnvironment']['WSO2ISURL'],
				(config['TargetEnvironment']['ClientID'], config['TargetEnvironment']['ClientSecret'])
			)
		)
	except graphit.WSO2Error as e:
		print >>sys.stderr, "Error connecting to {url}: {msg}".format(
			url=config['TargetEnvironment']['WSO2ISURL'],
			msg=e)
		sys.exit(5)
	except graphit.RESTError as e:
		print >>sys.stderr, "Error connecting to {url}: {msg}".format(
			url=config['TargetEnvironment']['GraphitURL'],
			msg=e)
		sys.exit(5)
	try:
		target_graph = graphit.GraphAPI(
			"https://{lh}:{lp}".format(**tun.fwd['graphit']),
			graphit.WSO2Auth(
				"https://{lh}:{lp}".format(**tun.fwd['wso2']),
				(config['SourceEnvironment']['ClientID'], config['SourceEnvironment']['ClientSecret'])
			), host=config['SourceEnvironment']['WSO2ISURL']
		)
	except graphit.WSO2Error as e:
		print >>sys.stderr, "Error connecting to {url} (through ssh tunnel): {msg}".format(
			url=config['SourceEnvironment']['WSO2ISURL'], msg=e)
		sys.exit(5)
	except graphit.RESTError as e:
		print >>sys.stderr, "Error connecting to {url} (through ssh tunnel): {msg}".format(
			url=config['SourceEnvironment']['GraphitURL'], msg=e)
		sys.exit(5)
	issue = source_graph.get('/{iid}'.format(iid=iid))
	issue=graphit.cleanup_issue(issue, del_attribs=['IID', 'UID', 'CTIME', 'ETIME', 'MTIME', 'LastCommand', 'LastMessage', 'LastMoved', 'LastProcessingKI', 'LastStatusChange', 'ProcessingTime', 'State'], set_attribs={'ExecIdle':'0'}, rename_attribs=[('CurrentNodeID', 'NodeID')])
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
		except graphit.RESTError as e:
			print >>sys.stderr, "Error updating issue state in {url}: {msg}".format(
				url=config['SourceEnvironment']['GraphitURL'], msg=e)

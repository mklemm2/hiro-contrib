#!/usr/bin/env python
"""\
Usage:
  connectit-stresstest.py [options] do USECASE on CONFIGITEM...

Options:
  -u URL --url=URL               REST API to use [default: https://localhost:8185/connectit/api]
  -p PROCESS --process=PROCESS   ITSM Process to use [default: Event]
  -r RATE --rate=RATE            Issues per minute [default: 3]
  -x                             Apply workaround for connectit call_id bug
  -v --verbose                   Print SDF data
  -t NUM --threads=NUM           Number of producer threads [default: 10]

"""
from __future__ import division
from gevent import monkey; monkey.patch_all()
import gevent, gevent.pool, gevent.hub
import requests, json, random, uuid, time, itertools, signal, sys, fcntl, os
from gevent.socket import wait_read
from datetime import datetime, timedelta
from docopt import docopt
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class EventSDF:
	def __init__(
			self, eventId, delta=True,
			description="Test if the Event arrives in GraphIT",
			eventName="TestEvent",
			instance="mockup.nfi.dev",
			isRoot=True,
			**kwargs
	):
		self._data = {
			"call_id": "",
			"cb_Topic": "",
			"delta": True,
			"free": {},
			"mand": {
				"description": description,
				"eventId": eventId,
				"eventName": eventName,
				"instance": instance,
				"sourceId": "REST-Connect2"
			},
			"opt": {
				"isRoot": isRoot
			},
			"nestedStates": True,
			"prod_id": None,
			"sdfType": "EVENT",
			"sdfVersion": "1.0",
			"send_Topic": None
		}
		for name, value in kwargs.items():
			self._data['opt'][name] = value

	def set(self, context=None, **kwargs):
		if context:
			for name, value in kwargs.items():
				self._data[context][name] = value
		else:
			for name, value in kwargs.items():
				self._data[name] = value

	def set_mand(self, **kwargs):
		self.set(context="mand", **kwargs)

	def set_opt(self, **kwargs):
		self.set(context="opt", **kwargs)

	def set_free(self, **kwargs):
		self.set(context="free", **kwargs)

	@property
	def json(self):
		return json.dumps(self._data)

class Producer:
	def __init__(self, url, send_Topic, prod_id="test"):
		self.url=url
		self.session=requests.Session()
		self.session.verify=False
		self.send_Topic=send_Topic
		self.prod_id=prod_id

	def send(self, sdf):
		sdf.set(send_Topic=self.send_Topic, prod_id=self.prod_id)
		headers = {'Content-type':'application/json'}
		try:
			resp = self.session.request('POST', self.url, headers=headers, data=sdf.json)
			resp.raise_for_status()
		except requests.exceptions.HTTPError as e:
			print(e)

class Last(object):
	def __init__(self):
		self.ts=time.time()

	def update(self):
		self.ts=time.time()

	@property
	def val(self):
		return self.ts

class Offset(object):
	def __init__(self):
		self.one = 0.0
		self.two = 0.0
		self.three = 0.0

	def update(self, val):
		self.one, self.two, self.three = val, self.one, self.two

	@property
	def val(self):
		#print(self.one, self.two, self.three)
		return (self.one + self.two + self.three) / 3

if __name__ == '__main__':
	args = docopt(__doc__, version='connectit-stresstest 0.1')
	print(args)
	ipm = float(args['--rate'])
	#print(ipm)
	last = Last()
	offset = Offset()
	pool = gevent.pool.Pool(int(args['--threads']))
	counter = itertools.count(1)

	def submit(last, ipm, offset, counter, fill_call_id=False, verbose=False):
		#start_ts = time.time()

		config_item = random.choice(args['CONFIGITEM'])

		sdf = EventSDF(str(uuid.uuid4()))
		sdf.set_mand(eventName=args['USECASE'], description=args['USECASE'])
		#sdf.set_free(affectedCI=config_item)
		sdf.set_opt(affectedCI=config_item)

		if fill_call_id:
			sdf.set(call_id=str(uuid.uuid4()))

		if verbose:
			print(json.dumps(
				sdf._data,
				sort_keys=True,
				indent=4))

		producer = Producer(args['--url'], args['--process'])
		producer.send(sdf)
		offset.update(max(0, (time.time() - last.val) - (60 / ipm)))
		print("Event {n} sent, delay={delay}, issues/min={ipm}, offset={offset}".format(n=next(counter), delay= 60 / ipm, ipm=ipm, offset = offset.val))
		last.update()

	def loop():
		while True:
			pool.spawn(submit, last, ipm, offset, counter, fill_call_id=args['-x'], verbose=args['--verbose'])
			#print(60 / ipm)
			gevent.sleep(max((60 / ipm) - offset.val, 0.0001))

	x = gevent.spawn(loop)
	def exit_gracefully():
		x.kill()
	gevent.hub.signal(signal.SIGINT, exit_gracefully)
	gevent.hub.signal(signal.SIGTERM, exit_gracefully)
	try:
		x.join()
	except KeyboardInterrupt:
		print("\nexiting...")
		sys.exit(0)

#!/usr/bin/env python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import random

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
				"sourceId": "REST-Connect"
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
			print(json.dumps(
				sdf._data,
				sort_keys=True,
				indent=4))
		except requests.exceptions.HTTPError as e:
			print(e)

baseurl = "https://localhost:8185/connectit/api"

usecases = [
	"Swapping",
	"No response"
]

num1=random.choice([10237, 9651, 8651, 10437, 289])

x = EventSDF("{num:06d}TEST_COL2".format(num=random.randrange(999999)))
x.set_mand(description="Benchmark", eventName="Benchmark")
#x.set_free(affectedCI="UBS:APAC:Machine:{num}".format(num=num1))
x.set_opt(affectedCI="UBS:APAC:Machine:{num}".format(num=num1))

x.set_free(additional_payload="1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF")

y = Producer(baseurl, "Event")
y.send(x)

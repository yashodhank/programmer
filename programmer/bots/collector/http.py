#-*- coding: utf-8 -*-

from __future__ import unicode_literals
import requests
import sys

from ..bot import Bot
from ..harmonization import DateTime
from ..message import Report

try:
	import urllib3.contrib.pyopenssl
	urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
	pass

class HTTPColectorBot(Bot):
	def init(self):
		self.http_header = self.parameters.get('http_header', {})
		self.verify_cert = self.parameters.get('verify_cert', True)

		if self.parameters.has_key('username') and self.parameters.has_key('password'):
			self.auth = (self.parameters.username, self.parameters.password)

		if self.parameters.has_key('http_proxy') and self.parameters.has_key('https_proxy'):
			self.proxy = {'http': self.parameters.http_proxy, 'https': self.parameters.https_proxy}
		else:
			self.proxy = None

		self.http_header['user-agent'] = self.parameters.http_user_agent

	def process(self):
		self.logger.info('Downloading report from %s' % self.parameters.url)

		resp = requests.get(
			url=self.parameters.url,
			auth=self.auth,
			proxies=self.proxy,
			headers=self.http_header,
			verify=self.verify_cert
		)

		if resp.status_code // 100 != 2:
			raise ValueError('HTTP Response status code was {}'.format(res.status_code))
		self.logger.info('Report downloaded.')

		report = Report()
		report.add('raw', resp.text, sanitize=True)
		report.add('feed.name', self.parameters.feed, sanitize=True)
		report.add('feed.url', self.parameters.url, sanitize=True)
		time_observation = DateTime.generate_datetime_now()
		report.add('time.observation', time_observation, sanitize=True)

		self.send_message(report)
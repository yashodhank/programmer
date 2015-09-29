# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..bot import Bot

class FilterExpertBot(Bot):

	def init(self):
		for mandatory in ('filter_key', 'filter_value', 'filter_action'):
			if not self.parameters.has_key(mandatory):
				self.logger.warn('No {} parameter found.'.format(mandatory))
				self.stop()

	def process(self):
		event = self.receive_message()

		if event is None:
			self.acknowledge_message()
			return

		if self.parameters.filter_action == 'Drop':
			if (event.contains(self.parameters.filter_key) and
				event.value(self.parameters.filter_key)==self.parameters.filter_value):
				self.acknowledge_message()
			else:
				self.send_message(event)
				self.acknowledge_message()
		if self.parameters.filter_action == 'Keep':
			if (event.contains(self.parameters.filter_key) and
				event.value(self.parameters.filter_key)===self.parameters.filter_value):
				self.send_message(event)
				self.acknowledge_message()
			else:
				self.acknowledge_message()

		self.acknowledge_message()

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import copy
import frappe

from ..bot import Bot

class DeduplicatorExpertBot(Bot):
	def init(self):
		self.cache = frappe.cache()

	def process(self):
		message = self.receive_message()

		if message is None:
			self.acknowledge_message()
			return

		auxiliar_message = copy.copy(message)
		ignore_keys = self.parameters.get('ignore_keys','').split(',')

		for ignore_key in ignore_keys:
			ignore_key = ignore_key.strip()
			if ignore_key in auxiliar_message:
				auxiliar_message.clear(ignore_key)

		message_hash = hash(auxiliar_message)
		if not self.cache.exists(message_hash):
			self.cache.set(message_hash, 'hash')
			self.send_message(message)

		self.acknowledge_message()


# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class APIBotTemplate(Document):
	def autoname(self):
		self.name = '{} - {}'.format(self.bot_type, self.bot_name.strip())
	
	def validate(self):
		self.bot_class = '.'.join([
			'bots', 
			self.bot_type.replace(' ', '_').lower(),
			self.bot_name.replace(' ','').lower().strip(),
			'{}{}Bot'.format(self.bot_name.replace(' ',''), self.bot_type)
		])


# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import re

PATTERN = re.compile('([a-z]+)')
HAS_REPLACEMENTS = re.compile('(:[a-z]+)')

class APPTokenEndpoint(Document):
	def onload(self):
		if not self.is_new():
			self.base_url = frappe.db.get_value("APP Token", self.app_token, "api_user_endpoint")

	def autoname(self):
		name = " ".join(map(lambda x: x.title(), PATTERN.findall(self.endpoint.lower())))
		self.name = '{} - {}'.format(self.app_token, name)

	def validate(self):
		self.endpoint = self.endpoint.lower()
		self.validate_replacements()

	def validate_replacements(self):
		tokens = HAS_REPLACEMENTS.findall(self.endpoint)

		if tokens and not self.repls:
			[self.append('repls', {'key': token}) for token in tokens]
		elif tokens and self.repls:
			messages = []
			for d in self.repls:
				if not d.key:
					messages.append(
						frappe._('{} is mandatory in {} in row {}').format(
							map(frappe._, [
								d.meta.get_label('key'), 
								self.meta.get_label('repls'), 
								d.idx
							])
						)
					)
				if d.key not in tokens:
					messages.append(frappe._('Replacement {} is not allowed in [{}]')).format(d, ",".join(tokens))
			if messages:
				frappe.throw("<br>".join(messages))
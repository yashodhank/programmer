# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from programmer.apis.oauth2 import get_oauth_session

class APPToken(Document):
	
	def validate(self):
		pass

	def clear_endpoints(self):
		if self.endpoints:
			self.endpoints = []

	def before_save(self):
		self.clear_endpoints()
# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class APIResource(Document):
	def autoname(self):
		self.name = "{} - {} - {}".format(
			self.api, self.resource, self.data_format
		)

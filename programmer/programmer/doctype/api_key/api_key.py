# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.model.document import Document

class APIKey(Document):
	def update_token(self, data):
		pass

# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CodeProjectSettings(Document):
	def validate(self):
		if self.use_wakatime:
			self.validate_wakatime()
		else:
			self.clean_wakatime_settings()

	def validate_wakatime(self):
		pass
		#self.validate_table_has_rows('wakatime_projects')

	def clean_wakatime_settings(self):
		self.update({
			'wakatime_api_token': None,
		})

		for project in self.wakatime_projects:
			self.remove(project)
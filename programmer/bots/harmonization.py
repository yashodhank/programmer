#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import dateutil.parser
import pytz
import types

from frappe import utils

class GenericType(object):
	@staticmethod
	def is_valid(value, sanitize=False):
		if sanitize:
			value = GenericType.sanitize(value)

		if not value or not isinstance(value, basestring) or not len(value):
			return False
		return True

	@staticmethod
	def sanitize(value):
		if not value:
			return None

		if isinstance(value, basestring):
			return value.strip()
		elif isinstance(value, (basestring, bytes)):
			try:
				value = value.decode('utf-8')
			except UnicodeDecodeError:
				value = value.decode('utf-8', 'ignore')
			return value.strip()

		return None

class Boolean(GenericType):
	'''
	Boolean type. Without sanitization only python bool is accepted.

	Sanitization accepts string 'true', 'yes', 'false' and 'no' and integers 0 and 1
	'''

	@staticmethod
	def is_valid(value, sanitize=False):
		if isinstance(value, bool):
			return True
		elif sanitize:
			value = Boolean.sanitize(value)
			if value is not None:
				return True
		return False

	@staticmethod
	def sanitize(value):
		if isinstance(value, (basestring, bytes)):
			value = value.strip().lower()
			if value in ('true', 'yes'):
				return True
			elif value in ('false', 'no'):
				return False
		elif isinstance(value, int):
			if value == 0:
				return False
			elif value == 1:
				return True

		return None

class Select(GenericType):
	@staticmethod
	def is_valid(value, sanitize=True, allowed_values=()):
		if sanitize:
			value = Select.sanitize(value)

		if not GenericType.is_valid(value):
			return False

		if not isinstance(value, basestring):
			return False

		if value not in allowed_values:
			return False

		return True

class DateTime(GenericType):
	pass
# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
import six
import hmac

from frappe.model.document import Document
from six.moves.urllib.parse import quote
from hashlib import sha256

re_path_template = re.compile('{\w+}')

def encode_string(value):
	return value.encode('utf-8') \
		if isinstance(value, six.text_type) else str(value)

class ClientError(Exception):
	def __init__(self, error_message, status_code=None):
		self.status_code = status_code
		self.error_message = error_message

	def __str__(self):
		if self.status_code:
			return '(%s) %s' % (self.status_code, self.error_message)
		else:
			return self.error_message

class APIError(Exception):
	def __init__(self, status_code, error_type, error_message, *args, **kwargs):
		self.status_code = status_code
		self.error_type = error_type
		self.error_message = error_message

	def __str__(self):
		return '(%s) %s-%s' % (self.status_code, self.error_type, self.error_message)

def bind(**config):
	class APIMethod(object):
		'''common parameters for a api action'''
		path = config['path']
		method = config.get('method', 'GET')
		accepts_parameters = config.get('accepts_parameters', '').split(',')
		signature = config.get('signature', False)
		requires_target_user = config.get('requires_target_user', False)
		paginates = config.get('paginates', False)
		root_class = config.get('response_type', 'List')
		include_secret = config.get('include_secret', False)
		objectify_response = config.get('objectify_response', False)
		exclude_format = config.get('exclude_format', False)

		def __init__(self, api, *args, **kwargs):
			self.api = api
			self.as_generator = kwargs.pop('as_generator', False)
			if self.as_generator:
				self.pagination_format = 'next_url'
			else:
				self.pagination_format = kwargs.pop('pagination_format', 'next_url')
			self.return_json = kwargs.pop('return_json', False)
			self.max_pages = kwargs.pop('max_pages', 3)
			self.with_next_url = kwargs.pop('with_next_url', None)
			self.parameters = {}
			self._build_parameters(args, kwargs)
			self._build_path()

		def _build_parameters(self, args, kwargs):
			for index, value in enumerate(args):
				if value is None:
					continue

				try:
					self.parameters[self.accepts_parameters[index]] = encode_string(value)
				except IndexError:
					raise ClientError('Too many arguments supplied')

				for key, value in six.iteritems(kwargs):
					if value is None:
						continue
					if key in self.parameters:
						raise ClientError('Parameter %s already supplied'%key)
					self.parameters[key] = encode_string(value)

				if 'user_id' in self.accepts_parameters and not user_id in self.parameters \
					and not self.requires_target_user:
						self.parameters['user_id'] = 'self'

		def _build_path(self):
			for variable in re_path_template.findall(self.path):
				name = variable.strip("{}")
				try:
					value = quote(self.parameters[name])
				except KeyError:
					raise Exception('No parameter found for path variable: %s' %name)

				self.path = self.path.replace(variable, value)

			if self.api.format and not self.exclude_format:
				self.path = self.path + '.%s' % self.api.format

		def _build_pagination_info(self, content_obj):
			''' Extract pagination information in the desired format '''
			pagination = content_obj.get('pagination', {})
			if self.pagination_format == 'next_url':
				return pagination.get('next_url')
			if self.pagination_format == 'Dict':
				return pagination
			raise Exception('Invalid value for pagination_format: %s' % self.pagination_format)

		def _do_api_request(self, url, method='GET'):
			pass
			
HOST_HEADERS = [
	'Authorization',
	'Host',
	'X-Forwarded-For',
	'X-Forwarded-Proto',
	'X-Forwarded-Protocol',
	'X-Real-Ip',
	'X-Request-Start'
]

class API(Document):
	def autoname(self):
		self.name = ' - '.join([self.api_name, self.api_type, self.api_auth_method])

	def onload(self):
		dl = frappe.db.sql("""
		SELECT 
			`tabAPI Resource`.resource as resource,
			`tabAPI Resource Attribute`.attribute as attribute,
			`tabAPI Resource Attribute`.attribute_type as attribute_type,
			t2.resource as of
		FROM `tabAPI Resource`
		    INNER JOIN `tabAPI Resource Attribute` ON `tabAPI Resource Attribute`.parent = `tabAPI Resource`.name
		    LEFT JOIN `tabAPI Resource` t2 ON  t2.name = `tabAPI Resource Attribute`.of
		WHERE `tabAPI Resource`.api = %s;
		""", (self.name, ), as_dict=True)
		for d in dl:
			self.append('resources', d)

	def before_update(self):
		self.resources = []

	def init_valid_columns(self):
		super(API, self).init_valid_columns()

		for method in self.methods:
			pass

	def prepare_headers(self, step):
		step = step.strip().lower().title()
		filters = {
			'ctx': ['=', '{} Request'.format(step)],
			'parameter': ['not in', HOST_HEADERS],
			'value': ['not in', ('', None)]	
		}
		headers = {h.parameter: h.value for h in self.get('parameters', filters=filters)}

@frappe.whitelist()
def get_dialog_details(name):
	doc = API('API', name)
	fields = []
	childs = doc.get('parameters', {'value': None, 'ctx': 'Class'})
	favicon = doc.get('parameters', {'parameter', 'favicon_url'})
	if not favicon: 
		favicon = 'https://www.google.com/s2/favicons?domain={}'.format(doc.provider_url)

	for child in childs:
		fields.append({
			'fieldtype': 'Data',
			'reqd': True,
			'fieldname': child.parameter,
			'label': " ".join(map(lambda x: x.title(), child.parameter.split('_'))),
		})
	ret = {
		'fields': fields,
		'title': '<img src="{0}" /> <b>{1} {2} API {3} Info</b>'.format(favicon, doc.api_name, doc.api_type, doc.api_auth_method),
	}

@frappe.whitelist()
def toggle_status(name, activate=True, **kwargs):
	doc = API('API', name)
	doc.active = activate
	for k,v in kwargs.items():
		d = doc.get('parameters', {'parameter': k})
		if not d:
			d = doc.append('parameters',{
				'parameter': k,
				'value': v
			})
		else:
			if isinstance(d, (list, tuple, set)): d = d[0]
			d.value = v if activate else None
	doc.save()

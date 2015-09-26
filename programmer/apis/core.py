
from __future__ import unicode_literals

import frappe
import datetime

from functools import wraps

def auth_endpoint(fn):
	@wraps(fn)
	def wrapper(alias, *args, **kwargs):
		pass

def get_user(user=None):
	return user or frappe.get_user().name

def get_traversed_params(param_list, replacements={}):
	""" Adds the replacements in the param list """
	response = {}
	for row in param_list:
		v = row.v
		if v and v.startswith(':'):
			v = v.replace(':', '')
			if hasattr(replacements, v):
				v = getattr(replacements, v)
			elif hasattr(replacements, 'has_key') and replacements.has_key(v):
				v = replacements[v]
			elif hasattr(replacements, 'get'):
				v = replacements.get(v)
			response[row.k] = v
		else:
			response[row.k] = v
	return response

def get_traversed_data(service, field, repl={}):
	""" Format the request headers """
	dl = frappe.get_all("APP Token Params", fields=["k", "v"], filters=[
		["APP Token Params", "parent", "=", service],
		["APP Token Params", "parentfield", "=", field]
	])
	return get_traversed_params(dl, repl)

def get_headers_data(service, repl={}):
	return get_traversed_data(service, "session_header_params", repl)

def get_request_data(service, repl={}):
	return get_traversed_data(service, "params", repl)

def get_session_data(service, repl={}):
	return get_traversed_data(service, "session_data_params", repl)

def store_user_token(data, service, user=None):
	user = get_user(user)
	if not frappe.db.exists('API Key', {'parent': service, 'user':user}):
		doc = frappe.new_doc('API Key')
		doc.update({
			'parent': service,
			'user': user,
			'parenttype': 'API',
			'parentfield': 'users'
		})
	else:
		doc = frappe.db.get_doc('API Key', {'parent': service, 'user': user})

	if data.get('expires_in'):
		expires_in = datetime.timedelta(seconds=int(data['expires_in']))
		expires = datetime.datetime.now() + expires_in
	else:
		expires = None

	doc.update({
		'access_token': data['access_token'],
		'secret': data.get('secret', None),
		'expires': expires,
		'refresh_token': data.get('refresh_token', None),
		'api_user_id': data.get('service_user_id', None)
	})
	doc.save()
	frappe.db.commit()
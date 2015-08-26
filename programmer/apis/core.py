
from __future__ import unicode_literals
import frappe

def get_traversed_params(param_list, replacements={}):
	""" Adds the replacements in the param list """
	response = {}
	for row in param_list:
		value = row.value
		if value and value.startswith(':'):
			value = value.replace(':', '')
			if hasattr(replacements, value):
				value = getattr(replacements, value)
			elif hasattr(replacements, 'has_key') and replacements.has_key(value):
				value = replacements[value]
			elif hasattr(replacements, 'get'):
				value = replacements.get(value)
			response[row.key] = value
		else:
			response[row.key] = value
	return response

def get_traversed_data(service, field, repl={}):
	""" Format the request headers """
	dl = frappe.get_all("APP Token Params", fields=["key", "value"], filters=[
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

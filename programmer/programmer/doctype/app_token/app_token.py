# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import time

from collections import defaultdict
from rauth import OAuth2Service
from frappe.model.document import Document

class APPToken(Document):
	def on_update(self):
		pass

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
	return response

def get_oauth_service(service):
	""" Returns the OAuth2Service instance """
	fields = frappe.db.get_values(
		"APP Token",
		service,
		["name", "client_id", "cliend_secret", "autorization_url", "access_token_url", "base_url"]
	)
	return OAuth2Service(**fields)

def get_traversed_data(service, field, repl={}):
	""" Format the request headers """
	dl = frappe.get_all("APP Token Params", fields=["key", "value"], filters=[
		["APP Token Params", "parent", "=", service],
		["APP Token Params", "params", "=", field]
	])
	return get_traversed_params(dl, repl)

def get_oauth_headers_data(service, repl={}):
	return get_traversed_data(service, "session_headers_params", repl)

def get_oauth_request_data(service, repl={}):
	return get_traversed_data(service, "params", repl)

def get_oauth_session_data(service, repl={}):
	return get_traversed_data(service, "session_data_params", repl)

def get_user(user=None):
	return user or frappe.get_user().name
	
def get_oauth_user(service, user):
	""" Return the user id in the Service """
	dl = frappe.get_all("APP Token User", fields="app_user_id", filters=[
		["APP Token User", "user", "=", user],
		["APP Token User", "parent", "=", service]
	])
	return dl[0].app_user_id if dl else None

@frappe.whitelist()
def request_oauth_code(service, user=None):
	state = frappe.db.set_temp(json.dumps({
		"service": service,
		"user": user
	}))

	data = get_oauth_request_data(service, {'state': state})
	flow = get_oauth_service(service)
	url = flow.get_authorize_url(**data)

	msg = '''
	Visit <a class="btn btn-xs btn-default" href="{url}" target="_blank">this link</a> for autorize <b>{name}</b> in this app.
	'''.format(url=url, name=doc.name)

	frappe.msgprint(msg)

def _store_oauth_token(code=None, state=None):
	if not code:
		return {"FAIL": frappe._("You did not authorized the request")}

	if state:
		try:
			raw = json.loads(frappe.db.get_temp(state))
			user = raw["user"]
			service = raw["service"]
		except ValueError:
			raise {"FAIL": frappe._("The given status dont match with the status provided")}

	headers = get_oauth_headers_data(service, {"code": code, "state": state})
	data = get_oauth_session_data(service, {"code": code, "state": state})
	flow = get_oauth_service(service)

	src = frappe.db.get_values("APP Token", service, ["session_given_by", "api_user_endpoint"])
	if src.session_given_by == "Simple Session":
		session = flow.get_auth_session(data=data)
		response = session.get(src.api_user_endpoint).json()
		update_token(
			service, 
			response["auth_token"], 
			user, 
			response["expires_in"], 
			response["refresh_token"]
		)
	else:
		session = flow.get_raw_access_token(data=data)
		response = session.get(src.api_user_endpoint)
		update_token(service, 
			response.auth_token,
			user
		)
	return {'OK': frappe._("Token stored successfull")}

def update_token(service, token="", user=None, expires_in=-1, refresh=None):
	user = get_user(user)
	dl = frappe.get_all("APP Token User", fields=["name", "auth_token"], filters=[
		["APP Token User", "user", "=", user],
		["APP Token User", "parent", "=", service]
	])
	if dl:
		doc = frappe.get_doc("APP Token User", dl["name"])
	else:
		doc = frappe.new_doc("APP Token User")
	data = {
		"auth_token": token,
		"expires_in": expires_in,
		"refresh_token": refresh
	}
	doc.update(data)
	doc.save()
	frappe.db.commit()

	return token

def get_token(service, user=None):
	user = get_user(user)
	dl = frappe.get_all("APP Token User", fields="auth_token", filters=[
		["APP Token User", "user", "=", user],
		["APP Token User", "parent", "=", service]
	])
	if dl:
		return dl[0].auth_token

def clear_oauth_token(service, user=None):
	return get_update_token(service, "", user)

def refresh_oauth_token(service, user=None):
	pass

def get_oauth_session(service, user=None):
	
	current = int(time())

	if not user:
		user = frappe.get_user().name

	filters = [
		["APP Token User", "parent", "=", service],
		["APP Token User", "user", "=", user]
	]

	dl = frappe.get_all("APP Token User", fields=["auth_token", "app_user_id"], filters=filters)

	if not dl or not dl[0].auth_token:
		return request_oauth_code(service, user)
	elif dl[0].expires_in and dl.expires_in > -1 and (dl[0].expires_in - current) <= 0:
		auth_token = refresh_oauth_token(service, user)
	else:
		auth_token = dl[0].auth_token

	doc = frappe.get_doc("APP Token", service)	
	oserv = get_oauth_service(doc)
	session = oserv.get_session(auth_token)
	response = session.get(doc.api_user_endpoint)

	if response.status_code != 200:
		replacers = {
			"auth_token": auth_token
		}
		data = traverse_params(doc.session_data_params, replacements=replacers)		
		session = oserv.get_auth_session(data=data)
		
	return session
	
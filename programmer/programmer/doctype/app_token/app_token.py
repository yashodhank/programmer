# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json

from rauth import OAuth2Service
from frappe.model.document import Document

class APPTokenError(Exception):
	pass

class APPToken(Document):
	def on_update(self):
		auth = filter(lambda x: x.user==self.owner, self.authenticated_users)
		if not auth or not auth[0].auth_token:
			request_auth_code(self.name, self.owner)
		get_oauth_session(self.name, self.owner)

def traverse_params(param_list, replacements={}):
	response = {}
	for row in param_list:
		value = row.value
		if value.startswith(':'):
			value = value.replace(':', '')
			if hasattr(replacements, value):
				value = getattr(replacements, value)
			elif hasattr(replacements, 'has_key') and replacements.has_key(value):
				value = replacements[value]
			elif hasattr(replacements, 'get'):
				value = replacements.get(value)
		response[row.key] = value
	return response

def get_oauth_service(doc):
	return OAuth2Service(
		name=doc.title,
		client_id=doc.client_id,
		client_secret=doc.client_secret,
		authorize_url=doc.authorize_url,
		access_token_url=doc.access_token_url,
		base_url=doc.base_url
	)

@frappe.whitelist()
def request_oauth_code(service, user=None):
	doc = frappe.get_doc('APP Token', service)
	if not user:
		user = frappe.get_user().name
	params = traverse_params(doc.params, replacements=doc)
	state = frappe.db.set_temp(json.dumps({
		'service': service, 
		'user': user, 
		'parser': doc.user_id_parser,
		'endpoint': doc.api_user_endpoint }))
	params['state'] = state
	oserv = get_oauth_service(doc)
	url = oserv.get_authorize_url(**params)

	msg = '''
		Visit <a class="btn btn-xs btn-default" href="{url}" target="_blank">this link</a>  for autorize <b>{name}</b> in this app.
	'''.format(url=url, name=doc.name)

	frappe.msgprint(msg)

def _store_oauth_token(code, state):
	from programmer.data_tools import get_uri_parsed
	from pprint import pprint

	data = json.loads(frappe.db.get_temp(state))
	service = data['service']
	user = data['user']

	pprint(data)

	filters = [
		["APP Token User", "parent", "=", service],
		["APP Token User", "user", "=", user]
	]
	dl = frappe.get_all("APP Token User", fields=["name", "app_user_id"], filters=filters)
	if data.has_key("parser") and data.has_key("endpoint") and all([data["parser"], data["endpoint"]]):
		app_user_id = get_uri_parsed(service, data["endpoint"], data["parser"], user=user, code=code)
	else:
		app_user_id = None

	if dl:
		frappe.db.set_value("APP Token User", dl[0]["name"], "auth_token", code)
		if app_user_id and (not dl[0].app_user_id):
			frappe.db.set_value("APP Token User", dl[0]["name"], "app_user_id", app_user_id)
	else:
		doc = frappe.new_doc("APP Token User")
		doc.update({
			"parent": service,
			"parenttype": "APP Token",
			"parentfield": "authenticated_users",
			"user": user,
			"auth_token": code 
		})
		if app_user_id:
			doc["app_user_id"] = app_user_id
		doc.save()
	frappe.db.commit()

	return {'OK': frappe._('Authorization Code Stored')}

def clear_oauth_token(service, user=None):
	if not user:
		user = frape.get_user().name

	filters = [
		["APP Token User", "parent", "=", service],
		["APP Token User", "user", "=", user]
	]

	dl = frappe.get_all("APP Token User", fields=["name", "auth_token"], filters=filters)
	if not dl or dl[0].auth_token:
		return
	frappe.db.set_value("APP Token User", dl[0].name, "auth_token", None)
	frappe.db.commit()

def get_oauth_session(service, user=None, code=None):
	if not code:
		if not user:
			user = frappe.get_user().name

		filters = [
			["APP Token User", "parent", "=", service],
			["APP Token User", "user", "=", user]
		]

		dl = frappe.get_all("APP Token User", fields=["auth_token", "app_user_id"], filters=filters)
		if not dl or not dl[0].auth_token:
			return request_oauth_code(service, user)
		auth_token = dl[0].auth_token
		app_user_id = dl[0].app_user_id
	else:
		auth_token = code
		app_user_id = ""

	replacers = {
		"auth_token": auth_token,
		"user": app_user_id
	}

	doc = frappe.get_doc("APP Token", service)
	headers = traverse_params(doc.session_header_params, replacements=replacers)
	data = traverse_params(doc.session_data_params, replacements=replacers)
	oserv = get_oauth_service(doc)
	try:
		session = oserv.get_auth_session(
			headers=headers, 
			data=data
		)
		return session
	except KeyError, e:
		if 'expired' in e.message.lower() or 'invalid' in e.message.lower():
			clear_oauth_token(service, user)
			request_oauth_code(service, user)
			frappe.msgprint("The active AuthCode is {}".format('expired' if 'experied' in e.message.lower() else 'invalid'))
		else: 
			raise KeyError(e)
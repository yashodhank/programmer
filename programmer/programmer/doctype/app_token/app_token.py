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
		try:
			get_oauth_session(self.name, self.owner)
		except KeyError, e:
			frappe.msgprint(e)
			frappe.db.commit()
			request_oauth_code(self.name, self.owner)

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

def _store_oauth_token(code=None, state=None):
	if not code:
		return {'FAIL': 'You did not authorized the request'}
	from programmer.data_tools import get_uri_parsed

	data = json.loads(frappe.db.get_temp(state))
	service = data['service']
	user = data['user']
	filters = [
		["APP Token User", "parent", "=", service],
		["APP Token User", "user", "=", user]
	]
	doc = frappe.get_doc("APP Token", service)

	replacers = {
		"auth_token": code
	}

	oserv = get_oauth_service(doc)
	data = traverse_params(doc.session_data_params, replacements=replacers)
	
	response = oserv.get_raw_access_token(data=data).json()

	dl = frappe.get_all("APP Token User", fields=["name", "app_user_id"], filters=filters)

	if dl:
		user_token_name = dl[0].name
		d = frappe.get_doc("APP Token User", user_token_name)
		d.update({
			"auth_token": response["access_token"],
			"expires_in": response["expires_in"],
			"refresh_token": response["refresh_token"]
		})
		d.save()
	else:
		d = frappe.new_doc("APP Token User")
		d.update({
			"parent": service,
			"parenttype": "APP Token",
			"parentfield": "authenticated_users",
			"user": user,
			"auth_token": response["access_token"],
			"expires_in": response["expires_in"],
			"refresh_token": response["refresh_token"]
		})
		d.save()
		user_token_name = d.name

	frappe.db.commit()

	if dl and (not dl[0].app_user_id) and data.has_key("parser") and data.has_key("endpoint") and all([data["parser"], data["endpoint"]]):
		app_user_id = get_uri_parsed(service, data["endpoint"], data["parser"], user=user, code=code)
	else:
		app_user_id = None

		if app_user_id and (not dl[0].app_user_id):
			frappe.db.set_value("APP Token User", user_token_name, "app_user_id", app_user_id)
			frappe.db.commit()

	return {'OK': frappe._('Authorization Code Stored'), 'autorized': response}

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
	frappe.db.set_value("APP Token User", dl[0].name, "auth_token", "")
	frappe.db.commit()

def refresh_oauth_token(service, user=None):
	if not user:
		user = frape.get_user().name

	filters = [
		["APP Token User", "parent", "=", service],
		["APP Token User", "user", "=", user]
	]
	dl = frappe.get_all("APP Token User", fields=["name"], filters=filters)
	if dl and dl[0].name:
		d = frappe.get_doc("APP Token User", dl[0]["name"])
	doc = frappe.get_doc("APP Token", service)
	data = {
		'refresh_token': d.refresh_token,
		'grant_type': 'refresh_token'
	}
	osrv = get_oauth_service(doc)
	response = osrv.get_raw_access_token(data=data).json()
	d.update({
		"auth_token": response["access_token"],
		"expires_in": response["expires_in"],
		"refresh_token": response["refresh_token"]	
	})
	d.save()
	frappe.db.commit()
	return response["access_token"]

def get_oauth_session(service, user=None):
	from time import time

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
	elif dl[0].expires_in and (dl[0].expires_in - current) <= 0:
		auth_token = refresh_oauth_token(service, user)
	else:
		auth_token = dl[0].auth_token

	doc = frappe.get_doc("APP Token", service)	
	oserv = get_oauth_service(doc)
	session = oserv.get_session(auth_token)

	return session
	
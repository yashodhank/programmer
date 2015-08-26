#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import frappe
import json


from time import time
from collections import defaultdict
from rauth import OAuth2Service
import requests
import requests.auth
from base64 import b64encode
from .core import get_headers_data, get_request_data, get_session_data

class APITokenError(frappe.ValidationError):
	pass

def get_oauth_service(service):
	""" Returns the OAuth2Service instance """
	fields = frappe.db.get_values(
		"APP Token",
		service,
		["name", "client_id", "client_secret", "authorize_url", "access_token_url", "base_url"],
	as_dict=True)[0]
	return OAuth2Service(**fields)

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

	data = get_request_data(service, {'state': state})
	flow = get_oauth_service(service)
	url = flow.get_authorize_url(**data)

	msg = '''
	Visit <a class="btn btn-xs btn-default" href="{url}" target="_blank">this link</a> for autorize <b>{service}</b>.
	'''.format(url=url, service=service)

	frappe.flags.roolback_on_exceptions = False
	frappe.throw(msg, APITokenError)

def _store_oauth_token(code=None, state=None):
	if not code:
		return {"FAIL": frappe._("You did not authorized the request")}

	try:
		raw = json.loads(frappe.db.get_temp(state))
		user = raw["user"]
		service = raw["service"]
	except TypeError:
		return {"FAIL": frappe._("The given data don't match with a JSON data")}
	except KeyError :
		return {"FAIL": frappe._("The given status don't match with the status provided")}

	replacements = frappe.db.get_values("APP Token", service, fieldname=["client_id", "client_secret"], as_dict=True)[0]
	replacements.update({
		"auth_token": code,
		"state": state
	})

	headers = get_headers_data(service, replacements)
	params = get_session_data(service, replacements)
	token_url, token_method, user_endpoint, user_parser = frappe.db.get_values("APP Token", service, 
		["access_token_url", "session_given_by", "api_user_endpoint", "user_id_parser"])[0]
	flow = get_oauth_service(service)

	if token_method == "Simple Session":
		session = requests.Session()
		session.auth = requests.auth.HTTPBasicAuth(flow.client_id, flow.client_secret)
		session.headers.update(headers)
		response = session.post(token_url, data=params)
		if response.status_code == 200:
			data = response.json()
			args = {
				"service": service,
				"token": data["access_token"],
				"user": user,
				"token_type": data["token_type"],
				"expires_in": data.get("expires_in", None)
			}
			if "scope" in data:	args["scopes"] = data["scope"]
			if "scopes" in data: args["scopes"] = data["scopes"]

			update_token(**args)
			return {'OK': frappe._("Token stored successfull")}
	return {"method": "POST", "params": params, "raw_response": response.json(), "url":response.url, "status": response.status_code, 'e': e.message}
		
def update_token(service, token="", user=None, expires_in=-1, refresh=None, scopes=None, token_type=None):
	user = get_user(user)
	dl = frappe.get_all("APP Token User", fields=["name", "auth_token"], filters=[
		["APP Token User", "user", "=", user],
		["APP Token User", "parent", "=", service]
	])
	if dl:
		doc = frappe.get_doc("APP Token User", dl[0]["name"])
	else:
		doc = frappe.new_doc("APP Token User")
	data = {
	    "parent": service,
	    "parenttype": "APP Token",
	    "parentfield": "authenticated_users",
		"user": user,
		"auth_token": token,
		"expires_in": expires_in,
		"refresh_token": refresh,
		"scopes": scopes,
		"token_type": token_type
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

@frappe.whitelist()
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

	session_provider = frappe.db.get_value("APP Token", service, "session_given_by")	
	flow = get_oauth_service(service)
	
	headers = get_headers_data(service, {'auth_token': auth_token, 'client_id': flow.client_id, 'client_secret': flow.client_secret})

	if session_provider == "Simple Session":
		session = requests.Session()
		session.auth = requests.auth.HTTPBasicAuth(flow.client_id, flow.client_secret)
		session.headers.update(headers)

	return session
	
@frappe.whitelist()
def do_request(service, method, endpoint, **params):
	session = get_oauth_session(service)
	fn = getattr(session, method.lower())
	response = fn(endpoint, params=params)
	return response.json()
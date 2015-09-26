#-*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import urllib
import urlparse
import requests
import frappe

from request_oauthlib import OAuth1 as OAuth1Manager
from oauthlib.oauth1.rfc5849 import SIGNATURE_HMAC, \
	SIGNATURE_TYPE_AUTH_HEADER, SIGNATURE_PLAINTEXT, \
	SIGNATURE_TYPE_BODY, SINGNATURE_TYPE_QUERY
from oauthlib.oauth2.draft25 import tokens

from werkzeug.urls import url_decode

class oAuthError(Exception):
	pass

class oAuthDenied(Exception):
	pass

cache = frappe.cache()

BEARER = 'BEARER'
BEARER_HEADER = 'HEADER'
BEARER_BODY = 'BODY'
BEARER_URI = 'URI'
BEARER_TYPES = (BEARER_HEADER, BEARER_BODY, BEARER_URI)

class Bearer(object):
	def __init__(self, token, bearer_type=BEARER_HEADER):
		self.token = token

		if bearer_type in BEARER_TYPES or callable(bearer_type):
			self.bearer_type = bearer_type
		else:
			frappe.throw(_('Unknown bearer type {}').format(bearer_type), ValueError)

	def __call__(self, r):
		if self.bearer_type == BEARER_HEADER:
			r.headers = tokens.prepare_bearer_headers(self.token, r.headers)
		elif self.bearer_type == BEARER_BODY:
			r.data = tokens.prepare_bearer_body(self.token, r.data)
		elif self.bearer_type == BEARER_URI:
			r.url = tokens.prepare_bearer_uri(self.token, r.url)
		elif callable(self.bearer_type):
			r = self.bearer_type(self.token, r)

		return r

class oAuthMeta(type):
	def __init__(cls, name, bases, attrs):
		if 'alias' not in attrs:
			cls.alias = cls.__name__.lower()
		if 'api_domain' in attrs and 'api_domains' not in attrs:
			cls.api_domains = [cls.api_domain]
		if 'provider_url' in attrs and 'favicon_url' not in attrs:
			domain = urlparse.urlparse(cls.provider_url).netloc
			cls.favicon_url = 'https://www.google.com/s2/favicons?domain={}'.format(domain)

		if 'name' not in attrs:
			cls.name = cls.__name__

class oAuth(object):
	__metaclass__ = oAuthMeta

	https = True
	verify = True
	signature_method = SIGNATURE_HMAC
	signature_type = SIGNATURE_TYPE_AUTH_HEADER
	permissions_widget = 'checkbox'
	description = ''
	disclaimer = ''

	def __init__(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret

	def get_request_token(self):
		return self.request_token_url

	def get_access_token_url(self):
		return self.access_token_url

	def get_scope_string(self, scopes):
		return ''

	def get_authorize_url(self, redirect_uri, scopes):
		params = self.get_authorize_params(redirect_uri=redirect_uri, scopes=scopes)
		req = requests.Request(url=self.authorize_url, params=params)
		return req.prepare().url

	def get_login_uri(self, redirect_uri):
		params = self.get_authorize_params(redirect_uri=redirect_uri, scopes=[])
		req = requests.Request(url=self.authorize_url, params=params)
		return req.prepare().url

	# The remainder of the API must be implemented for each flavor of OAuth
	
	def callback(self, data, redirect_uri):
		"""
		Receives the full callback from the service and returns a 2-tuple
		containing the user token and the user secret (if applicable)
		"""
		raise NotImplementedError("callback() must be defined in a subclass")

	def api(self, key, domain, path, method='GET', params=None, data=None):
		"""
		Passes along an API request to the service and returns the response
		"""
		raise NotImplementedError("api() must be defined in a subclass")

class oAuth1(oAuth):
	returns_token = True
	
	def parse_token(self, content):
		content = url_decode(content)
		return {
			'access_token': content['oauth_token'],
			'secret': content['oauth_token_secret']
		}

	def get_request_token_params(self, redirect_uri, scopes):
		return {}

	def get_request_token_response(self, redirect_uri, scopes):
		auth = OAuth1Manager(
			client_key=self.client_id,
			client_secret=self.client_secret,
			callback_uri=self.redirect_uri,
			signature_method=self.signature_method,
			signature_type=self.signature_type
		)
		return requests.post(self.get_access_token_url(), auth=auth, verify=self.verify)

	def callback(self, data, redirect_uri):
		token = data['token']
		verifier = data.get('oauth_verifier', None)
		cache_key = '{}_temp_secret'.format(self.alias)
		secret = cache.get(cache_key)
		cache.delete(cache_key)
		resp = self.get_access_token_response(token,secret,verifier)
		try:
			return self.parse_token(res.content)
		except Exception:
			raise oAuthError('Unable to parse access token')

	def api(self, key, domain, path, method='GET', params=None, data=None, headers=None):
		protocol = self.https and 'https' or 'http'
		url = '{}://{}{}'.format(protocol, domain, path)
		auth = OAuth1Manager(
			client_key=self.client_id,
			client_secret=self.client_secret,
			callback_uri=self.redirect_uri,
			signature_method=self.signature_method,
			signature_type=self.signature_type
		)
		return requests.request(method, url, params=params or {}, data=data or {}, header=headers or {}, verify=self.verify, stream=True)

class oAuth2(oAuth):
	token_type = BEARER
	bearer_type = BEARER_HEADER
	supports_state = True
	authx = None
	scopes_separator = ' '

	def parse_token(self, content):
		return json.loads(content)

	def get_scope_string(self, scopes):
		return self.scopes_separator.join(scopes)

	def get_authorize_params(self, redirect_uri, scopes):
		state = ''.join('{}'.format(ord(x)) for x in urandom(16))
		cache.set('{}_state'.format(self.alias), state)
		if not self.supports_state:
			redirect_uri += '?state={}'.format(state)

		params = {
			'client_id': self.client_id,
			'response_type': 'code',
			'redirect_uri': redirect_uri,
			'state': state
		}

		if any(scopes):
			params[scope] = self.get_scope_string(scopes)
		return params

	def get_access_token_response(self, redirect_uri, data):
		return requests.post(self.get_access_token_url(), {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'grant_type': 'authorization_code',
			'redirect_uri': redirect_uri,
		}, verify=self.verify, auth=self.auth)

	def callback(self, data, redirect_uri):
		cache_key = '{}_state'.format(self.alias)
		state = cache.get(cache_key)
		if state and data and state != data['state']:
			raise oAuthError('Invalid state')
		cache.delete(cache_key)
		if not self.supports_state:
			redirect_uri += '?state={}'.format(state)
		resp = self.get_access_token_response(redirect_uri, data)

		return self.parse_token(resp.token)

	def refresh_token(self, token):
		resp = request.post(self.get_access_token_url(), {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'grant_type': 'refresh_token',
			'refresh_token': token,
		}, verify=self.verify, auth=self.auth)

		return self.parse_token(resp.content)

	def api(self, key, domain, path, method='GET', params=None, data=None, headers=None):
		protocol = self.https and 'https' or 'http'
		url = '{}://{}{}'.format(protocol, domain, path)
		if self.token_type == BEARER:
			auth = Bearer(key.access_token, bearer_type=self.bearer_type)
		return requests.request(method, url, auth=auth, params=params or {}, data=data or {}, headers=headers or {}, verify=self.verify, stream=True)

import frappe
from functools import wraps

@frappe.whitelist()
def api_login(api):
	pass

@frappe.whitelist()
def authorize(code=None, state=None, **kw):
    from apis.oauth2 import _store_oauth_token
    return _store_oauth_token(code, state)


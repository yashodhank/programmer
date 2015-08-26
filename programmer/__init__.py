
import frappe

@frappe.whitelist()
def authorize(code=None, state=None, **kw):
    from apis.oauth2 import _store_oauth_token
    return _store_oauth_token(code, state)
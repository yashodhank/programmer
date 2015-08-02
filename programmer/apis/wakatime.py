
from __future__ import unicode_literals
import frappe
import .core

def get_session():
    settings = frappe.get_doc("Code Project Settings")
    api_token = settings.wakatime_api_token
    secret_key = settings.wakatime_secret_key

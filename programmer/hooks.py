# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "programmer"
app_title = "programmer"
app_publisher = "MaxMorais"
app_description = "ERPNext Projects for ERPNext programmers"
app_icon = "octicon octicon-octoface"
app_color = "grey"
app_email = "max.morais.dmm@gmail.com"
app_version = "0.0.1"

required_apps = [
    "frappe",
    "erpnext"
]

fixtures = [
    "API",
    "API Template"
]
    
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/programmer/css/programmer.css"
# app_include_js = "/assets/programmer/js/programmer.js"

# include js, css files in header of web template
# web_include_css = "/assets/programmer/css/programmer.css"
# web_include_js = "/assets/programmer/js/programmer.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "programmer.install.before_install"
# after_install = "programmer.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "programmer.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"programmer.tasks.all"
# 	],
# 	"daily": [
# 		"programmer.tasks.daily"
# 	],
# 	"hourly": [
# 		"programmer.tasks.hourly"
# 	],
# 	"weekly": [
# 		"programmer.tasks.weekly"
# 	]
# 	"monthly": [
# 		"programmer.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "programmer.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "programmer.event.get_events"
# }


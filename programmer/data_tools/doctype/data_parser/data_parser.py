# -*- coding: utf-8 -*-
# Copyright (c) 2015, MaxMorais and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.utils
from frappe.model.document import Document
from frappe.model import display_fieldtypes
from programmer.jsonpath import jsonpath

class DataParser(Document):
	pass

@frappe.whitelist()
def get_fields(doctype):
    table_fields = frappe.get_all("DocField", fields=["options", "fieldname"], filters=[
        ["DocField", "fieldtype", "=", "Table"],
        ["DocField", "parent", "=", doctype]
    ])
    table_fields = dict([(t.fieldname, t.options) for t in table_fields])

    doc_fields = frappe.get_all("DocField", fields=["label", "fieldname", "fieldtype", "parent", "options", "reqd"], filters=[
        ["DocField", "parent", "in", list(set(table_fields.values()+[doctype]))],
        ["DocField", "fieldtype", "not in", display_fieldtypes]
    ])

    res = []
    pop = ["fieldname", "options"] 

    for f in filter(lambda x: x.parent==doctype and x.fieldtype != "Table", doc_fields):
        fcopy = f.copy()
        fcopy.name = "{parent}.{fieldname}".format(**f)
        map(fcopy.pop, pop)
        res.append(fcopy)
    for b in filter(lambda x: x.parent==doctype and x.fieldtype == "Table", doc_fields):
        for f in filter(lambda x: x.parent==b.options, doc_fields):
            fcopy = f.copy()
            fcopy.name = "{doctype}.{field}.{parent}.{fieldname}".format(
                doctype=doctype,
                field=b.fieldname,
                parent=f.parent,
                fieldname=f.fieldname
            )
            fcopy.parent_label = b.label or b.parent
            map(fcopy.pop, pop)
            res.append(fcopy)

    return res

def is_list(x):
    return isinstance(x, (list, tuple, set))

def _cast_data(cast, data, fieldtype):
    fake_field = frappe._dict(fieldtype=fieldtype)
    return cast(data, fake_field)

def _get_data_from_json(data, parsers, cast, parent=None):
    if len(parsers) == 1:
        ret = jsonpath(data, parsers[0].path)
        if parsers[0].first:
            ret = ret[0]
        return _cast_data(cast, ret, parsers[0].formatter)
    for parser in parsers:
        parsed = jsonpath(data, parser.path)
        if is_list(x):
            field = parser.target_field
            if field.count(".") == 1 and is_list(parsed):
                ret[parser.target_field] = jsonpath(data, parser.path)[0]

def _get_data_from_xml(data, parsers):
    pass

def _get_parsed_data(data, parsers, data_format, cast):
    if data_format == "JSON":
        return _get_data_from_json(data, parsers, cast)
    if data_format == "XML":
        return _get_data_from_xml(data, parsers, cast)

def get_uri_parsed(app_name, uri, parser, user=None, code=None):
    from programmer.apis.core import get_session

    session = get_session(app_name, user=user, code=code)
    parser = frappe.get_doc("Data Parser", parser)
    cast = parser.cast
    request = session.get(uri)
    if not request:
        raise RuntimeError("Request can't be created")
    if parser.data_format == "JSON":
        raw_data = request.json()
    elif parser.data_format == "XML":
        raw_data = request.xml()
    data = _get_parsed_data(raw_data, parser.data_bind, parser.data_format, cast)
    return data

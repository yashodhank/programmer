frappe.require("assets/programmer/3rd-party/json-view/jquery.jsonview.css");
frappe.require("assets/programmer/3rd-party/json-view/jquery.jsonview.js");

cur_frm.add_fetch("app_token", "api_user_endpoint", "base_url");

cur_frm.cscript.refresh = function(doc, cdt, cdn){
    if (!doc.__islocal){
        cur_frm.add_custom_button(__("Make a Test Request"), cur_frm.cscript["Make a Test Request"])
    }
}

cur_frm.cscript["Make a Test Request"] = function(){
    var fields = [],
        dataMap = {
            "String": "Data",
            "Bool": "Check",
            "Long": "Int"
        },
        d;
    if (cur_frm.doc.repls && cur_frm.doc.repls.length){
        fields.push({"fieldtype": "Column Break", label: __("Replacements")})
    }
    cur_frm.doc.repls.forEach(function(row){
        fields.push({
            label: row.key.replace(":","").replace("_", " ").replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();}),
            fieldname: row.key,
            fieldtype: (row.value || "").split('\n').length > 1 ? "Select" : "Data",
            reqd: row.default_option ? false: true,
            "default": row.default_option,
            options: row.value
        })
    })
    fields.push({"fieldtype": "Column Break", label: __("Parameters")})
    cur_frm.doc.params.forEach(function(row){
        fields.push({
            label: row.parameter.replace("_", " ").replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();}),
            fieldname: row.parameter,
            fieldtype: dataMap.hasOwnProperty(row.datatype) ? dataMap[row.datatype] : row.datatype,
            reqd: row.reqd,
            description: row.helper,
            'default': row['default']
        });
    });
    fields.push({
        "fieldtype": "Section Break", "label": __("Request Result")
    });
    fields.push({
        "fieldtype": "HTML", "fildname": "result", "options": "<div id='json'></div>"
    });

    d = new frappe.ui.Dialog({
        fields: fields,
         title: __("Test Endpoint"),
    })
    d.set_primary_action("Test", function(){
        var values = d.get_values();
        values["service"] = cur_frm.doc.app_token;  
        values["endpoint"] = cur_frm.doc.endpoint;
        values["method"] = cur_frm.doc.http_method;
        frappe.call({
            "method": "programmer.apis.oauth2.do_request",
            "args": values,
            "callback": function(res){
                debugger;
                $('#json').JSONView(res.message);
            }
        })
    })
    d.show();
}
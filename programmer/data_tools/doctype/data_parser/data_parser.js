frappe.ui.form.on("Data Parser", "refresh", function(frm){
    cur_frm.cscript.fields = {};
    frm.set_df_property('help_html', 'options', frappe.render_template("data_parser_help",{}));
    if (!frm.doc.__islocal){
        frappe.ui.form.trigger("Data Parser", "target_doctype");
    }
});

frappe.ui.form.on("Data Parser", "data_bind_add", function(){
    console.log(arguments);
});

frappe.ui.form.on("Data Parser", "target_doctype", function(frm){
    function sorter(a,b){
        if (a.label > b.label){
            return 1;
        } else if (a.label < b.label){
            return -1
        } 
        return 0;
    }
    frappe.call({
        "method": "programmer.data_tools.doctype.data_parser.data_parser.get_fields",
        "args": {
            "doctype": frm.doc.target_doctype,
        },
        "callback": function(res){
            if (!res.message) return;
            var row, options = [];
            for (var i = 0, j=res.message.length; i < j; i++){
                row = res.message[i];
                cur_frm.cscript.fields[row.name] = row.fieldtype;
                if (!row.parent_label){
                    options.push({
                        label: __(row.label) + (row.reqd ? " *": ""),
                        value: row.name
                    });
                } else {
                    options.push({
                        label: format("{0} [{1}]{2}", [__(row.parent_label), __(row.label), row.reqd ? " *": ""]),
                        value: row.name
                    });
                }
            }
            console.table(res.message);
            frm.set_df_property("target_field", "options", [""].concat(options), null, "data_bind");
            refresh_field("target_field", null, "data_bind");
        }
    });
});

frappe.ui.form.on("Data Bind", "target_field", function(frm, cdt, cdn){
    var doc = locals[cdt][cdn],
    formatter = cur_frm.cscript.fields[doc.target_field];
    frappe.model.set_value(
        doc.doctype,
        doc.name,
        "formatter",
        formatter
    );
    frm.set_df_property("formatter", "reqd", in_list(["Currency", "Date", "Datetime", "Time"], frm));
    refresh_field("target_field", null, "data_bind");
})
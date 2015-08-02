frappe.ui.form.on('Code Project Settings', 'use_wakatime', function(frm, cdt, cdn){
    cur_frm.toggle_reqd('wakatime_api_token', frm.doc.use_wakatime);
});
frappe.ui.form.on('API Bot Template', {
    'onload': function(frm){
        frappe.meta.get_docfield('API Template Parameters', 'default_value').on_make = function(field){
            if (!field.doc.link) return;
            field.$input.addClass('ui-front');
            field.$input.autocomplete({
                minLength: 0,
                minChars: 0,
                source: function(request, response){
                    frappe.call({
                        'method': 'frappe.client.get_list',
                        'args': {
                            'doctype': ''
                        }
                    })
                }
            })
        }
    }
})
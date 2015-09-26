cur_frm.cscript.make_http_selector = function(field){
    var prepend = $(format('<div class="input-group-addon http">{0}</div>', [cur_frm.doc.https?'HTTPS://':'HTTP://'])).css({'cursor': 'pointer'}).on('click', function(event){
        event.preventDefault();
        event.target.innerText = event.target.innerText ==='HTTP://' ? 'HTTPS://' : 'HTTP://';
        cur_frm.set_value('https', event.target.innerText==='HTTPS://');
        $('div.http').text(cur_frm.doc.https ? 'HTTPS://' : 'HTTP://');
    });
    field.$input.parent().addClass('input-group').prepend(prepend);
};

cur_frm.cscript.make_parameter_selector = function(field){
    var options = JSON.parse(field.doc.accepts_parameters ||'[]'),
        lis = options.map(function(tag){
            return format('<li>{0}</li>', [tag]);
        }).join('\n'),
        initialized = false;
    field.$tags = $(format('<ul class="input-with-feedback form-control">{0}</ul>', [lis])).tagit({
        animate: false,
        allowSpaces: false,
        placeholderText: __('Add a parameter') + '...',
        onTagAdded: function(ev, tag){
            if (initialized && !field.$tags.refreshing){
                var tag = tag.find('.tagit-label').text().toLowerCase(),
                    parameters = JSON.parse((field.doc.accepts_parameters || '[]'));
                if (parameters.indexOf(tag)===-1){
                    parameters.push(tag);
                }
                field.doc.accepts_parameters = JSON.stringify(parameters);
            }
        },
        onTagRemoved: function(ev, tag){
            if (!field.$tags.refreshing){
                var tag = tag.find('.tagit-label').text().toLowerCase(),
                    parameters = JSON.parse(field.doc.accepts_parameters||'');
                if (parameters.indexOf(tag)>-1){
                    parameters.splice(parameters.indexOf(tag), 1);
                }
                field.doc.accepts_parameters = JSON.stringify(parameters);
            }
        },
        onTagClicked: function(val, tag){
            tag = tag.tag.find('.tagit-label').text();
            field.$tags.refreshing = true;
            var html = '<ul class="options nav nav-pills nav-stacked"></ul>',
                fields = [],
                options = JSON.parse(field.doc.acceptable_values || '{}'),
                d;
            function append_option(k, target){
                $(format('<li><span class="label label-danger" data-option="{0}"><a>x</a></span> <span class="label">{0}</span></li>', [k])).appendTo(target);             
            }
            (options[tag]||[]).forEach(function(k){
                append_option(k, html);
            });
            fields = [
                {
                    fieldtype: 'HTML',
                    options: html,
                },
                {
                    fieldtype: 'Section Break',
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'allowed_value',
                    label: __('Allowed Value'),
                    reqd: true
                },
                {
                    fieldtype: 'Button',
                    fieldname: 'btn_append',
                    label: __('Append')
                }
            ];
            d = new frappe.ui.Dialog({'fields': fields, 'title': format(__('Add allowed values for {0}'), [tag])});
            d.fields_dict.btn_append.$input.on('click', function(evt){
                var val = d.get_value('allowed_value');
                if (val){
                    append_option(val, $('ul.options'));
                    if (!options.hasOwnProperty(tag)) options[tag] = [];
                    options[tag].push(val);
                    field.doc.acceptable_values = JSON.stringify(options);
                    d.set_value('allowed_value', null);
                }
            });
            d.set_primary_action(__('Save'), function(){
                var values = d.get_values();
                if (!values) return;
                d.hide();
            });
            d.show();
            field.$tags.refreshing = false; 
        },
        preprocessTag: function(val){
            if (!val || !val.length) return;
            return val.toLowerCase().replace('-', '_');
        }
    });
    initialized = true;
    field.$input.addClass('hide').parent().prepend(field.$tags);
    var refresh = field.refresh;
    field.refresh = function(){
        refresh(field);
        console.log('refreshing');
        var tag = field.$input.$tags;
        if (!tag.initialized || tag.refreshing) return;
        tag.refreshing = true;
        try {
            tag.tagit('removeAll');
        } catch (e){
            tag.refreshing = false
        }
        me.refreshing = false;
    }
};

cur_frm.cscript['Activate API'] = function(){
    var fields = [],
        favicon = 'https://www.google.com/s2/favicons?domain='+frm.doc.provider_url,
        title,
        d;

    frm.doc.parameters.forEach(function(param){
        if (param.ctx === "Class" && !param.value){
            fields.push({
                fieldtype: "Data",
                reqd: true,
                fieldname: param.parameter,
                label: param.parameter.replace('_', " ").replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();})
            });
        } else if (param.ctx === "Class" && param.parameter==="favicon_url"){
            favicon = param.value;
        }
    });
    title = format('<b><img src="{0}"/> {1} {2} API {3} Info</b>', [favicon, frm.doc.api_name, frm.doc.api_type, frm.doc.api_auth_method]);
    d = frappe.prompt(
        fields, 
        function(values){
            var childs = frappe.utils.filter_dicts({
                'parameter': ["in", values.keys()]
            }).forEach(function(child){
                child.value = values[child.parameter];
            });
            frm.set_value('active', true);
            frm.save();
        },
        title,
        format(__('Activate {0} API'), [frm.doc.api_name])
    );    
};

cur_frm.cscript['Deactivate API'] = function(){}

frappe.ui.form.on('API', {
    onload: function(frm){
        ['provider_url', 'api_domain'].forEach(function(field){
            frappe.meta.get_docfield(frm.doctype, field).on_make = frm.cscript.make_http_selector;
        });
        var fld = frappe.meta.get_docfield('API Method', 'accepts_parameters')
        fld.on_make =  frm.cscript.make_parameter_selector;
        fld.on_refresh = function(){
            console.log(arguments);
            console.log("Awesome ?");
        }
    },
    refresh: function(frm){
        $('div.http').text(cur_frm.doc.https ? 'HTTPS://' : 'HTTP://');
        if (!frm.doc.__islocal && !frm.doc.active){
            frm.add_custom_button(__("Activate"), cur_frm.cscript['Activate API']);
        } else if (!frm.doc.__islocal && frm.doc.active){
            frm.set_custom_button(__('Deactivate'), function(){
                frm.set_value('active', false);
                frm.save();
            });
        }
    },
    provider_url: function(frm){
        if (frm.doc.provider_url) cur_frm.set_value('api_domain', 'api.'+frm.doc.provider_url.replace('www.','').split('/')[0]);
    },
    api_type: function(frm){
        if (frm.doc.api_type){
            frappe.call({
                'method': "frappe.client.get_list",
                'args': {
                    'doctype': 'API Template',
                    'filters': [
                        ["api_type", "=", cur_frm.doc.api_type]
                    ],
                    'fields': ['api_auth_method']
                },
                'callback': function(r){
                    cur_frm.set_df_property('api_auth_method', 'options', $.unique($.map(r.message, function(d){return d.api_auth_method})).join("\n"));
                }
            });
        }
    },
    api_auth_method: function(frm){
        var child;
        if (frm.doc.api_auth_method){
            frappe.call({
                'method': "frappe.client.get",
                'args': {
                    'doctype': 'API Template',
                    "filters": {
                        "api_type": frm.doc.api_type,
                        "api_auth_method": frm.doc.api_auth_method
                    }
                },
                'callback': function(r){
                    frappe.model.clear_table(cur_frm.doc, 'parameters');
                    r.message.parameters.forEach(function(row){
                        child = frappe.model.add_child(cur_frm.doc, 'API Parameters', 'parameters');
                        child.ctx = row.ctx;
                        child.parameter = row.parameter;
                        child.value = row.dflt;
                        cur_frm.refresh_field('parameters');
                    });
                    child = frappe.model.add_child(cur_frm.doc, 'API Parameters', 'parameters');
                    child.ctx = 'Class';
                    child.parameter = 'redirect_uri';
                    child.value = window.location.origin + 'api/method/programmer.authorize'
                    cur_frm.refresh_field('parameters');
                }
            });
        }
    }
});

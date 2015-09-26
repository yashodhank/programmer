frappe.provide('programmer');
frappe.provide('programmer.widgets.API')
programmer.widgets.API.StatusToggler = Class({
    init: function(api, status){
        this.api = api;
        this.status = status;
    },
    make: function(){
        var self = this;
        if (this.status === 'activate'){
            frappe.call({
                'method': 'programmer.programmer.doctype.api.api.get_dialog_details',
                'args': {
                    'name': this.api
                },
                'callback': function(res){
                    if (res.exc) throw new Error(res.exc);
                    self.dialog = frappe.prompt({
                        res.message.fields,
                        self.action,
                        res.message.title,
                        format(__('Activate {0} API'), self.api)
                    });
                }
            });
        }
    },
    action: function(values){
        
    }
});
programmer.widgets.API.Authorize = Class({
    init: function(api, options){
        this.api = api;
        $.extend(this, options);
        this.make();
    },
    make: function(){
        this.make_dialog()
    },
    make_dialog: function(){
        $.ajax({
            url: "/api/resource/API/"+this.api,
            data: {
                fields:'*'
            },
            success: function(data){
                console.log(data);
                if (!data.data.length){

                }
            }
        });
    }
}),
$( document ).ready(function()
{
openerp.spc_bureau_ordre = function (instance, local)
{
    var self = this;//window
    var QWeb = instance.web.qweb;
    var FormView = instance.web.FormView;
    var vars = {};
    var parts = window.location.href.replace(/[?&#]+([^=&]+[^#])=([^&]*)/gi, function(m,key,value) {
              vars[key] = value;
            });
    console.log('parts..................',parts,'....vars-',vars);
    if (vars.model) {
        var model = vars.model;
    }
    console.log('model..................',model);
//    else model
//
//    console.log('MODEL..................',model);


//    var model = new instance.web.Model("cci.courrier.entrant");

    FormView.include({
        button_clicked_mass: function() {
            console.log('button_clicked_mass...........',this);

            //get type
            new instance.web.Model("type.courrier.entrant")
            .query(['name'])
            .all()
            .then(function (result)
            {
                var documenttypes = "";
                    var i = 0;
                    for(i in result) {


                        documenttypes += result[i]['id'] + ":" + result[i]['name'] +';';

                        }
                console.log('documenttypes:',documenttypes);
                var session = new openerp.Session();
                var vars_mass = {};


                //get identity
                var parts_mass = window.location.href.replace(/[?&#]+([^=&]+[^#])=([^&]*)/gi, function(m,key,value) {
                    vars_mass[key] = value;
                });
                 //get model_id
                 //get id
                if (vars_mass.id)
                {
                     var idEntity = vars_mass.id;

                }
                console.log('......idEntity..........',idEntity);
                if (vars_mass.model)
                {
                     var typeEntity = vars_mass.model;

                }

                console.log('......typeEntity..........',typeEntity);
                //get session_id
                var sid = document.cookie.match('session_id=([^;]*)')[1];

                console.log('......sid..........',sid);
                window.location.href="isante-scan://?type=bulk-test&appUrl=127.0.0.1&port=8069&http-port=8862&session="+sid+"&documenttypes="+documenttypes+"&idEntity="+idEntity+"&typeEntity="+typeEntity;
                console.log('....OK..');

            });
        },

        button_clicked: function()
        {
        console.log('button_clicked...........',this);
            var session = new openerp.Session();
            var vars = {};


            //get identity
            var parts = window.location.href.replace(/[?&#]+([^=&]+[^#])=([^&]*)/gi, function(m,key,value) {
                vars[key] = value;
            });

            if (vars.id)
                {
                    var idEntity = vars.id;

                }
                console.log('......idEntity..........',idEntity);
                if (vars.model)
                {
                    var typeEntity = vars.model;
                }
                console.log('......typeEntity..........',typeEntity);
            console.log('go on and get the session...........');
            //get session_id
            var sid = document.cookie.match('session_id=([^;]*)')[1];
            //get model_id
            console.log('model...........',model);
            if (model){

                        new instance.web.Model('ir.model')
            .query(['id'])
            .filter([['model', '=', model]])
            .all()
            .then(function (result_nature)
            {
                console.log('result_nature:',result_nature);
                nature = result_nature[0]['id'];
                 console.log('......nature..........',nature);
                //call scan app
                window.location.href="isante-scan://?type=test&appUrl=127.0.0.1&port=8069&http-port=8862&session="+sid+"&idEntity="+idEntity+"&nature="+nature+"&typeEntity="+typeEntity;
            });
            }



        },

        load_record: function(record)
        {
                this._super.apply(this, arguments);
                console.log('this...........',this);
                console.log('Début : this.model............',this.model);

                if (this.model=='courrier.entrant' && this.$el.find('button.oe_button.oe_form_button.class')){
                    console.log('SCAN NORMAL');
                    this.$el.find('button.oe_button.oe_form_button.class').click(this.button_clicked);
                }
                if (this.model=='courrier.entrant' && this.$el.find('button.oe_button.oe_form_button.your_class_mass')){
                    console.log('SCAN EN MASSE');
                    this.$el.find('button.oe_button.oe_form_button.your_class_mass').click(this.button_clicked_mass);
                }
                if (this.model=='courrier.sortant'){
                    this.$el.find('button.oe_button.oe_form_button.your_class_mass').click(this.button_clicked_mass);
                    this.$el.find('button.oe_button.oe_form_button.class').click(this.button_clicked);
                }

        }
        })
}
});
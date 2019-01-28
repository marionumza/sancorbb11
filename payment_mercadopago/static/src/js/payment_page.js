odoo.define('payment_mercadopago.mercadopago_payment',function(require){
    "use_strict";

    var core = require('web.core');
//	var session = require('web.session');
	var ajax = require('web.ajax');
//	var Users = new Model('res.users');
//	var company = new Model('res.company');
//	var framework = require('web.framework');
//
//	var _t = core._t;
	var QWeb = core.qweb;

    $(document).ready(function (){
        console.log("Ready on load");
//        console.log(this);
//        console.log($('.mp_form'));
        var mpForm = $('#mp_form').html();
        var conceptName = ""

        $('select[name=payment_method]').on('change',function(e) {
            e.preventDefault();

            var checked_radio = $('input[type="radio"]:checked');
            var partner_id = $('.o_payment_form').data('partner-id')
            var csrf_token = $("input[name=csrf_token]").val()
            if (checked_radio.data('acquirer-id')){
                var acquirer_id = checked_radio.data('acquirer-id');
            }
            if (this.value == 'credit_debit') {
//                $('#mp_form').html('Hello');
//                var temp_mp;
//                var templ = ajax.jsonRpc('/web/dataset/call_kw', 'call', {
//                    model:  'payment.acquirer',
//                    method: 'get_s2s_form_xml_id',
//                    args: [acquirer_id],
//                    kwargs: {}
//                }).then(function(data){
//                    console.log(data)
//                    temp_mp = data
//
//                });
//                console.log("id : ",templ);

//                $('#mp_form').html(QWeb.render('payment_mercadopago.mercado_s2s_form', {'id' : acquirer_id, 'partner_id' :                          partner_id, 'return_url' : ''}));
                $('#mp_form').html(mpForm);
                $('#payment_type_bank').addClass('hidden');


//                $('#mp_form').html(QWeb.render('payment.acquirer('+acquirer_id+').sudo().get_s2s_form_xml_id()'));
//                alert("Allot Thai Gayo Bhai");
            }
            else if (this.value == 'cash') {
                $('#payment_type_bank').addClass('hidden');
                $('#mp_form').html('<input type="hidden" name="data_set" data-create-route="/payment/mercadopago/deposit"/>'+
                '<input type="hidden" name="partner_id" value='+partner_id+'></input>'+
                '<input type="hidden" name="acquirer_id" value='+acquirer_id+'></input>'+
                '<input type="hidden" name="payment_method" value='+this.value+'></input>'+
                '<input type="hidden" name="csrf_token" value='+csrf_token+'></input>');
//                alert("Transfer Thai Gayo");
            }
            else if (this.value == 'bank_transfer') {
                $('#payment_type_bank').removeClass('hidden');
//                var conceptName = $('#payment_type_bank').find(":selected").text();
                console.log(conceptName);
               $('#mp_form').html('<input type="hidden" name="data_set" data-create-route="/payment/mercadopago/deposit"/>'+
                '<input type="hidden" name="partner_id" value='+partner_id+'></input>'+
                '<input type="hidden" name="acquirer_id" value='+acquirer_id+'></input>'+
                '<input type="hidden" name="payment_method" value='+this.value+'></input>'+
                '<input type="hidden" name="payment_type_bank" value='+conceptName+'></input>'+
                '<input type="hidden" name="csrf_token" value='+csrf_token+'></input>');
//                 alert("Transfer Thai Gayo");
            }
        });

        $('select[name=payment_type_bank]').on('click', function(e) {
            e.preventDefault();
            console.log('>>>>>>',this.value);
            console.log('>>>>>>',$('select[name=payment_method]').val());
            conceptName = this.value;
            var checked_radio = $('input[type="radio"]:checked');
            var partner_id = $('.o_payment_form').data('partner-id');
            var csrf_token = $("input[name=csrf_token]").val();
            if (checked_radio.data('acquirer-id')){
                var acquirer_id = checked_radio.data('acquirer-id');
            }

            var mpForm = $('#mp_form').html();

            $('#mp_form').html('<input type="hidden" name="data_set" data-create-route="/payment/mercadopago/deposit"/>'+
            '<input type="hidden" name="partner_id" value='+partner_id+'></input>'+
            '<input type="hidden" name="acquirer_id" value='+acquirer_id+'></input>'+
            '<input type="hidden" name="payment_method" value='+$('select[name=payment_method]').val()+'></input>'+
            '<input type="hidden" name="payment_type_bank" value='+conceptName+'></input>'+
            '<input type="hidden" name="csrf_token" value='+csrf_token+'></input>');

        });

    });
})
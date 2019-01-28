
//console.log("COD custom js caleedddddddddddddddddddddddddddddddddd")
odoo.define('bi_website_cash_on_delivery.website_cod_payment', function(require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var flag = 0;

    var ajax = require('web.ajax');
    $(document).ready(function() {
	    var oe_website_sale = this;
	    //var $payment = $("#payment_method");
        var $payment = $("panel panel-default");
        var $carrier = $("#delivery_carrier");

        var payment_form = $('.o_payment_form');
        //$("input[data-provider ='cod']").attr('checked', 'checked');
        //var acquirer_id = payment_form.find('input[type="radio"][data-provider="stripe"]:checked').data('acquirer-id');
        //console.log('===============================================================',flag);

        /*payment_form.on("click", "input[name='pm_id']", function (ev) {
        var payment_id = payment_form.find("input[data-provider='cod']").data('acquirer-id');
        if (payment_form.find("input[data-provider='cod']")[0].checked == true){
                    var cod = $(this).is(':checked');
                    $payment.find("input[provider='cod']").prop("checked", true);
                        ajax.jsonRpc('/shop/payment/cod', 'call', {
					                'payment_id': payment_id,
				                }).then(function (order) {
				                    var x = 0;
				                    alert('Extra Fees will be Added for Cash on Delivery');
					                //localStorage.checked = true; //Once you select COD, After Reloading the Page, Still COD is Remain Selected...!!
					                //payment.find("input[provider='cod']").prop("checked", true);
					                
					                //console.log('ooooooooooooooooooooooooooooooo',order)
					                //$("input[provider='cod']").attr('checked', true);
					                //window.location.reload();
					                //payment.find("input[provider='cod']").prop("checked", true);
                        });
       }*/
       
       
       
       //$("input[data-provider='cod']").attr('checked', 'checked');
      /* else{
       		localStorage.checked = false;
       		//$payment.find("input[provider='cod']")[0].checked = false;
       		$payment.find("input[provider='cod']").prop("checked", false);
       }
       */
		
    //});
    });
        
});

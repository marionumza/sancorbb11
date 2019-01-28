odoo.define('payment_mercadopago.mercadopago',function(require){
    "use_strict";

//    var Model = require('web.Model');

    $(document).ready(function (){
        console.log("Ready on load");
        var flag = true
        var total = $('input[name="order_total"]').val();
        $('.mercadopago_cc_number').on('change',function(event){
            console.log('Change');
            flag = true
            guessingPaymentMethod(event);

        })

        $('.mercadopago_cc_number').on('keyup', function(event){
            console.log('Key-up', event);
            flag = true
            guessingPaymentMethod(event);
        })

        $('input[name="pm_id"]').on('change', function(event){
//            console.log("-----------")
            console.log("token val is : ",$('#token').val());
            if ($('#token').val() != null){
            if ($('#token').val().split(":")[0] != null){
//                console.log('call for guessing payment method', $('#token').val().split(":")[0])
                flag = false
                guessingPaymentMethod1(event);
                }
            }
        });
        Mercadopago.setPublishableKey("TEST-5757d909-809a-439c-b6ca-ef6d90c77a50");
        Mercadopago.getIdentificationTypes();

        function getBin() {
            var ccNumber = document.querySelector('input[name="cc_number"]');
            return ccNumber.value.replace(/[ .-]/g, '').slice(0, 6);
        };

        function getBin1() {
                    var ccNumber = $('#token').val().split(":")[0];
                    console.log('ccNumber : ',ccNumber)
                    return ccNumber.slice(0, 6);
                };


        function guessingPaymentMethod(event) {
//            console.log('Called', event);
            var bin = getBin();
//            console.log('---------bin-',bin)
//            console.log('---------$.val()-',$('#order_total').val())
            if (event.type == "keyup") {
                console.log('bin :-', bin);
                if (bin.length >= 6) {
                    Mercadopago.getPaymentMethod({
                        "bin": bin
                    }, setPaymentMethodInfo);
                    Mercadopago.getInstallments({
                        "bin": bin,
                        "amount": total
                    },  setInstallmentInfo);
                }
            } else {
                setTimeout(function() {
                    if (bin.length >= 6) {
                        Mercadopago.getPaymentMethod({
                            "bin": bin
                        }, setPaymentMethodInfo);
                    }
                }, 100);
            }

        };

        function guessingPaymentMethod1(event) {
//                    console.log('Called', event);
                    var bin = getBin1();
//                    console.log('---------bin-',bin)
//                    console.log('---------$.val()-',$('#order_total').val())
                    if (event.type == "keyup") {
                        console.log('bin :-', bin);
                        if (bin.length >= 6) {
                            Mercadopago.getPaymentMethod({
                                "bin": bin
                            }, setPaymentMethodInfo);
                            Mercadopago.getInstallments({
                                "bin": bin,
                                "amount": total
                            },  setInstallmentInfo);
                        }
                    } else {
                        setTimeout(function() {
                            if (bin.length >= 6) {
                                Mercadopago.getPaymentMethod({
                                    "bin": bin
                                }, setPaymentMethodInfo);

                                Mercadopago.getInstallments({
                                "bin": bin,
                                "amount": total
                            },  setInstallmentInfo1);
                            }
                        }, 100);
                    }

                };

        function setInstallmentInfo(status, response){
//            console.log('status     ===== ',status);
//            console.log("response ====",response);
            if (response && response[0] && response[0]['payer_costs']){
                document.getElementById('installments_value').options.length = 0;
                for(var i=0; i < response[0]['payer_costs'].length; i++){
                    $('#installments_value').append("<option value='"+ response[0]['payer_costs'][i]['installments'] +"'>"+ response[0]['payer_costs'][i]['recommended_message'] +"</option>")
                }

            var selectorInstallments = document.getElementById('installments_value'),
            fragment = document.createDocumentFragment();
            selectorInstallments.options.length = 0;
            if (response.length > 0){
                var option = new Option("Elija una cuota...", '-1'),
                    payerCosts = response[0].payer_costs;
                fragment.appendChild(option);
                for (var i = 0; i < payerCosts.length; i++) {
                    option = new Option(payerCosts[i].recommended_message || payerCosts[i].installments, payerCosts[i].installments);
                    var tax = payerCosts[i].labels;
                    if(tax.length > 0){
                        for (var l = 0; l < tax.length; l++) {
                            if (tax[l].indexOf('CFT_') !== -1){
                                option.setAttribute('data-tax', tax[l]);
                            }
                        }
                    }
                    fragment.appendChild(option);
                }
                selectorInstallments.appendChild(fragment);
                selectorInstallments.removeAttribute('disabled');
                }
            }
            else {
                console.log('Error: Could not get installments');
            }


        };


        function setInstallmentInfo1(status, response){
//                    console.log('status     ===== ',status);
//                    console.log("response ====",response);
                    if (response && response[0] && response[0]['payer_costs']){
                        document.getElementById('installments_value1').options.length = 0;
                        for(var i=0; i < response[0]['payer_costs'].length; i++){
                            $('#installments_value1').append("<option value='"+ response[0]['payer_costs'][i]['installments'] +"'>"+ response[0]['payer_costs'][i]['recommended_message'] +"</option>")
                        }
                    var selectorInstallments = document.getElementById('installments_value1'),
                    fragment = document.createDocumentFragment();
                    selectorInstallments.options.length = 0;
                    if (response.length > 0){
                        var option = new Option("Elija una cuota...", '-1'),
                        payerCosts = response[0].payer_costs;
                        fragment.appendChild(option);
                        for (var i = 0; i < payerCosts.length; i++) {
                            option = new Option(payerCosts[i].recommended_message || payerCosts[i].installments, payerCosts[i].installments);
                            var tax = payerCosts[i].labels;
                            if(tax.length > 0){
                                for (var l = 0; l < tax.length; l++) {
                                    if (tax[l].indexOf('CFT_') !== -1){
                                        option.setAttribute('data-tax', tax[l]);
                                    }
                                }
                            }
                            fragment.appendChild(option);
                        }
                        selectorInstallments.appendChild(fragment);
                        selectorInstallments.removeAttribute('disabled');
                    }
                    }
                    else {
                        console.log('Error: Could not get installments');
                    }


        };

        function showTaxes(tax){
            var tax_split = tax.split('|');
            var CFT = tax_split[0].replace('CFT_', ''),
            TEA = tax_split[1].replace('TEA_', '');
            document.getElementById('cft').innerHTML = CFT;
            document.getElementById('tea').innerHTML = TEA;
        }

        function setPaymentMethodInfo(status, response) {
            if (status == 200) {
//                console.log('------status------',status);
//                console.log('------response------',response);
                if (response && response[0] && response[0]['secure_thumbnail']){
                    console.log('-------',response[0]['secure_thumbnail'])
                    $('.card_placeholder').css({"background-image":'url("'+response[0]['secure_thumbnail']+'")'});
                }
                if (response && response[0] && response[0]['id']){
                    console.log('-------',response[0]['id'])
                    $('.mercadopago_cc_brand').val(response[0]['id']);
                }



                // do somethings ex: show logo of the payment method
//                var form = document.querySelector('.o_payment_form');

//                if (document.querySelector("input[name=paymentMethodId]") == null) {
//                    var paymentMethod = document.createElement('input');
//                    paymentMethod.setAttribute('name', "paymentMethodId");
//                    paymentMethod.setAttribute('type', "hidden");
//                    paymentMethod.setAttribute('value', response[0].id);
//                    console.log("paymentMethos", paymentMethod);
//                    form.appendChild(paymentMethod);
//                } else {
//                    document.querySelector("input[name=paymentMethodId]").value = response[0].id;
//                }

//                console.log("paymentMethodId",document.querySelector("input[name=paymentMethodId]").value);
            }
        };

        $( ".mercadopago_installments" ).change(function(event) {
            var cur_i = this.options[this.selectedIndex].getAttribute('data-tax');
            console.log("cur_i : ",cur_i);
            if(cur_i != null){
                document.getElementById('total-financed').innerHTML = this.options[this.selectedIndex].text;
                showTaxes(cur_i);
            }
            }
            );

        $( ".installments_value1" ).change(function(event) {
            var cur_i = this.options[this.selectedIndex].getAttribute('data-tax');
            console.log("cur_i : ",cur_i);
            if(cur_i != null){
                document.getElementById('total-financed').innerHTML = this.options[this.selectedIndex].text;
                showTaxes(cur_i);
            }
        });


//       if (document.getElementById("installments_value") != null){
//            console.log("Installments value is not null")
//
//            document.getElementById("installments_value").onchange = function(event) {
//            event.preventDefault();
//            console.log("Installment has been changed");
//            var cur_i = this.options[this.selectedIndex].getAttribute('data-tax');
//            if(cur_i != null){
//                document.getElementById('total-financed').innerHTML = this.options[this.selectedIndex].text;
//                showTaxes(cur_i);
//            }
//        }};
//        function showTaxes(tax){
//            var tax_split = tax.split('|');
//            var CFT = tax_split[0].replace('CFT_', ''),
//            TEA = tax_split[1].replace('TEA_', '');
//            document.getElementById('cft').innerHTML = CFT;
//            document.getElementById('tea').innerHTML = TEA;
//        }


    });
});
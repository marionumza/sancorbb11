odoo.define('update_variants_in_cart', function (require) {
"use strict";

    require('web.dom_ready');
    var base = require('web_editor.base'),
        core = require('web.core'),
        _t = core._t,
        ajax = require('web.ajax');

    var url = window.location.origin + window.location.pathname + '/'

    $('.oe_website_sale').each(function() {
        var oe_website_sale = this;

        if ($('div.cart-actions').length) {
            $(oe_website_sale).on('click', '.js_change_product', function() {
                var self = this;
                var target_item_row;
                target_item_row = $(this).closest('tr');
                var line_id = target_item_row.find('.js_quantity').data('line-id');
                var product_id = parseInt(target_item_row.find('.js_quantity').data('product-id'), 10);
                change_cart_item(target_item_row, line_id, product_id);
            });
        }
    });

    function change_cart_item(target_item_row, line_id, product_id) {
        var cols = target_item_row.find('td').length;

        jQuery.ajax({
            url: url + product_id + '/variants',
            type: 'POST',
            dataType: 'html',
            beforeSend: function(){target_item_row.block({message: null, overlayCSS: {background: '#fff', opacity: 0.4}});},
            data: {
                'previous_line_id': line_id
            },
            success: function(result) {
                var form_present = $('tr.new_item_' + line_id).length;
                if (form_present === 0) {
                    var cart_item_html = '<tr class="new_item_'+line_id+'" id="new_item">
                                            <td colspan="'+cols+'">
                                                <table class="update_variant_form">
                                                    <tr>
                                                        <td id="thumbnail_'+line_id+'" class="uvc_thumbnail">
                                                            <img class="img img-responsive img-rounded" \
                                                            src="/website/image/product.product/' + product_id +'/image_medium" \
                                                            data-o_src="/web/static/src/img/placeholder.png" width="128" height="128"/>
                                                        </td>
                                                        <td class="uvc_variants">'+result+'</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>';
                    target_item_row.after(cart_item_html).hide();

                    $('tr.new_item_' + line_id + ' .variants_form').attr('id', 'uvc_form_' + line_id);
                    target_item_row.addClass('old_item_' + line_id).fadeOut(300);

                    // cancel button
                    $('tr.new_item_' + line_id).fadeIn(300);
                    $('tr.new_item_' + line_id).on('click', 'span#cancel', {
                        'line_id': line_id
                    }, cancel_update_variants);

                    $('.variants_form').each(function() {
                        $(this).wc_variant_form();
                    });
                }
            },
            complete:function(){
                target_item_row.unblock();
            }
        });

    }

    function delete_cart_item(target_item_row, line_id, product_id) {
        target_item_row.fadeOut(600).fadeTo(150, 1);
        ajax.jsonRpc("/shop/cart/update_json", 'call', {
            'line_id': parseInt(line_id, 10),
            'product_id': product_id,
            'set_qty': 0
        }).then(function(data) {
            location.reload(true);
            return;
        });
    }

    function cancel_update_variants(e) {
        var line_id = e.data.line_id;
        $('tr.new_item_' + line_id).remove();
        $('tr.old_item_' + line_id).fadeIn(150).fadeTo(150, 1).removeClass('old_item_' + line_id);
    }
});

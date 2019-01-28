(function() {

    var url = window.location.origin + window.location.pathname + '/';

    var variantUpdateForm = function($form) {
        this.$form = $form;
        this.$attributeFields = $form.find('.variants select');
        this.$singleVariant = $form.find('.single_variant'),
            this.$singleVariantWrap = $form.find('.single_variant_wrap');
        this.$resetAttributes = $form.find('.reset_attributes');
        this.$msg = $form.find('.msg');
        this.$btn = $form.find('.single_add_to_cart_button');
        this.$allAttributesSelected = true;
        this.$variant_id = parseInt($form.find('input[name="variant_id"], input.variant_id').val(), 10) || undefined;
        this.$message;
        var variationData = $form.data( 'product-variations' );
        this.$variationDataJson = JSON.parse(variationData.replace(/'/g, '"')) || undefined;
        this.$precision = parseInt($(".decimal_precision").last().data('precision')) || 2;

        // Initial State
        this.$resetAttributes.unbind('click');
        this.$attributeFields.unbind('change');

        // Events
        $form.on('click', '.reset_attributes', {variantUpdateForm: this}, this.onReset);
        $form.on('message_action', {variantUpdateForm: this}, this.onMessageAction);
        $form.on('click', '.single_add_to_cart_button', {variantUpdateForm: this}, this.onAddToCart);
        $form.on('reset_data', {variantUpdateForm: this}, this.onResetDisplayedVariant);
        $form.on('reset_image', {variantUpdateForm: this}, this.onResetImage);
        $form.on('change', '.variants select', {variantUpdateForm: this}, this.onChange);
        $form.on('check_variants', {variantUpdateForm: this}, this.onFindVariant);
        $form.on('found_variant', {variantUpdateForm: this}, this.onFoundVariant);
    };

    /**
     * Reset all fields.
     */
    variantUpdateForm.prototype.onReset = function(event) {
        event.preventDefault();
        var form = event.data.variantUpdateForm;
        form.$attributeFields.val('').change();
        form.$message = undefined;
        form.$form.trigger('reset_data');
    };

    /**
     * Triggered when an attribute field changes.
     */
    variantUpdateForm.prototype.onChange = function(event) {
        event.preventDefault();
        var form = event.data.variantUpdateForm;
        if (this.value > 0) {
            $(this).closest('.form-group').removeClass('has-error');
        }
        form.$form.find('input[name="variant_id"], input.variant_id').val('').change();
        form.$form.trigger('check_variants');
    };

    /**
     * Show / Hide messages.
     */
    variantUpdateForm.prototype.onMessageAction = function(event) {
        event.preventDefault();
        var form = event.data.variantUpdateForm;
        if (form.$message) {
            form.$msg.text(form.$message).slideDown(200);
        } else {
            form.$msg.text('').slideUp(200);
        }
    };

    /**
     * Looks for matching variants for current selected attributes.
     */
    variantUpdateForm.prototype.onFindVariant = function(event) {
        event.preventDefault();
        var form = event.data.variantUpdateForm,
            attributes = form.getChosenAttributes(),
            currentAttributes = attributes.data,
            product_tmpl_id = parseInt(form.$form.data('product-tmpl-id'), 10);

        if (attributes.count === attributes.chosenCount) {
            form.$allAttributesSelected = true;

            arrVariant = jQuery.grep(form.$variationDataJson, function( n, i ) {
                return (_.isEqual(n.attribute_value_ids.sort(), currentAttributes.sort()) );
            });

            if (arrVariant.length) {
                form.$btn.attr('disabled', false);
                form.$form.trigger('found_variant', [arrVariant[0]]);
            } else {
                form.$message = 'Not available';
                form.$btn.attr('disabled', true);
                form.$form.trigger('reset_data');
            }

        } else {
            form.$allAttributesSelected = false;
            form.$btn.attr('disabled', false);
            form.$message = undefined;
            form.$form.trigger('reset_data');
        }
        // Show reset link.
        form.toggleResetLink(attributes.chosenCount > 0);
    };

    /**
     * Triggered when a variant has been found which matches all attributes.
     */
    variantUpdateForm.prototype.onFoundVariant = function(event, variant) {
        event.preventDefault();
        var form = event.data.variantUpdateForm;

        // update image
        form.$form.wc_variants_image_update(variant);
        // update variant id
        form.$variant_id = variant.id;
        form.$form.find('input[name="variant_id"], input.variant_id').val(variant.id).change();
        // update price
        var discounted_price = variant.price.toFixed(form.$precision);
        var lst_price = variant.lst_price.toFixed(form.$precision);
        form.$singleVariant.find('span.discounted_price').attr('data-oe-id', variant.id);
        form.$singleVariant.find('del.lst_price').attr('data-oe-id', variant.id);

        form.$singleVariant.find('del.lst_price .oe_currency_value').text(lst_price);
        form.$singleVariant.find('span.discounted_price .oe_currency_value').text(discounted_price);
        form.$singleVariant.slideDown(200);
        // reset message
        form.$message = undefined;
        form.$form.trigger('message_action');
    };

    /**
     * Get chosen attributes from form.
     * @return array
     */
    variantUpdateForm.prototype.getChosenAttributes = function() {
        var data = [],
            count = 0,
            chosen = 0;

        this.$attributeFields.each(function() {
            var attribute_name = $(this).data('attribute_name') || $(this).attr('name'),
                value = $(this).val() || '';

            if (value.length > 0) {
                chosen++;
                data.push(parseInt(value, 10));
            }

            count++;
        });

        return {
            'count': count,
            'chosenCount': chosen,
            'data': data,
        };
    };

    /**
     * Show or hide the reset link.
     */
    variantUpdateForm.prototype.toggleResetLink = function(on) {
        if (on) {
            if (this.$resetAttributes.css('visibility') === 'hidden') {
                this.$resetAttributes.css('visibility', 'visible').hide().fadeIn();
            }
        } else {
            this.$resetAttributes.css('visibility', 'hidden');
        }
    };

    /**
     * When the cart button is pressed.
     */
    variantUpdateForm.prototype.onAddToCart = function(event) {
        event.preventDefault();
        var form = event.data.variantUpdateForm;

        var cartProducts = $('input.js_quantity').map(function() {
            return parseInt($(this).data('product-id'), 10);
        }).get();

        if (form.$message) {
            form.$form.trigger('message_action');
        } else if (!form.$allAttributesSelected) {
            form.$attributeFields.filter(function() {
                return !this.value || $.trim(this.value).length == 0;
            }).closest('div.form-group').addClass('has-error');

            form.$message = "Please select some product options before adding this product to your cart."
            form.$form.trigger('message_action');
        } else if (cartProducts.includes(form.$variant_id)) {
            form.$message = 'Already in cart';
            form.$form.trigger('message_action');
        } else {
            var form_id = this.form.id;
            $.ajax({
                url: url + 'update/variant?' + $('#' + form_id).serialize(),
                type: 'POST',
                dataType: 'json',
                success: function(response) {
                    if (response.status) {
                        location.reload(true);
                    }
                }
            });
        }
    };

    /**
     * When displayed variant data is reset.
     */
    variantUpdateForm.prototype.onResetDisplayedVariant = function(event) {
        var form = event.data.variantUpdateForm;
        form.$form.trigger('reset_image');
        form.$variant_id = undefined;
        form.$singleVariant.find('span.discounted_price').attr('data-oe-id', '');
        form.$singleVariant.find('del.lst_price').attr('data-oe-id', '');
        form.$singleVariant.slideUp(200).find('del.lst_price .oe_currency_value').text('');
        form.$singleVariant.slideUp(200).find('span.discounted_price .oe_currency_value').text('');


        form.$form.trigger('message_action');
    };

    /**
     * When the product image is reset.
     */
    variantUpdateForm.prototype.onResetImage = function(event) {
        event.data.variantUpdateForm.$form.wc_variants_image_update(false);
    };

    /**
     * Sets product images for the chosen variant
     */
    $.fn.wc_variants_image_update = function(variant) {
        var $form = this,
            $tr = $form.closest('tr'),
            $img = $tr.find('td.uvc_thumbnail img')

        if (variant) {
            $img.wc_set_variant_attr('src', "/website/image/product.product/" + variant.id + "/image_medium")
        } else {
            $img.wc_reset_variant_attr('src');
        }

    };

    /**
     * Stores a default attribute for an element so it can be reset later
     */
    $.fn.wc_set_variant_attr = function(attr, value) {
        if (undefined === this.attr('data-o_' + attr)) {
            this.attr('data-o_' + attr, (!this.attr(attr)) ? '' : this.attr(attr));
        }
        if (false === value) {
            this.removeAttr(attr);
        } else {
            this.attr(attr, value);
        }
    };

    /**
     * Reset a default attribute for an element so it can be reset later
     */
    $.fn.wc_reset_variant_attr = function(attr) {
        if (undefined !== this.attr('data-o_' + attr)) {
            this.attr(attr, this.attr('data-o_' + attr));
        }
    };

    /**
     * Function to call wc_variant_form on jquery selector.
     */
    $.fn.wc_variant_form = function() {
        new variantUpdateForm(this);
        return this;
    };
})();
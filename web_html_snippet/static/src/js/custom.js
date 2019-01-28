odoo.define('web_html_snippet.embeded_snippet',function(require) {
'use strict';
      var core = require('web.core');
      var QWeb = core.qweb;
      var options = require('web_editor.snippets.options');
      var ajax = require('web.ajax');
      var _t = core._t;
      var Dialog = require('web.Dialog');
      ajax.loadXML('/web_html_snippet/static/src/xml/block.xml', core.qweb);
      options.registry.summernote_embeded = options.Class.extend({
      xmlDependencies: ['/web_html_snippet/static/src/xml/v.xml'],
      start : function () {
            console.log("dsdsdsd");
            var self = this;
            this.id = this.$target.attr("id");
            var markupStr =this.$target.html();
            var conent = QWeb.render("web_html_snippet.embeded_blocks");
            var dialog =new Dialog(self, {
                size: 'medium',
                title: 'Embeded',
                buttons: [{text: _t('Select'), classes: 'btn-primary', close: true, click: function () {
                var new_qty = $('.o_mail_theme_selector').find('.note-editable').html();
                self.$target.html(new_qty);
                self.trigger_up('rte_change', {target: self.$target});
            	self.$target.parents().find('#wrap').addClass('o_dirty');
            	return new_qty;
                }
            }, {text: _t('Discard'), close: true}],
               $content: QWeb.render("web_html_snippet.embeded_blocks"),
            });
            dialog.opened().then(function (embed) {
            var d = $('<div>').html(markupStr);
            $('.summernotevvvv').summernote({height:500});
            $('.summernotevvvv').summernote('pasteHTML', d);  
			$('.summernotevvvv').summernote({
				dialogsInBody: true
			});
          
            });
            dialog.open();          
      },
      modify_note : function(){
            var self = this;
            this.id = this.$target.attr("id");
            var markupStr =this.$target.html();
            var conent = QWeb.render("web_html_snippet.embeded_blocks");
            var dialog =new Dialog(self, {
                size: 'medium',
                title: 'Embeded',
                buttons: [{text: _t('Select'), classes: 'btn-primary', close: true, click: function () {
                var new_qty = $('.o_mail_theme_selector').find('.note-editable').html();
                var data = self.$target.empty().append(new_qty);
                }
            }, {text: _t('Discard'), close: true}],
               $content: QWeb.render("web_html_snippet.embeded_blocks"),
            });
            dialog.opened().then(function (embed) {
            $('.summernotevvvv').summernote({height:500,dialogsInBody: true});
            var d = $('<div>').html(markupStr);           
            $('.summernotevvvv').summernote('pasteHTML', d);
			$('.summernotevvvv').summernote({
				dialogsInBody: true
			});
            });
            dialog.open();     
      }
      
    })
});

/*global tinyMCE: false, document: false, window: false, jQuery: false */
(function ($) {
    "use strict";
    var original_fields = [],
        destination_fields = [],
        padding = 0;

    function sync_element(original, destination, padding, first) {
        var default_props = {
            position: "",
            top: ""
        },
            original_top = 0,
            original_padding = 0,
            destination_top = 0,
            destination_padding = 0,
            shift = 0,
            more_padding = 0,
            images;

        function distance(a, b) {
            return b.position().top - a.position().top - a.height();
        }
        if (destination.is(":visible")) {
            original.show();
            if (original.css("position") === "relative") {
                original.css(default_props);
            }
            if (destination.css("position") === "relative") {
                destination.css(default_props);
            }
            original_top = original.position().top;

            images = original.find('img');
            images.each(function (index, img) {
                var qimg = $(img);
                if (qimg.width() > original.width()) {
                    qimg.width(original.width() * 0.8);
                }
            });
            destination_top = destination.position().top;
            shift = Math.abs(original_top - destination_top);
            if (original_top > destination_top) {
                destination_padding = shift;
            } else {
                original_padding = shift;
            }

            // The next calculation of padding is necessary if both elements
            // have to be shifted down.
            if (!first && original.prev().is(":visible")) {
                // Calulate distance between bottom of prev element and top
                // of current element. add Padding. If > 0, add to more_padding
                more_padding = Math.max(-1 * (distance(original.prev(), original) + original_padding - padding), 0);
                more_padding += Math.max(-1 * (distance(destination.prev(), destination) + destination_padding - padding), 0);
            }
            original_padding += more_padding;
            destination_padding += more_padding;
            if (original_padding) {
                original.css({
                    position: 'relative',
                    top: original_padding
                });
            } else {
                original.css(default_props);
            }
            if (destination_padding) {
                destination.css({
                    position: 'relative',
                    top: destination_padding
                });
            } else {
                destination.css(default_props);
            }

        } else {
            original.hide();
            destination.css(default_props);
            original.css(default_props);
        }
        // With all that padding, the form might need to be pushed down in 
        // some cases.
        $([original, destination]).each(function (index, item) {
            var $item = $(item),
                outer_padding = 0,
                parent = $item.parent();
            outer_padding = Math.max($item.position().top + $item.height() - (parent.position().top + parent.height()) + padding, 0);
            if (outer_padding) {
                parent.height(parent.height() + outer_padding);
            }
        });
    }

    function sync_elements() {
        // We do NOT calculate padding here again, because we might get
        // to high padding because fields might have been shifted, increasing
        // the padding.
        var i = 0;
        $.each(original_fields, function (i) {
            sync_element($(original_fields[i]), $(destination_fields[i]), padding, i === 0);
        });
    }

    function update_view() {
        var order = 1,
            url_translate = $('input#url_translate').val(),
            langSource = $('#frame-content #view_language')[0].innerHTML;

        original_fields = $('#frame-content .field');
        destination_fields = $('#form-target fieldset > .field');

        if (original_fields.length > 1) {
            padding = ($(original_fields[1]).position().top - $(original_fields[0]).position().top - $(original_fields[0]).height());
        }
        $.each(original_fields, function (index, value) {
            var original_field = $(value),
                destination_field = $(destination_fields[index]);
            sync_element(original_field, destination_field, padding, index === 0);
            if (original_field.find('.richtext-field, textline-field, .localstatic-field, .ArchetypesField-TextField').length > 0) {
                original_field.prepend("<div class='translator-widget' id='item_translation_" + order + "'></div>");
                original_field.children('.translator-widget').click(function () {
                    var field = $(value).attr("id"),
                        // Fetch source of text to translate.
                        jsondata = {
                            'field': field,
                            'lang_source': langSource
                        },
                        targetelement = destination_field.find('input') || destination_field.find("textarea"),
                        tiny_editor = destination_field.find("textarea.mce_editable");
                    // Now we call the data
                    $.ajax({
                        url: url_translate + '/gtranslation_service',
                        data: jsondata,
                        dataType: 'json',
                        type: 'POST',
                        success: function (data) {
                            var text_target = data.data.translations[0].translatedText;
                            if (tiny_editor) {
                                tinyMCE.get(tiny_editor.attr('id')).setContent(text_target);
                            } else {
                                targetelement.val(text_target); // Inserts translated text.
                            }
                        }
                    });
                });
                original_field.children('.translator-widget').hide();
                order += 1;
            }
        });
    }

    $(document).ready(function () {

        /* alert about language independent field */
        $('.languageindependent').click(function () {
            alert('Is a languageindependent!');
            $(this).css('opacity', '1');
        });

        /* change the language trigger */
        $('#lang-select').change(function () {
            var url = $('#lang-select option:selected').val();
            $('#frame-content').load(url, function () {
                $("#frame-content fieldset legend").unwrap().remove();
                update_view();
            });
        });

        /* select a field on both sides and change the color */
        var babel_selected = null,
            orig_babel_select = null;
        $('#babel-edit #fieldset-default .field').click(function () {
            var index = $('#form-target .field').index($(this));
            if (babel_selected) {
                $(babel_selected).toggleClass("selected");
                $(orig_babel_select).toggleClass("selected");
                $(orig_babel_select).children('.translator-widget').hide();
            }
            babel_selected = this;
            $(this).toggleClass("selected");
            orig_babel_select = $('#frame-content .field')[index];
            $(orig_babel_select).toggleClass("selected");
            $(orig_babel_select).children('.translator-widget').show();
        });

        var url = $('#lang-select option:selected').val();
        $('#frame-content').load(url, function () {
            $("#frame-content fieldset legend").unwrap().remove();
            update_view();
        });

        $(".formTabs").click(sync_elements);
    });
}(jQuery));
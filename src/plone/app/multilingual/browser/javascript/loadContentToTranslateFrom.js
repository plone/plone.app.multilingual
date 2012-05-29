/*global tinyMCE: false, document: false, window: false, jQuery: false */
(function ($) {
    "use strict";

    function reload_height() {
        var original_fields = $('#frame-content .field'),
            destination_fields = $('#form-target .field'),
            order = 1,
            url_translate = $('input#url_translate').val(),
            langSource = $('#frame-content #view_language')[0].innerHTML;

        $.each(original_fields, function (index, value) {
            var original_field = $(value),
                destination_field = $(destination_fields[index]),
                original_height = original_field.height(),
                destination_height = destination_field.height();
            if (original_height > destination_height) {
                destination_field.height(original_height);
            } else {
                original_field.height(destination_height);
            }
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
                reload_height();
            });
        });

        /* header height */
        $('#trans-selector').height($('#header-translation').height() + 13 + $('.formTabs').height());

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
            reload_height();
        });
    });
}(jQuery));

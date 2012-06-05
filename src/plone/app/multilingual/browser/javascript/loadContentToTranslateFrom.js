/*global tinyMCE: false, document: false, window: false, jQuery: false */
(function ($) {
    "use strict";
    var original_fields = [],
        destination_fields = [];

    function sync_element(original, destination) {
        var default_props = {
            position: "",
            top: ""
        },
            original_top = 0,
            destination_top = 0,
            shift = 0;
        if (destination.is(":visible")) {
            original.show();
            if (original.css("position") === "relative") {
                original.css(default_props);
            }
            if (destination.css("position") === "relative") {
                destination.css(default_props);
            }
            original_top = original.position().top;
            destination_top = destination.position().top;
            shift = Math.abs(original_top - destination_top);
            if (original_top > destination_top) {
                destination.css({
                    position: 'relative',
                    top: shift
                });
                original.css(default_props);
            } else {
                original.css({
                    position: 'relative',
                    top: shift
                });
                destination.css(default_props);
            }
        } else {
            original.hide();
            destination.css(default_props);
            original.css(default_props);
        }
    }

    function sync_elements() {
        var i = 0;
        $.each(original_fields, function (i) {
            sync_element($(original_fields[i]), $(destination_fields[i]));
        });
    }

    function update_view() {
        var order = 1,
            url_translate = $('input#url_translate').val(),
            langSource = $('#frame-content #view_language')[0].innerHTML;

        original_fields = $('#frame-content .field');
        destination_fields = $('#form-target fieldset > .field');

        $.each(original_fields, function (index, value) {
            var original_field = $(value),
                destination_field = $(destination_fields[index]);
            sync_element(original_field, destination_field);
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
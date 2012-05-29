/*global tinyMCE: false, document: false, window: false, jQuery: false */
(function ($) {
    "use strict";

    function reload_height() {
        var orig = $('#frame-content .field'),
            desti = $('#form-target .field'),
            order = 1;
        $.each(orig, function (index, value) {
            if ($(value).height() > $(desti[index]).height()) {
                $(desti[index]).height($(value).height());
            } else {
                $(value).height($(desti[index]).height());
            }
            if (($(value).find('.richtext-field').length > 0) || ($(value).find('.textline-field').length > 0) || ($(value).find('.localstatic-field').length > 0) || ($(value).find('.ArchetypesField-TextField').length > 0)) {
                $(value).prepend("<div class='translator-widget' id='item_translation_" + order + "'></div>");
                $(value).children('.translator-widget').click(function () {
                    var langSource = $('#frame-content #view_language')[0].innerHTML,
                        field = $(value).attr("id"),
                        // Fetch source of text to translate.
                        jsondata = {
                            'field': field,
                            'lang_source': langSource
                        },
                        url_translate = $('input#url_translate').val(),
                        is_tiny = false,
                        targetelement = false,
                        editor = false;
                    if ($(desti[index]).find('input').length) {
                        // Input field
                        targetelement = $(desti[index]).find('input');
                    } else if ($(desti[index]).find('textarea.mce_editable').length) {
                        // mceEditor
                        editor = $(desti[index]).find('textarea.mce_editable').attr('id');
                        is_tiny = true;
                    } else if ($(desti[index]).find('textarea').length) {
                        // Textarea field
                        targetelement = $(desti[index]).find('textarea');
                    }
                    // Now we call the data
                    $.ajax({
                        url: url_translate + '/gtranslation_service',
                        data: jsondata,
                        dataType: 'json',
                        type: 'POST',
                        success: function (data) {
                            // console.log(data);
                            var text_target = data.data.translations[0].translatedText;
                            // console.log(text_target);
                            if (is_tiny) {
                                tinyMCE.get(editor).setContent(text_target);
                            } else {
                                targetelement.val(text_target); // Inserts translated text.
                            }
                        }
                    });
                });
                $(value).children('.translator-widget').hide();
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
        var babel_selectec = null,
            orig_babel_select = null;
        $('#babel-edit #fieldset-default .field').click(function () {
            var index = $('#form-target .field').index($(this));
            if (babel_selectec) {
                $(babel_selectec).toggleClass("selected");
                $(orig_babel_select).toggleClass("selected");
                $(orig_babel_select).children('.translator-widget').hide();
            }
            babel_selectec = this;
            $(this).toggleClass("selected");
            orig_babel_select = $('#frame-content .field')[index];
            $(orig_babel_select).toggleClass("selected");
            $(orig_babel_select).children('.translator-widget').show();
        });

    });

    $(window).load(function () { /* initial load the default language left side */
        var url = $('#lang-select option:selected').val();
        $('#frame-content').load(url, function () {
            reload_height();
        });
    });
}(jQuery));

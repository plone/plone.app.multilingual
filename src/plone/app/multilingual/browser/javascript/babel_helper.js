/*global tinyMCE: false, document: false, window: false, jQuery: false */
(function ($) {
    "use strict";

    var original_fields = [],
        destination_fields = [],
        padding = 0;

    function sync_element_vertically(original, destination, padding, first) {
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
            images, new_distance;

        function distance(a, b) {
            return b.position().top - a.position().top - a.height();
        }
        if (destination.is(":visible")) {
            original.show();
            // reset fields
            if (original.css("position") === "relative") {
                original.css(default_props);
            }
            if (destination.css("position") === "relative") {
                destination.css(default_props);
            }
            original_top = original.position().top;

            // Make images smaller
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
                new_distance = distance(original.prev(), original);
                new_distance += original_padding;
                if (new_distance < padding) {
                    more_padding += padding - new_distance;
                }
                new_distance = distance(destination.prev(), destination);
                new_distance += destination_padding + more_padding;
                if (new_distance < padding) {
                    more_padding += padding - new_distance;
                }
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

    function sync_elements_vertically() {
        // We do NOT calculate padding here again, because we might get
        // to high padding because fields might have been shifted, increasing
        // the padding.
        var i = 0;
        $.each(original_fields, function (i) {
            sync_element_vertically($(original_fields[i]), $(destination_fields[i]), padding, i === 0);
        });
    }

    function update_view() {
        var order = 1,
            url_translate = $('input#url_translate').val(),
            langSource = $('#frame-content #view_language')[0].innerHTML;

        $('#form-target fieldset > div > .field').unwrap();

        original_fields = $('#frame-content .field');
        destination_fields = $('#form-target fieldset > .field');

        // Calculate the padding between fields as intended by css
        if (original_fields.length > 1) {
            padding = ($(original_fields[1]).position().top - $(original_fields[0]).position().top - $(original_fields[0]).height());
        }
        $.each(original_fields, function (index, value) {
            var original_field = $(value);
            var destination_field = $(destination_fields[index]);
            sync_element_vertically(original_field, destination_field, padding, index === 0);

            // Add the google translation field
            if ($('#gtranslate_service_available').attr('value') === "True" && ((original_field.find('.richtext-field, .textline-field, .text-field, .localstatic-field, .ArchetypesField-TextField').length > 0) || ($('#at-babel-edit').length > 0))) {
                original_field.prepend("<div class='translator-widget' id='item_translation_" + order + "'></div>");
                original_field.children('.translator-widget').click(function () {
                    var field = $(value).attr("rel");
                        // Fetch source of text to translate.
                    var jsondata = {
                            'field': field,
                            'lang_source': langSource
                        };
                    var targetelement = destination_field.find('textarea');
                    var tiny_editor = destination_field.find("textarea.mce_editable");
                    if (!targetelement.length) {
                        targetelement = destination_field.find("input");
                    }
                    // Now we call the data
                    $.ajax({
                        url: url_translate + '/gtranslation_service',
                        data: jsondata,
                        dataType: 'json',
                        type: 'POST',
                        success: function (data) {
                            var text_target = data.data;
                            if (tiny_editor.length > 0) {
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
            $(this).css('opacity', '1');
        });

        /* change the language trigger */
        $('#trans-selector button').click(function () {
            var url = $(this).data('url');
            $('#frame-content').load(url, function () {
                $("#frame-content fieldset legend").unwrap().remove();
                update_view();
            });
            $('#trans-selector button.active').removeClass('active');
            $(this).addClass('active');
        });
        /* change the language trigger, this time for the drop-down, which is
        used when too many translations are present to fit into buttons */
        $('#trans-selector select').change(function () {
            var selected_elem = $(this).children('option').eq(this.selectedIndex);
            var url = selected_elem.val();
            $('#frame-content').load(url, function () {
                $("#frame-content fieldset legend").unwrap().remove();
                update_view();
            });
        });

        /* select a field on both sides and change the color */
        var babel_selected = null,
            orig_babel_select = null;
        $('#babel-edit *[id^=fieldset] .field').click(function () {
            var index = $('#form-target .field').index($(this));
            if (babel_selected) {
                $(babel_selected).addClass('selected');
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

        // Fetch default content
        var initialFetch = $('#trans-selector button.active').data('url');
        // Can be null if not buttons, but the drop-down is present
        if (initialFetch === null) {
            initialFetch = $('#trans-selector select option:selected').val();
        }
        $('#frame-content').load(initialFetch, function () {
            $("#frame-content fieldset legend").unwrap().remove();
            update_view();
        });

        $(".formTabs, .pat-autotoc a").click(sync_elements_vertically);
    });
}(jQuery));

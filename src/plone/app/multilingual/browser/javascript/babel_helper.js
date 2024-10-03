/*global tinyMCE: false, document: false, window: false, jQuery: false */
(function ($) {
    "use strict";

    function sync_element_vertically(original, destination) {
        // sync vertical position
        const orig_rect = original.getBoundingClientRect()
        const dest_rect = destination.getBoundingClientRect()

        // make the wrapper heights equally
        var max_height = Math.max(orig_rect.height, dest_rect.height);

        original.style.height = `${max_height}px`;
        destination.style.height = `${max_height}px`;
    }

    function update_view() {
        let order = 1;
        const url_translate = document.querySelector('input#url_translate')?.value;
        const langSource = document.querySelector('#frame-content #view_language').innerHTML;

        // unwrap(document.querySelectorAll('#form-target fieldset > div > .field'));
        $('#form-target fieldset > div > .field').unwrap();

        const original_fields = document.querySelectorAll('#frame-content .field');
        const destination_fields = document.querySelectorAll('#form-target fieldset > .field');
        const visible_destination_fields = [...destination_fields].filter(it => it.closest("fieldset.active") != null);

        // show only fields of current tab
        original_fields.forEach((field) => {
            field.style.display = "none";
            visible_destination_fields.forEach((dst_fld) => {
                if (dst_fld.dataset.fieldname.endsWith(field.id)) {
                    field.style.display = "block";
                    return;
                }
            })
        });

        visible_destination_fields.forEach(dest_field => {
            var orig_field = [...original_fields].filter(it => dest_field.dataset.fieldname.endsWith(it.id));

            if (!orig_field.length) {
                // field not found
                return;
            } else {
                orig_field = orig_field[0];
            }

            sync_element_vertically(orig_field, dest_field);

            const gtranslate_enabled = document.getElementById("gtranslate_service_available");

            // Add the google translation field
            if (
                gtranslate_enabled.value === "True" &&
                dest_field.querySelectorAll('.text-widget, .textarea-widget, .richTextWidget').length &&
                !orig_field.querySelector(".translator-widget")
            ) {
                const translator_widget = document.createElement("div");

                translator_widget.classList.add("translator-widget");
                translator_widget.id = `item_translation_${order}`;

                translator_widget.addEventListener("click", async function () {
                    var field = orig_field.getAttribute("rel");

                    // we use the current URL to get the context's UID
                    var url_parts = document.location.pathname.split('++addtranslation++');

                    var postdata = new URLSearchParams({
                        'field': field,
                        'lang_source': langSource,
                        // we use the second part of the url_parts, the uid itself
                        'context_uid': url_parts[1]
                    });

                    const translate_service_url = url_translate + '/gtranslation_service';

                    // Now we call the data
                    const response = await fetch(translate_service_url, {
                        method: "POST",
                        headers: {
                            "Content-type": "application/x-www-form-urlencoded; charset: utf-8",
                        },
                        body: postdata,
                    });

                    if (!response.ok) {
                        console.log(`Could not load ${translate_service_url}: ${response.statusText}`);
                        return;
                    }

                    const json = await response.json();
                    var text_target = json.data;

                    var target_el = dest_field.querySelector('textarea,input');
                    const target_tiny = tinymce.get(target_el.id);

                    if (target_tiny) {
                        // a TinyMCE editor is present
                        await target_tiny.setContent(text_target);
                    } else {
                        // set value of textarea
                        target_el.value = text_target;
                    }
                    // need to trigger "change" event to make validation (and tiny) happy
                    $(target_el).trigger("change");
                });

                orig_field.prepend(translator_widget);
                order += 1;
            }
        });
    }

    function init_tab_switch() {
        // init fieldset switch
        document.querySelector("#form-target form").querySelectorAll(".autotoc-nav a").forEach((item) => {
            // NOTE: the "clicked" event is triggered in pat-autotoc
            $(item).on("clicked", (e) => {
                update_view();
            });
        });
    }

    function init_sync_active_click() {
        /* select a field on both sides and change the color */
        let babel_selected = null;
        let orig_babel_selected = null;

        document.querySelectorAll('#form-target fieldset .field').forEach((field) => {
            field.addEventListener("click", () => {
                const original_fields = document.querySelectorAll('#frame-content .field');

                if (babel_selected) {
                    babel_selected.classList.remove("selected");
                    orig_babel_selected.classList.remove("selected");
                }
                babel_selected = field;
                babel_selected.classList.add("selected");
                const orig_field = [...original_fields].filter(it => babel_selected.dataset.fieldname.endsWith(it.id));
                if(!orig_field.length) {
                    return;
                }
                orig_babel_selected = orig_field[0];
                orig_babel_selected.classList.add("selected");
            });
        });
    }

    function load_default_language() {
        // Fetch default language content
        const trans_buttons = document.querySelectorAll("#trans-selector button");
        const active_buttons = [...trans_buttons].filter(it => it.classList.contains("active"));
        const trans_select = document.querySelector("#trans-selector select");

        let initialFetchUrl = "";

        if (active_buttons.length) {
            initialFetchUrl = active_buttons[0].dataset.url;
        } else if (trans_buttons.length) {
            trans_buttons[0].classList.add("active");
            initialFetchUrl = trans_buttons[0].dataset.url;
        } else if (trans_select) {
            initialFetchUrl = trans_select.value;
        } else {
            // no chance to get original language content
            return;
        }

        $('#frame-content').load(initialFetchUrl, function () {
            $("#frame-content fieldset legend").unwrap().remove();
            update_view();
        });
    }

    function init_babel_view() {

        /* change the language trigger */
        $('#trans-selector button').on("click", function () {
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
        $('#trans-selector select').on("change", function () {
            var selected_elem = $(this).children('option').eq(this.selectedIndex);
            var url = selected_elem.val();
            $('#frame-content').load(url, function () {
                $("#frame-content fieldset legend").unwrap().remove();
                update_view();
            });
        });

        // initialize tab change
        init_tab_switch();

        // initialize synchron active fields when clicked
        init_sync_active_click();

        // load original language
        load_default_language();
    };

    let initInterval = null;
    initInterval = setInterval(() => {
        if (!document.querySelector("body.patterns-loaded")) {
            // wait for loaded patterns
            return;
        }
        clearInterval(initInterval);
        init_babel_view();
    }, 500);


}(jQuery));

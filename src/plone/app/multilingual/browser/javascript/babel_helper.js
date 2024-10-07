(function ($) {
    "use strict";

    let babel_selected = null;
    let orig_babel_selected = null;

    function sync_heights(el1, el2) {
        if (el1.style.height != "auto") {
            // reset if previously set
            el1.style.height = "auto";
        }
        if (el2.style.height != "auto") {
            // reset if previously set
            el2.style.height = "auto";
        }
        const max_height = Math.max(
            el1.getBoundingClientRect().height,
            el2.getBoundingClientRect().height,
        );
        el1.style.height = `${max_height}px`;
        el2.style.height = `${max_height}px`;
    }

    function sync_header_height() {
        // sync header and tab/button heights to ensure the fields are aligned synchronous
        sync_heights(
            document.querySelector("#babel-edit > div > h2"),
            document.querySelector("#header-translation h2"),
        )

        // sync translation button and tab heights
        sync_heights(
            document.querySelector("#babel-edit #trans-selector"),
            document.querySelector("#form-target .autotoc-nav"),
        )
    }

    function sync_focus(orig_field, focus_field, focus_tinymce) {
        const click_field = (field) => {
            if (babel_selected) {
                babel_selected.classList.remove("selected");
                orig_babel_selected.classList.remove("selected");
            }
            babel_selected = focus_field;
            babel_selected.classList.add("selected");
            orig_babel_selected = orig_field;
            orig_babel_selected.classList.add("selected");
        };

        /* select a field on both sides and change the color */
        focus_field.addEventListener("click", click_field);

        if(focus_tinymce) {
            focus_tinymce.on("focus", click_field);
        }
    }

    function update_view() {
        let order = 1;
        const url_translate = document.querySelector('input#url_translate')?.value;
        const langSource = document.querySelector('#frame-content #view_language').innerHTML;

        sync_header_height();

        const original_fields = document.querySelectorAll('#frame-content .field');
        const destination_fields = document.querySelectorAll('#form-target fieldset .field');
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

            const gtranslate_enabled = document.getElementById("gtranslate_service_available");
            const target_el = dest_field.querySelector('textarea,input');
            const target_tiny = tinymce.get(target_el.id);

            sync_focus(orig_field, dest_field, target_tiny);
            sync_heights(orig_field, dest_field);

            // Add the google translation field
            if (
                gtranslate_enabled.value === "True" && (
                    // it is either a text widget, a text area or rich widget
                    dest_field.querySelectorAll('.text-widget, .textarea-widget, .richTextWidget').length ||
                    // or it is a tinymce richtextfield without wrapping CSS class
                    target_tiny !== null
                ) &&
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

                    if (!text_target) {
                        return;
                    }

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
            // defer updating
            setTimeout(update_view, 500);
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

        // load original language and update the view
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

    // fix field alignment on window resize
    let deferResize = null;
    window.addEventListener("resize", () => {
        if (deferResize) {
            clearTimeout(deferResize);
        }
        deferResize = setTimeout(update_view, 500);
    });

}(jQuery));

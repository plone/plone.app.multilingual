

function reload_height() {
  orig = $('#frame-content .field');
  desti = $('#form-target .field');
  order = 1;
  $.each(orig, function(index, value) { 
    if ($(value).height()>$(desti[index]).height()) {
      $(desti[index]).height($(value).height());
    } else {
      $(value).height($(desti[index]).height());
    }
    if (($(value).find('.richtext-field').length>0) || ($(value).find('.textline-field').length>0) || ($(value).find('.localstatic-field').length>0) || ($(value).find('.ArchetypesField-TextField').length>0)) {
      $(value).prepend("<div class='translator-widget' id='item_translation_"+order+"'></div>");
      $(value).children('.translator-widget').click(function() {
        var langSource = $('#frame-content #view_language')[0].innerHTML;
        var field = $(value).attr("id"); // Fetch source of text to translate.
        var jsondata = {'field':field,'lang_source':langSource};
        var url_translate = $('input#url_translate').val();

        is_tiny = false;
        if ($(desti[index]).find('input').length) {
          // Input field
          var targetelement = $(desti[index]).find('input');
        } else if ($(desti[index]).find('textarea.mce_editable').length) {
          // mceEditor
          var editor=$(desti[index]).find('textarea.mce_editable').attr('id');
          var is_tiny = true;
        } else if ($(desti[index]).find('textarea').length) {
          // Textarea field
          var targetelement = $(desti[index]).find('textarea');
        }
        // Now we call the data
        $.ajax({
          url: url_translate+'/gtranslation_service',
          data: jsondata,
          dataType: 'json',
          type: 'POST',
          success: function(data){
            // console.log(data);
            text_target = data.data.translations[0].translatedText;
            console.log(text_target);
            if (is_tiny) {
              tinyMCE.get(editor).setContent(text_target);
            } else {
              targetelement.val(text_target); // Inserts translated text.
            }
          }
        });
      });
      $(value).children('.translator-widget').hide()
      order += 1;
    }
  });
}

jq(document).ready(function() { 

  /* alert about language independent field */
  $('.languageindependent').click(function() {
    alert('Is a languageindependent!');
    $(this).css('opacity','1');
  });

  /* change the language trigger */
  jq('#lang-select').change(function() {
    var url = jq('#lang-select option:selected').val(); 
    jq('#frame-content').load(url, function() {
      reload_height();
    });
  }); 

  /* header height */
  $('#trans-selector').height($('#header-translation').height()+13+$('.formTabs').height());

  /* select a field on both sides and change the color */
  var babel_selectec = null;
  var orig_babel_select = null;
  jq('#babel-edit #fieldset-default .field').click(function() {
    if (babel_selectec) {
      $(babel_selectec).toggleClass("selected");
      $(orig_babel_select).toggleClass("selected");
      $(orig_babel_select).children('.translator-widget').hide()
    }
    babel_selectec = this;
    $(this).toggleClass("selected");
    index = $('#form-target .field').index($(this));
    orig_babel_select = $('#frame-content .field')[index];
    $(orig_babel_select).toggleClass("selected");
    $(orig_babel_select).children('.translator-widget').show()
  });

});

$(window).load(function() {
  /* initial load the default language left side */
  var url = jq('#lang-select option:selected').val();
  jq('#frame-content').load(url, function() {
      reload_height();
  });
});


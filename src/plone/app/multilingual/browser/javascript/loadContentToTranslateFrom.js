

jq(document).ready(function() { 

  $('.languageindependent').click(function() {
    alert('Is a languageindependent!');
    $(this).css('opacity','1');
  });

  jq('#lang-select').change(function() {
    var url = jq('#lang-select option:selected').val(); 
    jq('#frame-content').load(url, function() {
      orig = $('#frame-content .field');
      desti = $('#form .field');
      $.each(orig, function(index, value) { 
        $(value).height($(desti[index]).height());
      });
    });
  }); 
  $('#trans-selector').height($('#header-translation').height()+3+$('.formTabs').height());
  var babel_selectec = null;
  var orig_babel_select = null;
  jq('#babel-edit #fieldset-default .field').click(function() {
    if (babel_selectec) {
      $(babel_selectec).toggleClass("selected");
      $(orig_babel_select).toggleClass("selected");
    }
    babel_selectec = this;
    /*$(this).css('background-color','#205c90');*/
    $(this).toggleClass("selected");
    index = $('#form .field').index($(this));
    orig_babel_select = $('#frame-content .field')[index];
    $(orig_babel_select).toggleClass("selected");
  });

});

$(window).load(function() {
  var url = jq('#lang-select option:selected').val();
  jq('#frame-content').load(url, function() {
    orig = $('#frame-content .field');
    desti = $('#form .field');
    $.each(orig, function(index, value) { 
      $(value).height($(desti[index]).height());
    });
  });
});


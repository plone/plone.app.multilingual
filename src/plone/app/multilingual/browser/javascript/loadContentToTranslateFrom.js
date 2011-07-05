jq(document).ready(function() { 
  jq('#selec').change(function() {
    var languageChanged = document.getElementById('selec').value 
    var baseUrl = jq('base').attr('href');
    if (!baseUrl) {
        var pieces = window.location.href.split('/');
        pieces.pop();
        baseUrl = pieces.join('/');
    }
    jq('#contentToTranslate').load(baseUrl + "/babel_view?langchangeto=" + languageChanged); 
  }); 
});
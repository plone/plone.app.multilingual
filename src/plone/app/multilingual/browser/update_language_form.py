from five import grok
from z3c.form import button
from plone.directives import form
from plone.app.multilingual.browser.utils import multilingualMoveObject
from plone.multilingual.interfaces import ITranslatable

from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import IUpdateLanguage


class UpdateLanguageForm(form.SchemaForm):

    grok.name("update_language")
    grok.context(ITranslatable)
    grok.require("cmf.ModifyPortalContent")
    schema = form.IFormFieldProvider(IUpdateLanguage)
    ignoreContext = True
    label = _(u"label_update_language", default=u"Update Language")
    status = _(u"label_alert_update",
        default=u"""By updating the content language will trigger its move to the correct language folder in the site's hierarchy""")

    @button.buttonAndHandler(_(u"update_language",
                               default=u"Update Language"))
    def handle_update(self, action):
        data, errors = self.extractData()
        new_object = self.context

        if not errors:
            language = data['language']
            # We need to move the object to its place!!
            new_object = multilingualMoveObject(self.context, language)

        return self.request.response.redirect(new_object.absolute_url() + '?set_language=' + language)

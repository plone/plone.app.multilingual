from five import grok
from z3c.form import button
from plone.directives import form
from plone.multilingual.interfaces import (
    ITranslationManager,
    ITranslatable,
    ILanguage
)
from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import IAddTranslation


class AddTranslationsForm(form.SchemaForm):

    grok.name("add_translations")
    grok.context(ITranslatable)
    grok.require("plone.app.multilingual.ManageTranslations")
    schema = form.IFormFieldProvider(IAddTranslation)
    ignoreContext = True
    label = _(u"label_add_translations", default=u"Add translations")

    @button.buttonAndHandler(_(u"add_translations",
                               default=u"Add translations"))
    def handle_add(self, action):
        data, errors = self.extractData()
        if not errors:
            content = data['content']
            language = data['language']
            ITranslationManager(self.context).register_translation(language,\
                content)
            ILanguage(content).set_language(language)

        return self.request.response.redirect(self.context.absolute_url()\
             + '/add_translations')

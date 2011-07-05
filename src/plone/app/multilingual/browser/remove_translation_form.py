from five import grok
from z3c.form import button
from plone.directives import form
from Acquisition import aq_parent
from plone.multilingual.interfaces import (
    ITranslationManager,
    ITranslatable,
)
from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import IRemoveTranslation


class RemoveTranslationsForm(form.SchemaForm):

    grok.name("remove_translations")
    grok.context(ITranslatable)
    grok.require("plone.app.multilingual.ManageTranslations")
    schema = form.IFormFieldProvider(IRemoveTranslation)
    ignoreContext = True
    label = _(u"label_remove_translations")

    @button.buttonAndHandler(_(u"unlink selected"))
    def handle_unlink(self, action):
        data, errors = self.extractData()
        manager = ITranslationManager(self.context)
        if not errors:
            for language in data['languages']:
                manager.remove_translation(language)
        return self.request.response.redirect(self.context.absolute_url() \
            + '/remove_translations')

    @button.buttonAndHandler(_(u"remove selected"))
    def handle_remove(self, action):
        data, errors = self.extractData()
        manager = ITranslationManager(self.context)
        if not errors:
            for language in data['languages']:
                content = manager.get_translation(language)
                manager.remove_translation(language)
                aq_parent(content).manage_delObjects([content.getId()])
        return self.request.response.redirect(self.context.absolute_url() \
            + '/remove_translations')

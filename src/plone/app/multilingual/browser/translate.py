from five import grok
from z3c.form import button
from plone.directives import form
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.multilingual.interfaces import (
    ITranslationManager,
    ITranslatable,
)
from plone.multilingual.interfaces import ILanguage

from plone.app.multilingual.browser.interfaces import ICreateTranslation
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual import _


class TranslationForm(form.SchemaForm):
    """ Translation Form """

    grok.name('create_translation')
    grok.context(ITranslatable)
    grok.require('plone.app.multilingual.ManageTranslations')
    schema = ICreateTranslation
    ignoreContext = True

    @button.buttonAndHandler(_(u'Create'))
    def handle_create(self, action):
        data, errors = self.extractData()
        if not errors:
            language = data['language']
            translation_manager = ITranslationManager(aq_inner(self.context))
            if ILanguage(self.context).get_language() == LANGUAGE_INDEPENDENT:
                language_tool = getToolByName(self.context, 'portal_languages')
                default_language = language_tool.getDefaultLanguage()
                ILanguage(self.context).set_language(default_language)
                translation_manager.update()
                self.context.reindexObject(idxs='language')

            translation_manager.add_translation(language)
            translated = translation_manager.get_translation(language)
            return self.request.response.redirect(translated.absolute_url() \
                + '/edit?set_language=%s' % language)

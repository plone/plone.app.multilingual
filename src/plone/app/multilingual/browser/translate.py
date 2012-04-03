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
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema

from plone.app.multilingual.browser.interfaces import ICreateTranslation
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual import _
from Products.Five import BrowserView
from plone.multilingual.interfaces import ITranslationManager, ILanguage
import urllib


class gtranslation_service_dexterity(BrowserView):

    def __call__(self):
        if (self.request.method != 'POST' and
            not ('field' in self.request.form.keys() and
                'lang_source' in self.request.form.keys())):
            return _("Need a field")
        else:
            manager = ITranslationManager(self.context)
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
            lang_target = ILanguage(self.context).get_language()
            lang_source = self.request.form['lang_source']
            orig_object = manager.get_translation(lang_source)
            if hasattr(orig_object, self.request.form['field']):
                question = getattr(orig_object, self.request.form['field'], '')
                if hasattr(question, 'raw'):
                    question = question.raw
            else:
                return _("Invalid field")
            if len(question)>1600:
                return _("Too long field")
            data = {'key': settings.google_translation_key,
                        'target': lang_target,
                        'source': lang_source,
                        'q': question}
            params = urllib.urlencode(data)

            url = 'https://www.googleapis.com/language/translate/v2'
            retorn = urllib.urlopen(url + '?' + params)
            return retorn.read()


class gtranslation_service_at(BrowserView):

    def __call__(self):
        if (self.request.method != 'POST' and
            not ('field' in self.request.form.keys() and
                'lang_source' in self.request.form.keys())):
            return _("Need a field")
        else:
            manager = ITranslationManager(self.context)
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
            lang_target = ILanguage(self.context).get_language()
            lang_source = self.request.form['lang_source']
            orig_object = manager.get_translation(lang_source)
            try:
                question = orig_object.getField(self.request.form['field']).get(orig_object)
            except AttributeError:
                return _("Invalid field")
            if len(question)>1600:
                return _("Too long field")
            data = {'key': settings.google_translation_key,
                        'target': lang_target,
                        'source': lang_source,
                        'q': question}
            params = urllib.urlencode(data)

            url = 'https://www.googleapis.com/language/translate/v2'
            retorn = urllib.urlopen(url + '?' + params)
            return retorn.read()


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
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
            if settings.redirect_babel_view:
                return self.request.response.redirect(translated.absolute_url() \
                    + '/babel_edit')
            else:
                return self.request.response.redirect(translated.absolute_url() \
                    + '/edit?set_language=%s' % language)

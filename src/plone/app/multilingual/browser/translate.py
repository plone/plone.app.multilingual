import urllib

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from five import grok
from plone.directives import form
from plone.multilingual.interfaces import ILanguage
from plone.multilingual.interfaces import ITranslatable
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.registry.interfaces import IRegistry
from z3c.form import button
from zope.component import getUtility
from urllib import quote_plus

import json

from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import ICreateTranslation
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema


def google_translate(question, key, lang_target, lang_source):
    length = len(question)
    translated = ''
    url = 'https://www.googleapis.com/language/translate/v2'
    temp_question = question
    while(length > 400):
        temp_question = question[:399]
        index = temp_question.rfind(' ')
        temp_question = temp_question[:index]
        question = question[index:]
        length = len(question)
        data = {'key': key,
                'target': lang_target,
                'source': lang_source,
                'q': temp_question}
        params = urllib.urlencode(data)

        retorn = urllib.urlopen(url + '?' + params)
        translated += json.loads(retorn.read())['data']['translations'][0]['translatedText']

    data = {'key': key,
            'target': lang_target,
            'source': lang_source,
            'q': temp_question}
    params = urllib.urlencode(data)

    retorn = urllib.urlopen(url + '?' + params)
    translated += json.loads(retorn.read())['data']['translations'][0]['translatedText']
    return json.dumps({'data': translated})


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
            field = self.request.form['field'].split('.')[-1]
            if hasattr(orig_object, field):
                question = getattr(orig_object, field, '')
                if hasattr(question, 'raw'):
                    question = question.raw
            else:
                return _("Invalid field")
            return google_translate(question, settings.google_translation_key, lang_target, lang_source)


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
                question = orig_object.getField(
                    self.request.form['field']).get(orig_object)
            except AttributeError:
                return _("Invalid field")
            return google_translate(question, settings.google_translation_key, lang_target, lang_source)


class TranslationForm(BrowserView):
    """ Translation Form """

    def __call__(self):
        import pdb; pdb.set_trace()
        language = self.request.get('language', None)
        if language:
            translation_manager = ITranslationManager(aq_inner(self.context))
            if ILanguage(self.context).get_language() == LANGUAGE_INDEPENDENT:
                # XXX : Why we need this ? the subscriber from pm should maintain it
                language_tool = getToolByName(self.context, 'portal_languages')
                default_language = language_tool.getDefaultLanguage()
                ILanguage(self.context).set_language(default_language)
                translation_manager.update()
                self.context.reindexObject()

            # OLD code that creates the object before translating
            # translation_manager.add_translation(language)
            # translated = translation_manager.get_translation(language)
            # registry = getUtility(IRegistry)
            # settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
            # if settings.redirect_babel_view:
            #     return self.request.response.redirect(
            #         translated.absolute_url() + '/babel_edit?set_language=%s' % language)
            # else:
            #     return self.request.response.redirect(
            #         translated.absolute_url() + '/edit?set_language=%s' %
            #         language)

            # We get the new parent
            new_parent = translation_manager.add_translation_delegated(language)

            registry = getUtility(IRegistry)
            settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)

            sdm = self.context.session_data_manager
            session = sdm.getSessionData(create=True)
            session.set("tg", translation_manager.tg)

            # We set the language and redirect to babel_view or not
            if settings.redirect_babel_view:
                pass
            else:
                # We look for the creation url for this content type

                # Get the factory
                baseUrl = new_parent.absolute_url()
                types_tool = getToolByName(self.context, 'portal_types')

                # Note: we don't check 'allowed' or 'available' here, because these are
                # slow. We assume the 'allowedTypes' list has already performed the
                # necessary calculations
                actions = types_tool.listActionInfos(
                    object=new_parent,
                    check_permissions=False,
                    check_condition=False,
                    category='folder/add',
                )

                addActionsById = dict([(a['id'], a) for a in actions])

                typeId = self.context.portal_type

                addAction = addActionsById.get(typeId, None)

                if addAction is not None:
                    url = addAction['url']

                if not url:
                    url = '%s/createObject?type_name=%s' % (baseUrl, quote_plus(typeId))

                # url = new_parent.absolute_url() + '/++addtranslation++'+self.context.portal_type+'++'+translation_manager.tg
                return self.request.response.redirect(url)




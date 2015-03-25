# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five import BrowserView
from plone.app.multilingual import _
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITranslationManager
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
import json
import urllib


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
        translated += json.loads(
            retorn.read())['data']['translations'][0]['translatedText']

    data = {'key': key,
            'target': lang_target,
            'source': lang_source,
            'q': temp_question}
    params = urllib.urlencode(data)

    retorn = urllib.urlopen(url + '?' + params)
    translated += json.loads(
        retorn.read())['data']['translations'][0]['translatedText']
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
            settings = registry.forInterface(IMultiLanguageExtraOptionsSchema, prefix="plone")
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
            return google_translate(question,
                                    settings.google_translation_key,
                                    lang_target,
                                    lang_source)


class TranslationForm(BrowserView):
    """Translation Form
    """

    def __call__(self):
        language = self.request.get('language', None)
        if language:
            context = aq_inner(self.context)
            translation_manager = ITranslationManager(context)
            new_parent = translation_manager.add_translation_delegated(language)  # noqa
            baseUrl = new_parent.absolute_url()
            url = '%s/++addtranslation++%s' % (baseUrl, IUUID(context))
            return self.request.response.redirect(url)

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.app.multilingual import _
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITranslationManager
from plone.registry.interfaces import IRegistry
from urllib import quote_plus
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
            return google_translate(question,
                                    settings.google_translation_key,
                                    lang_target,
                                    lang_source)


class TranslationForm(BrowserView):
    """ Translation Form """

    def __call__(self):
        language = self.request.get('language', None)
        if language:
            context = aq_inner(self.context)
            translation_manager = ITranslationManager(context)
            # if ILanguage(context).get_language() == LANGUAGE_INDEPENDENT:
            #     # XXX : Why we need this ? the subscriber from pm should
            #             maintain it
            #     language_tool = getToolByName(context, 'portal_languages')
            #     default_language = language_tool.getDefaultLanguage()
            #     ILanguage(context).set_language(default_language)
            #     translation_manager.update()
            #     context.reindexObject()

            new_parent = translation_manager.add_translation_delegated(language)  # noqa

            registry = getUtility(IRegistry)
            settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
            sdm = self.context.session_data_manager
            session = sdm.getSessionData(create=True)
            session.set("tg", translation_manager.tg)
            session.set("old_lang", ILanguage(self.context).get_language())

            baseUrl = new_parent.absolute_url()
            # We set the language and redirect to babel_view or not
            if settings.redirect_babel_view:
                # Call the ++addtranslation++ adapter to show the babel
                # add form
                url = '%s/++addtranslation++%s' % (
                    baseUrl, self.context.portal_type)
                return self.request.response.redirect(url)
            else:
                # We look for the creation url for this content type

                # Get the factory
                types_tool = getToolByName(self.context, 'portal_types')

                # Note: we don't check 'allowed' or 'available' here,
                # because these are slow. We assume the 'allowedTypes'
                # list has already performed the necessary calculations
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
                    url = '%s/createObject?type_name=%s' % (
                        baseUrl, quote_plus(typeId))
                return self.request.response.redirect(url)

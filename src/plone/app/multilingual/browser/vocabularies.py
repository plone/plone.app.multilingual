# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.multilingual.browser.utils import is_language_independent
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ITranslationManager
from plone.i18n.locales.interfaces import ILanguageAvailability
from zope.component import getGlobalSiteManager
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def untranslated_languages(context):
    language_tool = getToolByName(context, 'portal_languages')
    language_infos = language_tool.getAvailableLanguages()
    available_portal_languages = language_tool.supported_langs
    manager = ITranslationManager(context)
    translated_languages = manager.get_translated_languages()
    if is_language_independent(context):
        translated_languages = []
    languages = []
    for lang in available_portal_languages:
        if lang not in translated_languages:
            native = language_infos[lang].get('native', None)
            name = language_infos[lang].get('name', lang)
            languages.append(
                SimpleVocabulary.createTerm(lang, lang, native or name))
    return SimpleVocabulary(languages)


@provider(IContextSourceBinder)
def translated_languages(context):
    language_tool = getToolByName(context, 'portal_languages')
    language_infos = language_tool.getAvailableLanguages()
    manager = ITranslationManager(context)
    # take care to filter out translated contents
    # wich do no have supported language information
    translated_languages = [a
                            for a in manager.get_translated_languages()
                            if a in language_infos]
    content_language = ILanguage(context).get_language()
    if content_language in translated_languages:
        translated_languages.remove(content_language)
    languages = []
    for lang in translated_languages:
        native = language_infos[lang].get('native', None)
        name = language_infos[lang].get('name', lang)
        languages.append(
            SimpleVocabulary.createTerm(lang, lang, native or name))
    return SimpleVocabulary(languages)


@provider(IContextSourceBinder)
def translated_urls(context):
    manager = ITranslationManager(context)
    translated_languages = manager.get_translated_languages()
    content_language = ILanguage(context).get_language()
    if content_language in translated_languages:
        translated_languages.remove(content_language)
    languages = []
    for lang in translated_languages:
        translation = manager.get_restricted_translation(lang)
        if translation is not None:
            languages.append(
                SimpleVocabulary.createTerm(
                    lang, lang, translation.absolute_url()))
    return SimpleVocabulary(languages)


@provider(IContextSourceBinder)
def deletable_languages(context):
    manager = ITranslationManager(context)
    translated_languages = manager.get_translated_languages()
    language_tool = getToolByName(context, 'portal_languages')
    language_infos = language_tool.getAvailableLanguages()
    content_language = ILanguage(context).get_language()
    languages = []
    for lang in translated_languages:
        if lang not in content_language:
            native = language_infos[lang].get('native', None)
            name = language_infos[lang].get('name', lang)
            languages.append(
                SimpleVocabulary.createTerm(lang, lang, native or name))
    return SimpleVocabulary(languages)


def sort_key(language):
    return language[1]


@implementer(IVocabularyFactory)
class AllContentLanguageVocabulary(object):
    """ Vocabulary factory for all content languages in the portal.
    """

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ltool = getToolByName(context, 'portal_languages')
        gsm = getGlobalSiteManager()
        util = gsm.queryUtility(ILanguageAvailability)
        if ltool.use_combined_language_codes:
            languages = util.getLanguages(combined=True)
        else:
            languages = util.getLanguages()

        items = [
            (l, languages[l].get('native', languages[l].get('name', l)))
            for l in languages
        ]
        items.sort(key=sort_key)
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)

AllContentLanguageVocabularyFactory = AllContentLanguageVocabulary()


@implementer(IVocabularyFactory)
class AllAvailableLanguageVocabulary(object):
    """ Vocabulary factory for all enabled languages in the portal.
    """

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ltool = getToolByName(context, 'portal_languages')
        gsm = getGlobalSiteManager()
        util = gsm.queryUtility(ILanguageAvailability)
        if ltool.use_combined_language_codes:
            languages = util.getLanguages(combined=True)
        else:
            languages = util.getLanguages()

        supported_languages = ltool.supported_langs
        items = [
            (l, languages[l].get('native', languages[l].get('name', l)))
            for l in languages
            if l in supported_languages
        ]

        items.sort(key=sort_key)
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)

AllAvailableLanguageVocabularyFactory = AllAvailableLanguageVocabulary()

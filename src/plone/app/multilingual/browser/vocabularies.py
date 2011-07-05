from plone.multilingual.interfaces import ITranslationManager, ILanguage
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT


@grok.provider(IContextSourceBinder)
def untranslated_languages(context):
    language_tool = getToolByName(context, 'portal_languages')
    language_infos = language_tool.getAvailableLanguages()
    default_language = language_tool.getDefaultLanguage()
    available_portal_languages = language_tool.supported_langs
    manager = ITranslationManager(context)
    translated_languages = manager.get_translated_languages()
    content_language = ILanguage(context).get_language()
    filter_default = (content_language == LANGUAGE_INDEPENDENT)
    languages = []
    for lang in available_portal_languages:
        if lang not in translated_languages:
            if not (filter_default and lang == default_language):
                languages.append(SimpleVocabulary.createTerm(lang, lang, \
                    language_infos[lang].get('name', lang)))
    return SimpleVocabulary(languages)


@grok.provider(IContextSourceBinder)
def deletable_languages(context):
    manager = ITranslationManager(context)
    translated_languages = manager.get_translated_languages()
    language_tool = getToolByName(context, 'portal_languages')
    language_infos = language_tool.getAvailableLanguages()
    content_language = ILanguage(context).get_language()
    languages = []
    for lang in translated_languages:
        if lang not in content_language:
            languages.append(SimpleVocabulary.createTerm(lang, lang, \
                language_infos[lang].get('name', lang)))
    return SimpleVocabulary(languages)

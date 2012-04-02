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
def translated_languages(context):
    language_tool = getToolByName(context, 'portal_languages')
    language_infos = language_tool.getAvailableLanguages()
    manager = ITranslationManager(context)
    translated_languages = manager.get_translated_languages()
    content_language = ILanguage(context).get_language()
    if content_language in translated_languages:
        translated_languages.remove(content_language)
    languages = []
    for lang in translated_languages:
        languages.append(SimpleVocabulary.createTerm(lang, lang, \
            language_infos[lang].get('name', lang)))
    return SimpleVocabulary(languages)


@grok.provider(IContextSourceBinder)
def translated_urls(context):
    manager = ITranslationManager(context)
    translated_languages = manager.get_translated_languages()
    content_language = ILanguage(context).get_language()
    if content_language in translated_languages:
        translated_languages.remove(content_language)
    languages = []
    for lang in translated_languages:
        languages.append(SimpleVocabulary.createTerm(lang, lang, \
            manager.get_translation(lang).absolute_url()))
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



from plone.i18n.locales.interfaces import ILanguageAvailability
from zope.component import getGlobalSiteManager
from zope.i18nmessageid import Message, MessageFactory
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.CMFCore.utils import getToolByName

_ = MessageFactory('plone.app.multilingual')


def sort_key(language):
    return language[1]


class AllContentLanguageVocabulary(object):
    """Vocabulary factory for all content languages in the portal.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ltool = getToolByName(context, 'portal_languages')
        gsm = getGlobalSiteManager()
        util = gsm.queryUtility(ILanguageAvailability)
        if ltool.use_combined_language_codes:
            languages = util.getLanguages(combined=True)
        else:
            languages = util.getLanguages()

        items = [(l, languages[l].get('name', l)) for l in languages]
        items.sort(key=sort_key)
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)

AllContentLanguageVocabularyFactory = AllContentLanguageVocabulary()

class AllAvailableLanguageVocabulary(object):
    """Vocabulary factory for all enabled languages in the portal.
    """
    implements(IVocabularyFactory)

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
        items = [(l, languages[l].get('name', l)) for l in languages if l in supported_languages]

        items.sort(key=sort_key)
        items = [SimpleTerm(i[0], i[0], i[1]) for i in items]
        return SimpleVocabulary(items)

AllAvailableLanguageVocabularyFactory = AllAvailableLanguageVocabulary()


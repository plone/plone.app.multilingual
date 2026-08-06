from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import implementer

import json
import urllib


def google_translate(question, key, lang_target, lang_source):
    length = len(question)
    translated = ""
    url = "https://www.googleapis.com/language/translate/v2"
    temp_question = question
    while length > 400:
        temp_question = question[:399]
        index = temp_question.rfind(" ")
        temp_question = temp_question[:index]
        question = question[index:]
        length = len(question)
        data = {
            "key": key,
            "target": lang_target,
            "source": lang_source,
            "q": temp_question,
        }
        params = urllib.parse.urlencode(data)

        retorn = urllib.request.urlopen(url + "?" + params)
        translated += json.loads(retorn.read())["data"]["translations"][0][
            "translatedText"
        ]

    data = {
        "key": key,
        "target": lang_target,
        "source": lang_source,
        "q": temp_question,
    }
    params = urllib.parse.urlencode(data)

    retorn = urllib.request.urlopen(url + "?" + params)
    translated += json.loads(retorn.read())["data"]["translations"][0]["translatedText"]
    return translated


@implementer(IExternalTranslationService)
class GoogleTranslator:
    order = 100

    def is_available(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMultiLanguageExtraOptionsSchema, prefix="plone"
        )
        key = settings.google_translation_key
        return key is not None and len(key.strip()) > 0

    def available_languages(self):
        return []

    def translate_content(self, content, source_language, target_language):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMultiLanguageExtraOptionsSchema, prefix="plone"
        )
        key = settings.google_translation_key
        return google_translate(content, key, target_language, source_language)


def translate_text(original_text, source_language, target_language, service=None):
    """translate the text"""

    if original_text:
        # Initial shortcut: translate only non-empty values

        if service is not None:
            # if an specific adapter is requested, use it if available

            utility = getUtility(IExternalTranslationService, name=service)
            if not utility.is_available():
                return None

            utilities = [utility]

        else:
            # Get all available adapters
            utilities = [
                utility
                for name, utility in getUtilitiesFor(IExternalTranslationService)
                if utility.is_available()
            ]

        sorted_adapters = sorted(utilities, key=lambda x: int(x.order))

        for adapter in sorted_adapters:
            available_languages = adapter.available_languages()
            if (
                not available_languages
                or (source_language, target_language) in available_languages
            ):
                translation = adapter.translate_content(
                    original_text, source_language, target_language
                )

                if translation:
                    return translation

    return None

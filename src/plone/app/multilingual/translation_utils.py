from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual import logger
from plone.registry.interfaces import IRegistry
from zope.component import getUtilitiesFor
from zope.component import getUtility

import json
import urllib


def google_translate(question, key, lang_target, lang_source):
    # Put the API key in the URL, but the text payload in the body
    url = "https://translation.googleapis.com/language/translate/v2"

    data = {
        "q": question,
        "target": lang_target,
        "source": lang_source,
    }

    # URL encode the payload and convert to bytes for the POST request body
    encoded_data = urllib.parse.urlencode(data).encode("utf-8")

    # Pass the API key using the X-Goog-Api-Key header
    headers = {
        "X-Goog-Api-Key": key
    }

    # Supplying 'data' forces a POST request, bypassing URL length limits
    req = urllib.request.Request(url, data=encoded_data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["data"]["translations"][0]["translatedText"]
    except urllib.error.URLError as e:
        logger.error("Translation API Error: %s", str(e))
        return ""


class GoogleTranslatorFactory:
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


GoogleTranslator = GoogleTranslatorFactory()


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

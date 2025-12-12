from plone.app.multilingual.interfaces import IExternalTranslationService
from zope.component import getUtilitiesFor
from zope.component import getUtility


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

from plone.app.multilingual.interfaces import IExternalTranslationService
from zope.component import getUtilitiesFor
from zope.component import getUtility


def translate_text(original_text, source_language, target_language, service=None):
    """translate the text"""

    if original_text:
        # Initial shortcut: translate only non-empty values

        if service is not None:
            # if an specific adapter is requested, use it if available

            adapter = getUtility(IExternalTranslationService, name=service)
            if not adapter.is_available():
                return None

            adapters = [adapter]

        else:
            # Get all available adapters
            adapters = [
                adapter
                for _, adapter in getUtilitiesFor(IExternalTranslationService)
                if adapter.is_available()
            ]

        sorted_adapters = sorted(adapters, key=lambda x: x.order)

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

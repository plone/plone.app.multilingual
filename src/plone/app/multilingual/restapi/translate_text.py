from plone.app.multilingual.browser.translate import translate_text
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service


class TranslateTextService(Service):
    """this endpoints tries to translate the given text into the given language, using the previously registered ExternalTranslationServices"""

    def reply(self):
        body = json_body(self.request)
        source_language = body.get("source_language")
        target_language = body.get("target_language")
        original_text = body.get("original_text")
        service = body.get("service")

        translation = translate_text(
            original_text, source_language, target_language, service
        )

        if translation is None:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="Translation service not available",
                    message="The requested translation service is not available.",
                )
            )

        return {"data": translation}

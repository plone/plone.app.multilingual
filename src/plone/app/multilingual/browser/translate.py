from Acquisition import aq_inner
from plone.app.multilingual import _
from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.uuid.utils import uuidToObject
from plone.base.interfaces import ILanguage
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView
from zope.component import getUtilitiesFor
from zope.component import getUtility

import json


def translate_text(original_text, source_language, target_language, service=None):
    """translate the text"""

    if service is not None:
        # if an specific adapter is requested, use it if available

        adapter = getUtility(IExternalTranslationService, name=service)
        if not adapter.is_available():
            return None

        adapters = [adapter]

    else:

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


class gtranslation_service_dexterity(BrowserView):
    def __call__(self):
        if self.request.method != "POST" and not (
            "field" in self.request.form.keys()
            and "lang_source" in self.request.form.keys()
        ):
            return _("Need a field")
        else:
            context_uid = self.request.form.get("context_uid", None)
            if context_uid is None:
                # try with context if no translation uid is present
                manager = ITranslationManager(self.context)
            else:
                context = uuidToObject(context_uid)
                if context is not None:
                    manager = ITranslationManager(context)
                else:
                    manager = ITranslationManager(self.context)

            lang_target = ILanguage(self.context).get_language()
            lang_source = self.request.form["lang_source"]
            orig_object = manager.get_translation(lang_source)
            field = self.request.form["field"].split(".")[-1]
            if hasattr(orig_object, field):
                question = getattr(orig_object, field, "") or ""
                if hasattr(question, "raw"):
                    question = question.raw
            else:
                return _("Invalid field")

            translation = translate_text(question, lang_source, lang_target)
            if translation is None:
                return json.dumps({"data": ""})

            return json.dumps({"data": translation})


class TranslationForm(BrowserView):
    """Translation Form"""

    def __call__(self):
        language = self.request.get("language", None)
        if language:
            context = aq_inner(self.context)
            translation_manager = ITranslationManager(context)
            new_parent = translation_manager.add_translation_delegated(language)  # noqa
            baseUrl = new_parent.absolute_url()
            url = f"{baseUrl}/++addtranslation++{IUUID(context)}"
            return self.request.response.redirect(url)

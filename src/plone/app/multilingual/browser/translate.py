from Acquisition import aq_inner
from plone.app.multilingual import _
from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.uuid.utils import uuidToObject
from plone.base.interfaces import ILanguage
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView
from zope.component import getAdapters

import json


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

            registry = getUtility(IRegistry)
            settings = registry.forInterface(
                IMultiLanguageExtraOptionsSchema, prefix="plone"
            )
            lang_target = ILanguage(self.context).get_language()
            lang_source = self.request.form["lang_source"]
            orig_object = manager.get_translation(lang_source)
            field = self.request.form["field"].split(".")[-1]
            if hasattr(orig_object, field):
                question = getattr(orig_object, field, "")
                if hasattr(question, "raw"):
                    question = question.raw
            else:
                return _("Invalid field")

            adapters = [
                adapter
                for _, adapter in getAdapters(
                    (self.context,), IExternalTranslationService
                )
                if adapter.is_available()
            ]

            sorted_adapters = sorted(adapters, key=lambda x: x.order)

            for adapter in sorted_adapters:
                available_languages = adapter.available_languages()
                if (
                    not available_languages
                    or (lang_source, lang_target) in available_languages
                ):
                    translation = adapter.translate_content(
                        question, lang_source, lang_target
                    )

                    if translation:
                        return json.dumps({"data": translation})

            return json.dumps({"data": ""})


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

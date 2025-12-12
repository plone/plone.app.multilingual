from plone.app.multilingual import _
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.translation_utils import translate_text
from plone.app.uuid.utils import uuidToObject
from plone.base.interfaces import ILanguage
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service


class TranslationService(Service):

    def reply(self):
        body = json_body(self.request)
        if "field" not in body:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": _("Invalid parameter error"),
                    "message": _(
                        "The parameter ${field} is required.",
                        mapping={"field": "field"},
                    ),
                }
            }

        if "lang_source" not in body:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": _("Invalid parameter error"),
                    "message": _(
                        "The parameter ${field} is required.",
                        mapping={"field": "lang_source"},
                    ),
                }
            }

        context_uid = body.get("context_uid", None)
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
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": _("Invalid field error"),
                    "message": _(
                        "The field ${field} is not valid.",
                        mapping={"field": field},
                    ),
                }
            }

        translation = translate_text(question, lang_source, lang_target)
        if translation is None:
            return {"data": ""}

        return {"data": translation}

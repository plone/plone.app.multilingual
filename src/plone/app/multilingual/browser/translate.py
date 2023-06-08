from Acquisition import aq_inner
from plone.app.multilingual import _
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.uuid.utils import uuidToObject
from plone.base.interfaces import ILanguage
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView
from zope.component import getUtility

import json
import logging
import requests


logger = logging.getLogger(__name__)


def safe_get_chunk(text, length):
    # The idea of this function is to get the safest index on where to make
    # the cut when splitting HTML in chunks, so to not get a tag half-way
    # through (Like ['<a href="http://www.goog', 'le.com">Google</a>'])
    # Up to length size
    aux = text[:length]
    open_tag = aux.rfind("<")
    close_tag = aux.rfind(">")
    if close_tag < open_tag:
        # we have an opened tag
        return open_tag
    else:
        return length


def google_translate(question, key, lang_target, lang_source):
    translated = ""
    url = "https://translation.googleapis.com/language/translate/v2"
    temp_question = []
    aux = question
    size_per_chunk = 400  #  XXX:Cannot find doc about this, is this value ok?
    max_chunks = 128
    # You can provide up to 128 text chunks for translating
    # https://cloud.google.com/translate/docs/basic/translating-text
    while len(aux):
        if len(temp_question) < max_chunks:
            if len(aux) > size_per_chunk:
                idx = safe_get_chunk(aux, size_per_chunk)
                temp_question.append(aux[:idx])
                aux = aux[idx:]
            else:
                temp_question.append(aux)
                aux = ""

            if not aux or len(temp_question) == max_chunks:
                data = {
                    "key": key,
                    "target": lang_target,
                    "source": lang_source,
                    "q": temp_question,
                }
                # params = urllib.parse.urlencode(data)
                results = requests.post(url, data=data)
                if results.status_code != 200:
                    logger.error("Received an error from Google")
                    logger.error(results.text)
                    return json.dumps({"error": "Received error from Google, check logs"})
                else:
                    for translation in results.json()['data']['translations']:
                        translated += translation['translatedText']

                temp_question = []

    if len(temp_question):
        data = {
            "key": key,
            "target": lang_target,
            "source": lang_source,
            "q": temp_question,
        }
        # params = urllib.parse.urlencode(data)
        results = requests.post(url, data=data)
        if results.status_code != 200:
            logger.error("Received an error from Google")
            logger.error(results.text)
            return json.dumps({"error": "Received error from Google, check logs"})
        else:
            for translation in results.json()['data']['translations']:
                translated += translation['translatedText']

        temp_question = []

    return json.dumps({"data": translated})


class gtranslation_service_dexterity(BrowserView):
    def __call__(self):
        if self.request.method != "POST" and not (
            "field" in self.request.form.keys()
            and "lang_source" in self.request.form.keys()
        ):
            return _("Need a field")
        else:
            uid = self.request.get("uid")
            ctx = None
            if uid:
                ctx = uuidToObject(uid)
            if ctx is None:
                ctx = self.context
            manager = ITranslationManager(ctx)
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
            return google_translate(
                question, settings.google_translation_key, lang_target, lang_source
            )


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

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
import os
import requests


logger = logging.getLogger(__name__)


try:
    from google.cloud import translate_v3 as translate
    from google.oauth2 import service_account
    HAS_GCLOUD_V3 = True
except:
    HAS_GCLOUD_V3 = False
    logger.info("Cloud Translation V3 is not available.")


def safe_get_chunk(text, length):
    # The idea of this function is to get the safest index on where to make
    # the cut when splitting HTML in chunks, so to not get a tag half-way
    # through (Like ['<a href="http://www.goog', 'le.com">Google</a>'])
    # Up to length size
    returned_length = length
    aux = text[:length]
    open_tag = aux.rfind("<")
    close_tag = aux.rfind(">")
    if close_tag == -1 and open_tag >= 0:
        returned_length = open_tag
    elif close_tag < open_tag:
        # we have an opened tag
        returned_length = open_tag
    else:
        # Don't cut a word in the middle. Look for the last space
        returned_length = aux.rfind(" ")

    return returned_length


def google_translate_v2(question, key, lang_target, lang_source):
    translated = ""
    url = "https://translation.googleapis.com/language/translate/v2"
    temp_question = []
    aux = question
    size_per_chunk = 800  #  XXX:Cannot find doc about this, is this value ok?
    max_chunks = 6
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


def google_translate_v3(question, settings, lang_target, lang_source):
    credentials_file = os.getenv("GCLOUD_V3_JSON", None)
    if not credentials_file:
        logger.warning("GCLOUD_V3_JSON environment variable is not defined")
        return json.dumps({"error": "Google Cloud translation is misconfigured, please refer to package README."})

    credentials = service_account.Credentials.from_service_account_file(credentials_file)
    client = translate.TranslationServiceClient(credentials=credentials)
    project_id = credentials.project_id
    location = settings.gcloud_v3_location
    parent = f'projects/{project_id}/locations/{location}'
    translated = ""
    temp_question = []
    aux = question
    size_per_chunk = 800  #  XXX:Cannot find doc about this, is this value ok?
    max_chunks = 6
    glossary_id = settings.gcloud_v3_glossary
    glossary_config = None
    if glossary_id:
        logger.info(f"Will use glossary {glossary_id} for translating")
        glossary = client.glossary_path(
            project_id, location, glossary_id  # The location of the glossary
        )
        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)
    else:
        logger.info(f"Will not use a glossary for translating")

    # XXX: Cannot find doc for this, will leave it at the same limit as we have for basic.
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
                    "parent": parent,
                    "target_language_code": lang_target,
                    "source_language_code": lang_source,
                    "contents": temp_question,
                }
                if glossary_config:
                    data['glossary_config'] = glossary_config
                try:
                    response = client.translate_text(request=data)
                except Exception as e:
                    logger.error("Received an error from Google")
                    logger.error(e.message)
                    return json.dumps({"error": "Received error from Google, check logs"})

                if glossary_config:
                    for translation in response.glossary_translations:
                        translated += translation.translated_text
                else:
                    for translation in response.translations:
                        translated += translation.translated_text

                temp_question = []

    if len(temp_question):
        data = {
            "parent": parent,
            "target_language_code": lang_target,
            "source_language_code": lang_source,
            "contents": temp_question,
        }
        if glossary_config:
            data['glossary_config'] = glossary_config

        try:
            response = client.translate_text(request=data)
        except Exception as e:
            logger.error("Received an error from Google")
            logger.error(e.message)
            return json.dumps({"error": "Received error from Google, check logs"})

        if glossary_config:
            for translation in response.glossary_translations:
                translated += translation.translated_text
        else:
            for translation in response.translations:
                translated += translation.translated_text

        temp_question = []

    return json.dumps({"data": translated})


def google_translate(question, settings, lang_target, lang_source):
    use_v3 = settings.gcloud_use_v3
    results = ""
    if HAS_GCLOUD_V3 and use_v3:
        results = google_translate_v3(question, settings, lang_target, lang_source)
    else:
        key = settings.google_translation_key
        results = google_translate_v2(question, key, lang_target, lang_source)

    return results


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
                question, settings, lang_target, lang_source
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

# -*- coding: utf-8 -*-

import json
import urllib

from plone.app.multilingual.interfaces import (
    IExternalTranslationService,
    IMultiLanguageExtraOptionsSchema,
)
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, adapter
from zope.interface import implementer, Interface


@implementer(IExternalTranslationService)
@adapter(Interface)
class GoogleCloudTranslationAPI:
    """implement the external translation using Google Cloud Translation API"""

    order = 999

    def __init__(self, context):
        self.context = context

    def is_available(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMultiLanguageExtraOptionsSchema, prefix="plone"
        )
        key = settings.google_translation_key
        return key is not None and len(key.strip()) > 0

    def available_languages(self):
        # All languages are supported
        return []

    def translate_content(self, content, source_language, target_language):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMultiLanguageExtraOptionsSchema, prefix="plone"
        )

        question = content
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
                "key": settings.google_translation_key,
                "target": target_language,
                "source": source_language,
                "q": temp_question,
            }
            params = urllib.parse.urlencode(data)

            retorn = urllib.request.urlopen(url + "?" + params)
            translated += json.loads(retorn.read())["data"]["translations"][0][
                "translatedText"
            ]

        data = {
            "key": settings.google_translation_key,
            "target": target_language,
            "source": source_language,
            "q": temp_question,
        }
        params = urllib.parse.urlencode(data)

        retorn = urllib.request.urlopen(url + "?" + params)
        translated += json.loads(retorn.read())["data"]["translations"][0][
            "translatedText"
        ]
        return translated

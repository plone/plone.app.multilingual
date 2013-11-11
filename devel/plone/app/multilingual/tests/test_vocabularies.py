# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from plone.app.multilingual.browser.vocabularies import untranslated_languages
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING


class TestVocabularies(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        # Create language root folder for 'en'
        self.portal.portal_languages.supported_langs = ['en']
        self.portal.invokeFactory(type_name="Folder", id="en")
        self.portal['en'].setLanguage('en')

        # Create sample document in 'en' and index it into catalog
        content_id = self.portal['en'].invokeFactory(
            type_name="Document", id="sampledocument")
        self.content = self.portal['en'][content_id]
        notify(ObjectAddedEvent(self.content))

    def testContentLanguageIsInTheOnlySupportedLanguage(self):
        self.assertEquals(len(untranslated_languages(self.content)), 0)

    def testSupportingSomeMoreLanguages(self):
        self.portal.portal_languages.supported_langs = ['en', 'de', 'it', 'es']

        languages = untranslated_languages(self.content).by_token.keys()

        self.assertEquals(len(languages), 3)
        self.assertIn('de', languages)
        self.assertIn('es', languages)
        self.assertIn('it', languages)

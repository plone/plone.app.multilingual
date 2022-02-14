from plone.app.multilingual import api
from plone.app.multilingual.browser.vocabularies import untranslated_languages
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.interface import alsoProvides

import unittest


class TestVocabularies(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        self.portal = self.layer["portal"]

    def test_content_is_translated_into_all_languages(self):
        a_ac = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        api.translate(a_ac, "en")
        api.translate(a_ac, "es")

        self.assertEqual(len(untranslated_languages(a_ac)), 0)

    def test_content_is_not_translated_to_any_language(self):
        a_ac = createContentInContainer(self.portal, "Document", title="Test document")

        languages = untranslated_languages(a_ac).by_token.keys()

        self.assertEqual(len(languages), 3)
        self.assertIn("ca", languages)
        self.assertIn("es", languages)
        self.assertIn("en", languages)

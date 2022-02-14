from plone.app.multilingual import api
from plone.app.multilingual.browser.viewlets import AlternateLanguagesViewlet
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.interface import alsoProvides

import unittest


class TestAlternateLanguagesViewlet(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

    def test_alternates(self):
        # Create
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        # Translate
        a_en = api.translate(a_ca, "en")

        # Get the viewlet
        viewlet = AlternateLanguagesViewlet(a_en, self.request, None, None)
        viewlet.update()

        # Get translations
        translations = ITranslationManager(a_ca).get_translations()

        # Check translations
        self.assertEqual(len(viewlet.alternates), 2)
        for item in viewlet.alternates:
            self.assertIn(item["lang"], translations)
            self.assertEqual(item["url"], translations[item["lang"]].absolute_url())

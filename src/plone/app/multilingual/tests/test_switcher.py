from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.testing.zope import Browser
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides

import transaction
import unittest


class TestLanguageSwitcher(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        # Set test variables
        self.portal = self.layer["portal"]
        self.language_tool = getToolByName(self.portal, "portal_languages")
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

        # Add Indonesian as supported language, because this has corner cases:
        # it's LRF cannot have id "id", so it is "id-id".
        self.language_tool.addSupportedLanguage("id")
        multilingual_setup_tool = SetupMultilingualSite()
        multilingual_setup_tool.setupSite(self.portal)
        transaction.commit()

        # Setup testbrowser
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False

    def test_switcher_redirects_to_default_english(self):
        self.browser.open(self.portal_url)
        self.assertEqual(self.browser.url, self.portal_url + "/en")
        self.assertEqual(self.browser.cookies["I18N_LANGUAGE"], "en")

    def test_switcher_redirects_to_default_indonesian(self):
        self.language_tool.setDefaultLanguage("id")
        transaction.commit()
        self.browser.open(self.portal_url)
        self.assertEqual(self.browser.url, self.portal_url + "/id-id")
        self.assertEqual(self.browser.cookies["I18N_LANGUAGE"], "id")

    def test_switcher_redirects_to_preferred_catalan(self):
        # Tell Plone that we prefer Catalan.
        self.browser.open(self.portal_url + "/ca?set_language=ca")
        # Go to the site root.
        self.browser.open(self.portal_url)
        # We get redirected to our preferred language root folder.
        self.assertEqual(self.browser.url, self.portal_url + "/ca")
        self.assertEqual(self.browser.cookies["I18N_LANGUAGE"], "ca")

    def test_switcher_redirects_to_preferred_indonesian(self):
        # Tell Plone that we prefer Indonesian.
        self.browser.open(self.portal_url + "/id-id?set_language=id")
        # Go to the site root.
        self.browser.open(self.portal_url)
        # We get redirected to our preferred language root folder.
        self.assertEqual(self.browser.url, self.portal_url + "/id-id")
        self.assertEqual(self.browser.cookies["I18N_LANGUAGE"], "id")

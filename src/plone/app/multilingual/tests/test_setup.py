from Acquisition import aq_base
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.browser.vocabularies import (  # noqa: E501
    AllContentLanguageVocabulary,
)
from plone.app.multilingual.interfaces import ATTRIBUTE_NAME
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.testing import PAM_INTEGRATION_PRESET_TESTING
from plone.app.multilingual.testing import PAM_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides

import unittest


class TestSetupMultilingualSite(unittest.TestCase):
    """Testing multilingual site without predefined languages."""

    layer = PAM_INTEGRATION_TESTING

    def setUp(self):
        """Setting up the test."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.language_tool = getToolByName(self.portal, "portal_languages")
        self.languages = self.language_tool.getSupportedLanguages()
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

    def test_single_language(self):
        """Only one language is set."""
        self.assertEqual(len(self.languages), 1)

    def test_portal_has_tg_attribute(self):
        """The site root should have the TG attribute set after installing"""
        tg_attribute = getattr(aq_base(self.portal), ATTRIBUTE_NAME, None)
        self.assertIsNotNone(tg_attribute)

    def test_no_languagefolder_created(self):
        """On a single language no folder creation is done."""
        portal_objects = self.portal.objectIds()
        for lang in self.languages:
            self.assertNotIn(lang, portal_objects)

    def test_all_supported_languages(self):
        """There was a language which code is 'id'.
        This broke the root language folder setup process.
        To get rid of that the folder is 'id-id'.
        """
        all_langs = AllContentLanguageVocabulary()(self.portal)
        for lang in all_langs:
            self.language_tool.addSupportedLanguage(lang.value)

        workflow_tool = getToolByName(self.portal, "portal_workflow")
        workflow_tool.setDefaultChain("simple_publication_workflow")

        setup_tool = SetupMultilingualSite()
        setup_tool.setupSite(self.portal)

        portal_objects = self.portal.objectIds()

        for lang in all_langs.by_value.keys():
            if lang == "id":
                self.assertIn("id-id", portal_objects)
            else:
                self.assertIn(lang, portal_objects)

    def test_type_of_language_folders(self):
        """The created objects have to be 'Language Root Folder'."""
        all_langs = AllContentLanguageVocabulary()(self.portal)
        for lang in all_langs:
            self.language_tool.addSupportedLanguage(lang.value)

        workflow_tool = getToolByName(self.portal, "portal_workflow")
        workflow_tool.setDefaultChain("simple_publication_workflow")

        setup_tool = SetupMultilingualSite()
        setup_tool.setupSite(self.portal)

        for lang in all_langs.by_value.keys():
            if lang == "id":
                self.assertEqual(self.portal.get("id-id").portal_type, "LRF")
            else:
                self.assertEqual(self.portal.get(lang).portal_type, "LRF")


class TestSetupMultilingualPresetSite(unittest.TestCase):
    """Testing multilingual site with predefined languages."""

    layer = PAM_INTEGRATION_PRESET_TESTING

    def setUp(self):
        """Setting up the test."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.language_tool = getToolByName(self.portal, "portal_languages")
        self.languages = self.language_tool.getSupportedLanguages()
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

    def test_language_folders_created(self):
        """Available languages are: 'en', 'ca', 'es'.
        After setup has run there should be
        new objects in the portal named after the languages.
        """
        portal_objects = self.portal.objectIds()
        for lang in self.languages:
            self.assertIn(lang, portal_objects)

    def test_type_of_language_folders(self):
        """The created objects have to be 'Language Root Folder'."""
        for lang in self.languages:
            self.assertEqual(self.portal.get(lang).portal_type, "LRF")

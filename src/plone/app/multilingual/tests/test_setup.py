from Acquisition import aq_base
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.browser.vocabularies import AllContentLanguageVocabulary
from plone.app.multilingual.interfaces import ATTRIBUTE_NAME
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.multilingual.testing import PAM_INTEGRATION_PRESET_TESTING
from plone.app.multilingual.testing import PAM_INTEGRATION_TESTING
from plone.app.multilingual.testing import VOLTO_MULTILINGUAL_INTEGRATION_TESTING
from plone.base.interfaces import ILanguage
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
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
        """There is a language which code is 'id'.

        This is Indonesian, or Bahasa Indonesia in that language.
        This broke the root language folder setup process.
        To get rid of that the folder is 'id-id'.
        Here we test all languages, to be sure we catch such a corner case.

        Also, the created objects have to be 'Language Root Folder'.
        """
        all_langs = AllContentLanguageVocabulary()(self.portal)
        # We used to call self.language_tool.addSupportedLanguage for each
        # language value, but that would make over 400 registry modifications,
        # each of which resulting in an event notification that triggers
        # our `change_language_settings` subscriber, which calls
        # SetupMultilingualSite.setupSite.  Doing this 400 times takes
        # several minutes.  So instead we compile the list and set the record
        # once.
        alist = self.language_tool.settings.available_languages[:]
        for lang in all_langs:
            alist.append(lang.value)
        self.language_tool.settings.available_languages = alist

        workflow_tool = getToolByName(self.portal, "portal_workflow")
        workflow_tool.setDefaultChain("simple_publication_workflow")

        setup_tool = SetupMultilingualSite()
        # Note: since we have 400 languages, the next call can take 10
        # seconds or more.
        setup_tool.setupSite(self.portal)

        portal_objects = self.portal.objectIds()

        for lang in all_langs.by_value.keys():
            # Special handling for Indonesian.
            folder_id = "id-id" if lang == "id" else lang
            self.assertIn(folder_id, portal_objects)
            folder = self.portal[folder_id]
            self.assertEqual(folder.portal_type, "LRF")
            self.assertEqual(ILanguage(folder).get_language(), lang)

    def test_lrf_has_locking_behavior(self):
        """LRF type should have plone.locking behavior enabled."""
        portal_types = getToolByName(self.portal, "portal_types")
        lrf_type = portal_types.get("LRF")

        # Get the behaviors for LRF type
        behaviors = getattr(lrf_type, "behaviors", ())

        # Check if plone.locking behavior is present
        self.assertIn(
            "plone.locking",
            behaviors,
            "LRF type should have plone.locking behavior enabled",
        )

    def test_lrf_does_not_have_volto_blocks_behavior(self):
        """LRF type should NOT have volto.blocks behavior without Volto installed."""
        portal_types = getToolByName(self.portal, "portal_types")
        lrf_type = portal_types.get("LRF")

        behaviors = getattr(lrf_type, "behaviors", ())

        self.assertNotIn(
            "volto.blocks",
            behaviors,
            "LRF type should not have volto.blocks behavior without Volto",
        )


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


class TestSetupWithVolto(unittest.TestCase):
    """Testing multilingual site with plone.volto installed first.

    This test verifies that installing plone.app.multilingual:default
    after plone.volto:default works correctly.
    """

    layer = VOLTO_MULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        """Setting up the test."""
        from plone.app.testing import applyProfile

        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

        # Install plone.app.multilingual after plone.volto is already installed
        applyProfile(self.portal, "plone.app.multilingual:default")

    def test_volto_is_installed(self):
        """plone.volto should be installed."""
        # Check if volto browserlayer is registered
        from plone.browserlayer.utils import registered_layers
        from plone.volto.interfaces import IPloneVoltoCoreLayer

        self.assertIn(IPloneVoltoCoreLayer, registered_layers())

    def test_pam_is_installed(self):
        """plone.app.multilingual should be installed after volto."""
        portal_types = getToolByName(self.portal, "portal_types")
        # LRF type should exist
        self.assertIn("LRF", portal_types.objectIds())

    def test_lrf_has_volto_blocks_behavior(self):
        """LRF type should have volto.blocks behavior when Volto is installed first."""
        portal_types = getToolByName(self.portal, "portal_types")
        lrf_type = portal_types.get("LRF")

        behaviors = getattr(lrf_type, "behaviors", ())

        self.assertIn(
            "volto.blocks",
            behaviors,
            "LRF type should have volto.blocks behavior when Volto is installed first",
        )


class TestSetupMultilingualFunctional(unittest.TestCase):
    """Testing multilingual site functional."""

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        """Setting up the test."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.language_tool = getToolByName(self.portal, "portal_languages")
        self.registry = getUtility(IRegistry)
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

    def test_adding_language_immediately_creates_lrf(self):
        """Test that adding a language in the registry immediately creates the LRF.
        This is what fails currently as described in issue #543.
        """
        # Initially we have en, ca, es (from PAM_FUNCTIONAL_TESTING which uses MULTIPLE_LANGUAGES_LAYER)
        self.assertEqual(
            self.language_tool.getSupportedLanguages(),
            ["en", "ca", "es"],
        )
        self.assertNotIn("it", self.portal.objectIds())

        # Now we add 'it' to the supported languages via registry
        # This should trigger the change_language_settings subscriber
        languages = self.registry["plone.available_languages"]
        if "it" not in languages:
            new_languages = list(languages) + ["it"]
            self.registry["plone.available_languages"] = new_languages

        # Check if the 'it' LRF was created
        self.assertIn(
            "it",
            self.portal.objectIds(),
            "The 'it' LRF should have been created immediately",
        )
        self.assertEqual(self.portal["it"].portal_type, "LRF")
        self.assertEqual(ILanguage(self.portal["it"]).get_language(), "it")

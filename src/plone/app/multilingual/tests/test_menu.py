from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.testing._z2_testbrowser import Browser
from zope.interface import alsoProvides

import transaction
import unittest


class TestMenu(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        # Setup test browser
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            f"Basic {SITE_OWNER_NAME:s}:{SITE_OWNER_PASSWORD:s}",
        )

        # Create sample document in 'en' and index it into catalog
        self.a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        transaction.commit()

    def test_menu_is_visible(self):
        self.browser.open(self.a_ca.absolute_url())
        # 'Translate' in Catalan:
        self.assertIn("Tradueix", self.browser.contents)

    def test_menu_contains_translatable_entries(self):
        self.browser.open(self.a_ca.absolute_url())
        self.assertIn("translate_into_es", self.browser.contents)
        self.assertIn("translate_into_en", self.browser.contents)

    def test_menu_does_not_contain_translated_entries(self):
        self.browser.open(self.a_ca.absolute_url())
        self.assertNotIn("translate_into_ca", self.browser.contents)

    def test_menu_does_not_appear_without_ITranslatable(self):
        self.assertFalse(ITranslatable.providedBy(self.portal))
        self.browser.open(self.portal.absolute_url() + "/folder_listing")
        self.assertNotIn("Translate", self.browser.contents)

    def test_menu_is_visible_on_folder_default_page(self):
        createContentInContainer(self.portal["ca"], "Folder", title="Test folder")
        createContentInContainer(
            self.portal["ca"]["test-folder"], "Document", title="Test document"
        )
        self.portal["ca"]["test-folder"].setDefaultPage("test-document")

        transaction.commit()

        self.browser.open(self.portal["ca"]["test-folder"].absolute_url())
        self.assertIn("test-folder/@@create_translation", self.browser.contents)
        self.assertIn("test-document/@@create_translation", self.browser.contents)

    def test_menu_is_not_visible_without_permission(self):
        # Add a new user without Owner, Editor or Manager role on
        # self.a_ca document
        self.portal.portal_registration.addMember(
            "a_user",
            "a_password",
            [
                "Reader",
                "Contributor",
                "Reviewer",
            ],
        )

        transaction.commit()

        browser = Browser(self.layer["app"])
        browser.addHeader("Authorization", "Basic a_user:a_password")

        browser.open(self.a_ca.absolute_url())
        self.assertNotIn("plone-contentmenu-multilingual", browser.contents)

# -*- coding: utf-8 -*-
import transaction
import unittest2 as unittest
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.testing._z2_testbrowser import Browser


class TestMenu(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        # Setup test browser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization', 'Basic %s:%s' % (
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD))

        # Create sample document in 'en' and index it into catalog
        self.a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        transaction.commit()

    def test_menu_is_visible(self):
        self.browser.open(self.a_ca.absolute_url())
        self.assertIn('Translate', self.browser.contents)

    def test_menu_contains_translatable_entries(self):
        self.browser.open(self.a_ca.absolute_url())
        self.assertIn('translate_into_es', self.browser.contents)
        self.assertIn('translate_into_en', self.browser.contents)

    def test_menu_does_not_contain_translated_entries(self):
        self.browser.open(self.a_ca.absolute_url())
        self.assertNotIn('translate_into_ca', self.browser.contents)

    def test_menu_does_not_appear_without_ITranslatable(self):
        self.browser.open(self.portal.absolute_url() + '/folder_listing')
        self.assertNotIn('Translate', self.browser.contents)

    def test_menu_is_visible_on_folder_default_page(self):
        createContentInContainer(
            self.portal['ca'], 'Folder', title=u"Test folder")
        createContentInContainer(
            self.portal['ca']['test-folder'], 'Document',
            title=u"Test document")
        self.portal['ca']['test-folder'].setDefaultPage('test-document')

        transaction.commit()

        self.browser.open(
            self.portal['ca']['test-folder'].absolute_url())
        self.assertIn(
            "test-folder/@@create_translation", self.browser.contents)
        self.assertIn(
            "test-document/@@create_translation", self.browser.contents)

# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
import unittest2 as unittest
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing._z2_testbrowser import Browser


class TestMenu(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        # Setup test browser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization', 'Basic %s:%s' % (
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD))

        # Configure languages
        self.portal_url = self.portal.absolute_url()
        self.lang_tool = getToolByName(self.portal, 'portal_languages')
        self.lang_tool.supported_langs = ['en', 'it', 'de']

        # Create language root folder for 'en'
        self.portal.invokeFactory(type_name="Folder", id="en")
        self.container = self.portal['en']
        self.container.setLanguage('en')

        # Create sample document in 'en' and index it into catalog
        content_id = self.container.invokeFactory(
            type_name="Document", id="sampledocument-form")
        self.content = self.container[content_id]
        self.content.setLanguage('en')
        notify(ObjectAddedEvent(self.content))

        import transaction
        transaction.commit()

    def testMenuIsVisible(self):
        self.browser.open(self.content.absolute_url())
        self.assertIn('Translate', self.browser.contents)

    def testMenuContainsTranslatableEntries(self):
        self.browser.open(self.content.absolute_url())
        self.assertIn('translate_into_it', self.browser.contents)
        self.assertIn('translate_into_de', self.browser.contents)

    def testMenuDoesNotContainTranslatedEntries(self):
        self.browser.open(self.content.absolute_url())
        self.assertNotIn('translate_into_en', self.browser.contents)

    def testMenuDoesNotAppearWithoutITranslatable(self):
        self.browser.open(self.portal.absolute_url() + '/folder_listing')
        self.assertNotIn('Translate', self.browser.contents)

    def testMenuIsVisibleOnFolderDefaultPage(self):
        self.container.setDefaultPage('sampledocument-form')

        import transaction
        transaction.commit()

        self.browser.open(self.container.absolute_url())
        self.assertIn("en/@@create_translation", self.browser.contents)
        self.assertIn("sampledocument-form/@@create_translation",
                      self.browser.contents)

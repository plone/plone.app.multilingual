import unittest2 as unittest
from AccessControl import Unauthorized

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ILanguage
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.browser.utils import multilingualMoveObject


import transaction


class PAMFuncTestHelperViews(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.portal_url = self.portal.absolute_url()
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

    def test_universal_link_view(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))
        self.browser.addHeader('Accept-Language', 'ca')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        doc1 = makeContent(self.portal, 'Document', id='doc1')
        doc1.setLanguage('en')
        doc1_ca = makeTranslation(doc1, 'ca')
        doc1_ca.edit(title="Foo", language='ca')
        doc1_es = makeTranslation(doc1, 'es')
        doc1_es.edit(title="Foo", language='es')
        transaction.commit()

        self.browser.open(doc1.absolute_url())
        self.browser.getLink("Universal Link").click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/doc1-ca')


class PAMIntTestHelperViews(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.language_tool = getToolByName(self.portal, 'portal_languages')
        self.language_tool.addSupportedLanguage('ca')
        self.language_tool.addSupportedLanguage('es')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

    def test_move_content_proper_language_folder(self):

        self.assertTrue(getattr(self.portal, 'en'))

        self.portal.en.invokeFactory('Folder', 'new1', title=u"An archetypes based folder")
        new1 = self.portal.en['new1']
        new1.invokeFactory('Document', 'doc1', title=u"An archetypes based doc")
        transaction.commit()

        # Change the content language of the created folder to 'ca'
        multilingualMoveObject(new1, 'ca')
        self.assertTrue(self.portal.ca.new1)
        self.assertTrue(self.portal.ca.new1.doc1)
        self.assertEqual(ILanguage(self.portal.ca.new1).get_language(), 'ca')
        self.assertEqual(ILanguage(self.portal.ca.new1.doc1).get_language(), 'ca')

    def test_move_content_proper_language_folder_existing_translation_inside(self):

        self.assertTrue(getattr(self.portal, 'en'))

        self.portal.en.invokeFactory('Folder', 'new11', title=u"An archetypes based folder")
        new11 = self.portal.en['new11']
        new11.invokeFactory('Document', 'doc11', title=u"An archetypes based doc")
        doc1_ca = makeTranslation(self.portal.en.new11.doc11, 'ca')
        doc1_ca.edit(title="Foo", language='ca')
        self.assertTrue(self.portal.ca.doc11)
        transaction.commit()

        # Change the content language of the created folder to 'ca'

        multilingualMoveObject(new11, 'ca')
        self.assertTrue(self.portal.ca.new11)
        self.assertTrue(self.portal.ca.new11.doc11)
        self.assertEqual(ITranslationManager(self.portal.ca.new11.doc11).get_translations(),
                         {'ca': self.portal.ca.new11.doc11})
        self.assertEqual(ITranslationManager(doc1_ca).get_translations(),
                         {'ca': doc1_ca})
        self.assertEqual(ILanguage(self.portal.ca.new11).get_language(), 'ca')
        self.assertEqual(ILanguage(self.portal.ca.new11.doc11).get_language(), 'ca')

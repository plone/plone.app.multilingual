import unittest2 as unittest
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING
from AccessControl import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.testing import applyProfile

from Products.LinguaPlone.tests.utils import makeContent, makeTranslation
from Products.LinguaPlone.interfaces import ITranslatable
from plone.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled


class migrationLPToPAM(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneAppMultilingualInstalled)
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

    def testSupportedLanguages(self):
        language_tool = getToolByName(self.portal, 'portal_languages')
        self.failUnless(language_tool.getSupportedLanguages(), ['en', 'ca', 'es'])

    def testMigration(self):
        self.doc1 = makeContent(self.portal, 'Document', id='doc1')
        self.doc1.setLanguage('en')
        self.doc1_ca = makeTranslation(self.doc1, 'ca')
        self.doc1_ca.edit(title="Foo", language='ca')
        self.doc1_es = makeTranslation(self.doc1, 'es')
        self.doc1_es.edit(title="Foo", language='es')
        migration_view = getMultiAdapter((self.portal, self.request), name='migration-view')
        migration_view()
        self.assertEqual(ITranslationManager(self.doc1).get_translations(),
            {'ca': self.doc1_ca, 'en': self.doc1, 'es': self.doc1_es})

    def testRelocator(self):
        self.doc1 = makeContent(self.portal, 'Document', id='doc2')
        self.doc1.setLanguage('en')
        self.doc1_ca = makeTranslation(self.doc1, 'ca')
        self.doc1_ca.edit(title="Foo", language='ca')
        self.doc1_es = makeTranslation(self.doc1, 'es')
        self.doc1_es.edit(title="Foo", language='es')
        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        relocator_view = getMultiAdapter((self.portal, self.request),
                                          name='relocateContentByLanguage')
        relocator_view()

        self.assertTrue(getattr(self.portal.en, 'doc2', False))
        self.assertTrue(getattr(self.portal.es, 'doc2-es', False))
        self.assertTrue(getattr(self.portal.ca, 'doc2-ca', False))

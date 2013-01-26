import unittest2 as unittest
import transaction
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
        #language_tool.addSupportedLanguage('es')

    def testSupportedLanguages(self):
        language_tool = getToolByName(self.portal, 'portal_languages')
        self.failUnless(language_tool.getSupportedLanguages(), ['en', 'ca'])

    def testRelocatorOfMisplacedContent(self):
        self.a_en = makeContent(self.portal, 'Folder', id='a_en')
        self.a_en.edit(language='en')
        self.a_1_1_ca = makeContent(self.a_en, 'Folder', id='a_1_1_ca')
        self.a_1_1_ca.edit(language='ca')
        self.a_2_1_en = makeContent(self.a_1_1_ca, 'Document', id='a_2_1_en')
        self.a_2_1_en.edit(language='en')
        self.a_2_2_ca = makeContent(self.a_1_1_ca, 'Document', id='a_2_2_ca')
        self.a_2_2_ca.edit(language='ca')
        self.a_1_2_en = makeContent(self.a_en, 'Folder', id='a_1_2_en')
        self.a_1_2_en.edit(language='en')

        self.b_ca = makeContent(self.portal, 'Folder', id='b_ca')
        self.b_ca.edit(language='ca')
        self.b_1_1_en = makeContent(self.b_ca, 'Folder', id='b_1_1_en')
        self.b_1_1_en.edit(language='en')
        self.b_2_1_en = makeContent(self.b_1_1_en, 'Document', id='b_2_1_en')
        self.b_2_1_en.edit(language='en')
        self.b_2_1_ca = makeTranslation(self.b_2_1_en, 'ca')
        transaction.commit()
        self.b_2_1_ca.edit(id='b_2_1_ca', language='ca')

        relocator_view = getMultiAdapter((self.portal, self.request),
                                          name='relocate-content')
        relocator_view.step1andstep2()

        self.assertTrue(getattr(self.portal, 'b_1_1_en', False))
        self.assertTrue(getattr(self.portal, 'a_1_1_ca', False))
        self.assertEqual(self.a_en.objectIds(), ['a_1_2_en', 'a_2_1_en'])
        self.assertEqual(self.a_en.b_1_1_en.objectIds(), ['b_2_1_en'])
        self.assertEqual(self.b_ca.objectIds(), ['b_2_1_ca'])
        self.assertEqual(self.b_ca.a_1_1_ca.objectIds(), ['a_2_2_ca'])

        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        relocator_view.step3()

        # Test that the resultant Plone site is 'clean'
        rlfs = [rlf for rlf in self.portal.objectIds() if ITranslatable.providedBy(getattr(self.portal, rlf))]
        self.assertEqual(rlfs, ['en', 'ca', 'shared'])

    def testMigration(self):
        self.doc1 = makeContent(self.portal, 'Document', id='doc1')
        self.doc1.setLanguage('en')
        self.doc1_ca = makeTranslation(self.doc1, 'ca')
        self.doc1_ca.edit(title="Foo", language='ca')
        self.doc1_es = makeTranslation(self.doc1, 'es')
        self.doc1_es.edit(title="Foo", language='es')
        migration_view = getMultiAdapter((self.portal, self.request), name='transfer-lp-catalog')
        migration_view()
        self.assertEqual(ITranslationManager(self.doc1).get_translations(),
                         {'ca': self.doc1_ca,
                          'en': self.doc1,
                          'es': self.doc1_es}
                        )

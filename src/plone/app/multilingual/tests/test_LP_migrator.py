import unittest2 as unittest
from plone.app.multilingual.tests._testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING
from AccessControl import Unauthorized
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.testing import applyProfile

from Products.LinguaPlone.tests.utils import makeContent, makeTranslation
from Products.LinguaPlone.interfaces import ITranslatable


class migrationLPToPAM(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

        self.doc1 = makeContent(self.portal, 'Document', id='doc1')
        self.doc1.setLanguage('en')
        self.doc1_ca = makeTranslation(self.doc1, 'ca')
        self.doc1_ca.setLanguage('ca')
        self.doc1_es = makeTranslation(self.doc1, 'es')
        self.doc1_es.setLanguage('es')

    def testSupportedLanguages(self):
        language_tool = getToolByName(self.portal, 'portal_languages')
        self.failUnless(language_tool.getSupportedLanguages(), ['en', 'ca', 'es'])

    def testMigration(self):
        pc = getToolByName(self.portal, 'portal_catalog')
        import ipdb;ipdb.set_trace()
        results = pc.searchResults(object_provides=ITranslatable.__identifier__)
        print results

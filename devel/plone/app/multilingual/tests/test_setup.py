import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from plone.testing.z2 import Browser

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING
from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.app.multilingual.browser.vocabularies import AllContentLanguageVocabulary
from plone.app.multilingual.browser.setup import SetupMultilingualSite

import transaction


class SetupViews(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_add_all_supported_languages(self):
        """ There was a language which code is 'id'
            and it broke the root language folder setup process
        """
        language_tool = getToolByName(self.portal, 'portal_languages')
        for lang in AllContentLanguageVocabulary()(self.portal):
            language_tool.addSupportedLanguage(lang.value)

        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')

        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

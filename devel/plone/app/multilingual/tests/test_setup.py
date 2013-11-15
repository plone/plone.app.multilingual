# -*- coding: utf-8 -*-
import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from plone.app.multilingual.testing import PAM_INTEGRATION_TESTING
from plone.app.multilingual.browser.vocabularies import\
    AllContentLanguageVocabulary
from plone.app.multilingual.browser.setup import SetupMultilingualSite


class TestSetupMultilingualSite(unittest.TestCase):

    layer = PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_add_all_supported_languages(self):
        """There was a language which code is 'id' and it broke the root
        language folder setup process
        """
        language_tool = getToolByName(self.portal, 'portal_languages')
        for lang in AllContentLanguageVocabulary()(self.portal):
            language_tool.addSupportedLanguage(lang.value)

        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')

        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        for lang in AllContentLanguageVocabulary()(self.portal):
            if lang.value == 'id':
                self.assertIn('id-id', self.portal.objectIds())
            else:
                self.assertIn(lang.value, self.portal.objectIds())

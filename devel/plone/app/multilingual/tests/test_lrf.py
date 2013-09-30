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

from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import (
    IPloneAppMultilingualInstalled,
    ILanguage,
    ITranslationManager
    )


class test_real_lrf(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneAppMultilingualInstalled)
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')

        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        # self.a_ca = makeContent(self.portal.ca, 'dxdoc', id='a_ca')

    def test_shared_content(self):
        self.root_a_ca = makeContent(self.portal, 'dxdoc', id='a_ca')

        # Check shared is there
        self.assertTrue(self.root_a_ca == self.portal.ca.a_ca)
        self.assertTrue(self.root_a_ca == self.portal.es.a_ca)

        # Check remove root from lrf and catalog update

        from OFS.event import ObjectWillBeRemovedEvent
        from zope.event import notify

        notify(ObjectWillBeRemovedEvent(self.portal.a_ca))
        self.portal.manage_delObjects(self.root_a_ca.id)

        self.assertTrue('a_ca' not in self.portal.ca)

    def test_shared_catalog_content(self):
        self.root_a_ca = makeContent(self.portal, 'dxdoc', id='a_ca')

        elements = self.portal.portal_catalog.searchResults(id='a_ca')

        # Check catalog on lrf is indexed
        self.assertTrue(len(elements) == 4)

        # Check remove root from lrf and catalog update

        from OFS.event import ObjectWillBeRemovedEvent
        from zope.event import notify

        notify(ObjectWillBeRemovedEvent(self.portal.a_ca))
        self.portal.manage_delObjects(self.root_a_ca.id)

        elements = self.portal.portal_catalog.searchResults(id='a_ca')

        # Check catalog on lrf is indexed
        self.assertTrue(len(elements) == 0)


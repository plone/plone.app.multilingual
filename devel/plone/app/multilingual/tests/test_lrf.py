import unittest2 as unittest
import transaction
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING
from AccessControl import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.testing import applyProfile
from plone.testing.z2 import Browser

from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import (
    IPloneAppMultilingualInstalled,
    ILanguage,
    ITranslationManager
    )
from plone.app.multilingual.browser.utils import multilingualMoveObject
from plone.app.multilingual.browser.utils import is_shared


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

    def test_uuid_shared(self):
        self.root_a_ca = makeContent(self.portal, 'dxdoc', id='a_ca')
        
        from plone.uuid.interfaces import IUUID

        rootuuid = IUUID(self.root_a_ca)
        shareduuid = IUUID(self.portal.ca.a_ca)
        self.assertTrue(rootuuid + '-ca' == shareduuid)

    def test_shared_to_lrf(self):
        self.root_a_ca = makeContent(self.portal, 'dxdoc', id='a_ca')

        from plone.uuid.interfaces import IUUID
        old_uuid = IUUID(self.root_a_ca)
        # The ghost is ghost
        self.assertTrue(is_shared(self.portal.ca.a_ca))

        # Check is in the catalog 
        brains = self.portal.portal_catalog.searchResults(UID=old_uuid)
        self.assertTrue(len(brains) == 1)
        self.assertTrue(brains[0].getPath() == '/plone/a_ca')

        brains = self.portal.portal_catalog.searchResults(UID=old_uuid + '-ca')
        self.assertTrue(len(brains) == 1)
        self.assertTrue(brains[0].getPath() == '/plone/ca/a_ca')

        brains = self.portal.portal_catalog.searchResults(UID=old_uuid + '-es')
        self.assertTrue(len(brains) == 1)
        self.assertTrue(brains[0].getPath() == '/plone/es/a_ca')

        new_object = multilingualMoveObject(self.portal.ca.a_ca, 'ca')
        # check that the old and the new uuid are the same
        new_uuid = IUUID(self.portal.ca.copy_of_a_ca)
        self.assertTrue(old_uuid, new_uuid)
        self.assertFalse(is_shared(new_object))

        # check portal_catalog is updated

        brains = self.portal.portal_catalog.searchResults(UID=old_uuid)
        self.assertTrue(len(brains) == 1)
        self.assertTrue(brains[0].getPath() == '/plone/ca/copy_of_a_ca')

        brains = self.portal.portal_catalog.searchResults(UID=old_uuid + '-ca')
        self.assertTrue(len(brains) == 0)

        brains = self.portal.portal_catalog.searchResults(UID=old_uuid + '-es')
        self.assertTrue(len(brains) == 0)

        # Check which translations it have
        self.failUnless(ITranslationManager(new_object).get_translations(), {'ca': new_object})
        ITranslationManager(new_object).add_translation('es')
        self.failUnless(ITranslationManager(new_object).get_translations(), {'ca': new_object, 'es': self.portal.es.copy_of_a_ca})

        self.assertFalse(is_shared(self.portal.es.copy_of_a_ca))

# -*- coding: utf-8 -*-
from OFS.event import ObjectWillBeRemovedEvent
from plone.uuid.interfaces import IUUID

import unittest2 as unittest
from zope.event import notify

from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.browser.utils import multilingualMoveObject
from plone.app.multilingual.browser.utils import is_shared
from plone.dexterity.utils import createContentInContainer


class TestLanguageRootFolder(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_shared_content(self):
        # Create shared document
        createContentInContainer(
            self.portal, 'Document', title=u"Test document")

        # Check shared document is there
        self.assertEqual(self.portal['test-document'],
                         self.portal.ca['test-document'])
        self.assertEqual(self.portal['test-document'],
                         self.portal.es['test-document'])

        # Delete shared document
        notify(ObjectWillBeRemovedEvent(self.portal['test-document']))
        self.portal.manage_delObjects(self.portal['test-document'].id)

        # Check that it is not available in LRFs
        self.assertNotIn('test-document', self.portal['ca'].objectIds())
        self.assertNotIn('test-document', self.portal['es'].objectIds())

    def test_shared_content_indexing(self):
        # Create shared document
        createContentInContainer(
            self.portal, 'Document', title=u"Test document")

        # Check that shared document is indexed in root and in all LRFs
        elements = self.portal.portal_catalog.searchResults(id='test-document')
        self.assertEqual(len(elements), 4)

        # Remove shared document
        notify(ObjectWillBeRemovedEvent(self.portal['test-document']))
        self.portal.manage_delObjects(self.portal['test-document'].id)

        # Check that shared document is unindexed
        elements = self.portal.portal_catalog.searchResults(id='test-document')
        self.assertEqual(len(elements), 0)

    def test_shared_content_uuid(self):
        # Create shared document
        createContentInContainer(
            self.portal, 'Document', title=u"Test document")

        root_uuid = IUUID(self.portal['test-document'])
        shared_uuid = IUUID(self.portal.ca['test-document'])

        self.assertEqual('{0:s}-ca'.format(root_uuid), shared_uuid)

    def test_moving_shared_content_to_lrf(self):
        # Create shared document
        createContentInContainer(
            self.portal, 'Document', title=u"Test document")
        uuid = IUUID(self.portal['test-document'])

        # CHeck thats ghost is ghost
        self.assertTrue(is_shared(self.portal.ca['test-document']))

        # Check is in the catalog 
        brains = self.portal.portal_catalog.searchResults(UID=uuid)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), '/plone/test-document')

        brains = self.portal.portal_catalog.searchResults(
            UID='{0:s}-ca'.format(uuid))
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), '/plone/ca/test-document')

        brains = self.portal.portal_catalog.searchResults(
            UID='{0:s}-es'.format(uuid))
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), '/plone/es/test-document')

        # MOVE!
        moved = multilingualMoveObject(self.portal.ca['test-document'], 'ca')

        # Check that the old and the new uuid are the same
        moved_uuid = IUUID(self.portal.ca['copy_of_test-document'])

        self.assertEqual(uuid, moved_uuid)
        self.assertFalse(is_shared(moved))

        # Check portal_catalog is updated after move
        brains = self.portal.portal_catalog.searchResults(UID=uuid)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(),
                         '/plone/ca/copy_of_test-document')

        brains = self.portal.portal_catalog.searchResults(
            UID='{0:s}-ca'.format(uuid))
        self.assertEqual(len(brains), 0)

        brains = self.portal.portal_catalog.searchResults(
            UID='{0:s}-es'.format(uuid))
        self.assertEqual(len(brains), 0)

        # Check which translations it have
        self.assertEqual(
            ITranslationManager(moved).get_translations(), {'ca': moved})
        ITranslationManager(moved).add_translation('es')
        self.assertEqual(
            ITranslationManager(moved).get_translations(),
            {'ca': moved, 'es': self.portal.es['copy_of_test-document']})

        # Check that ghost is no longer ghost
        self.assertFalse(
            is_shared(self.portal.es['copy_of_test-document']))

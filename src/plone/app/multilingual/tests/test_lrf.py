# -*- coding: utf-8 -*-
from OFS.event import ObjectWillBeRemovedEvent
from plone.app.multilingual.browser.utils import is_language_independent
from plone.app.multilingual.browser.utils import multilingualMoveObject
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.event import notify
import unittest2 as unittest
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from zope.interface import alsoProvides


class TestLanguageRootFolder(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)

    def test_shared_content(self):
        # Create shared document
        createContentInContainer(
            self.portal.en.media, 'Document', title=u"Test document")

        # Check shared document is there
        self.assertEqual(self.portal.en.media['test-document'],
                         self.portal.ca.media['test-document'])
        self.assertEqual(self.portal.en.media['test-document'],
                         self.portal.es.media['test-document'])

        # Delete shared document
        notify(ObjectWillBeRemovedEvent(self.portal.en.media['test-document']))
        self.portal.en.media.manage_delObjects('test-document')

        # Check that it is not available in LRFs
        self.assertNotIn('test-document', self.portal.ca.media.objectIds())
        self.assertNotIn('test-document', self.portal.es.media.objectIds())

    def test_shared_content_indexing(self):
        # Create shared document
        createContentInContainer(
            self.portal.en.media, 'Document', title=u"Test document")

        # Check that shared document is indexed in all LRFs
        elements = self.portal.portal_catalog.searchResults(id='test-document')
        self.assertEqual(len(elements), 3)

        # Remove shared document
        notify(ObjectWillBeRemovedEvent(self.portal.en.media['test-document']))
        self.portal.en.media.manage_delObjects('test-document')

        # Check that shared document is unindexed
        elements = self.portal.portal_catalog.searchResults(id='test-document')
        self.assertEqual(len(elements), 0)

    def test_shared_content_uuid(self):
        # Create shared document
        createContentInContainer(
            self.portal, 'LIF', title=u"Media", checkConstraints=False)
        createContentInContainer(
            self.portal.media, 'Document', title=u"Test document")

        root_uuid = IUUID(self.portal.media['test-document'])
        shared_uuid = IUUID(self.portal.ca.media['test-document'])

        self.assertEqual('{0:s}-ca'.format(root_uuid), shared_uuid)

    def test_moving_shared_content_to_lrf(self):
        # Create shared document
        createContentInContainer(
            self.portal, 'LIF', title=u"Media", checkConstraints=False)
        createContentInContainer(
            self.portal.media, 'Document', title=u"Test document")
        uuid = IUUID(self.portal.media['test-document'])

        # Check that ghost is ghost
        self.assertTrue(
            is_language_independent(self.portal.ca.media['test-document']))

        # Check is in the catalog
        brains = self.portal.portal_catalog.searchResults(UID=uuid)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), '/plone/media/test-document')

        brains = self.portal.portal_catalog.searchResults(
            UID='{0:s}-ca'.format(uuid))
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), '/plone/ca/media/test-document')

        brains = self.portal.portal_catalog.searchResults(
            UID='{0:s}-es'.format(uuid))
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), '/plone/es/media/test-document')

        # MOVE!
        moved = multilingualMoveObject(
            self.portal.ca.media['test-document'], 'ca')

        # Check that the old and the new uuid are the same
        moved_uuid = IUUID(self.portal.ca['test-document'])

        self.assertEqual(uuid, moved_uuid)
        self.assertFalse(is_language_independent(moved))

        # Check portal_catalog is updated after move
        brains = self.portal.portal_catalog.searchResults(UID=uuid)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(),
                         '/plone/ca/test-document')

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
            {'ca': moved, 'es': self.portal.es['test-document']})

        # Check that ghost is no longer ghost
        self.assertFalse(
            is_language_independent(self.portal.es['test-document']))

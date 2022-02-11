from OFS.event import ObjectWillBeRemovedEvent
from plone.app.multilingual.browser.utils import is_language_independent
from plone.app.multilingual.browser.utils import multilingualMoveObject
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from zope.event import notify
from zope.interface import alsoProvides

import unittest


class TestLanguageRootFolder(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

    def test_shared_content(self):
        # Create shared document
        createContentInContainer(
            self.portal.en.assets, "Document", title="Test document"
        )

        # Check shared document is there
        self.assertEqual(
            self.portal.en.assets["test-document"],
            self.portal.ca.recursos["test-document"],
        )
        self.assertEqual(
            self.portal.en.assets["test-document"],
            self.portal.es.recursos["test-document"],
        )

        # Delete shared document
        notify(ObjectWillBeRemovedEvent(self.portal.en.assets["test-document"]))
        self.portal.en.assets.manage_delObjects("test-document")

        # Check that it is not available in LRFs
        self.assertNotIn("test-document", self.portal.ca.recursos.objectIds())
        self.assertNotIn("test-document", self.portal.es.recursos.objectIds())

    def test_shared_content_indexing(self):
        # Create shared document
        createContentInContainer(
            self.portal.en.assets, "Document", title="Test document"
        )

        # Check that shared document is indexed in all LRFs
        elements = self.portal.portal_catalog.searchResults(id="test-document")
        self.assertEqual(len(elements), 3)

        # Remove shared document
        notify(ObjectWillBeRemovedEvent(self.portal.en.assets["test-document"]))
        self.portal.en.assets.manage_delObjects("test-document")

        # Check that shared document is unindexed
        elements = self.portal.portal_catalog.searchResults(id="test-document")
        self.assertEqual(len(elements), 0)

    def test_shared_content_uuid(self):
        # Create shared document
        createContentInContainer(
            self.portal, "LIF", title="Assets", checkConstraints=False
        )
        createContentInContainer(self.portal.assets, "Document", title="Test document")

        root_uuid = IUUID(self.portal.assets["test-document"])
        shared_uuid = IUUID(self.portal.ca.recursos["test-document"])

        self.assertEqual(f"{root_uuid:s}-ca", shared_uuid)

    def test_moving_shared_content_to_lrf(self):
        # Create shared document
        createContentInContainer(
            self.portal, "LIF", title="Assets", checkConstraints=False
        )
        createContentInContainer(self.portal.assets, "Document", title="Test document")
        uuid = IUUID(self.portal.assets["test-document"])

        # Check that ghost is ghost
        self.assertTrue(
            is_language_independent(self.portal.ca.recursos["test-document"])
        )

        # Check is in the catalog
        brains = self.portal.portal_catalog.searchResults(UID=uuid)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/assets/test-document")

        brains = self.portal.portal_catalog.searchResults(UID=f"{uuid:s}-ca")
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/ca/recursos/test-document")

        brains = self.portal.portal_catalog.searchResults(UID=f"{uuid:s}-es")
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/es/recursos/test-document")

        # MOVE!
        moved = multilingualMoveObject(self.portal.ca.recursos["test-document"], "ca")

        # Check that the old and the new uuid are the same
        moved_uuid = IUUID(self.portal.ca["test-document"])

        self.assertEqual(uuid, moved_uuid)
        self.assertFalse(is_language_independent(moved))

        # Check portal_catalog is updated after move
        brains = self.portal.portal_catalog.searchResults(UID=uuid)
        self.assertEqual(len(brains), 1)
        self.assertEqual(brains[0].getPath(), "/plone/ca/test-document")

        brains = self.portal.portal_catalog.searchResults(UID=f"{uuid:s}-ca")
        self.assertEqual(len(brains), 0)

        brains = self.portal.portal_catalog.searchResults(UID=f"{uuid:s}-es")
        self.assertEqual(len(brains), 0)

        # Check which translations it have
        self.assertEqual(ITranslationManager(moved).get_translations(), {"ca": moved})
        ITranslationManager(moved).add_translation("es")
        self.assertEqual(
            ITranslationManager(moved).get_translations(),
            {"ca": moved, "es": self.portal.es["test-document"]},
        )

        # Check that ghost is no longer ghost
        self.assertFalse(is_language_independent(self.portal.es["test-document"]))

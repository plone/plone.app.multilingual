from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguage
from zope.interface import alsoProvides

import unittest


class TestSubscribers(unittest.TestCase):
    """There are some events that are fired when an object
    is created, moved or copied.

    plone.multilingual registers some subscribers for each event
    to change the language of the object from the container where
    it has been created, moved or copied
    """

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        self.portal = self.layer["portal"]

    def test_created_event(self):
        """When an object is created in a folder it takes its language from the
        folder itself
        """
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )
        self.assertEqual(ILanguage(a_ca).get_language(), "ca")

    def test_created_event_on_portal(self):
        """When an object is created on portal it should be language
        independent
        """
        a_ca = createContentInContainer(self.portal, "Document", title="Test document")
        self.assertEqual(ILanguage(a_ca).get_language(), "")

    def test_moved_event(self):
        """When an object is moved from within one Language Root Folder into
        a different Language Root Folder it changes its language to that of the
        folder it is copied into
        """
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        id_ = self.portal["ca"].manage_cutObjects(a_ca.id)
        self.portal["en"].manage_pasteObjects(id_)
        a_ca_copied = self.portal["en"][a_ca.id]
        self.assertEqual(ILanguage(a_ca_copied).get_language(), "en")

    def test_copied_event(self):
        """When an object is copied from within one Language Root Folder into
        a different Language Root Folder it changes its language to that of the
        folder it is copied into
        """
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        id_ = self.portal["ca"].manage_copyObjects(a_ca.id)
        self.portal["en"].manage_pasteObjects(id_)
        a_ca_copied = self.portal["en"][a_ca.id]
        self.assertEqual(ILanguage(a_ca_copied).get_language(), "en")

    def test_moved_to_assets_folder(self):
        """When an object is moved from within one Language Root Folder into
        the Language Independent Folder (named 'Assets') it becomes language
        independent, and it should be visible from the assets folder accessed
        from within other Language Root Folders
        """
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        # Test a paste into a subfolder to be ultra cautious
        ca_assets_subfolder = createContentInContainer(
            self.portal["ca"]["recursos"], "Folder", title="A Folder"
        )

        subfolder_name = ca_assets_subfolder.id

        id_ = self.portal["ca"].manage_cutObjects(a_ca.id)
        ca_assets_subfolder.manage_pasteObjects(id_)

        # Get both assets folders afresh
        ca_assets_subfolder = self.portal["ca"]["recursos"][subfolder_name]
        en_assets_subfolder = self.portal["en"]["assets"][subfolder_name]

        # Check it is in both folder listings
        self.assertTrue(a_ca.id in ca_assets_subfolder)
        self.assertTrue(a_ca.id in en_assets_subfolder)

        # Check it is language independent
        copy_in_en = en_assets_subfolder[a_ca.id]
        self.assertEqual(ILanguage(copy_in_en).get_language(), "")
        copy_in_ca = ca_assets_subfolder[a_ca.id]
        self.assertEqual(ILanguage(copy_in_ca).get_language(), "")

        # Check it is returned in catalog search
        catalog = getToolByName(self.portal, "portal_catalog")

        ca_subfolder_path = "/".join(ca_assets_subfolder.getPhysicalPath())
        ca_folder_contents = [r.id for r in catalog(path=ca_subfolder_path)]
        self.assertTrue(a_ca.id in ca_folder_contents)

        en_subfolder_path = "/".join(en_assets_subfolder.getPhysicalPath())
        en_folder_contents = [r.id for r in catalog(path=en_subfolder_path)]
        self.assertTrue(a_ca.id in en_folder_contents)

    def test_copied_to_assets_folder(self):
        """When an object is copied from within one Language Root Folder into
        the Language Independent Folder (named 'Assets') it becomes language
        independent, and it should be visible from the assets folder accessed
        from within other Language Root Folders
        """
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        # Test a paste into a subfolder to be ultra cautious
        ca_assets_subfolder = createContentInContainer(
            self.portal["ca"]["recursos"], "Folder", title="A Folder"
        )

        subfolder_name = ca_assets_subfolder.id
        id_ = self.portal["ca"].manage_copyObjects(a_ca.id)
        ca_assets_subfolder.manage_pasteObjects(id_)

        # Get both assets folders afresh
        ca_assets_subfolder = self.portal["ca"]["recursos"][subfolder_name]
        en_assets_subfolder = self.portal["en"]["assets"][subfolder_name]

        # Check it is in both folder listings
        self.assertTrue(a_ca.id in ca_assets_subfolder)
        self.assertTrue(a_ca.id in en_assets_subfolder)

        # Check it is language independent
        copy_in_en = en_assets_subfolder[a_ca.id]
        self.assertEqual(ILanguage(copy_in_en).get_language(), "")
        copy_in_ca = ca_assets_subfolder[a_ca.id]
        self.assertEqual(ILanguage(copy_in_ca).get_language(), "")

        # Check it is returned in catalog search
        catalog = getToolByName(self.portal, "portal_catalog")

        ca_subfolder_path = "/".join(ca_assets_subfolder.getPhysicalPath())
        ca_folder_contents = [r.id for r in catalog(path=ca_subfolder_path)]
        self.assertTrue(a_ca.id in ca_folder_contents)

        en_subfolder_path = "/".join(en_assets_subfolder.getPhysicalPath())
        en_folder_contents = [r.id for r in catalog(path=en_subfolder_path)]
        self.assertTrue(a_ca.id in en_folder_contents)

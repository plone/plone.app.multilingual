# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

import transaction
import unittest2 as unittest


class TestSubscribers(unittest.TestCase):
    """There are some events that are fired when an object
    is created, moved or copied.

    plone.multilingual registers some subscribres for each event
    to change the language of the object from the container where
    it has been created, moved or copied
    """
    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.folder_it = self._add_content(self.portal, 'Folder', 'it')
        self.folder_en = self._add_content(self.portal, 'Folder', 'en')
        ILanguage(self.folder_it).set_language('it')

    def _add_content(self, container, ptype, id_):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        content_id = container.invokeFactory(ptype, id_)
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        return container[content_id]

    def test_created_event(self):
        """when an object is created in a folder
           it takes its language from the folder itself
        """
        folder_1 = self._add_content(self.folder_it, 'Folder', 'folder_1')
        self.assertEqual(ILanguage(folder_1).get_language(), 'it')

    def test_created_event_on_portal(self):
        """when an object is created on portal it should get the default
           language because 'language independent' is not allowed.
        """
        language_tool = getToolByName(self.portal, 'portal_languages')
        folder_1 = self._add_content(self.portal, 'Folder', 'folder_1')
        self.assertEqual(ILanguage(folder_1).get_language(), '')

    def test_moved_event(self):
        folder = self._add_content(self.folder_it, 'Folder', 'folder_1')
        transaction.commit()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        id_ = self.folder_it.manage_cutObjects(folder.getId())
        self.folder_en.manage_pasteObjects(id_)
        copied_folder = getattr(self.folder_en, "folder_1")
        self.assertEqual(ILanguage(copied_folder).get_language(), '')

    def test_copied_event(self):
        folder = self._add_content(self.folder_it, 'Folder', 'folder_1')
        id_ = self.folder_it.manage_copyObjects(folder.getId())
        self.folder_en.manage_pasteObjects(id_)
        copied_folder = getattr(self.folder_en, "folder_1")
        self.assertEqual(ILanguage(copied_folder).get_language(), '')
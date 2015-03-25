# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from zope.interface import alsoProvides


class TestSubscribers(unittest.TestCase):
    """There are some events that are fired when an object
    is created, moved or copied.

    plone.multilingual registers some subscribers for each event
    to change the language of the object from the container where
    it has been created, moved or copied
    """
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)
        self.portal = self.layer['portal']

    def test_created_event(self):
        """When an object is created in a folder it takes its language from the
        folder itself
        """
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")
        self.assertEqual(ILanguage(a_ca).get_language(), 'ca')

    def test_created_event_on_portal(self):
        """When an object is created on portal it should be language
        independent
        """
        a_ca = createContentInContainer(
            self.portal, 'Document', title=u"Test document")
        self.assertEqual(ILanguage(a_ca).get_language(), '')

    def test_moved_event(self):
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        id_ = self.portal['ca'].manage_cutObjects(a_ca.id)
        self.portal['en'].manage_pasteObjects(id_)
        a_ca_copied = self.portal['en'][a_ca.id]
        self.assertEqual(ILanguage(a_ca_copied).get_language(), 'en')

    def test_copied_event(self):
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        id_ = self.portal['ca'].manage_copyObjects(a_ca.id)
        self.portal['en'].manage_pasteObjects(id_)
        a_ca_copied = self.portal['en'][a_ca.id]
        self.assertEqual(ILanguage(a_ca_copied).get_language(), 'en')

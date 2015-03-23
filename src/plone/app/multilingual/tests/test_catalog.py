# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
import unittest
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from zope.interface import alsoProvides


class TestIndependentLanguageFolder(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)
        createContentInContainer(
            self.portal['en']['media'], 'Document', title=u"Test document")
        # ^ This will be shadowed to all language independent folders

        createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        createContentInContainer(
            self.portal['es'], 'Document', title=u"Test document")

        createContentInContainer(
            self.portal['en'], 'Document', title=u"Test document")

    def test_query_with_all(self):
        catalog = getToolByName(self.portal, 'portal_catalog')

        used_langs = \
            set([x.Language for x in catalog.searchResults(self.request)])

        self.assertIn(LANGUAGE_INDEPENDENT, used_langs)
        self.assertIn('es', used_langs)
        self.assertIn('ca', used_langs)
        self.assertIn('en', used_langs)

    def test_query_for_language_independent_content(self):
        catalog = getToolByName(self.portal, 'portal_catalog')

        kw = {'Language': LANGUAGE_INDEPENDENT}
        lang_independent = \
            [x.Language for x in catalog.searchResults(self.request, **kw)]

        self.assertIn(LANGUAGE_INDEPENDENT, lang_independent)
        self.assertEqual(len(lang_independent), 3)

    def test_query_for_one_language(self):
        catalog = getToolByName(self.portal, 'portal_catalog')

        kw = {'Language': 'ca'}
        self.assertEqual([x.Language for x
                          in catalog.searchResults(self.request, **kw)],
                         ['ca', 'ca', 'ca'])

# -*- coding: utf-8 -*-
import unittest
from Products.CMFCore.utils import getToolByName
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from plone.app.multilingual.interfaces import ILanguage, LANGUAGE_INDEPENDENT
from plone.app.multilingual.testing import (
    PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
)


class TestCatalogPatch(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        documents = []
        for i in range(0,3):
            content_id = self.portal.invokeFactory(
                type_name='Document', id='sampledocument_%d' % i)
            content = self.portal[content_id]
            notify(ObjectAddedEvent(content))
            documents.append(content)

        import transaction
        transaction.commit()

        for cnt, lang in enumerate(['', 'it', 'en']):
            ILanguage(documents[cnt]).set_language(lang)
            documents[cnt].reindexObject()

        self.catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        self.request = self.layer['request']

    def testQueryWithAll(self):
        used_langs = [x.Language for x
                      in self.catalog.searchResults(self.request)]
        self.assertIn(LANGUAGE_INDEPENDENT, used_langs)
        self.assertIn('it', used_langs)
        self.assertIn('en', used_langs)

    def testQueryForLanguageIndependentContent(self):
        kw = {'Language': LANGUAGE_INDEPENDENT}
        lang_independent = [x.Language for x
                            in self.catalog.searchResults(self.request, **kw)]
        self.assertIn(LANGUAGE_INDEPENDENT, lang_independent)
        self.assertEqual(len(lang_independent), 1)

    def testQueryForOneLanguage(self):
        kw = {'Language': 'it'}
        self.assertEqual([x.Language for x
                          in self.catalog.searchResults(self.request, **kw)],
                         ['it'])

    def testQueryWithoutLanguageSet(self):
        """result should contain default_language and independent content)"""

        used_langs = [x.Language for x
                      in self.catalog.searchResults(self.request)]
        self.assertIn(LANGUAGE_INDEPENDENT, used_langs)
        self.assertIn('en', used_langs)



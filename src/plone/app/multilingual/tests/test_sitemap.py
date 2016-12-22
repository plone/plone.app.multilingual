# -*- coding: utf-8 -*-
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from gzip import GzipFile
from plone import api
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from .utils import makeContent
from .utils import makeTranslation
from zope.interface import alsoProvides
from plone.app.layout.navigation.interfaces import INavigationRoot

import unittest

PLONE_VERSION = api.env.plone_version()

# This class largely inspired by plone/app/layout/sitemap/tests/test_sitemap.py
class TestSitemap(unittest.TestCase):
    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal.portal_languages.addSupportedLanguage('ca')
        self.portal.portal_languages.addSupportedLanguage('es')
        en = makeContent(self.portal, 'Folder', id='en')
        en.setLanguage('en')
        ca = makeTranslation(en, 'ca')
        ca.setId('ca')
        alsoProvides(ca, INavigationRoot)
        es = makeTranslation(en, 'es')
        es.setId('es')
        alsoProvides(es, INavigationRoot)
        self.sitemap = getMultiAdapter((self.portal, self.portal.REQUEST),
                                       name='sitemap.xml.gz')
        self.site_properties = getToolByName(
            self.portal, 'portal_properties').site_properties
        self.site_properties.manage_changeProperties(enable_sitemap=True)
        docca = makeContent(
            self.portal['ca'],
            'Document',
            title=u'Test document',
            id='test-document')
        doces = makeContent(
            self.portal['es'],
            'Document',
            title=u'Test document',
            id='test-document')
        docen = makeContent(
            self.portal['en'],
            'Document',
            title=u'Test document',
            id='test-document')
        docca.setLanguage('ca')
        doces.setLanguage('es')
        docen.setLanguage('en')

    def uncompress(self, sitemapdata):
        sio = StringIO(sitemapdata)
        unziped = GzipFile(fileobj=sio)
        xml = unziped.read()
        unziped.close()
        return xml

    @unittest.skipIf(PLONE_VERSION < '4.3',
                     "expect portalroot sitemap broken for Plone 4.2")
    def test_portalroot_sitemap(self):
        '''
        Requests for the sitemap on portalroot return all languages
        '''
        xml = self.uncompress(self.sitemap())
        self.assertTrue(
            '<loc>http://nohost/plone/ca/test-document</loc>' in xml)
        self.assertTrue(
            '<loc>http://nohost/plone/en/test-document</loc>' in xml)
        self.assertTrue(
            '<loc>http://nohost/plone/es/test-document</loc>' in xml)

    @unittest.skipIf(PLONE_VERSION < '4.3',
                     "expect navroot sitemap broken for Plone 4.2")
    def test_navroot_sitemap(self):
        '''
        Sitemap generated from a LanguageRootFolder (an INavigationRoot)
        '''
        sitemap = getMultiAdapter(
            (self.portal.es, self.portal.REQUEST), name='sitemap.xml.gz')
        xml = self.uncompress(sitemap())
        self.assertFalse(
            '<loc>http://nohost/plone/ca/test-document</loc>' in xml)
        self.assertFalse(
            '<loc>http://nohost/plone/en/test-document</loc>' in xml)
        self.assertTrue(
            '<loc>http://nohost/plone/es/test-document</loc>' in xml)

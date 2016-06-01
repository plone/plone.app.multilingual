# -*- coding: utf-8 -*-
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from gzip import GzipFile
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.component import getMultiAdapter

import unittest

# This class largely inspired by plone/app/layout/sitemap/tests/test_sitemap.py
class TestSitemap(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.sitemap = getMultiAdapter((self.portal, self.portal.REQUEST),
                                       name='sitemap.xml.gz')
        self.site_properties = getToolByName(
            self.portal, 'portal_properties').site_properties
        self.site_properties.manage_changeProperties(enable_sitemap=True)

        createContentInContainer(
            self.portal['en']['media'], 'Document', title=u"Test document")
        # ^ This will be shadowed to all language independent folders

        createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        createContentInContainer(
            self.portal['es'], 'Document', title=u"Test document")

        createContentInContainer(
            self.portal['en'], 'Document', title=u"Test document")

    def uncompress(self, sitemapdata):
        sio = StringIO(sitemapdata)
        unziped = GzipFile(fileobj=sio)
        xml = unziped.read()
        unziped.close()
        return xml

    def test_portalroot_sitemap(self):
        '''
        Requests for the sitemap on portalroot return all languages
        '''

        xml = self.uncompress(self.sitemap())
        self.assertTrue('<loc>http://nohost/plone/ca/test-document</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/en/test-document</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/es/test-document</loc>' in xml)

        self.assertTrue('<loc>http://nohost/plone/ca/media/test-document</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/en/media/test-document</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/es/media/test-document</loc>' in xml)


    def test_navroot_sitemap(self):
        '''
        Sitemap generated from a LanguageRootFolder (an INavigationRoot)
        '''
        sitemap = getMultiAdapter((self.portal.es, self.portal.REQUEST),
                                       name='sitemap.xml.gz')
        xml = self.uncompress(sitemap())
        self.assertFalse('<loc>http://nohost/plone/ca/test-document</loc>' in xml)
        self.assertFalse('<loc>http://nohost/plone/en/test-document</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/es/test-document</loc>' in xml)

        self.assertFalse('<loc>http://nohost/plone/ca/media/test-document</loc>' in xml)
        self.assertFalse('<loc>http://nohost/plone/en/media/test-document</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/es/media/test-document</loc>' in xml)

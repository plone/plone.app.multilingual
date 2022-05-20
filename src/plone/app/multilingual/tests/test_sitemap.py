from gzip import GzipFile
from io import BytesIO
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides

import unittest


# This class largely inspired by plone/app/layout/sitemap/tests/test_sitemap.py
class TestSitemap(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

        registry = getUtility(IRegistry)
        self.site_settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.site_settings.enable_sitemap = True

        self.sitemap = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="sitemap.xml.gz"
        )

        createContentInContainer(
            self.portal["en"]["assets"], "Document", title="Test document"
        )
        # ^ This will be shadowed to all language independent folders

        createContentInContainer(self.portal["ca"], "Document", title="Test document")

        createContentInContainer(self.portal["es"], "Document", title="Test document")

        createContentInContainer(self.portal["en"], "Document", title="Test document")

    def uncompress(self, sitemapdata):
        sio = BytesIO(sitemapdata)
        unziped = GzipFile(fileobj=sio)
        xml = unziped.read()
        unziped.close()
        return xml

    def test_portalroot_sitemap(self):
        """
        Requests for the sitemap on portalroot return all languages
        """

        xml = self.uncompress(self.sitemap())
        self.assertIn(b"<loc>http://nohost/plone/ca/test-document</loc>", xml)
        self.assertIn(b"<loc>http://nohost/plone/en/test-document</loc>", xml)
        self.assertIn(b"<loc>http://nohost/plone/es/test-document</loc>", xml)

        self.assertIn(b"<loc>http://nohost/plone/ca/recursos/test-document</loc>", xml)
        self.assertIn(b"<loc>http://nohost/plone/en/assets/test-document</loc>", xml)
        self.assertIn(b"<loc>http://nohost/plone/es/recursos/test-document</loc>", xml)

    def test_navroot_sitemap(self):
        """
        Sitemap generated from a LanguageRootFolder (an INavigationRoot)
        """
        sitemap = getMultiAdapter(
            (self.portal.es, self.portal.REQUEST), name="sitemap.xml.gz"
        )
        xml = self.uncompress(sitemap())
        self.assertNotIn(
            b"<loc>http://nohost/plone/ca/test-document</loc>", xml
        )  # noqa
        self.assertNotIn(
            b"<loc>http://nohost/plone/en/test-document</loc>", xml
        )  # noqa
        self.assertIn(b"<loc>http://nohost/plone/es/test-document</loc>", xml)

        self.assertNotIn(
            b"<loc>http://nohost/plone/ca/recursos/test-document</loc>", xml
        )
        self.assertNotIn(b"<loc>http://nohost/plone/en/assets/test-document</loc>", xml)
        self.assertIn(b"<loc>http://nohost/plone/es/recursos/test-document</loc>", xml)

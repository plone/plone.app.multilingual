import unittest2 as unittest
from plone.app.multilingual.tests._testing import PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from AccessControl import Unauthorized
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.testing import applyProfile

from plone.app.multilingual.tests.utils import makeContent, makeTranslation

from plone.multilingual.interfaces import ITranslationManager


class PAMHelperViews(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.portal_url = self.portal.absolute_url()
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

    def test_universal_link_view(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))
        self.browser.addHeader('Accept-Language', 'ca')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        doc1 = makeContent(self.portal, 'Document', id='doc1')
        doc1.setLanguage('en')
        doc1_ca = makeTranslation(doc1, 'ca')
        doc1_ca.edit(title="Foo", language='ca')
        doc1_es = makeTranslation(doc1, 'es')
        doc1_es.edit(title="Foo", language='es')
        import transaction; transaction.commit()

        self.browser.open(doc1.absolute_url())
        self.browser.getLink("Universal Link").click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/doc1-ca')

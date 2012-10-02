import unittest2 as unittest
from Products.CMFCore.utils import getToolByName

from plone.testing.z2 import Browser

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from plone.app.multilingual.tests.utils import makeContent, makeTranslation

import transaction


class BabelViews(unittest.TestCase):

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

    def test_babel_edit_buttons(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        doc1 = makeContent(self.portal, 'Document', id='doc1')
        transaction.commit()

        self.browser.open(doc1.absolute_url() + '/@@create_translation')
        self.browser.getControl(name="form.widgets.language:list").value = ['ca']
        self.browser.getControl(name="form.buttons.create").click()

        # Now in the babel_edit form
        self.browser.getControl(name="title").value = "Doc ca"

        self.assertTrue('name="button-English"' in self.browser.contents)

        self.assertTrue('name="button-Catala"' not in self.browser.contents)

        self.browser.getControl(name="form.button.save").click()

        self.browser.open(doc1.absolute_url() + '/@@create_translation')
        self.browser.getControl(name="form.widgets.language:list").value = ['es']
        self.browser.getControl(name="form.buttons.create").click()

        # Now in the babel_edit form
        self.browser.getControl(name="title").value = "Doc es"

        self.assertTrue('name="button-English"' in self.browser.contents)
        self.assertTrue('name="button-Spanish"' not in self.browser.contents)
        self.assertTrue('name="button-Catalan"' in self.browser.contents)

        self.browser.getControl(name="form.button.save").click()

        # TODO: Test for permissions visibility of buttons

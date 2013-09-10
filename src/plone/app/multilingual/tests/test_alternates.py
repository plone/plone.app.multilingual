# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.testing import \
    PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from plone.app.multilingual.tests.utils import makeContent
from plone.app.multilingual.tests.utils import makeTranslation
from plone.app.multilingual.browser.viewlets import AlternateLanguagesViewlet
from plone.dexterity.utils import createContentInContainer
from plone.multilingual.interfaces import ILanguage
from plone.multilingual.interfaces import ITranslationManager

import transaction
import unittest2 as unittest


class TestAlternateLanguagesViewlet(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.error_log._ignored_exceptions = ()
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.language_tool = getToolByName(self.portal, 'portal_languages')
        self.language_tool.addSupportedLanguage('ca')
        self.language_tool.addSupportedLanguage('es')

        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

    def _validate_alternates(self, context):

        # Get the viewlet
        viewlet = AlternateLanguagesViewlet(context, self.request, None, None)
        viewlet.update()

        # Get translations
        translations = ITranslationManager(context).get_translations()

        for item in viewlet.alternates:
            self.assertIn(item['lang'], translations)
            self.assertEqual("{0}/{1}".format(viewlet.site_url, item['url']),
                             translations[item['lang']].absolute_url())

    def test_alternates_AT(self):
        atdoc = makeContent(
            self.portal['en'], 'Document', id='atdoc', title='EN doc')
        atdoc.setLanguage('en')
        atdoc_ca = makeTranslation(atdoc, 'ca')
        atdoc_ca.edit(title="CA doc", language='ca')

        transaction.savepoint()

        self._validate_alternates(atdoc)

    def test_alternates_DX(self):
        dxdoc = createContentInContainer(
            self.portal['en'], "dxdoc", id="dxdoc", title='EN doc')
        ILanguage(dxdoc).set_language('en')
        dxdoc_ca = makeTranslation(dxdoc, 'ca')
        dxdoc_ca.title = "CA doc"
        ILanguage(dxdoc_ca).set_language('ca')

        transaction.savepoint()

        self._validate_alternates(dxdoc)

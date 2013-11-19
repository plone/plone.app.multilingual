# -*- coding: utf-8 -*-
import unittest2 as unittest
import transaction
from plone.dexterity.utils import createContentInContainer

from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.multilingual import api
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.browser.utils import multilingualMoveObject


class PAMFuncTestHelperViews(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization',
                               'Basic %s:%s' % (TEST_USER_NAME,
                                                TEST_USER_PASSWORD))

    def test_universal_link_view(self):
        self.browser.addHeader('Accept-Language', 'ca')

        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")
        a_en = api.translate(a_ca, 'en')
        api.translate(a_ca, 'es')

        transaction.commit()

        self.browser.open(a_en.absolute_url())
        self.browser.getLink("Universal Link").click()
        self.assertEqual(self.browser.url, a_ca.absolute_url())


class PAMIntTestHelperViews(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_move_content_proper_language_folder(self):
        f_ca = createContentInContainer(
            self.portal['ca'], 'Folder', title=u"Test folder")

        a_ca = createContentInContainer(
            self.portal['ca']['test-folder'],
            'Document', title=u"Test document")

        # Change the content language of the created folder to 'es'
        multilingualMoveObject(f_ca, 'es')

        self.assertIn(f_ca.id, self.portal['es'].objectIds())
        self.assertEqual(f_ca, self.portal['es'][f_ca.id])

        self.assertIn(a_ca.id, self.portal['es'][f_ca.id].objectIds())
        self.assertEqual(a_ca, self.portal['es'][f_ca.id][a_ca.id])

        adapter = ILanguage(self.portal['es'][f_ca.id])
        self.assertEqual(adapter.get_language(), 'es')

        adapter = ILanguage(self.portal['es'][f_ca.id][a_ca.id])
        self.assertEqual(adapter.get_language(), 'es')

    def test_move_content_existing_translation_inside(self):
        f_ca = createContentInContainer(
            self.portal['ca'], 'Folder', title=u"Test folder")

        a_ca = createContentInContainer(
            self.portal['ca']['test-folder'],
            'Document', title=u"Test document")

        a_en = api.translate(a_ca, 'en')
        translations = ITranslationManager(self.portal['en'][a_en.id])
        self.assertEqual(translations.get_translations(),
                         {'ca': self.portal['ca'][f_ca.id][a_ca.id],
                          'en': self.portal['en'][a_ca.id]})

        self.assertIn(a_en.id, self.portal['en'].objectIds())
        self.assertEqual(a_en, self.portal['en'][a_en.id])

        # Change the content language of the created folder to 'en'
        multilingualMoveObject(f_ca, 'en')

        self.assertIn(f_ca.id, self.portal['en'].objectIds())
        self.assertEqual(f_ca, self.portal['en'][f_ca.id])

        self.assertIn(a_ca.id, self.portal['en'][f_ca.id].objectIds())
        self.assertEqual(a_ca, self.portal['en'][f_ca.id][a_ca.id])

        adapter = ILanguage(self.portal['en'][f_ca.id])
        self.assertEqual(adapter.get_language(), 'en')

        adapter = ILanguage(self.portal['en'][f_ca.id][a_ca.id])
        self.assertEqual(adapter.get_language(), 'en')

        translations = ITranslationManager(self.portal['en'][f_ca.id][a_ca.id])
        self.assertEqual(translations.get_translations(),
                         {'en': self.portal['en'][f_ca.id][a_ca.id]})

        translations = ITranslationManager(self.portal['en'][a_en.id])
        self.assertEqual(translations.get_translations(),
                         {'en': self.portal['en'][a_en.id]})

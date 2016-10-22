# -*- coding: utf-8 -*-
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.testing._z2_testbrowser import Browser
import transaction
import unittest2 as unittest
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from zope.interface import alsoProvides


class TestForm(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)
        # Setup test browser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization', 'Basic %s:%s' % (
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD))

    def test_all_translation_links_are_shown(self):
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        transaction.commit()

        self.browser.open(a_ca.absolute_url())
        self.assertIn('plone-contentmenu-multilingual', self.browser.contents)
        self.assertIn('translate_into_es', self.browser.contents)
        self.assertIn('translate_into_en', self.browser.contents)

    def test_translation_form_creates_translation(self):
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        transaction.commit()

        # Translate content
        self.browser.open(
            a_ca.absolute_url() + '/@@create_translation?language=en')

        # Fill in translation details
        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = u"Test document"
        self.browser.getControl(name="form.buttons.save").click()

        self.portal._p_jar.sync()

        self.assertIn("test-document", self.portal['en'].objectIds())

        self.browser.open(a_ca.absolute_url())
        self.assertIn('plone-contentmenu-multilingual', self.browser.contents)
        self.assertIn('translate_into_es', self.browser.contents)
        self.assertNotIn('translate_into_en', self.browser.contents)

    def test_translation_form_prevents_translating_twice(self):
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        transaction.commit()

        # Translate content
        self.browser.open(
            a_ca.absolute_url() + '/@@create_translation?language=en')

        # Save ++add++translation... URL
        add_translation_url = self.browser.url

        # Fill in translation details
        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = u"Test document"
        self.browser.getControl(name="form.buttons.save").click()

        self.portal._p_jar.sync()

        # Revisit the saved ++add++translation... URL
        self.browser.open(add_translation_url)

        # Which should now redirect to the created translation
        self.assertEqual(self.portal['en']['test-document'].absolute_url(),
                         self.browser.url)

    def test_translation_can_be_unregistered(self):
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        transaction.commit()

        # Create translation
        self.browser.open(a_ca.absolute_url() +
                          '/@@create_translation?language=en')

        # Fill in translation details
        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = u"Test document"
        self.browser.getControl(name="form.buttons.save").click()

        # Unregister translation
        self.browser.open(a_ca.absolute_url() +
                          '/disconnect_translation?came_from={0}&language=en'
                          .format(a_ca.UID()))
        self.browser.getForm(index=1).submit()

        self.portal._p_jar.sync()

        self.assertNotIn('en', ITranslationManager(a_ca).get_translations())


        # self.assertEqual(
        #     self.browser.getControl(name="form.widgets.languages:list").value,
        #     ['en'])
        # self.browser.getControl(name='form.buttons.unlink').click()
        # self.assertEqual(
        #     self.browser.getControl(name="form.widgets.languages:list").value,
        #     [])

        # Translation is unregistered
        self.browser.open(a_ca.absolute_url())
        self.assertIn('plone-contentmenu-multilingual', self.browser.contents)
        self.assertIn('translate_into_es', self.browser.contents)
        self.assertIn('translate_into_en', self.browser.contents)

        transaction.commit()

        # Content is still available
        self.assertIn('test-document', self.portal['en'].contentIds())

    # Removed because its testes on robot framework with the relation pattern
    # def test_registering_translation(self):
    #     a_ca = createContentInContainer(
    #         self.portal['ca'], 'Document', title=u"Test document")

    #     b_ca = createContentInContainer(
    #         self.portal['ca'], 'Document', title=u"Test document")

    #     transaction.commit()

    #     # Register translation
    #     self.browser.open(
    #         a_ca.absolute_url() + '/add_translations')
    #     self.assertEqual(self.browser.getControl(
    #         name="form.widgets.language:list").options, ['en', 'es'])

    #     # Fill in form
    #     form = self.browser.getForm(index=1)
    #     form.mech_form.new_control(
    #         type='radio',
    #         name='form.widgets.content:list',
    #         attrs=dict(checked='checked',
    #                    value='%s' % '/'.join(b_ca.getPhysicalPath()),
    #                    id='form-widgets-content-0'))
    #     self.browser.getControl(
    #         name="form.widgets.language:list").value = ['en']
    #     self.browser.getControl(
    #         name='form.buttons.add_translations').click()

    #     # Language is removed from nontranslated languages
    #     self.assertEqual(self.browser.getControl(
    #         name="form.widgets.language:list").options, ['es'])

    #     # And translation can be unregistered
    #     self.browser.open(a_ca.absolute_url() + '/remove_translations')
    #     self.assertEqual(self.browser.getControl(
    #         name="form.widgets.languages:list").value, ['en'])

    def test_translation_can_be_removed_by_deleting(self):
        a_ca = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")

        transaction.commit()

        # Translate content
        self.browser.open(a_ca.absolute_url() +
                          '/@@create_translation?language=en')

        # Fill in translation details
        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = u"Test document"
        self.browser.getControl(name="form.buttons.save").click()

        # Remove translation
        self.browser.open(
            ITranslationManager(a_ca).get_translation('en').absolute_url() +
            '/delete_confirmation')
        self.browser.getControl(name='form.buttons.Delete').click()

        self.portal._p_jar.sync()
        self.assertNotIn('en', ITranslationManager(a_ca).get_translations())

    def test_folderish_content_can_be_translated(self):
        createContentInContainer(
            self.portal['ca'], 'Folder', title=u"Test folder")

        transaction.commit()

        self.browser.open(self.portal.absolute_url() +
                          '/ca/test-folder/@@create_translation?language=en')

        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = u"Test folder"
        self.browser.getControl(name="form.buttons.save").click()

        self.portal._p_jar.sync()

        self.assertIn('test-folder', self.portal['en'].objectIds())

    def test_content_in_folders_can_be_translated(self):
        af_ca = createContentInContainer(
            self.portal['ca'], 'Folder', title=u"Test folder")

        b_ca = createContentInContainer(
            self.portal['ca']['test-folder'],
            'Document', title=u"Test document")

        transaction.commit()

        self.browser.open(af_ca.absolute_url() + '/' + b_ca.id +
                          '/@@create_translation?language=en')

        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = u"Test folder"
        self.browser.getControl(name="form.buttons.save").click()

        self.portal._p_jar.sync()

        self.assertIn('test-folder', self.portal['en'].objectIds())

# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
import unittest2 as unittest
from zope.event import notify
from zope.lifecycleevent import ObjectAddedEvent
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing._z2_testbrowser import Browser


class TestForm(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        # Setup multilingual site
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('it')
        language_tool.addSupportedLanguage('de')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        # Setup test browser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization', 'Basic %s:%s' % (
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD))

        # Create sample document in 'en' and index it into catalog
        self.container = self.portal['en']
        self.content_id = self.container.invokeFactory(
            type_name="Document", id="sampledocument-form")
        self.content = self.container[self.content_id]
        self.content.setLanguage('en')
        notify(ObjectAddedEvent(self.content))

        import transaction
        transaction.commit()

    def testAllTranslationLinksAreShown(self):
        self.browser.open(self.content.absolute_url())
        self.assertIn('plone-contentmenu-multilingual', self.browser.contents)
        self.assertIn('translate_into_it', self.browser.contents)
        self.assertIn('translate_into_de', self.browser.contents)

    def testTranslationFormCreatesTranslation(self):
        # Translate content
        self.browser.open(
            self.content.absolute_url()
            + '/@@create_translation?language=de')

        # Fill in translation details
        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = "sample title de"
        self.browser.getControl(name="form.buttons.save").click()

        import transaction
        transaction.commit()

        self.assertIn("sample-title-de", self.portal['de'].objectIds())

        self.browser.open(self.content.absolute_url())
        self.assertIn('plone-contentmenu-multilingual', self.browser.contents)
        self.assertIn('translate_into_it', self.browser.contents)
        self.assertNotIn('translate_into_de', self.browser.contents)

    def testTranslationCanBeUnregistered(self):
        # Create translation
        self.browser.open(
            self.content.absolute_url()
            + '/@@create_translation?language=de')

        # Fill in translation details
        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = "sample title de"
        self.browser.getControl(name="form.buttons.save").click()

        import transaction
        transaction.commit()

        # Unregister translation
        self.browser.open(self.content.absolute_url()
                          + '/remove_translations?set_language=en')
        self.assertEqual(
            self.browser.getControl(name="form.widgets.languages:list").value,
            ['de'])
        self.browser.getControl("unlink selected").click()
        self.assertEqual(
            self.browser.getControl(name="form.widgets.languages:list").value,
            [])

        # Translation is unregistered
        self.browser.open(self.content.absolute_url())
        self.assertIn('plone-contentmenu-multilingual', self.browser.contents)
        self.assertIn('translate_into_it', self.browser.contents)
        self.assertIn('translate_into_de', self.browser.contents)

        transaction.commit()

        # Content is still available
        self.assertIn('sample-title-de', self.portal['de'].contentIds())


    def testRegisteringTranslation(self):
        # Create another page
        container = self.portal['de']
        content_id = container.invokeFactory(
            type_name="Document", id="sampleform-de")
        content = container[content_id]
        content.setLanguage('de')
        notify(ObjectAddedEvent(content))

        import transaction
        transaction.commit()

        # Register translation
        self.browser.open(
            self.content.absolute_url() + '/add_translations')
        self.assertEqual(self.browser.getControl(
            name="form.widgets.language:list").options, ['it', 'de'])

        # Fill in form
        form = self.browser.getForm(index=1)
        form.mech_form.new_control(
            type='radio',
            name='form.widgets.content:list',
            attrs=dict(checked='checked',
                       value='%s' %'/'.join(content.getPhysicalPath()),
                       id='form-widgets-content-0'))
        self.browser.getControl(
            name="form.widgets.language:list").value = ['de']
        self.browser.getControl(
            name='form.buttons.add_translations').click()

        # Language is removed from nontranslated languages
        self.assertEqual(self.browser.getControl(
            name="form.widgets.language:list").options, ['it'])

        # And translation can be unregistered
        self.browser.open(self.content.absolute_url() + '/remove_translations')
        self.assertEqual(self.browser.getControl(
            name="form.widgets.languages:list").value, ['de'])

    def testTranslationCanBeRemovedByDeleting(self):
        # Translate content
        self.browser.open(
            self.content.absolute_url()
            + '/@@create_translation?language=de')

        # Fill in translation details
        self.browser.getControl(
            name="form.widgets.IDublinCore.title").value = "sample title de"
        self.browser.getControl(name="form.buttons.save").click()

        # Remove translation
        self.browser.open(self.content.absolute_url() + '/remove_translations')
        self.browser.getControl("remove selected").click()

        self.assertEqual(self.browser.getControl(
            name="form.widgets.languages:list").value, [])

        self.portal._p_jar.sync()

        self.assertNotIn('sample-title-de', self.portal['de'].objectIds())

    def testFolderishContentCanBeTransalte(self):
        self.container.invokeFactory(type_name="Folder", id="samplefolder")
        notify(ObjectAddedEvent(self.container.samplefolder))

        import transaction
        transaction.commit()

        self.browser.open(
            self.portal.absolute_url()
            + '/en/samplefolder/@@create_translation?language=de')

        self.browser.getControl(name="form.widgets.IDublinCore.title").value =\
            "sample folder title de"
        self.browser.getControl(name="form.buttons.save").click()

        self.portal._p_jar.sync()

        self.assertIn('sample-folder-title-de', self.portal['de'].objectIds())

    def testContentInFoldersCanBeTranslated(self):
        self.container.invokeFactory(type_name="Folder", id="samplefolder")
        notify(ObjectAddedEvent(self.container.samplefolder))

        folder = self.container['samplefolder']
        content_id = folder.invokeFactory(
            type_name="Document", id="sampledocument_in_folder")
        notify(ObjectAddedEvent(folder[content_id]))

        import transaction
        transaction.commit()

        self.browser.open(
            folder.absolute_url() + '/' + content_id
            + '/@@create_translation?language=de')

        self.browser.getControl(name="form.widgets.IDublinCore.title").value =\
            "sample folder content title de"
        self.browser.getControl(name="form.buttons.save").click()

        self.portal._p_jar.sync()

        self.assertIn('sample-folder-content-title-de',
                      self.portal['de'].objectIds())

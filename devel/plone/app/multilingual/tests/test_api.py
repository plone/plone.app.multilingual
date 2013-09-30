import unittest2 as unittest
import transaction
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING
from AccessControl import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login, logout
from plone.app.testing import setRoles

from plone.app.testing import applyProfile

from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import (
    IPloneAppMultilingualInstalled,
    ILanguage,
    ITranslationManager
    )


class test_basic_api(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneAppMultilingualInstalled)
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')
        self.a_ca = makeContent(self.portal, 'dxdoc', id='a_ca')
        ILanguage(self.a_ca).set_language('ca')

    def testSupportedLanguages(self):
        language_tool = getToolByName(self.portal, 'portal_languages')
        self.failUnless(language_tool.getSupportedLanguages(), ['es', 'ca'])

    def test_get_translations(self):
        self.failUnless(ITranslationManager(self.a_ca).get_translations(), {'ca': self.a_ca})

    def test_get_translation(self):
        self.failUnless(ITranslationManager(self.a_ca).get_translation('ca'), self.a_ca)

    def test_get_translated_languages(self):
        self.failUnless(ITranslationManager(self.a_ca).get_translated_languages(), ['ca'])

    def test_has_translation(self):
        self.assertTrue(ITranslationManager(self.a_ca).has_translation('ca'))
        self.assertFalse(ITranslationManager(self.a_ca).has_translation('es'))

    def test_get_restricted_translations(self):
        # XXX : Test another user
        self.failUnless(ITranslationManager(self.a_ca).get_restricted_translations(), {'ca': self.a_ca})

    def test_get_restricted_translation(self):
        # XXX : Test another user
        self.failUnless(ITranslationManager(self.a_ca).get_restricted_translation('ca'), self.a_ca)

    def test_add_translation(self):
        # Create es translation
        ITranslationManager(self.a_ca).add_translation('es')

        # Check if it exists
        self.assertTrue('a_ca-es' in self.portal)
        self.a_ca_es = self.portal['a_ca-es']

        # Check language
        self.failUnless(ILanguage(self.a_ca_es).get_language(), 'es')

    def test_add_translation_delegated(self):
        # Create es translation
        self.failUnless(ITranslationManager(self.a_ca).add_translation_delegated('es'), self.portal)

    def test_register_translation(self):
        self.a_es = makeContent(self.portal, 'dxdoc', id='a_es')
        ILanguage(self.a_es).set_language('es')
        ITranslationManager(self.a_ca).register_translation('es', self.a_es)
        self.failUnless(ITranslationManager(self.a_ca).get_translations(), {'ca': self.a_ca, 'es': self.a_es})


class test_lrf_api(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneAppMultilingualInstalled)
        language_tool = getToolByName(self.portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')

        setupTool = SetupMultilingualSite()
        setupTool.folder_type = 'dxfolder'
        setupTool.setupSite(self.portal)

        self.a_ca = makeContent(self.portal.ca, 'dxdoc', id='a_ca')

    def test_initial_language_set(self):
        self.failUnless(ILanguage(self.a_ca).get_language(), 'ca')

    def test_add_translation(self):
        ITranslationManager(self.a_ca).add_translation('es')

        self.a_es = ITranslationManager(self.a_ca).get_translation('es')
        self.failUnless(ITranslationManager(self.a_ca).get_translations(), {'ca': self.a_ca, 'es': self.a_es})
        # Check is in the correct folder
        self.assertTrue(self.a_es.id in self.portal.es)

        # Try again
        self.assertRaises(KeyError, ITranslationManager(self.a_ca).add_translation, 'es')
        # Error language
        self.assertRaises(KeyError, ITranslationManager(self.a_ca).add_translation, None)

    def test_add_translation_delegated(self):
        new_path = ITranslationManager(self.a_ca).add_translation_delegated('es')
        self.failUnless(new_path, self.portal.es)

    def test_create_destroy_link_translations(self):
        ITranslationManager(self.a_ca).add_translation('es')
        self.a_es = ITranslationManager(self.a_ca).get_translation('es')

        self.b_es = makeContent(self.portal.es, 'dxdoc', id='b_es')

        ITranslationManager(self.b_es).add_translation('ca')
        self.b_ca = ITranslationManager(self.b_es).get_translation('ca')

        from OFS.event import ObjectWillBeRemovedEvent
        from zope.event import notify

        notify(ObjectWillBeRemovedEvent(self.a_es))
        self.portal.es.manage_delObjects(self.a_es.id)

        notify(ObjectWillBeRemovedEvent(self.b_ca))
        self.portal.ca.manage_delObjects(self.b_ca.id)

        id_b_es = ITranslationManager(self.b_es).query_canonical()
        id_a_ca = ITranslationManager(self.a_ca).query_canonical()
        self.assertFalse(id_b_es == id_a_ca)
        self.assertTrue(isinstance(id_b_es, str))
        self.assertTrue(isinstance(id_a_ca, str))

        ITranslationManager(self.a_ca).register_translation('es', self.b_es)

        id_b_es = ITranslationManager(self.b_es).query_canonical()
        id_a_ca = ITranslationManager(self.a_ca).query_canonical()
        self.assertTrue(id_b_es == id_a_ca)

    def test_create_relink_translation(self):
        """ We check the update function here """

        # ITranslationManager(self.a_ca).add_translation('es')
        # self.a_es = ITranslationManager(self.a_ca).get_translation('es')

        self.b_es = makeContent(self.portal.es, 'dxfolder', id='b_es')
        ITranslationManager(self.b_es).add_translation('ca')
        self.b_ca = ITranslationManager(self.b_es).get_translation('ca')

        ITranslationManager(self.a_ca).register_translation('es', self.b_es)

        self.assertFalse(ITranslationManager(self.b_ca).has_translation('es'))
        self.failUnless(ITranslationManager(self.b_es).get_translation('ca'), self.a_ca)

    def test_id_chooser(self):
        from plone.app.multilingual.interfaces import ITranslationIdChooser
        chooser = ITranslationIdChooser(self.a_ca)
        self.failUnless(chooser(self.portal, 'es'), 'a_ca-es')

    def test_locator(self):
        self.bf_ca = makeContent(self.portal.ca, 'dxfolder', id='bf_ca')
        self.bf2_ca = makeContent(self.portal.ca.bf_ca, 'dxfolder', id='bf2_ca')

        from plone.app.multilingual.interfaces import ITranslationLocator
        locator = ITranslationLocator(self.bf2_ca)
        self.failUnless(locator('es'), self.portal.es)

        ITranslationManager(self.bf_ca).add_translation('es')
        self.bf_es = ITranslationManager(self.bf_ca).get_translation('es')

        child_locator = ITranslationLocator(self.bf2_ca)
        self.failUnless(child_locator('es'), self.bf_es)

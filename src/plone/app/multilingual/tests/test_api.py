from OFS.event import ObjectWillBeRemovedEvent
from plone.app.multilingual import api
from plone.app.multilingual.interfaces import ATTRIBUTE_NAME
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationIdChooser
from plone.app.multilingual.interfaces import ITranslationLocator
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.testing import logout
from plone.dexterity.utils import createContentInContainer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguage
from zope.event import notify
from zope.interface import alsoProvides

import unittest


class TestAPI(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

    def test_get_translation_manager(self):
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )
        tm = api.get_translation_manager(a_ca)
        self.assertTrue(ITranslationManager.providedBy(tm))

    def test_translate(self):
        # Create
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        self.assertEqual(
            api.get_translation_manager(a_ca).get_translations(), {"ca": a_ca}
        )

        # Translate
        a_en = api.translate(a_ca, "en")

        # check
        self.assertEqual(
            api.get_translation_manager(a_ca).get_translations(),
            {"ca": a_ca, "en": a_en},
        )

    def test_get_translation_group(self):
        # Create
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )
        a_en = api.translate(a_ca, "en")

        # get groups
        tg_ca = api.get_translation_group(a_en)
        tg_en = api.get_translation_group(a_en)

        # check
        self.assertTrue(tg_ca is not None)
        self.assertTrue(tg_en is not None)
        self.assertEqual(tg_en, tg_ca)

    def test_translateable(self):
        # Create
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )
        # check
        self.assertTrue(api.is_translatable(a_ca))
        self.assertFalse(api.is_translatable(object()))


class TestBasicAPI(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        # Create
        self.a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

    def test_supported_languages(self):
        language_tool = getToolByName(self.portal, "portal_languages")
        self.assertEqual(language_tool.getSupportedLanguages(), ["en", "ca", "es"])

    def test_get_translations(self):
        translations = ITranslationManager(self.a_ca).get_translations()
        self.assertEqual(translations, {"ca": self.a_ca})

    def test_get_translation(self):
        a_ca = ITranslationManager(self.a_ca).get_translation("ca")
        self.assertEqual(a_ca, self.a_ca)

    def test_get_translated_languages(self):
        translated_languages = ITranslationManager(self.a_ca).get_translated_languages()
        self.assertEqual(translated_languages, ["ca"])

    def test_has_translation(self):
        translation_manager = ITranslationManager(self.a_ca)
        self.assertTrue(translation_manager.has_translation("ca"))
        self.assertFalse(translation_manager.has_translation("es"))

    def test_get_restricted_translation(self):
        restricted_translations = ITranslationManager(
            self.a_ca
        ).get_restricted_translations()
        self.assertEqual(restricted_translations, {"ca": self.a_ca})

    def test_get_restricted_translation_for_anonymous(self):
        logout()
        restricted_translations = ITranslationManager(
            self.a_ca
        ).get_restricted_translations()
        self.assertEqual(restricted_translations, {})

    def test_add_translation(self):
        # Check that document does not exists
        self.assertNotIn("test-document", self.portal["es"].objectIds())

        # Create es translation
        ITranslationManager(self.a_ca).add_translation("es")

        # Check if it exists
        self.assertIn("test-document", self.portal["es"].objectIds())

        # Check language
        language = ILanguage(self.portal["es"]["test-document"]).get_language()
        self.assertEqual(language, "es")

    def test_add_translation_delegated(self):
        # Create es translation
        portal_es = ITranslationManager(self.a_ca).add_translation_delegated("es")
        self.assertEqual(portal_es, self.portal["es"])

    def test_register_translation(self):
        a_es = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )

        ITranslationManager(self.a_ca).register_translation("es", a_es)

        translations = ITranslationManager(self.a_ca).get_translations()
        self.assertEqual(translations, {"ca": self.a_ca, "es": a_es})


class TestLanguageRootFolderAPI(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

    def test_initial_language_set(self):
        # Create
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        # Check that the content has language
        self.assertEqual(ILanguage(a_ca).get_language(), "ca")

    def test_add_translation(self):
        # Create
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        # Translate
        ITranslationManager(a_ca).add_translation("es")
        a_es = ITranslationManager(a_ca).get_translation("es")

        # Check that translation is registered
        self.assertEqual(
            ITranslationManager(a_ca).get_translations(), {"ca": a_ca, "es": a_es}
        )

        # Check that it is in the correct folder
        self.assertTrue(a_es.id in self.portal["es"])

        # Check that it cannot be translated again
        translation_manager = ITranslationManager(a_ca)
        self.assertRaises(KeyError, translation_manager.add_translation, "es")

        # Check that language must be valid
        self.assertRaises(KeyError, translation_manager.add_translation, None)

    def test_add_translation_delegated(self):
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        translation_manager = ITranslationManager(a_ca)
        portal_es = translation_manager.add_translation_delegated("es")

        self.assertEqual(portal_es, self.portal["es"])

    def test_create_destroy_link_translations(self):
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        ITranslationManager(a_ca).add_translation("es")
        a_es = ITranslationManager(a_ca).get_translation("es")

        # Create duplicate content
        another_es = createContentInContainer(
            self.portal["es"], "Document", title="Test another"
        )

        ITranslationManager(another_es).add_translation("ca")
        another_ca = ITranslationManager(another_es).get_translation("ca")

        # Delete original content
        notify(ObjectWillBeRemovedEvent(a_es))
        self.portal.es.manage_delObjects(a_es.id)

        notify(ObjectWillBeRemovedEvent(another_ca))
        self.portal.ca.manage_delObjects(another_ca.id)

        # Check canonical values are still different
        id_a_ca = ITranslationManager(a_ca).query_canonical()
        id_another_es = ITranslationManager(another_es).query_canonical()

        self.assertNotEqual(id_another_es, id_a_ca)
        self.assertTrue(isinstance(id_another_es, str))
        self.assertTrue(isinstance(id_a_ca, str))

        # Make documents translations of each other
        ITranslationManager(a_ca).register_translation("es", another_es)

        # Check that canonical values are now the same
        id_a_ca = ITranslationManager(a_ca).query_canonical()
        id_another_es = ITranslationManager(another_es).query_canonical()

        self.assertEqual(id_another_es, id_a_ca)

    def test_create_relink_translations(self):
        """We check the update function here"""
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        b_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        b_es = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        ITranslationManager(b_es).add_translation("ca")
        ITranslationManager(a_ca).register_translation("es", b_es)

        self.assertFalse(ITranslationManager(b_ca).has_translation("es"))
        self.assertEqual(ITranslationManager(b_es).get_translation("ca"), a_ca)

    def test_id_chooser(self):
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )

        chooser = ITranslationIdChooser(a_ca)
        self.assertEqual(chooser(self.portal, "es"), "test-document")

        createContentInContainer(self.portal, "Document", title="Another test")

        b_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Another test"
        )

        chooser = ITranslationIdChooser(b_ca)
        self.assertEqual(chooser(self.portal, "es"), "another-test-es")

    def test_locator(self):
        folder_ca = createContentInContainer(
            self.portal["ca"], "Folder", title="Test folder"
        )
        subfolder_ca = createContentInContainer(
            self.portal["ca"]["test-folder"], "Folder", title="Test folder"
        )

        locator = ITranslationLocator(subfolder_ca)
        self.assertEqual(locator("es"), self.portal["es"])

        ITranslationManager(folder_ca).add_translation("es")
        folder_es = ITranslationManager(folder_ca).get_translation("es")

        child_locator = ITranslationLocator(subfolder_ca)
        self.assertEqual(child_locator("es"), folder_es)

    def test_tg_view(self):
        a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document"
        )
        tg = getattr(a_ca, ATTRIBUTE_NAME)
        self.assertTrue(bool(tg))
        self.assertEqual(a_ca.restrictedTraverse("@@tg")(), tg)

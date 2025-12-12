from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.testing import CaEsTranslator
from plone.app.multilingual.testing import DisabledTranslator
from plone.app.multilingual.testing import NiTranslator
from plone.app.multilingual.testing import PAM_INTEGRATION_PRESET_TESTING
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
from zope.component import provideUtility
from zope.interface import alsoProvides
from plone.app.multilingual.translation_utils import translate_text

import json
import transaction
import unittest


class TestExternalServicesUtilities(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)

        self.a_ca = createContentInContainer(
            self.portal["ca"], "Document", title="Test document CA"
        )

        self.a_es = createContentInContainer(
            self.portal["es"], "Document", title="Test document ES"
        )

        manager = ITranslationManager(self.a_ca)
        manager.register_translation("es", self.a_es)

        provideUtility(
            NiTranslator(), IExternalTranslationService, name="ni_translator"
        )
        provideUtility(
            DisabledTranslator(),
            IExternalTranslationService,
            name="disabled_translator",
        )
        provideUtility(
            CaEsTranslator(), IExternalTranslationService, name="ca_es_translator"
        )

        transaction.commit()

    def test_translation_ca_es(self):
        """In this case the CaEsTranslator should be applied
        because it has a smaller number in the order
        and it has the ca-es language pair translation
        availability
        """
        result = translate_text(self.a_ca.Title(), "ca", "es")
        self.assertEqual(result, "text español")

    def test_translation_es_ca(self):
        """In this case the NiTranslator should be applied
        because the previous translators have not this language
        pair available or are disabled
        """
        result = translate_text(self.a_es.Title(), "es", "ca")
        self.assertEqual(result, "Test document ES NI!")

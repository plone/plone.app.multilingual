from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.testing import CaEsTranslator
from plone.app.multilingual.testing import DisabledTranslator
from plone.app.multilingual.testing import NiTranslator
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.testing._z2_testbrowser import Browser
from zope.component import provideUtility
from zope.interface import alsoProvides

import json
import transaction
import unittest


class TestExternalServices(unittest.TestCase):
    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        # Setup test browser
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )
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
        self.browser.open(
            f"{self.a_es.absolute_url()}/gtranslation_service",
            data={"field": "IDublinCore.title", "lang_source": "ca"},
        )

        result = json.loads(self.browser.contents)

        self.assertEqual(result.get("data"), "text español")

    def test_translation_es_ca(self):
        """In this case the NiTranslator should be applied
        because the previous translators have not this language
        pair available or are disabled
        """

        self.browser.open(
            f"{self.a_ca.absolute_url()}/gtranslation_service",
            data={"field": "IDublinCore.title", "lang_source": "es"},
        )

        result = json.loads(self.browser.contents)

        self.assertEqual(result.get("data"), "Test document ES NI!")

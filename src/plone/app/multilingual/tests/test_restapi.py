from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.app.multilingual.testing import CaEsTranslator
from plone.app.multilingual.testing import DisabledTranslator
from plone.app.multilingual.testing import NiTranslator
from plone.app.multilingual.testing import PAM_ROBOT_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from zope.component import provideUtility

import transaction
import unittest


class TestDefaultTranslationServices(unittest.TestCase):
    """Test the default translation services provided by plone.app.multilingual"""

    layer = PAM_ROBOT_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_available_services(self):
        """test that by default we have just one available service"""
        api_result = self.api_session.get("/@translation-services")
        self.assertEqual(len(api_result.json()), 0)


class TestSeveralTranslationServices(unittest.TestCase):
    """Test that when we register several translation services, those are correctly exposed
    in the REST API
    """

    layer = PAM_ROBOT_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
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

    def test_available_services(self):
        """test that by default we have just one available service"""
        api_result = self.api_session.get("/@translation-services")
        self.assertEqual(len(api_result.json()), 3)

    def test_that_one_is_disabled(self):
        """we have registered an adapter that is disabled, check that we get that information correctly"""
        api_result = self.api_session.get("/@translation-services")
        results = api_result.json()

        disabled_adapters = [
            adapter for adapter in results if not adapter["is_available"]
        ]
        self.assertEqual(len(disabled_adapters), 1)

        disabled_adapter_names = [adapter["name"] for adapter in disabled_adapters]
        self.assertIn("disabled_translator", disabled_adapter_names)


class TestTranslateTextServices(unittest.TestCase):
    layer = PAM_ROBOT_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
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

        api_result = self.api_session.post(
            "/@translate-text",
            json={
                "original_text": "Some text",
                "source_language": "ca",
                "target_language": "es",
            },
        )
        result = api_result.json()

        self.assertEqual(result.get("data"), "text español")

    def test_translation_es_fr(self):
        """In this case the NiTranslator should be applied
        because the previous translators have not this language
        pair available or are disabled
        """
        api_result = self.api_session.post(
            "/@translate-text",
            json={
                "original_text": "Some text",
                "source_language": "es",
                "target_language": "fr",
            },
        )
        result = api_result.json()

        self.assertEqual(result.get("data"), "Some text NI!")

    def test_translation_given_service(self):
        """test that using a given translation works, we are going to request the NI translator
        in a context when in normal circumstances another different translator would be used
        """
        api_result = self.api_session.post(
            "/@translate-text",
            json={
                "original_text": "Some other text",
                "source_language": "ca",
                "target_language": "es",
                "service": "ni_translator",
            },
        )
        result = api_result.json()

        self.assertEqual(result.get("data"), "Some other text NI!")

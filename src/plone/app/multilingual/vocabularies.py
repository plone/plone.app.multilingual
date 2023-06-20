from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import logging
import os

try:
    from google.cloud import translate_v3 as translate
    from google.oauth2 import service_account
    HAS_GCLOUD_V3 = True
except:
    HAS_GCLOUD_V3 = False


logger = logging.getLogger(__name__)


@implementer(IVocabularyFactory)
class GcloudGlossariesVocabulary:
    def __call__(self, context):
        results = []
        credentials_file = os.getenv("GCLOUD_V3_JSON", None)
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMultiLanguageExtraOptionsSchema, prefix="plone"
        )
        if HAS_GCLOUD_V3 and settings.gcloud_use_v3 and credentials_file:
            logger.info("Getting a list of glossaries.")
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
            client = translate.TranslationServiceClient(credentials=credentials)
            project_id = credentials.project_id
            location = settings.gcloud_v3_location
            parent = f'projects/{project_id}/locations/{location}'
            response = client.list_glossaries(parent=parent)
            for glossary in response:
                lang_codes = ', '.join(glossary.language_codes_set.language_codes)
                title = f"{glossary.display_name} ({lang_codes})"
                id = glossary.display_name
                results.append(SimpleTerm(id, id, title))
        else:
            # Ignore silently
            logger.info("Google Cloud Translation V3 is not configured.")

        return SimpleVocabulary(results)


GcloudGlossariesVocabularyFactory = GcloudGlossariesVocabulary()

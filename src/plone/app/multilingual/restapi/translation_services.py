from plone.app.multilingual.interfaces import IExternalTranslationService
from plone.restapi.services import Service
from zope.component import getUtilitiesFor


class TranslationServices(Service):
    """an endpoint to return all translation services registered in a portal that provide the IExternalTranslationService interface"""

    def reply(self):
        result = []

        for name, adapter in getUtilitiesFor(IExternalTranslationService):
            item = {}
            item["order"] = adapter.order
            item["is_available"] = adapter.is_available()
            item["available_languages"] = adapter.available_languages()
            item["name"] = name

            result.append(item)

        return sorted(result, key=lambda x: x["order"], reverse=True)

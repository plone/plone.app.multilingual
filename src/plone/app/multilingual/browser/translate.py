from Acquisition import aq_inner
from plone.app.multilingual.interfaces import ITranslationManager
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView


class TranslationForm(BrowserView):
    """Translation Form"""

    def __call__(self):
        language = self.request.get("language", None)
        if language:
            context = aq_inner(self.context)
            translation_manager = ITranslationManager(context)
            new_parent = translation_manager.add_translation_delegated(language)  # noqa
            baseUrl = new_parent.absolute_url()
            url = f"{baseUrl}/++addtranslation++{IUUID(context)}"
            return self.request.response.redirect(url)

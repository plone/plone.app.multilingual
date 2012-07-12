from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.interfaces import ITranslatable
from plone.multilingual.interfaces import ITranslationManager


class LP2PAMView(BrowserView):
    """View for migrating multilingual catalog from LP to PAM"""

    def __init__(self, context, request):
        self.context = context

    def __call__(self):
        pc = getToolByName(self.context, 'portal_catalog')
        pl = getToolByName(self.context, 'portal_languages')
        for language_supported in pl.getSupportedLanguages():
            translated_objects = pc.searchResults(object_provides=ITranslatable.__identifier__, Language=language_supported)
            for brain in translated_objects:
                obj = brain.getObject()
                if obj.isCanonical():
                    translations = obj.getTranslations(include_canonical=False)
                    for language in translations.keys():
                        ITranslationManager(obj).register_translation(language, translations[language][0])

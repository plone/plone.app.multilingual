from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.interfaces import ITranslatable
from plone.multilingual.interfaces import ITranslationManager
import logging


class LP2PAMView(BrowserView):
    """View for migrating multilingual catalog from LP to PAM"""

    template = ViewPageTemplateFile('migrator.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('plone.app.multilingual')

    def __call__(self):
        pc = getToolByName(self.context, 'portal_catalog')
        pl = getToolByName(self.context, 'portal_languages')
        self.results = []
        for language_supported in pl.getSupportedLanguages():
            translated_objects = pc.searchResults(object_provides=ITranslatable.__identifier__, Language=language_supported)
            for brain in translated_objects:
                obj = brain.getObject()
                if obj.isCanonical():
                    translations = obj.getTranslations(include_canonical=False)
                    if translations:
                        for language in translations.keys():
                            try:
                                ITranslationManager(obj).register_translation(language, translations[language][0])
                            except KeyError:
                                self.logger.warning('%s already translated to %s: %s' % (obj.id, language, str(ITranslationManager(obj).get_translations())))

                        self.results.append(ITranslationManager(obj).get_translations())

        return self.template()

from plone.multilingual.interfaces import ITranslationManager
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
import logging

LP_TRANSLATABLE = 'Products.LinguaPlone.interfaces.ITranslatable'

logger = logging.getLogger(__name__)


class LP2PAMView(BrowserView):
    """View for migrating multilingual catalog from LP to PAM"""

    template = ViewPageTemplateFile('templates/migrator.pt')

    def __call__(self):
        pc = getToolByName(self.context, 'portal_catalog')
        pl = getToolByName(self.context, 'portal_languages')
        self.results = []
        for language_supported in pl.getSupportedLanguages():
            translated_objects = pc.searchResults(
                object_provides=LP_TRANSLATABLE,
                Language=language_supported)
            for brain in translated_objects:
                obj = brain.getObject()
                if obj.isCanonical():
                    translations = obj.getTranslations(include_canonical=False)
                    manager = ITranslationManager(obj)
                    if translations:
                        for language in translations.keys():
                            try:
                                manager.register_translation(language,
                                    translations[language][0])
                            except KeyError:
                                logger.warning(
                                    '%s already translated to %s: %s' %
                                    (obj.id, language,
                                        str(manager.get_translations())))

                        self.results.append(manager.get_translations())

        return self.template()


class LP2PAMAfterView(BrowserView):

    template = ViewPageTemplateFile('templates/migrator_after.pt')

    def reset_relation_catalog(self):
        """
        Sometimes there are dependencies to the ITranslatable
        interface hidden in the relation catalog. This reset gets
        rid of them. (Assuming that Products.LinguaPlone is already
        uninstalled)
        """
        catalog = getUtility(ICatalog)
        relations = catalog.findRelations()
        catalog.clear()
        total = 0
        bad = []
        for relation in relations:
            total += 1
            try:
                catalog.index(relation)
            except KeyError:
                # If you read this because you wonder why you have many
                # missing relations, please inform do3cc
                logger.warning("A relation could not be recreated. You have "
                    "lost relations")
                bad.append(str(relation.__dict__))
        return total, bad

    def __call__(self):
        total, bad = self.reset_relation_catalog()
        self.total = total
        self.bad = bad
        return self.template()

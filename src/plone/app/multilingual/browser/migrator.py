from Acquisition import aq_inner, aq_parent
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ITranslationLocator, ILanguage
from plone.app.folder.utils import findObjects
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.multilingual.interfaces import ITranslatable
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

    template = ViewPageTemplateFile('templates/cleanup_results.pt')

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


class moveContentToProperRLF(BrowserView):
    """ This browser view moves the site's content to its corresponding root
        language folder.
    """

    def __call__(self):
        """ Explore the site's content and place it on the right RLF
        """
        context = aq_inner(self.context)
        pl = getToolByName(context, "portal_languages")
        pu = getToolByName(context, "portal_url")
        portal = pu.getPortalObject()
        supported_langs = pl.getSupportedLanguages()

        output = []
        for path, obj in findObjects(portal):
            try:
                lang_adptr = ILanguage(obj)
            except:
                info_str = "Found object %s with no language support." % (path)
                logger.info(info_str)
                output.append(info_str)
                continue

            obj_lang = lang_adptr.get_language()
            if obj_lang not in supported_langs:
                info_str = "Found object %s with unsupported language %s." % (
                                            path, obj_lang)
                logger.info(info_str)
                output.append(info_str)
            else:
                target_folder = ITranslationLocator(obj)(obj_lang)
                parent = aq_parent(obj)
                if IPloneSiteRoot.providedBy(parent) \
                   and ITranslatable.providedBy(obj) \
                   and not INavigationRoot.providedBy(obj):
                    target_folder = getattr(portal, obj_lang, None)

                if target_folder != parent:
                    cb_copy_data = parent.manage_cutObjects(obj.getId())
                    list_ids = target_folder.manage_pasteObjects(cb_copy_data)
                    new_id = list_ids[0]['new_id']
                    new_object = target_folder[new_id]
                    info_str = "Moved object %s to lang folder %s" % (
                                            parent.getPhysicalPath(), obj_lang)
                    logger.info(info_str)
                    output.append(new_object.id)

        return output

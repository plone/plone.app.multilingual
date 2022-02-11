from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.multilingual import _
from plone.app.multilingual.interfaces import ITranslationManager
from plone.locking.interfaces import ILockable
from Products.CMFCore.exceptions import ResourceLockedError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguage
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface.interfaces import ComponentLookupError

import logging
import warnings


try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    from plone.app.multilingual.interfaces import ITranslatable

try:
    from plone.dexterity.interfaces import IDexterityContent
except ImportError:

    class IDexterityContent(Interface):
        pass


try:
    from Products.Archetypes.interfaces import IBaseObject
except ImportError:

    class IBaseObject(Interface):
        pass


with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        message="LanguageRootFolder: LanguageRootFolders should be migrate "
        "to DexterityContainers",
    )
    from plone.app.multilingual.content.lrf import LanguageRootFolder


LP_TRANSLATABLE = "Products.LinguaPlone.interfaces.ITranslatable"
portal_types_blacklist = ["Collage", "FormFolder", "Ploneboard"]
logger = logging.getLogger(__name__)


class LP2PAMView(BrowserView):
    """View for migrating multilingual catalog from LP to PAM."""

    template = ViewPageTemplateFile("templates/migrator-results.pt")
    stepinfo = _("Transfer multilingual catalog information")

    def __call__(self):
        pc = getToolByName(self.context, "portal_catalog")
        pl = getToolByName(self.context, "portal_languages")
        self.results = []
        for language_supported in pl.getSupportedLanguages():
            translated_objects = pc.searchResults(
                object_provides=LP_TRANSLATABLE, Language=language_supported
            )
            for brain in translated_objects:
                obj = brain.getObject()
                if obj.isCanonical():
                    translations = obj.getTranslations(include_canonical=False)
                    manager = ITranslationManager(obj)
                    if translations:
                        for language in translations.keys():
                            try:
                                manager.register_translation(
                                    language, translations[language][0]
                                )
                            except KeyError:
                                logger.info(
                                    "%s already translated to %s: %s"
                                    % (
                                        obj.id,
                                        language,
                                        str(manager.get_translations()),
                                    )
                                )

                        self.results.append(str(manager.get_translations()))

        logger.info("Finished with transferring catalog information")
        return self.template()


class LP2PAMAfterView(BrowserView):

    template = ViewPageTemplateFile("templates/cleanup_results.pt")
    stepinfo = _("After migration relation cleanup")

    def reset_relation_catalog(self):
        """Sometimes there are dependencies to the ITranslatable interface
        hidden in the relation catalog. This reset gets rid of them. (Assuming
        that Products.LinguaPlone is already uninstalled).
        """
        try:
            catalog = getUtility(ICatalog)
        except ComponentLookupError:
            return 0, ["A zc.relation catalog is not present."]
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
                logger.warning(
                    "A relation could not be recreated. You have " "lost relations"
                )
                bad.append(str(relation.__dict__))
        return total, bad

    def __call__(self):
        total, bad = self.reset_relation_catalog()
        self.total = total
        self.bad = bad
        return self.template()


class moveContentToProperRLF(BrowserView):
    """This browser view moves the site's content to its corresponding root
    language folder and previously made a search for misplaced content through
    the site's content tree and moves them to its nearest translated parent.
    """

    template = ViewPageTemplateFile("templates/relocate-results.pt")
    stepinfo = _("Relocate content to the proper root language folder")
    blacklist = list()

    def findContent(self, content, depth):
        # only handle portal content
        if not IDexterityContent.providedBy(content) and not IBaseObject.providedBy(
            content
        ):
            logger.warning(
                "SKIP non-portal content %s (%s)"
                % (content.absolute_url(), content.meta_type)
            )
            return
        if (
            hasattr(aq_base(content), "objectIds")
            and aq_base(content).portal_type not in self.blacklist
        ):
            for id in content.objectIds():
                self.findContent(getattr(content, id), depth + 1)
        while len(self.content_tree) < depth + 1:
            self.content_tree.append([])
        if ITranslatable.providedBy(content):
            # The content parent has the same language?
            if (
                not IPloneSiteRoot.providedBy(aq_parent(content))
                and aq_parent(content).Language() != content.Language()
            ):
                self.content_tree[depth].append(content)

    def searchNearestTranslatedParent(self, content):
        parent = aq_parent(content)
        while parent.Language() != content.Language() and not IPloneSiteRoot.providedBy(
            parent
        ):
            parent = aq_parent(parent)
        return parent

    def __call__(self):
        """Note: Steps names don't correspond with the control panel ones"""
        blacklist = self.request.form.get("blacklist", "").split()
        self.blacklist = [x.strip() for x in blacklist if x.strip() != ""]
        self.results = self.step1andstep2()
        self.results += self.step3()
        return self.template()

    def step1andstep2(self):
        """Explore the site's content searching for misplaced content and move
        it to its nearest translated parent.
        """
        portal = getSite()

        output = []
        # Step 1 - Audit the content tree and make a list with the candidates
        # to be moved to the right RLF. Once we get a candidate, decide if it
        # should be moved to its nearest parent with the same language. Trying
        # to avoid the catalog in order to avoid problems with big sites and
        # bad or corrupted catalogs.
        self.content_tree = []
        self.findContent(portal, 0)
        logger.info("Step 1: Eligible content: %s" % self.content_tree)

        # We now have a list of lists that maps each eligible content with its
        # depth in the content tree

        # Step 2 - Move the eligible content to its nearest translated parent
        # from the most deepest located content to the outer ones
        self.content_tree.reverse()

        for depth in self.content_tree:
            if depth != []:
                for content in depth:
                    parent = aq_parent(content)
                    target_folder = self.searchNearestTranslatedParent(content)
                    # Test if the id already exist previously

                    try:
                        cutted = parent.manage_cutObjects(content.getId())
                    except ResourceLockedError:
                        lockable = ILockable(content)
                        lockable.unlock()
                        cutted = parent.manage_cutObjects(content.getId())
                    try:
                        target_folder.manage_pasteObjects(cutted)
                        info_str = "Step 2: Moved object {} to folder {}".format(
                            "/".join(content.getPhysicalPath()),
                            "/".join(target_folder.getPhysicalPath()),
                        )
                        log = logger.info
                    except Exception as err:
                        info_str = (
                            "ERROR. Step 2: not possible to move "
                            "object %s to folder %s. Error: %s"
                            % (
                                "/".join(content.getPhysicalPath()),
                                "/".join(target_folder.getPhysicalPath()),
                                err,
                            )
                        )
                        log = logger.error
                    log(info_str)
                    output.append(info_str)

        logger.info("Finished step 2")
        return output

    def step3(self):
        """Move the existing site content to its correspondent RLF."""
        portal = getSite()
        pc = getToolByName(portal, "portal_catalog")
        pl = getToolByName(portal, "portal_languages")

        supported_langs = pl.getSupportedLanguages()

        output = []
        # Step 3: Move all the remaining content to its correspondent RLFs
        for lang in supported_langs:
            RLF_id = "%s" % lang
            folder = getattr(portal, RLF_id, None)
            if not folder:
                raise AttributeError(
                    "One of the root language folder are \
                                      missing. Check the site's language \
                                      setup."
                )

            path = "/".join(portal.getPhysicalPath())
            objects = pc.searchResults(
                path={"query": path, "depth": 1},
                sort_on="getObjPositionInParent",
                Language=lang,
            )

            for brain in objects:
                if brain.id != lang:
                    old_path = brain.getPath()

                    try:
                        cutted = self.context.manage_cutObjects(brain.id)
                    except ResourceLockedError:
                        content = brain.getObject()
                        lockable = ILockable(content)
                        lockable.unlock()
                        cutted = self.context.manage_cutObjects(brain.id)
                    try:
                        folder.manage_pasteObjects(cutted)
                        info_str = "Moved object %s to language root folder " "%s" % (
                            old_path,
                            lang,
                        )
                        log = logger.info
                    except Exception as err:
                        info_str = (
                            "ERROR. Step 3: not possible to move "
                            "object %s to root language folder %s. Error: %s"
                            % (old_path, lang, err)
                        )
                        log = logger.error
                    log(info_str)
                    output.append(info_str)

        logger.info("Finished step 3")
        return output


class LP2PAMReindexLanguageIndex(BrowserView):

    template = ViewPageTemplateFile("templates/reindex-results.pt")
    stepinfo = "Reindex the LanguageIndex"

    def __call__(self):
        pc = getToolByName(self.context, "portal_catalog")
        index = pc._catalog.getIndex("Language")
        self.items_before = index.numObjects()
        pc.manage_reindexIndex(ids=["Language"])
        self.items_after = index.numObjects()

        return self.template()


class MigrateFolderToLRFView(BrowserView):
    def __call__(self):
        plone_utils = getToolByName(self.context, "plone_utils")

        if self.context.__class__ == LanguageRootFolder:
            self.request.response.redirect(self.context.absolute_url())
            return

        if not IPloneSiteRoot.providedBy(aq_parent(aq_inner(self.context))):
            plone_utils.addPortalMessage(
                _(
                    "folder_to_lrf_not_next_to_root",
                    default="Only folders just below the root " "can be transformed",
                )
            )
            self.request.response.redirect(self.context.absolute_url())
            return

        portal_languages = getToolByName(self.context, "portal_languages")
        available_languages = portal_languages.getAvailableLanguages()
        if self.context.id not in available_languages.keys():
            plone_utils.addPortalMessage(
                _(
                    "folder_to_lrf_id_not_language",
                    default="Folder's id is not a valid language code",
                )
            )
            self.request.response.redirect(self.context.absolute_url())
            return

        # Do the transform
        self.context.__class__ = LanguageRootFolder
        self.context._p_changed = aq_parent(self.context).p_changed = True
        self.context.portal_type = "LRF"

        # Update content language
        portal_catalog = getToolByName(self.context, "portal_catalog")
        search_results = portal_catalog.unrestrictedSearchResults(
            path="/".join(self.context.getPhysicalPath())
        )
        for brain in search_results:
            ob = brain._unrestrictedGetObject()
            language_aware = ILanguage(ob, None)
            if language_aware is not None:
                language_aware.set_language(self.context.id)
                ob.reindexObject(idxs=["Language", "TranslationGroup"])

        plone_utils.addPortalMessage(
            _(
                "folder_to_lrf_success",
                default="Folder has been successfully transformed to "
                "a language root folder",
            )
        )
        self.request.response.redirect(self.context.absolute_url())

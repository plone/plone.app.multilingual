from Acquisition import aq_inner, aq_parent
from zope.component.hooks import getSite
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ITranslationLocator, ILanguage
from plone.app.folder.utils import findObjects
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
import logging
from Acquisition import aq_base
from Products.CMFCore.exceptions import ResourceLockedError
from plone.locking.interfaces import ILockable

try:
    from Products.LinguaPlone.interfaces import ITranslatable
except:
    from plone.multilingual.interfaces import ITranslatable

LP_TRANSLATABLE = 'Products.LinguaPlone.interfaces.ITranslatable'

portal_types_blacklist = ['Collage', 'FormFolder', 'Ploneboard']

logger = logging.getLogger(__name__)


class LP2PAMView(BrowserView):
    """View for migrating multilingual catalog from LP to PAM"""

    template = ViewPageTemplateFile('templates/migrator-results.pt')
    stepinfo = u"Transfer multilingual catalog information"

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

                        self.results.append(str(manager.get_translations()))

        logger.info('Finished with transferring catalog information')
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
        try:
            catalog = getUtility(ICatalog)
        except ComponentLookupError:
            return 0, ['A zc.relation catalog is not present.']
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
        language folder and previously made a search for misplaced content
        through the site's content tree and moves them to its nearest translated
        parent.
    """

    template = ViewPageTemplateFile('templates/migrator-results.pt')
    stepinfo = u"Relocate content to the proper root language folder"
    blacklist = list()

    def findContent(self, content, depth):
        # only handle portal content
        if not getattr(content, 'portal_type', None):
            logger.warning('SKIP non-portal content %s (%s)' %
                (content.absolute_url(), content.meta_type))
            return
        if hasattr(aq_base(content), 'objectIds') \
            and content.portal_type not in self.blacklist:
            for id in content.objectIds():
                self.findContent(getattr(content, id), depth + 1)
        while len(self.content_tree) < depth + 1:
            self.content_tree.append([])
        if ITranslatable.providedBy(content):
            # The content parent has the same language?
            if not IPloneSiteRoot.providedBy(aq_parent(content)) \
               and aq_parent(content).Language() != content.Language():
                self.content_tree[depth].append(content)

    def searchNearestTranslatedParent(self, content):
        parent = aq_parent(content)
        while parent.Language() != content.Language() \
              and not IPloneSiteRoot.providedBy(parent):
            parent = aq_parent(parent)
        return parent

    def __call__(self):
        """ Note: Steps names don't correspond with the control panel ones """
        self.blacklist = [x.strip() for x in 
            self.request.get('blacklist', list()) if x.strip() != '']
        self.results = self.step1andstep2()
        self.results += self.step3()
        return self.template()

    def step1andstep2(self):
        """ Explore the site's content searching for misplaced content and move
            it to its nearest translated parent.
        """
        portal = getSite()

        output = []
        # Step 1 - Audit the content tree and make a list with the candidates to
        # be moved to the right RLF. Once we get a candidate, decide if it
        # should be moved to its nearest parent with the same language. Trying
        # to avoid the catalog in order to avoid problems with big sites and bad
        # or corrupted catalogs.
        self.content_tree = []
        self.findContent(portal, 0)
        logger.warning("Step 1: Eligible content: %s" % self.content_tree)

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
                        info_str = "Step 2: Moved object %s to folder %s" % (
                                   '/'.join(content.getPhysicalPath()),
                                   '/'.join(target_folder.getPhysicalPath()))
                        log = logger.warning
                    except Exception, err:
                        info_str = "ERROR. Step 2: not possible to move " \
                        "object %s to folder %s. Error: %s" % (
                                   '/'.join(content.getPhysicalPath()),
                                   '/'.join(target_folder.getPhysicalPath()),
                                   err)
                        log = logger.error
                    log(info_str)
                    output.append(info_str)

        logger.info('Finished step 2')
        return output

    def step3(self):
        """ Move the existing site content to its correspondent RLF.
        """
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
                raise AttributeError("One of the root language folder are \
                                      missing. Check the site's language \
                                      setup.")

            path = '/'.join(portal.getPhysicalPath())
            objects = pc.searchResults(path={'query': path, 'depth': 1},
                                       sort_on='getObjPositionInParent',
                                       Language=lang)

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
                        info_str = "Moved object %s to root language folder %s" % (
                                    old_path, lang)
                        log = logger.warning
                    except Exception, err:
                        info_str = "ERROR. Step 3: not possible to move "\
                        "object %s to root language folder %s. Error: %s" % (
                            old_path, lang, err)
                        log = logger.error
                    log(info_str)
                    output.append(info_str)

        logger.info('Finished step 3')
        return output


class LP2PAMReindexLanguageIndex(BrowserView):

    def __call__(self):
        pc = getToolByName(self.context, 'portal_catalog')
        index = pc._catalog.getIndex('Language')
        items_before = index.numObjects()
        pc.manage_reindexIndex(ids=['Language'])
        items_after = index.numObjects()
        output = '<div class="resultInfo"><h3>Reindex language index</h3>' \
        'The "Language" index was re-indexed. Before, it contained %d '\
        'items, now it contains %d items.</div>' % (items_before, items_after)
        return output

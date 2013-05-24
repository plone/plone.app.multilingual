from logging import getLogger
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual.interfaces import SHARED_NAME
from plone.app.multilingual import isDexterityInstalled
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ILanguage
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from zope.interface import alsoProvides
from Acquisition import aq_inner
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

LOG = getLogger('plone.app.multilingual')


# Setup view imported from LinguaPlone
class SetupView(BrowserView):

    def __init__(self, context, request):
        super(SetupView, self).__init__(context, request)

    def __call__(self, forceOneLanguage=False, forceMovingAndSetting=True):
        setupTool = SetupMultilingualSite()
        return setupTool.setupSite(self.context, forceOneLanguage)


class SetupMultilingualSite(object):

    # portal_type that is added as root language folder:
    folder_type = 'Folder'

    def __init__(self, context=None):
        self.previousDefaultPageId = None
        self.context = context

    def setupSite(self, context, forceOneLanguage=False):
        """
        This method is called from the control panel to setup a site in order
        to have root language folders and a redirect view.
        It needs to be executed everytime a new language is added to the
        Available Languages.
        """
        self.context = context
        doneSomething = False
        self.folders = {}
        if isDexterityInstalled:
            self.check_translatable_foldertype()
        pl = getToolByName(self.context, "portal_languages")
        self.languages = languages = pl.getSupportedLanguages()
        if len(languages) == 1 and not forceOneLanguage:
            return 'Only one supported language configured.'
        self.defaultLanguage = pl.getDefaultLanguage()
        available = pl.getAvailableLanguages()
        for language in languages:
            info = available[language]
            doneSomething += self.setUpLanguage(language,
                info.get('native', info.get('name')))
        doneSomething += self.linkTranslations()
        doneSomething += self.removePortalDefaultPage()
        if self.previousDefaultPageId:
            doneSomething += self.resetDefaultPage()
        doneSomething += self.setupSharedFolder()
        doneSomething += self.setupLanguageSwitcher()
        if not doneSomething:
            return "Nothing done."
        else:
            return "Setup of language root folders on Plone site '%s'" % (
                self.context.getId())

    def linkTranslations(self):
        """
        Links the translations of the default language Folders
        """
        doneSomething = False
        try:
            canonical = ITranslationManager(self.folders[self.defaultLanguage])
        except TypeError, e:
            raise TypeError(str(e) + " Are your folders ITranslatable?")
        for language in self.languages:
            if ((language != self.defaultLanguage) and (not
                canonical.has_translation(language))):
                canonical.register_translation(language,
                                               self.folders[language])
                doneSomething = True
        if doneSomething:
            LOG.info("Translations linked.")
        return doneSomething

    def set_default_language_content(self):
        """
        Set default language on content without language
        """
        context = aq_inner(self.context)
        pc = getToolByName(context, "portal_catalog")
        pl = getToolByName(context, "portal_languages")
        pu = getToolByName(context, "portal_url")
        portal = pu.getPortalObject()
        path = '/'.join(portal.getPhysicalPath())
        defaultLanguage = pl.getDefaultLanguage()
        objects = pc.searchResults(path=path, Language='all')
        for brain in objects:
            obj = brain.getObject()
            if ILanguage(obj).get_language() == '' and obj.id != SHARED_NAME:
                ILanguage(obj).set_language(defaultLanguage)
                obj.reindexObject(idxs=["Language"])
                LOG.info("Set language %s on object %s" % (
                    defaultLanguage, '/'.join(obj.getPhysicalPath())))
        pc.manage_reindexIndex(ids=['Language', ])

    def move_default_language_content(self):
        """ Move the content with default language on the root folder
        """
        context = aq_inner(self.context)
        pc = getToolByName(context, "portal_catalog")
        pl = getToolByName(context, "portal_languages")
        pu = getToolByName(context, "portal_url")
        defaultLanguage = pl.getDefaultLanguage()
        folderId = "%s" % defaultLanguage
        folder = getattr(self.context, folderId, None)
        portal = pu.getPortalObject()
        path = '/'.join(portal.getPhysicalPath())
        objects = pc.searchResults(path={'query': path, 'depth': 1},
                                   sort_on='getObjPositionInParent',
                                   Language=defaultLanguage)
        for brain in objects:
            if brain.id != defaultLanguage:
                old_path = brain.getPath()
                cutted = self.context.manage_cutObjects(brain.id)
                folder.manage_pasteObjects(cutted)
                LOG.info("Moved object %s to lang folder %s" % (
                    old_path, defaultLanguage))

    def setUpLanguage(self, code, name):
        """
        Create the language folders on top of the site
        """
        doneSomething = False
        folderId = "%s" % code if code != 'id' else 'id-id'
        folder = getattr(self.context, folderId, None)
        wftool = getToolByName(self.context, 'portal_workflow')
        if folder is None:
            self.context.invokeFactory(self.folder_type, folderId)
            folder = getattr(self.context, folderId)
            ILanguage(folder).set_language(code)
            folder.setTitle(name)
            state = wftool.getInfoFor(folder, 'review_state', None)
            # This assumes a direct 'publish' transition from the initial state
            # We are going to check if its private and has publish action for the out of the box case
            # otherwise don't do anything
            available_transitions = [t['id'] for t in wftool.getTransitionsFor(folder)]
            if state != 'published' and 'publish' in available_transitions:
                wftool.doActionFor(folder, 'publish')
            folder.reindexObject()
            doneSomething = True
            LOG.info("Added '%s' folder: %s" % (code, folderId))
        self.folders[code] = folder
        if not INavigationRoot.providedBy(folder):
            alsoProvides(folder, INavigationRoot)
            doneSomething = True
            LOG.info("INavigationRoot setup on folder '%s'" % code)
        return doneSomething

    def setupSharedFolder(self):
        """
        Create the shared neutral language folder
        """
        doneSomething = False
        folderId = SHARED_NAME
        folder = getattr(self.context, folderId, None)
        wftool = getToolByName(self.context, 'portal_workflow')
        if folder is None:
            # bypass all settings that don't allow creating
            # content in the Plone root
            _createObjectByType(self.folder_type,
                                self.context,
                                folderId)
            #self.context.invokeFactory(self.folder_type, folderId)
            folder = getattr(self.context, folderId)
            ILanguage(folder).set_language(LANGUAGE_INDEPENDENT)
            folder.setTitle("Language Shared")
            state = wftool.getInfoFor(folder, 'review_state', None)
            # This assumes a direct 'publish' transition from the initial state
            available_transitions = [t['id'] for t in wftool.getTransitionsFor(folder)]
            if state != 'published' and 'publish' in available_transitions:
                wftool.doActionFor(folder, 'publish')
            folder.reindexObject()
            doneSomething = True
            LOG.info("Added LANGUAGE_INDEPENDENT folder: %s" % (folderId))
        if not INavigationRoot.providedBy(folder):
            alsoProvides(folder, INavigationRoot)
            doneSomething = True
            LOG.info("INavigationRoot setup on shared folder ")
        return doneSomething

    def removePortalDefaultPage(self):
        """
        Remove the default page of the site
        """
        defaultPageId = self.context.getDefaultPage()
        if not defaultPageId:
            return False
        self.previousDefaultPageId = defaultPageId
        self.context.setDefaultPage(None)
        self.context.reindexObject()
        LOG.info('Portal default page removed.')
        return True

    def resetDefaultPage(self):
        """
        Maintain the default page of the site on the language it was defined
        """
        previousDefaultPage = getattr(self.context, self.previousDefaultPageId)
        languageWrapped = ILanguage(previousDefaultPage, None)
        # If the previous default page cannot be adapted, do nothing.
        # This might be the case if it is a Python Script or other non-portal
        # content
        if languageWrapped is None:
            return False
        language = languageWrapped.get_language()
        pageId = self.previousDefaultPageId
        # test language neutral
        if language == '':
            language = self.defaultLanguage
        target = self.folders[language]
        objects = self.context.manage_cutObjects(pageId)
        try:
            target.manage_pasteObjects(objects)
        except ValueError, exc:
            # This portal_type may not be allowed.  This should not be
            # fatal, so we only log a warning.
            LOG.warn("Could not move default page '%s' to folder '%s': %s"
                     % (pageId, target.getId(), exc))
            return False
        target.setDefaultPage(pageId)
        target.reindexObject()
        defaultPage = getattr(target, pageId)
        defaultPage.reindexObject()
        LOG.info("Moved default page '%s' to folder '%s'." %
            (pageId, target.getId()))
        return True

    def setupLanguageSwitcher(self):
        """
        Add the new default page
        """
        doneSomething = False
        tt = getToolByName(self.context, 'portal_types')
        site = tt['Plone Site']
        if 'language-switcher' not in site.view_methods:
            methods = site.view_methods
            site.view_methods = methods + ('language-switcher', )
            site.default_view = 'language-switcher'
            self.context.reindexObject()
            doneSomething = True
            LOG.info('Root language switcher set up.')
        return doneSomething

    def check_translatable_foldertype(self):
        from plone.dexterity.interfaces import IDexterityFTI
        from plone.multilingualbehavior.interfaces import IDexterityTranslatable
        pt = getToolByName(self.context, 'portal_types')
        fti = getattr(pt, self.folder_type)
        if IDexterityFTI.providedBy(fti):
            behaviors = list(fti.behaviors)
            behaviors.append(IDexterityTranslatable.__identifier__)
            fti.behaviors = behaviors

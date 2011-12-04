from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.interface import alsoProvides
from plone.multilingual.interfaces import ITranslationManager

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


# Setup view imported from LinguaPlone
class SetupView(BrowserView):

    def __init__(self, context, request):
        super(SetupView, self).__init__(context, request)

    def __call__(self, forceOneLanguage=False):
        setupTool = SetupMultilingualSite()
        return setupTool.setupSite(self.context, forceOneLanguage)


class SetupMultilingualSite(object):

    def __init__(self):
        self.previousDefaultPageId = None
        self.context = None

    def setupSite(self, context, forceOneLanguage=False):
        """
        This method is called from the control panel to setup a site in order
        to have root language folders and a redirect view.
        It needs to be executed everytime a new language is added to the
        Available Languages.
        """
        self.context = context
        result = []
        self.folders = {}
        pl = getToolByName(self.context, "portal_languages")
        self.languages = languages = pl.getSupportedLanguages()
        if len(languages) == 1 and not forceOneLanguage:
            return 'Only one supported language configured.'
        self.defaultLanguage = pl.getDefaultLanguage()
        available = pl.getAvailableLanguages()
        for language in languages:
            info = available[language]
            result.extend(self.setUpLanguage(language,
                info.get('native', info.get('name'))))
        result.extend(self.linkTranslations())
        result.extend(self.removePortalDefaultPage())
        if self.previousDefaultPageId:
            result.extend(self.resetDefaultPage())
        result.extend(self.setupLanguageSwitcher())
        if not result:
            return "Nothing done."
        else:
            result.insert(0, "Setup of language root folders on Plone site "
                "'%s'" % self.context.getId())
            return '\n'.join(result)

    def linkTranslations(self):
        """
        Links the translations of the default language Folders
        """
        result = []
        doneSomething = False
        canonical = ITranslationManager(self.folders[self.defaultLanguage])
        for language in self.languages:
            if ((language != self.defaultLanguage) and (not
                canonical.has_translation(language))):
                canonical.register_translation(language,
                                               self.folders[language])
                doneSomething = True
        if doneSomething:
            result.append("Translations linked.")
        return result

    def setUpLanguage(self, code, name):
        """
        Create the language folders on top of the site
        """
        result = []
        folderId = "%s" % code
        folder = getattr(self.context, folderId, None)
        wftool = getToolByName(self.context, 'portal_workflow')
        if folder is None:
            self.context.invokeFactory('Folder', folderId)
            folder = getattr(self.context, folderId)
            folder.setLanguage(code)
            folder.setTitle(name)
            state = wftool.getInfoFor(folder, 'review_state', None)
            # This assumes a direct 'publish' transition from the initial state
            if state != 'published':
                wftool.doActionFor(folder, 'publish')
            folder.reindexObject()
            result.append("Added '%s' folder: %s" % (code, folderId))
        self.folders[code] = folder
        if not INavigationRoot.providedBy(folder):
            alsoProvides(folder, INavigationRoot)
            result.append("INavigationRoot setup on folder '%s'" % code)
        return result

    def removePortalDefaultPage(self):
        """
        Remove the default page of the site
        """
        result = []
        defaultPageId = self.context.getDefaultPage()
        if not defaultPageId:
            return result
        self.previousDefaultPageId = defaultPageId
        self.context.setDefaultPage(None)
        self.context.reindexObject()
        result.append('Portal default page removed.')
        return result

    def resetDefaultPage(self):
        """
        Maintain the default page of the site on the language it was defined
        """
        result = []
        previousDefaultPage = getattr(self.context, self.previousDefaultPageId)
        language = previousDefaultPage.Language()
        pageId = self.previousDefaultPageId
        # test language neutral
        if language == '':
            language = self.defaultLanguage
        target = self.folders[language]
        objects = self.context.manage_cutObjects(pageId)
        target.manage_pasteObjects(objects)
        target.setDefaultPage(pageId)
        target.reindexObject()
        defaultPage = getattr(target, pageId)
        defaultPage.reindexObject()
        result.append("Moved default page '%s' to folder '%s'." %
            (pageId, target.getId()))
        return result

    def setupLanguageSwitcher(self):
        """
        Add the new default page
        """
        result = []
        tt = getToolByName(self.context, 'portal_types')
        site = tt['Plone Site']
        if 'language-switcher' not in site.view_methods:
            methods = site.view_methods
            site.view_methods = methods + ('language-switcher', )
            site.default_view = 'language-switcher'
            self.context.reindexObject()
            result.append('Root language switcher set up.')
        return result

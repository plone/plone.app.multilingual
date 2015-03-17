# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five import BrowserView
from logging import getLogger
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual.subscriber import set_recursive_language
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.locales.languages import _combinedlanguagelist
from plone.i18n.locales.languages import _languagelist
from zope.component.hooks import getSite
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

logger = getLogger('plone.app.multilingual')


# Setup view imported from LinguaPlone
class SetupView(BrowserView):

    def __init__(self, context, request):
        super(SetupView, self).__init__(context, request)

    def __call__(self, forceOneLanguage=False, forceMovingAndSetting=True):
        setupTool = SetupMultilingualSite()
        return setupTool.setupSite(self.context, forceOneLanguage)


class SetupMultilingualSite(object):

    # portal_type that is added as root language folder
    folder_type = 'LRF'

    # portal_type that is added as language independent media folder
    folder_type_language_independent = 'LIF'

    def __init__(self, context=None):
        self.context = context

        self.folders = {}
        self.languages = []
        self.defaultLanguage = None
        self.previousDefaultPageId = None

    def setupSite(self, context, forceOneLanguage=False):
        """This method is called from the control panel to setup a site in
        order to have root language folders and a redirect view. It needs to be
        executed every time a new language is added to the Available Languages.

        """
        self.context = context
        self.folders = {}

        self.ensure_translatable(self.folder_type)
        self.ensure_translatable(self.folder_type_language_independent)

        language_tool = getToolByName(self.context, 'portal_languages')
        self.languages = languages = language_tool.getSupportedLanguages()
        self.defaultLanguage = language_tool.getDefaultLanguage()

        if len(languages) == 1 and not forceOneLanguage:
            return u'Only one supported language configured.'

        doneSomething = False
        available = language_tool.getAvailableLanguages()
        for language in languages:
            info = available[language]
            name = info.get('native', info.get('name'))
            doneSomething += self.setUpLanguage(language, name)

        doneSomething += self.linkTranslations()
        doneSomething += self.removePortalDefaultPage()
        doneSomething += self.setupLanguageSwitcher()
        self.set_default_language_content()

        if not doneSomething:
            return u'Nothing done.'
        else:
            return u"Setup of language root folders on Plone site '%s'" % (
                self.context.getId())

    def linkTranslations(self):
        """Links the translations of the default language Folders
        """
        doneSomething = False

        try:
            canonical = ITranslationManager(self.folders[self.defaultLanguage])
        except TypeError, e:
            raise TypeError(str(e) + u' Are your folders ITranslatable?')

        for language in self.languages:
            if language == self.defaultLanguage:
                continue
            if not canonical.has_translation(language):
                language_folder = self.folders[language]
                canonical.register_translation(language, language_folder)
                doneSomething = True

        if doneSomething:
            logger.info(u'Translations linked.')

        return doneSomething

    def set_default_language_content(self):
        """Set default language on root to language independent
        """
        portal = getSite()
        defaultLanguage = LANGUAGE_INDEPENDENT

        for id_ in portal.objectIds():
            if all([id_ not in _languagelist,
                    id_ not in _combinedlanguagelist,
                    ITranslatable.providedBy(portal[id_])]):
                set_recursive_language(portal[id_], defaultLanguage)

    def setUpLanguage(self, code, name):
        """Create the language folders on top of the site
        """
        doneSomething = False

        if code == 'id':
            folderId = 'id-id'
        else:
            folderId = str(code)

        folder = getattr(self.context, folderId, None)
        wftool = getToolByName(self.context, 'portal_workflow')

        if folder is None:
            _createObjectByType(self.folder_type, self.context, folderId)
            _createObjectByType(self.folder_type_language_independent,
                                self.context[folderId], 'media')

            folder = self.context[folderId]

            ILanguage(folder).set_language(code)
            folder.setTitle(name)

            ILanguage(folder['media']).set_language(code)
            folder['media'].setTitle(u'Media')

            # This assumes a direct 'publish' transition from the initial state
            # We are going to check if its private and has publish action for
            # the out of the box case otherwise don't do anything
            state = wftool.getInfoFor(folder, 'review_state', None)
            available_transitions = [t['id'] for t in
                                     wftool.getTransitionsFor(folder)]
            if state != 'published' and 'publish' in available_transitions:
                wftool.doActionFor(folder, 'publish')

            state = wftool.getInfoFor(folder['media'], 'review_state', None)
            available_transitions = [t['id'] for t in
                                     wftool.getTransitionsFor(folder['media'])]
            if state != 'published' and 'publish' in available_transitions:
                wftool.doActionFor(folder['media'], 'publish')

            # Exclude folder from navigation (if applicable)
            adapter = IExcludeFromNavigation(folder, None)
            if adapter is not None:
                adapter.exclude_from_nav = True

            adapter = IExcludeFromNavigation(folder['media'], None)
            if adapter is not None:
                adapter.exclude_from_nav = True

            # We've modified the object; reindex.
            notify(modified(folder))
            notify(modified(folder['media']))

            doneSomething = True
            logger.info(u"Added '%s' folder: %s" % (code, folderId))

        self.folders[code] = folder
        if not INavigationRoot.providedBy(folder):
            alsoProvides(folder, INavigationRoot)

            doneSomething = True
            logger.info(u"INavigationRoot setup on folder '%s'" % code)

        return doneSomething

    def removePortalDefaultPage(self):
        """Remove the default page of the site
        """

        defaultPageId = self.context.getDefaultPage()
        if not defaultPageId:
            return False

        self.previousDefaultPageId = defaultPageId
        self.context.setDefaultPage(None)
        self.context.reindexObject()

        logger.info(u'Portal default page removed.')
        return True

    def resetDefaultPage(self):
        """Maintain the default page of the site on the language it was defined
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
            logger.warn((u"Could not move default page '{0:s}' j"
                         u"to folder '{1:s}': {2:s}").format(
                pageId, target.getId(), exc))
            return False

        target.setDefaultPage(pageId)
        target.reindexObject()
        defaultPage = getattr(target, pageId)
        defaultPage.reindexObject()

        logger.info(u"Moved default page '{0}' to folder '{1}'.".format(
            pageId, target.getId()))

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
            logger.info(u'Root language switcher set up.')

        return doneSomething

    def ensure_translatable(self, type_):
        types_tool = getToolByName(self.context, 'portal_types')
        fti = getattr(types_tool, type_)

        if IDexterityFTI.providedBy(fti):
            behaviors = list(fti.behaviors)
            behaviors.append(IDexterityTranslatable.__identifier__)
            behaviors = tuple(set(behaviors))
            fti._updateProperty('behaviors', behaviors)

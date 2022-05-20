from logging import getLogger
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual import _
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual.subscriber import set_recursive_language
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.locales.languages import _combinedlanguagelist
from plone.i18n.locales.languages import _languagelist
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguage
from Products.CMFPlone.utils import _createObjectByType
from Products.Five import BrowserView
from zope.component.hooks import getSite
from zope.event import notify
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.lifecycleevent import modified


logger = getLogger("plone.app.multilingual")


# Setup view imported from LinguaPlone
class SetupView(BrowserView):
    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self, forceOneLanguage=False, forceMovingAndSetting=True):
        setupTool = SetupMultilingualSite()
        return setupTool.setupSite(self.context, forceOneLanguage)


class SetupMultilingualSite:

    # portal_type that is added as root language folder
    folder_type = "LRF"

    # portal_type that is added as language independent asset folder
    folder_type_language_independent = "LIF"

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

        language_tool = getToolByName(self.context, "portal_languages")
        self.languages = languages = language_tool.getSupportedLanguages()
        self.defaultLanguage = language_tool.getDefaultLanguage()

        if len(languages) == 1 and not forceOneLanguage:
            return "Only one supported language configured."

        doneSomething = False
        available = language_tool.getAvailableLanguages()
        for language in languages:
            info = available[language]
            name = info.get("native", info.get("name"))
            doneSomething += self.setUpLanguage(language, name)

        doneSomething += self.linkTranslations()
        doneSomething += self.removePortalDefaultPage()
        doneSomething += self.setupLanguageSwitcher()
        self.set_default_language_content()

        if not doneSomething:
            return "Nothing done."
        else:
            return "Setup of language root folders on Plone site '%s'" % (
                self.context.getId()
            )

    def linkTranslations(self):
        """Links the translations of the default language Folders"""
        doneSomething = False

        try:
            canonical = ITranslationManager(self.folders[self.defaultLanguage])
        except TypeError as e:
            raise TypeError(str(e) + " Are your folders ITranslatable?")

        for language in self.languages:
            if language == self.defaultLanguage:
                continue
            if not canonical.has_translation(language):
                language_folder = self.folders[language]
                canonical.register_translation(language, language_folder)
                doneSomething = True

        if doneSomething:
            logger.info("Translations linked.")

        return doneSomething

    def set_default_language_content(self):
        """Set default language on root to language independent"""
        portal = getSite()
        defaultLanguage = LANGUAGE_INDEPENDENT

        for id_ in portal.objectIds():
            if all(
                [
                    id_ not in _languagelist,
                    id_ not in _combinedlanguagelist,
                    ITranslatable.providedBy(portal[id_]),
                ]
            ):
                set_recursive_language(portal[id_], defaultLanguage)

    def setUpLanguage(self, code, name):
        """Create the language folders on top of the site"""
        doneSomething = False

        if code == "id":
            folderId = "id-id"
        else:
            folderId = str(code)

        folder = getattr(self.context, folderId, None)
        wftool = getToolByName(self.context, "portal_workflow")

        assets_folder_id = translate(
            _("assets_folder_id", default="assets"),
            domain="plone",
            target_language=folderId,
        )
        assets_folder_title = translate(
            _("assets_folder_title", default="Assets"),
            domain="plone",
            target_language=folderId,
        )

        if folder is None:
            _createObjectByType(self.folder_type, self.context, folderId)
            _createObjectByType(
                self.folder_type_language_independent,
                self.context[folderId],
                assets_folder_id,
            )

            folder = self.context[folderId]

            ILanguage(folder).set_language(code)
            folder.setTitle(name)

            ILanguage(folder[assets_folder_id]).set_language(code)
            folder[assets_folder_id].setTitle(assets_folder_title)

            # This assumes a direct 'publish' transition from the initial state
            # We are going to check if its private and has publish action for
            # the out of the box case otherwise don't do anything
            state = wftool.getInfoFor(folder, "review_state", None)
            available_transitions = [t["id"] for t in wftool.getTransitionsFor(folder)]
            if state != "published" and "publish" in available_transitions:
                wftool.doActionFor(folder, "publish")

            state = wftool.getInfoFor(folder[assets_folder_id], "review_state", None)
            available_transitions = [
                t["id"] for t in wftool.getTransitionsFor(folder[assets_folder_id])
            ]  # noqa
            if state != "published" and "publish" in available_transitions:
                wftool.doActionFor(folder[assets_folder_id], "publish")

            # Exclude folder from navigation (if applicable)
            adapter = IExcludeFromNavigation(folder, None)
            if adapter is not None:
                adapter.exclude_from_nav = True

            adapter = IExcludeFromNavigation(folder[assets_folder_id], None)
            if adapter is not None:
                adapter.exclude_from_nav = True

            # We've modified the object; reindex.
            notify(modified(folder))
            notify(modified(folder[assets_folder_id]))

            doneSomething = True
            logger.info(f"Added '{code}' folder: {folderId}")

        self.folders[code] = folder
        if not INavigationRoot.providedBy(folder):
            alsoProvides(folder, INavigationRoot)

            doneSomething = True
            logger.info("INavigationRoot setup on folder '%s'" % code)

        return doneSomething

    def removePortalDefaultPage(self):
        """Remove the default page of the site"""

        defaultPageId = self.context.getDefaultPage()
        if not defaultPageId:
            return False

        self.previousDefaultPageId = defaultPageId
        self.context.setDefaultPage(None)
        self.context.reindexObject()

        logger.info("Portal default page removed.")
        return True

    def resetDefaultPage(self):
        """Maintain the default page of the site on the language it was defined"""
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
        if language == "":
            language = self.defaultLanguage
        target = self.folders[language]
        objects = self.context.manage_cutObjects(pageId)

        try:
            target.manage_pasteObjects(objects)
        except ValueError as exc:
            # This portal_type may not be allowed.  This should not be
            # fatal, so we only log a warning.
            logger.warn(
                (
                    "Could not move default page '{:s}' j" "to folder '{:s}': {:s}"
                ).format(pageId, target.getId(), exc)
            )
            return False

        target.setDefaultPage(pageId)
        target.reindexObject()
        defaultPage = getattr(target, pageId)
        defaultPage.reindexObject()

        logger.info(f"Moved default page '{pageId}' to folder '{target.getId()}'.")

        return True

    def setupLanguageSwitcher(self):
        """
        Add the new default page
        """
        doneSomething = False

        tt = getToolByName(self.context, "portal_types")
        site = tt["Plone Site"]

        methods = tuple(site.view_methods)
        if "language-switcher" not in methods:
            site.view_methods = methods + ("language-switcher",)
            site.default_view = "language-switcher"
            self.context.reindexObject()

            doneSomething = True
            logger.info("Root language switcher set up.")

        return doneSomething

    def ensure_translatable(self, type_):
        types_tool = getToolByName(self.context, "portal_types")
        fti = getattr(types_tool, type_)

        if IDexterityFTI.providedBy(fti):
            behaviors = list(fti.behaviors)
            behaviors.append("plone.translatable")
            behaviors = tuple(set(behaviors))
            fti._updateProperty("behaviors", behaviors)

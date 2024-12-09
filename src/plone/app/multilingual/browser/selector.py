from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema

from zope.component import getMultiAdapter
from plone.i18n.interfaces import INegotiateLanguage
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_chain
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import NOTG
from plone.app.multilingual.manager import TranslationManager
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import queryAdapter
from zope.component.hooks import getSite
from ZTUtils import make_query


def addQuery(request, url, exclude=tuple(), **extras):
    """Adds the incoming GET query to the end of the url
    so that is propagated through the redirect hoops
    """
    formvariables = {}
    for k, v in request.form.items():
        if k not in exclude:
            formvariables[k] = v
    for k, v in extras.items():
        formvariables[k] = v
    try:
        if len(formvariables) > 0:
            url += "?" + make_query(formvariables)
    # Again, LinguaPlone did this try/except here so I'm keeping it.
    except UnicodeError:
        pass
    return url


def get_root_request(request):
    """If in a subrequest, go up to the root request and return it"""

    def parent_request(current_request):
        preq = current_request.get("PARENT_REQUEST", None)
        if preq:
            return parent_request(preq)
        return current_request

    return parent_request(request)


def getPostPath(context, request):
    """Finds the path to be added at the end of a context.

    This is useful because you might have a view or even something more long
    (form and widget traversing) at the very end of the absolute_url
    of a translated item.
    When you get the translated item absolute_url,
    you want to also have the eventual views etc ported over:
    this function does that.
    """
    # This is copied over from LinguaPlone
    # because there's a lot of knowledge embed in it.

    # We need to find the actual translatable content object. As an
    # optimization we assume it is within the last three segments.
    path = context.getPhysicalPath()
    path_info = get_root_request(request).get("PATH_INFO", "")
    match = [p for p in path[-3:] if p]
    current_path = [pi for pi in path_info.split("/") if pi]
    append_path = []
    stop = False
    while current_path and not stop:
        check = current_path.pop()
        if check == "VirtualHostRoot" or check.startswith("_vh_"):
            # Once we hit a VHM marker, we should stop
            break
        if check not in match:
            append_path.insert(0, check)
        else:
            stop = True
    if append_path:
        append_path.insert(0, "")
    return "/".join(append_path)


NOT_TRANSLATED_YET_TEMPLATE = "/not_translated_yet"


class LanguageSelectorViewlet(LanguageSelector):
    """Language selector for translatable content."""

    def languages(self):
        languages_info = super().languages()
        results = []
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix="plone")
        translation_group = queryAdapter(self.context, ITG)
        if translation_group is None:
            translation_group = NOTG

        for lang_info in languages_info:
            # Avoid to modify the original language dict
            data = lang_info.copy()
            data["translated"] = True
            query_extras = {}
            if not settings.set_cookie_always:
                query_extras.update(
                    {
                        "set_language": data["code"],
                    }
                )
            post_path = getPostPath(self.context, self.request)
            if post_path:
                query_extras["post_path"] = post_path
            site = getSite()

            url = self.build_multilingual_url(translation_group, lang_info["code"])

            data["url"] = addQuery(
                self.request,
                site.absolute_url().rstrip("/")
                + "/@@multilingual-selector/%s/%s"
                % (translation_group, lang_info["code"]),
                **query_extras,
            )
            results.append(data)
        return results

    def build_multilingual_url(self, tg, lang):
        url = self.getDestination(tg, lang)
        if url:
            # We have a direct translation, full wrapping
            url = self.wrapDestination(url)
        else:
            registry = getUtility(IRegistry)
            policies = registry.forInterface(
                IMultiLanguageExtraOptionsSchema, prefix="plone"
            )
            if policies.selector_lookup_translations_policy == "closest":
                url = self.getClosestDestination(tg, lang)
            else:
                url = self.getDialogDestination(tg, lang)
            # No wrapping cause that's up to the policies
            # (they should already have done that)

        return url

    def wrapDestination(self, url, postpath=True):
        """Fix the translation url appending the query
        and the eventual append path.
        """
        if postpath:
            url += self.request.form.get("post_path", "")
        return addQuery(self.request, url, exclude=("post_path",))

    def getDialogDestination(self, tg, lang):
        """Get the "not translated yet" dialog URL.
        It's located on the root and shows the translated objects of that TG
        """
        dialog_view = NOT_TRANSLATED_YET_TEMPLATE
        postpath = False
        # The dialog view shouldn't appear on the site root
        # because that is untraslatable by default.
        # And since we are mapping the root on itself,
        # we also do postpath insertion (@@search case)

        root = getToolByName(self.context, "portal_url")
        url = root() + dialog_view + "/" + tg
        return self.wrapDestination(url, postpath=postpath)

    def getParentChain(self, context):
        # XXX: switch it over to parent pointers if needed
        return aq_chain(context)

    def getClosestDestination(self, tg, lang):
        """Get the "closest translated object" URL."""
        # We should travel the parent chain using the catalog here,
        # but I think using the acquisition chain is faster
        # (or well, __parent__ pointers) because the catalog
        # would require a lot of queries, while technically,
        # having done traversal up to this point you should
        # have the objects in memory already

        # As we don't have any content object we are going to look
        # for the best option

        site = getSite()
        root = getToolByName(site, "portal_url")
        ltool = getToolByName(site, "portal_languages")

        # We are using TranslationManager to get the translations of a
        # string tg
        try:
            manager = TranslationManager(tg)
            languages = manager.get_translations()
        except AttributeError:
            languages = []
        if len(languages) == 0:
            # If there is no results there are no translations
            # we move to portal root
            return self.wrapDestination(root(), postpath=False)

        # We are going to see if there is the preferred language translation
        # Otherwise we get the first as context to look for translation
        preferred = ltool.getPreferredLanguage(self.request)
        if preferred in languages:
            context = languages[preferred]
        else:
            context = languages[list(languages.keys())[0]]

        checkPermission = getSecurityManager().checkPermission
        chain = self.getParentChain(context)
        for item in chain:
            if ISiteRoot.providedBy(item) and not ILanguageRootFolder.providedBy(item):
                # We do not care to get a permission error
                # if the whole of the portal cannot be viewed.
                # Having a permission issue on the root is fine;
                # not so much for everything else so that is checked there
                return self.wrapDestination(item.absolute_url())
            try:
                canonical = ITranslationManager(item)
            except TypeError:
                if not ITranslatable.providedBy(item):
                    # In case there it's not translatable go to parent
                    # This solves the problem when a parent is not
                    # ITranslatable
                    continue
                else:
                    raise
            translation = canonical.get_translation(lang)
            if translation and (
                INavigationRoot.providedBy(translation)
                or bool(checkPermission("View", translation))
            ):
                # Not a direct translation, therefore no postpath
                # (the view might not exist on a different context)
                return self.wrapDestination(translation.absolute_url(), postpath=False)
        # Site root's the fallback
        return self.wrapDestination(root(), postpath=False)

    def getDestination(self, tg, lang):
        # Look for the element
        url = None
        # We check if it's shared content
        query = {"TranslationGroup": tg}
        ptool = getToolByName(self.context, "portal_catalog")
        brains = ptool.searchResults(query)
        is_shared = False
        for brain in brains:
            if "-" in brain.UID:
                is_shared = True
                brain_to_use = brain
                break
        if is_shared:
            target_uid = brain_to_use.UID.split("-")[0]
            if lang:
                target_uid += "-" + lang
            else:
                # The negotiated language
                language = getMultiAdapter(
                    (self.context, self.request), INegotiateLanguage
                ).language
                target_uid += "-" + language
            results = ptool.searchResults(UID=target_uid)
            if len(results) > 0:
                url = results[0].getURL()
            return url
        # Normal content
        query = {"TranslationGroup": tg}
        if lang:
            query = {"TranslationGroup": tg, "Language": lang}
        else:
            # The negotiated language
            language = getMultiAdapter(
                (self.context, self.request), INegotiateLanguage
            ).language
            query = {"TranslationGroup": self.tg, "Language": language}

        # Comparison to plone/app/multilingual/browser/setup.py#L129
        if query.get("Language") == "id-id":
            query["Language"] = "id"

        results = ptool.searchResults(query)
        if len(results) > 0:
            url = results[0].getURL()
        return url

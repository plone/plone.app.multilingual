from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import NOTG
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry
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
            data["url"] = addQuery(
                self.request,
                site.absolute_url().rstrip("/")
                + "/@@multilingual-selector/%s/%s"
                % (translation_group, lang_info["code"]),
                **query_extras
            )
            results.append(data)
        return results

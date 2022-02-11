from plone.app.layout.viewlets.common import ViewletBase
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguage
from urllib.parse import quote_plus


def _cache_until_catalog_change(fun, self):
    catalog = getToolByName(self.context, "portal_catalog")
    key = "{0}{1}{2}"
    key = key.format(
        fun.__name__, catalog.getCounter(), "/".join(self.context.getPhysicalPath())
    )
    return key


class OneLanguageConfiguredNoticeViewlet(ViewletBase):
    """Notice the user that PAM is installed and only one language
    is configured.
    """

    available = False

    def render(self):
        if self.available:
            return self.index()

        return ""

    def update(self):
        lt = getToolByName(self.context, "portal_languages")
        supported = lt.getSupportedLanguages()
        self.available = len(supported) <= 1


class AddFormIsATranslationViewlet(ViewletBase):
    """Notice the user that this add form is a translation"""

    available = False

    def language(self):
        return self.lang

    def languages(self):
        """Returns list of languages."""
        self.tool = getToolByName(self.context, "portal_languages", None)
        if self.tool is None:
            return []

        languages = {
            lang: info
            for (lang, info) in self.tool.getAvailableLanguageInformation().items()
            if info["selected"]
        }

        return languages

    def language_name(self, lang_code):
        return self.languages().get(lang_code).get("native")

    def render(self):
        if self.available:
            return self.index()
        return ""

    def returnURL(self):
        # Get translation info for getting the translation source
        translation_info = getattr(self.request, "translation_info", {})
        translation_group = translation_info.get("tg")
        source_language = translation_info.get("source_language")

        if not (translation_group or source_language):
            return ""

        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(Language=source_language, TranslationGroup=translation_group)
        if len(brains) != 1:
            return ""
        source = brains[0].getObject()

        # Get the factory
        types_tool = getToolByName(source, "portal_types")

        # Note: we don't check 'allowed' or 'available' here,
        # because these are slow. We assume the 'allowedTypes'
        # list has already performed the necessary calculations
        actions = types_tool.listActionInfos(
            object=self.context,
            check_permissions=False,
            check_condition=False,
            category="folder/add",
        )

        addActionsById = {a["id"]: a for a in actions}

        typeId = source.portal_type

        addAction = addActionsById.get(typeId, None)
        if addAction is None:
            url = None
        else:
            url = addAction["url"]
        if not url:
            url = "{}/createObject?type_name={}".format(
                source.absolute_url(),
                quote_plus(typeId),
            )
        return url

    def update(self):
        try:
            tg = self.request.translation_info["tg"]
        except AttributeError:
            return
        self.available = True
        if ITranslatable.providedBy(self.context):
            self.lang = ILanguage(self.context).get_language()
        else:
            self.lang = "NaN"
        catalog = getToolByName(self.context, "portal_catalog")
        query = {"TranslationGroup": tg}
        self.origin = catalog.searchResults(query)


class AddFormATIsATranslationViewlet(AddFormIsATranslationViewlet):
    # XXX move this class to archetypes multilingual!
    # btw., it is not used in here.
    """Notice the user that this AT add form is a translation"""

    def update(self):
        """It's only for AT on factory so we check"""
        factory = getToolByName(self.context, "portal_factory", None)
        if factory is None or not factory.isTemporary(self.context):
            return
        super(AddFormIsATranslationViewlet, self).update()


class AlternateLanguagesViewlet(ViewletBase):
    """Notice search engines about alternates languages of current
    content item
    """

    alternatives = []

    @ram.cache(_cache_until_catalog_change)
    def get_alternate_languages(self):
        """Cache relative urls only. If we have multilingual sites
        and multi domain site caching absolute urls will result in
        very inefficient caching. Build absolute url in template.
        """
        tm = ITranslationManager(self.context)
        catalog = getToolByName(self.context, "portal_catalog")
        results = catalog(TranslationGroup=tm.query_canonical())

        alternates = []
        for item in results:
            url = item.getURL()
            alternates.append(
                {
                    "lang": item.Language,
                    "url": url,
                }
            )

        return alternates

    def update(self):
        super().update()
        self.alternates = self.get_alternate_languages()

    @property
    def available(self):
        return len(self.alternates) > 1

    def render(self):
        if self.available:
            return self.index()
        return ""

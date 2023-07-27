from Acquisition import aq_inner
from plone.i18n.interfaces import ILanguageUtility
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility


class LanguageSwitcher(BrowserView):
    def __call__(self):
        """Redirect to the preferred language top-level folder.

        If no folder for preferred language exists, redirect to default
        language.

        Copy from LinguaPlone
        """
        context = aq_inner(self.context)
        plt = getToolByName(context, "portal_languages")
        pref = plt.getPreferredLanguage(self.request)
        default = plt.getDefaultLanguage()
        # Handle Indonesian: its language code "id" is not allowed in Plone as
        # content id, so its LRF is called "id-id".
        pref = "id-id" if pref == "id" else pref
        default = "id-id" if default == "id" else default
        ids = self.context.keys()
        target = (pref in ids) and pref or default
        url = f"{context.absolute_url()}/{target}"

        # We need to set the language cookie on the first response or it will
        # be set on the frontpage itself, making it uncachable
        # In case of Indonesian, we need to use 'id', not 'id-id'.
        target = "id" if target == "id-id" else target
        tool = getUtility(ILanguageUtility)
        # setLanguageCookie calls getLanguageCookie, and only sets a cookie when needed.
        tool.setLanguageCookie(target, request=self.request)

        self.request.response.redirect(url, status=302)

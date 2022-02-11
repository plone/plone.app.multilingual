from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


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
        ids = self.context.keys()
        target = (pref in ids) and pref or default
        url = f"{context.absolute_url()}/{target}"

        # We need to set the language cookie on the first response or it will
        # be set on the frontpage itself, making it uncachable
        langCookie = self.request.cookies.get("I18N_LANGUAGE")
        if not langCookie or langCookie != target:
            self.request.response.setCookie("I18N_LANGUAGE", target, path="/")

        self.request.response.redirect(url, status=302)

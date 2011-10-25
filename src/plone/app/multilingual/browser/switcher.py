from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.registry.interfaces import IRegistry
from plone.app.multilingual.interfaces import IMultilinguaSettings

class LanguageSwitcher(BrowserView):

    def __call__(self):
        """Redirect to the preferred language top-level folder.

        If no folder for preferred language exists, redirect to default
        language.
        """
        context = aq_inner(self.context)
        plt = getToolByName(context, 'portal_languages')
        pref = plt.getPreferredLanguage()
        default = plt.getDefaultLanguage()
        registry = getUtility(IRegistry)
        root_folder = registry.forInterface(IMultilinguaSettings)
        if pref in root_folder.default_layout_languages.keys():
            target = pref
            target_url = root_folder.default_layout_languages[pref]
        else:
            target = default
            target_url = "/"

        url = "%s/%s" % (context.absolute_url(), target_url)

        # We need to set the language cookie on the first response or it will
        # be set on the frontpage itself, making it uncachable
        langCookie = self.request.cookies.get('I18N_LANGUAGE')
        if not langCookie:
            self.request.response.setCookie('I18N_LANGUAGE', target, path='/')

        self.request.response.redirect(url, status=301)

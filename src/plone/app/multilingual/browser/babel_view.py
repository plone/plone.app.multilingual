from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.multilingual.interfaces import ITranslationManager
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from plone.app.i18n.locales.browser.selector import LanguageSelector
from AccessControl.SecurityManagement import getSecurityManager

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema


class BabelView(BrowserView):
    __call__ = ViewPageTemplateFile('babel_view.pt')


class BabelEdit(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.RESPONSE.redirect(self.context.absolute_url() + '/at_babel_edit')


class BabelUtils(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((context, request), name="plone_portal_state")
        self.portal_url = portal_state.portal_url()
        self.group = ITranslationManager(self.context)

    def getGroup(self):
        return self.group

    def getTranslatedLanguages(self):
        return self.group.get_translated_languages()

    def getPortal(self):
        portal_url = getToolByName(self.context, 'portal_url')
        return portal_url

    def objToTranslate(self):
        return self.context

    def gtenabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        return settings.google_translation_key != ''

    def languages(self):
        context = aq_inner(self.context)

        ls = LanguageSelector(self.context, self.request, None, None)
        ls.update()
        results = ls.languages()

        supported_langs = [v['code'] for v in results]
        missing = set([str(c) for c in supported_langs])

        lsv = LanguageSelectorViewlet(self.context, self.request, None, None)
        translations = lsv._translations(missing)

        # We want to see the babel_view
        append_path = ('', 'babel_view',)
        _checkPermission = getSecurityManager().checkPermission
        non_viewable = set()
        for data in results:
            code = str(data['code'])
            data['translated'] = code in translations.keys()

            appendtourl = '/'.join(append_path)

            if data['translated']:
                trans, direct, has_view_permission = translations[code]
                if not has_view_permission:
                    # shortcut if the user cannot see the item
                    non_viewable.add((data['code']))
                    continue
                data['url'] = trans.absolute_url() + appendtourl
            else:
                non_viewable.add((data['code']))

        # filter out non-viewable items
        results = [r for r in results if r['code'] not in non_viewable]
        return results

# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_chain
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.i18n.interfaces import INegotiateLanguage
from borg.localrole.interfaces import IFactoryTempFolder
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.browser.selector import NOT_TRANSLATED_YET_TEMPLATE
from plone.app.multilingual.browser.selector import addQuery
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.manager import TranslationManager
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

try:
    from Products.ATContentTypes.interfaces.factory import IFactoryTool
except ImportError:
    try:
        from Products.CMFPlone.interfaces.factory import IFactoryTool
    except ImportError:
        # gone in Plone 5.1 w/o ATCT

        class IFactoryTool(Interface):
            pass


@implementer(IPublishTraverse)
class universal_link(BrowserView):
    """ Redirects the user to the negotiated translated page
        based on the user preferences in the user's browser.
    """

    def __init__(self, context, request):
        super(universal_link, self).__init__(context, request)
        self.tg = None
        self.lang = None

    def publishTraverse(self, request, name):

        if self.tg is None:  # ../@@universal-link/translationgroup
            self.tg = name
        elif self.lang is None:  # ../@@universal-link/translationgroup/lang
            self.lang = name
        else:
            raise NotFound(self, name, request)

        return self

    def getDestination(self):
        # Look for the element
        url = None
        # We check if it's shared content
        query = {'TranslationGroup': self.tg}
        ptool = getToolByName(self.context, 'portal_catalog')
        brains = ptool.searchResults(query)
        is_shared = False
        for brain in brains:
            if '-' in brain.UID:
                is_shared = True
                brain_to_use = brain
                break
        if is_shared:
            target_uid = brain_to_use.UID.split('-')[0]
            if self.lang:
                target_uid += '-' + self.lang
            else:
                # The negotiated language
                language = getMultiAdapter((self.context, self.request),
                                           INegotiateLanguage).language
                target_uid += '-' + language
            results = ptool.searchResults(UID=target_uid)
            if len(results) > 0:
                url = results[0].getURL()
            return url
        # Normal content
        query = {'TranslationGroup': self.tg}
        if self.lang:
            query = {'TranslationGroup': self.tg, 'Language': self.lang}
        else:
            # The negotiated language
            language = getMultiAdapter((self.context, self.request),
                                       INegotiateLanguage).language
            query = {'TranslationGroup': self.tg, 'Language': language}

        # Comparison to plone/app/multilingual/browser/setup.py#L129
        if query.get('Language') == 'id-id':
            query['Language'] = 'id'

        results = ptool.searchResults(query)
        if len(results) > 0:
            url = results[0].getURL()
        return url

    def __call__(self):
        url = self.getDestination()
        if not url:
            root = getToolByName(self.context, 'portal_url')
            url = root()
        self.request.RESPONSE.redirect(url)


class selector_view(universal_link):

    def getDialogDestination(self):
        """Get the "not translated yet" dialog URL.
        It's located on the root and shows the translated objects of that TG
        """
        dialog_view = NOT_TRANSLATED_YET_TEMPLATE
        postpath = False
        # The dialog view shouldn't appear on the site root
        # because that is untraslatable by default.
        # And since we are mapping the root on itself,
        # we also do postpath insertion (@@search case)

        root = getToolByName(self.context, 'portal_url')
        url = root() + dialog_view + '/' + self.tg
        return self.wrapDestination(url, postpath=postpath)

    def getParentChain(self, context):
        # XXX: switch it over to parent pointers if needed
        return aq_chain(context)

    def getClosestDestination(self):
        """Get the "closest translated object" URL.
        """
        # We should travel the parent chain using the catalog here,
        # but I think using the acquisition chain is faster
        # (or well, __parent__ pointers) because the catalog
        # would require a lot of queries, while technically,
        # having done traversal up to this point you should
        # have the objects in memory already

        # As we don't have any content object we are going to look
        # for the best option

        site = getSite()
        root = getToolByName(site, 'portal_url')
        ltool = getToolByName(site, 'portal_languages')

        # We are using TranslationManager to get the translations of a
        # string tg
        manager = TranslationManager(self.tg)
        context = None
        languages = manager.get_translations()
        if len(languages) == 0:
            # If there is no results there are no translations
            # we move to portal root
            return self.wrapDestination(root(), postpath=False)

        # We are going to see if there is the preferred language translation
        # Otherwise we get the first as context to look for translation
        prefered = ltool.getPreferredLanguage(self.request)
        if prefered in languages:
            context = languages[prefered]
        else:
            context = languages[languages.keys()[0]]

        checkPermission = getSecurityManager().checkPermission
        chain = self.getParentChain(context)
        for item in chain:
            if ISiteRoot.providedBy(item) \
               and not ILanguageRootFolder.providedBy(item):
                # We do not care to get a permission error
                # if the whole of the portal cannot be viewed.
                # Having a permission issue on the root is fine;
                # not so much for everything else so that is checked there
                return self.wrapDestination(item.absolute_url())
            elif IFactoryTempFolder.providedBy(item) or \
                    IFactoryTool.providedBy(item):
                # TempFolder or portal_factory, can't have a translation
                continue
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
            translation = canonical.get_translation(self.lang)
            if translation and (
                INavigationRoot.providedBy(translation) or
                bool(checkPermission('View', translation))
            ):
                # Not a direct translation, therefore no postpath
                # (the view might not exist on a different context)
                return self.wrapDestination(translation.absolute_url(),
                                            postpath=False)
        # Site root's the fallback
        return self.wrapDestination(root(), postpath=False)

    def wrapDestination(self, url, postpath=True):
        """Fix the translation url appending the query
        and the eventual append path.
        """
        if postpath:
            url += self.request.form.get('post_path', '')
        return addQuery(
            self.request,
            url,
            exclude=('post_path')
        )

    def __call__(self):
        url = self.getDestination()
        if url:
            # We have a direct translation, full wrapping
            url = self.wrapDestination(url)
        else:
            registry = getUtility(IRegistry)
            policies = registry.forInterface(IMultiLanguageExtraOptionsSchema,
                                             prefix="plone")
            if policies.selector_lookup_translations_policy == 'closest':
                url = self.getClosestDestination()
            else:
                url = self.getDialogDestination()
            # No wrapping cause that's up to the policies
            # (they should already have done that)
        self.request.response.redirect(url)


@implementer(IPublishTraverse)
class not_translated_yet(BrowserView):
    """ View to inform user that the view requested is not translated yet,
        and shows the already translated related content.
    """
    __call__ = ViewPageTemplateFile('templates/not_translated_yet.pt')

    def __init__(self, context, request):
        super(not_translated_yet, self).__init__(context, request)
        self.tg = None

    def publishTraverse(self, request, name):
        if self.tg is None:  # ../@@not_translated_yet/translationgroup
            self.tg = TranslationManager(name)
        else:
            raise NotFound(self, name, request)
        return self

    def already_translated(self):
        if self.tg is not None:
            # Need to check if the user has permission
            return self.tg.get_restricted_translations().items()
        else:
            return []

    def has_any_translation(self):

        if self.tg is not None:
            return len(self.tg.get_restricted_translations().items()) > 0
        else:
            return 0

    def language_name(self, lang=None):
        """ Get the current language native name """
        if lang is None:
            lang_code = self.request.get('set_language')
        else:
            lang_code = lang
        util = getUtility(IContentLanguageAvailability)
        data = util.getLanguages(True)
        lang_info = data.get(lang_code)
        if lang_info is None:
            return None
        return lang_info.get('native', None) or lang_info.get('name')

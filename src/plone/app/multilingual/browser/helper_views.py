from zope.interface import implements
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse, NotFound

from Acquisition import aq_chain
from Acquisition import aq_inner
from AccessControl.SecurityManagement import getSecurityManager
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFPlone.interfaces.factory import IFactoryTool
from borg.localrole.interfaces import IFactoryTempFolder
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.registry.interfaces import IRegistry

from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ITranslatable
from plone.app.multilingual.browser.controlpanel import IMultiLanguagePolicies
from .selector import addQuery
from .selector import NOT_TRANSLATED_YET_TEMPLATE


class universal_link(BrowserView):
    """ Redirects the user to the negotiated translated page
        based on the user preferences in the user's browser.
    """

    implements(IPublishTraverse)

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
        ptool = getToolByName(self.context, 'portal_catalog')
        query = {'TranslationGroup': self.tg}
        if self.lang:
            query = {'TranslationGroup': self.tg, 'Language': self.lang}
        else:
            # The negotiated language
            ltool = getToolByName(self.context, 'portal_languages')
            if len(ltool.getRequestLanguages()) > 0:
                language = ltool.getRequestLanguages()[0]
                query = {'TranslationGroup': self.tg, 'Language': language}
        results = ptool.searchResults(query)
        url = None
        if len(results) > 0:
            url = results[0].getURL()
        return url

    def __call__(self):
        url = self.getDestination()
        if not url:
            root = getToolByName(self.context, 'portal_url')
            url = root.url()
        self.request.RESPONSE.redirect(url)


class selector_view(universal_link):

    def getDialogDestination(self):
        """Get the "not translated yet" dialog URL.
        """
        dialog_view = NOT_TRANSLATED_YET_TEMPLATE
        postpath = False
        # The dialog view shouldn't appear on the site root
        # because that is untraslatable by default.
        # And since we are mapping the root on itself,
        # we also do postpath insertion (@@search case)

        #if ISiteRoot.providedBy(self.context):
        #    dialog_view = ''
        #    postpath = True

        # We first look for the content on the request language
        ltool = getToolByName(self.context, 'portal_languages')
        self.lang = ltool.getRequestLanguages()
        url = self.getDestination()
        if url:
            return self.wrapDestination(url + dialog_view, postpath=postpath)
        # We look for the default language content
        self.lang = ltool.getDefaultLanguage()
        url = self.getDestination()
        if url:
            return self.wrapDestination(url + dialog_view, postpath=postpath)
        # We look for the first translation we find
        ptool = getToolByName(self.context, 'portal_catalog')
        query = {'TranslationGroup': self.tg}
        results = ptool.searchResults(query)
        url = None
        if len(results) > 0:
            url = results[0].getUrl()
            return self.wrapDestination(url + dialog_view, postpath=postpath)


    def getParentChain(self, context):
        # XXX: switch it over to parent pointers if needed
        return aq_chain(context)

    def getClosestDestination(self):
        """Get the "closest translated object" URL.
        """
        # We sould travel the parent chain using the catalog here,
        # but I think using the acquisition chain is faster
        # (or well, __parent__ pointers) because the catalog
        # would require a lot of queries, while technically,
        # having done traversal up to this point you should
        # have the objects in memory already

        # As we don't have any content object we are going to look 
        # for the best option

        ltool = getToolByName(self.context, 'portal_languages')
        ptool = getToolByName(self.context, 'portal_catalog')
        query = {'TranslationGroup': self.tg, 'Language': 'all'}
        results = ptool.searchResults(query)
        context = None
        if len(results) == 0:
            # If there is no results there are no translations
            # we move to portal root
            return self.wrapDestination(root.url(), postpath=False)
        for result in results:
            if result.Language in ltool.getRequestLanguages():
                context = result.getObject()
            elif result.Language == ltool.getDefaultLanguage():
                context = result.getObject()
        if context is None:
            context = results[0].getObject()

        checkPermission = getSecurityManager().checkPermission
        chain = self.getParentChain(context)
        for item in chain:
            if ISiteRoot.providedBy(item):
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
                    # This solves the problem when a parent is not ITranslatable
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
        root = getToolByName(self.context, 'portal_url')
        return self.wrapDestination(root.url(), postpath=False)

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
            policies = registry.forInterface(IMultiLanguagePolicies)
            if policies.selector_lookup_translations_policy == 'closest':
                url = self.getClosestDestination()
            else:
                url = self.getDialogDestination()
            # No wrapping cause that's up to the policies
            # (they should already have done that)
        self.request.RESPONSE.redirect(url)


class not_translated_yet(BrowserView):
    """ View to inform user that the view requested is not translated yet,
        and shows the already translated related content.
    """
    __call__ = ViewPageTemplateFile('templates/not_translated_yet.pt')

    def already_translated(self):
        return ITranslationManager(self.context).get_translations().items()

    def has_any_translation(self):
        return len(ITranslationManager(self.context).get_translations().items()) > 1

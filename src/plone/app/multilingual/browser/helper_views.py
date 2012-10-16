from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter
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
# XXX: this should be moved here oif it doesn't break anything else
from plone.app.multilingual.browser.selector import NOT_TRANSLATED_YET_TEMPLATE
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from .utils import propagateQuery, addPostPath


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

        if self.lang is None:  # ../@@universal-link/translationgroup
            self.lang = name
        elif self.tg is None:  # ../@@universal-link/translationgroup/lang
            self.tg = name
        else:
            raise NotFound(self, name, request)

        return self

    def getDestination(self):
        # Look for the element
        ptool = getToolByName(self.context, 'portal_catalog')
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
        state = getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )
        dialog_view = NOT_TRANSLATED_YET_TEMPLATE
        # The dialog view shouldn't appear on the site root
        # because that is untraslatable by default.
        if ISiteRoot.providedBy(self.context):
            dialog_view = ''
        try:
            return state.canonical_object_url() + dialog_view
        # XXX: this copied over from LinguaPlone, not sure this is still needed
        except AttributeError:
            return self.context.absolute_url() + dialog_view

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
        context = aq_inner(self.context)
        checkPermission = getSecurityManager().checkPermission
        chain = self.getParentChain(context)
        for item in chain:
            if ISiteRoot.providedBy(item):
                # We do not care to get a permission error
                # if the whole of the portal cannot be viewed.
                # Having a permission issue on the root is fine;
                # not so much for everything else so that is checked there
                return item.absolute_url()
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
            if INavigationRoot.providedBy(item) or \
                    bool(checkPermission('View', translation)):
                return item.absolute_url()
        # Site root's the fallback
        root = getToolByName(self.context, 'portal_url')
        return root.url()

    def wrapDestination(self, url):
        """Fix the translation url appending the query
        and the eventual append path.
        """
        return propagateQuery(
            self.request,
            addPostPath(
                self.context,
                self.request,
                url
            )
        )

    def __call__(self):
        url = self.getDestination()
        if not url:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
            if settings.selector_lookup_translations_policy == 'closest':
                url = self.getClosestDestination()
            else:
                url = self.getDialogDestination()
        self.request.RESPONSE.redirect(self.wrapDestination(url))


class not_translated_yet(BrowserView):
    """ View to inform user that the view requested is not translated yet,
        and shows the already translated related content.
    """
    __call__ = ViewPageTemplateFile('templates/not_translated_yet.pt')

    def already_translated(self):
        return ITranslationManager(self.context).get_translations().items()

    def has_any_translation(self):
        return len(ITranslationManager(self.context).get_translations().items()) > 1

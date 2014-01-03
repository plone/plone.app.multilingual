from Acquisition import aq_inner
from App.special_dtml import DTMLFile
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from plone.app.content.browser.foldercontents import (
    FolderContentsView,
    FolderContentsTable,
)
from plone.app.multilingual.interfaces import (
    IMultiLanguageExtraOptionsSchema,
    SHARED_NAME,
)
from plone.i18n.locales.languages import _languagelist
from plone.i18n.locales.languages import _combinedlanguagelist
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component.hooks import getSite


NO_FILTER = ['Language', 'UID', 'id', 'getId']
_enabled = []


def language_filter(query):

    if query.get('Language') == 'all':
        del query['Language']
        return
    for key in NO_FILTER:    # any "nofilter" indexing prevent mangling
        if key in query:
            return
    site = getSite()
    languageTool = getToolByName(site, 'portal_languages', None)
    if languageTool is None:
        return
    query['Language'] = [languageTool.getPreferredLanguage(),
                         LANGUAGE_INDEPENDENT]
    old_path = query.get('path', None)

    # In case the search is called from the search form,
    # append the shared folder.
    if isinstance(old_path, str) and IPloneSiteRoot.providedBy(site):
        # We are going to check if is language root
        root_path = '/'.join(site.getPhysicalPath())

        old_path_url = old_path
        if old_path:
            lang_path = old_path_url.split('/')[-1]
            if lang_path in _languagelist or \
                    lang_path in _combinedlanguagelist:
                query['path'] = {
                    'query': [old_path_url, root_path + '/' + SHARED_NAME],
                }

    # In case is a depth path search
    if isinstance(old_path, dict) and 'query' in old_path and \
                                      IPloneSiteRoot.providedBy(site):
        old_path_url = old_path['query']
        # We are going to check if is language root
        root_path = '/'.join(site.getPhysicalPath())

        # Check if it is a language root folder to add the shared folder

        # fgr: when location query can be a list (for now maybe only in
        # oldstyle collections but I expect new style collections may get the
        # option of multiple paths as well in that case no SHARED_NAME needs
        # to be added, because the path criterions are defined either with
        # languagefolder or language neutral context already. may be this fix
        # is somewhat dirty ... -fgr

        if old_path and old_path['query'] and \
                isinstance(old_path['query'], str):
            lang_path = old_path['query'].split('/')[-1]
            if lang_path in _languagelist or \
                    lang_path in _combinedlanguagelist:
                old_path['query'] = [old_path_url,
                                     root_path + '/' + SHARED_NAME]


def AlreadyApplied(patch):
    if patch in _enabled:
        return True
    _enabled.append(patch)
    return False


def I18nAwareCatalog():
    # Patches the catalog tool to filter languages
    if AlreadyApplied('I18nAwareCatalog'):
        return

    def searchResults(self, REQUEST=None, **kw):
        if REQUEST is not None and kw.get('Language', '') != 'all':
            language_filter(REQUEST)
        else:
            language_filter(kw)
        return self.__pam_old_searchResults(REQUEST, **kw)

    CatalogTool.__pam_old_searchResults = CatalogTool.searchResults
    CatalogTool.searchResults = searchResults
    CatalogTool.__call__ = searchResults
    CatalogTool.manage_catalogView = DTMLFile('www/catalogView', globals())


def I18nAwareFolderContents():

    if AlreadyApplied('I18nAwareFolderContents'):
        return

    def contents_table(self):
        try:
            settings = getUtility(IRegistry).forInterface(
                IMultiLanguageExtraOptionsSchema)
        except KeyError:
            table = FolderContentsTable(aq_inner(self.context), self.request)
            return table.render()
        if settings.filter_content:
            table = FolderContentsTable(aq_inner(self.context), self.request)
        else:
            table = FolderContentsTable(aq_inner(self.context), self.request,
                                        contentFilter={'Language': 'all'})
        return table.render()

    FolderContentsView.__pam_old_contents_table = \
        FolderContentsView.contents_table
    FolderContentsView.contents_table = contents_table

try:
    from Products.LinguaPlone import patches
except ImportError:
    I18nAwareCatalog()

I18nAwareFolderContents()

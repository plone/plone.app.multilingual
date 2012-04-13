from zope.app.component.hooks import getSite
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.utils import getToolByName
from plone.multilingual.interfaces import ILanguage, ITranslatable
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.indexer import indexer

from plone.app.content.browser.foldercontents import (FolderContentsView,
                                                     FolderContentsTable)
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from Acquisition import aq_inner
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from App.special_dtml import DTMLFile


NO_FILTER = ['language', 'UID', 'id', 'getId']
_enabled = []

@indexer(ITranslatable)
def language(object, **kw):
    language = ILanguage(object).get_language()
    return language


def language_filter(query):
    site = getSite()
    languageTool = getToolByName(site, 'portal_languages', None)
    if languageTool is None:
        return
    if query.get('language') == 'all':
        del query['language']
        return
    for key in NO_FILTER:    # any "nofilter" indexing prevent mangling
        if key in query:
            return
    query['language'] = [languageTool.getPreferredLanguage(), LANGUAGE_INDEPENDENT]


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
        if REQUEST is not None and kw.get('language', '') != 'all':
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
            settings = getUtility(IRegistry).forInterface(IMultiLanguageExtraOptionsSchema)
        except KeyError:
            table = FolderContentsTable(aq_inner(self.context), self.request)
            return table.render()
        if settings.filter_content:
            table = FolderContentsTable(aq_inner(self.context), self.request)
        else:
            table = FolderContentsTable(aq_inner(self.context), self.request, contentFilter={'language':'all'})            
        return table.render()

    FolderContentsView.__pam_old_contents_table = FolderContentsView.contents_table    
    FolderContentsView.contents_table = contents_table



I18nAwareCatalog()
I18nAwareFolderContents()
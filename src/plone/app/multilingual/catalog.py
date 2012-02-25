from zope.app.component.hooks import getSite
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.utils import getToolByName
from plone.multilingual.interfaces import ILanguage, ITranslatable
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.indexer import indexer

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
    # site = getSite()
    # add_language = True
    # language_tool = getToolByName(site, 'portal_languages', None)
    # if language_tool is not None:

    #     for key in NO_FILTER:
    #         if key in query:
    #             add_language = False

    #     if query.get('Language') == 'all':
    #         del query['Language']

    #     if query.get('Language') == '':
    #         query['Language'] = LANGUAGE_INDEPENDENT

    #     if add_language:
    #         query['Language'] = [language_tool.getPreferredLanguage(), \
    #             LANGUAGE_INDEPENDENT]
    # return




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


I18nAwareCatalog()
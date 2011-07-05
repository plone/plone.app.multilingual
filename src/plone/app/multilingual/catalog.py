from zope.app.component.hooks import getSite
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFCore.utils import getToolByName
from plone.multilingual.interfaces import ILanguage, ITranslatable
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.indexer import indexer

NO_FILTER = ['language', 'UID', 'id', 'getId']


@indexer(ITranslatable)
def language(object, **kw):
    language = ILanguage(object).get_language()
    return language


def language_filter(query):
    site = getSite()
    add_language = True
    language_tool = getToolByName(site, 'portal_languages', None)
    if language_tool is not None:

        for key in NO_FILTER:
            if key in query:
                add_language = False

        if query.get('language') == 'all':
            del query['language']

        if query.get('language') == '':
            query['language'] = LANGUAGE_INDEPENDENT

        if add_language:
            query['language'] = [language_tool.getPreferredLanguage(), \
                LANGUAGE_INDEPENDENT]
    return


def searchResults(self, REQUEST=None, **kw):
    if REQUEST is not None and kw.get('language', None) is None:
        language_filter(REQUEST)
    else:
        language_filter(kw)
    return self.__pam_old_searchResults(REQUEST, **kw)


CatalogTool.__pam_old_searchResults = CatalogTool.searchResults
CatalogTool.searchResults = searchResults

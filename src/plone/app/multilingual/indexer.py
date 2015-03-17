# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslatable
from plone.indexer import indexer


@indexer(ITranslatable)
def itgIndexer(obj):
    return ITG(obj, None)


@indexer(ITranslatable)
def LanguageIndexer(object, **kw):
    language = ILanguage(object).get_language()
    return language

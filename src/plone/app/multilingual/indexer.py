# -*- coding: utf-8 -*-
from plone.indexer import indexer
from Products.CMFPlone.interfaces import ILanguage

from plone.app.multilingual.interfaces import ITG, ITranslatable


@indexer(ITranslatable)
def itgIndexer(obj):
    return ITG(obj, None)


@indexer(ITranslatable)
def LanguageIndexer(object, **kw):
    return ILanguage(object).get_language()

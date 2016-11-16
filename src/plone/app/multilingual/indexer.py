# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslatable
from plone.indexer import indexer


@indexer(ITranslatable)
def itgIndexer(obj):
    itg = ITG(obj, None)
    if not itg:
        raise AttributeError
    return itg


@indexer(ITranslatable)
def LanguageIndexer(object, **kw):
    language = ILanguage(object).get_language()
    return language

from plone.indexer import indexer
from plone.app.multilingual.interfaces import ITranslatable, ITG, ILanguage


@indexer(ITranslatable)
def itgIndexer(obj):
    return ITG(obj, None)


@indexer(ITranslatable)
def LanguageIndexer(object, **kw):
    language = ILanguage(object).get_language()
    return language

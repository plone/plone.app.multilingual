from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ITranslationCloner
from zope import interface


class Cloner(object):
    interface.implements(ITranslationCloner)

    def __init__(self, context):
        self.context = context

    def __call__(self, obj):
        ILanguageIndependentFieldsManager(self.context).copy_fields(obj)

# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ITranslationCloner
from zope.interface import implementer


@implementer(ITranslationCloner)
class Cloner(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, obj):
        ILanguageIndependentFieldsManager(self.context).copy_fields(obj)

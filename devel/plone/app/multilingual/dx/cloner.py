# -*- coding: utf-8 -*-
from zope import interface

from plone.app.multilingual.interfaces import ITranslationCloner
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager


class Cloner(object):

    interface.implements(ITranslationCloner)

    def __init__(self, context):
        self.context = context

    def __call__(self, obj):
        ILanguageIndependentFieldsManager(self.context).copy_fields(obj)

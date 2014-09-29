# -*- coding: utf-8 -*-
from plone.app.multilingual.interfaces import ITranslatable
from zope.interface import Interface

MULTILINGUAL_KEY = u'plone.app.multilingual.languageindependent'


class IDexterityTranslatable(ITranslatable):
    """ special marker for dexterity """


class ILanguageIndependentField(Interface):
    """ Marker interface for language independent fields """

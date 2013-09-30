# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4:
from plone.app.multilingual.interfaces import (
    ITranslatable,
)

from directives import languageindependent
from zope.interface import Interface

MULTILINGUAL_KEY = languageindependent.dotted_name()


class IDexterityTranslatable(ITranslatable):
    """ special marker for dexterity """


class ILanguageIndependentField(Interface):
    """ Marker interface for language independent fields """

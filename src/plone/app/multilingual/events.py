# -*- coding: utf-8 -*-
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import implementer


class IObjectWillBeTranslatedEvent(IObjectEvent):
    """Sent before an object is translated."""

    object = Attribute("The object to be translated.")
    language = Attribute("Target language.")


class IObjectTranslatedEvent(IObjectEvent):
    """Sent after an object was translated."""

    object = Attribute("The object to be translated.")
    target = Attribute("The translation target object.")
    language = Attribute("Target language.")


@implementer(IObjectWillBeTranslatedEvent)
class ObjectWillBeTranslatedEvent(object):
    """Sent before an object is translated."""

    def __init__(self, context, language):
        self.object = context
        self.language = language


@implementer(IObjectTranslatedEvent)
class ObjectTranslatedEvent(object):
    """Sent after an object was translated."""

    def __init__(self, context, target, language):
        self.object = context
        self.target = target
        self.language = language

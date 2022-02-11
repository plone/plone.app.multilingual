from zope.interface import Attribute
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent


class IObjectWillBeTranslatedEvent(IObjectEvent):
    """Sent before an object is translated."""

    object = Attribute("The object to be translated.")
    language = Attribute("Target language.")


class IObjectTranslatedEvent(IObjectEvent):
    """Sent after an object was translated."""

    object = Attribute("The object to be translated.")
    target = Attribute("The translation target object.")
    language = Attribute("Target language.")


class ITranslationRegisteredEvent(IObjectEvent):
    """Sent after a new translation was registered.

    This is meant to be notified on low-level manager level only.
    """

    object = Attribute("The base object.")
    target = Attribute("The translated object.")
    language = Attribute("The language of the translated obejct.")


class ITranslationUpdatedEvent(IObjectEvent):
    """Sent after an translation was moved to point to a different object

    This is meant to be notified on low-level manager level only.
    """

    object = Attribute("The base object.")
    old_object = Attribute("The old translation, now orphaned.")
    language = Attribute("The language of the objects.")


class ITranslationRemovedEvent(IObjectEvent):
    """Sent after an translation was removed.

    This is meant to be notified on low-level manager level only.
    """

    object = Attribute("The base object.")
    old_object = Attribute("The old translation, now orphaned.")
    language = Attribute("The language of the objects.")


@implementer(IObjectWillBeTranslatedEvent)
class ObjectWillBeTranslatedEvent:
    """Sent before an object is translated."""

    def __init__(self, context, language):
        self.object = context
        self.language = language


@implementer(IObjectTranslatedEvent)
class ObjectTranslatedEvent:
    """Sent after an object was translated."""

    def __init__(self, context, target, language):
        self.object = context
        self.target = target
        self.language = language


@implementer(ITranslationRegisteredEvent)
class TranslationRegisteredEvent:
    """Sent after a new translation was registered."""

    def __init__(self, context, target, language):
        self.object = context
        self.target = target
        self.language = language


@implementer(ITranslationUpdatedEvent)
class TranslationUpdatedEvent:
    """Sent after an translation was moved to point to a different object"""

    def __init__(self, context, old_object, language):
        self.object = context
        self.old_object = old_object
        self.language = language


@implementer(ITranslationRemovedEvent)
class TranslationRemovedEvent:
    """Sent after an translation was moved to point to a different object"""

    def __init__(self, context, old_object, language):
        self.object = context
        self.old_object = old_object
        self.language = language

from plone.app.multilingual.interfaces import ITranslatable
from zope.interface import Interface


MULTILINGUAL_KEY = "plone.app.multilingual.languageindependent"


class IDexterityTranslatable(ITranslatable):
    """special marker for dexterity"""


class ILanguageIndependentField(Interface):
    """Marker interface for language independent fields"""


class IMultilingualAddForm(Interface):
    """Marker Interface for multilingual add forms

    This marker is intended to be provided by the main multilingual add form
    ans to be provided by the groups (aka fieldset) forms
    (plone.z3cform.fieldsets.group.Group). This is neccessary in order to
    make the special template renderer for ILanguageIndependentField fields
    work in fieldset tabs too.
    """

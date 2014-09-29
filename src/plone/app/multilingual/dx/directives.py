# -*- coding: utf-8 -*-
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.dx.interfaces import MULTILINGUAL_KEY
from plone.supermodel.directives import CheckerPlugin
from plone.supermodel.directives import MetadataListDirective
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface.interfaces import IInterface


LANGUAGE_INDEPENDENT_KEY = MULTILINGUAL_KEY


class languageindependent(MetadataListDirective):
    """Directive used to mark one or more fields as 'languageindependent'
    """

    key = LANGUAGE_INDEPENDENT_KEY
    value = 'true'

    def factory(self, *args):
        """The languageindependent directive accepts as arguments one or more
        fieldnames (string) of fields which should be searchable.
        """
        if not args:
            raise TypeError('The languageindependent directive expects at '
                            'least one argument.')

        form_interface = Interface
        if IInterface.providedBy(args[0]):
            form_interface = args[0]
            args = args[1:]
        return [(form_interface, field, self.value) for field in args]


class LanguageIndependentFieldsPlugin(CheckerPlugin):

    key = LANGUAGE_INDEPENDENT_KEY

    def __call__(self):
        schema = self.schema
        for fieldName in self.check():
            alsoProvides(schema[fieldName], ILanguageIndependentField)

    def fieldNames(self):
        if self.value is None:
            return
        for taggedValue in self.value:
            yield taggedValue[1]


__all__ = ('languageindependent', 'LanguageIndependentFieldsPlugin')

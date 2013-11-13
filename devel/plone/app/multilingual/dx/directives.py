from plone.supermodel.directives import MetadataListDirective
from zope.interface import Interface
from zope.interface.interfaces import IInterface


LANGUAGE_INDEPENDENT_KEY = u'plone.app.multilingual.languageindependent'


# Directives

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


__all__ = ('languageindependent',)

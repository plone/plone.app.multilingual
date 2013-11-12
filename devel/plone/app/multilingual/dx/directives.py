from plone.supermodel.directives import MetadataListDirective


LANGUAGE_INDEPENDENT_KEY = u'plone.app.multilingual.languageindependent'


# Directives

class languageindependent(MetadataListDirective):
    """Directive used to mark one or more fields as 'languageindependent'
    """

    key = LANGUAGE_INDEPENDENT_KEY
    value = 'true'


__all__ = ('languageindependent',)

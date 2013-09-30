import martian

from zope.interface.interface import TAGGED_DATA

TEMP_KEY = '__form_directive_values__'

# Storages

class LanguageIndependentStorage(object):
    """Stores the primary() directive value in a schema tagged value.
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {})
        tags.setdefault(directive.dotted_name(), []).extend(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(directive.dotted_name(), default)

    def setattr(self, context, directive, value):
        context.setTaggedValue(directive.dotted_name(), value)

# Directives

class languageindependent(martian.Directive):
    """Directive used to mark one or more fields as 'languageindependent'
    """

    scope = martian.CLASS
    store = LanguageIndependentStorage()

    def factory(self, *args):
        return args

__all__ = ('languageindependent',)

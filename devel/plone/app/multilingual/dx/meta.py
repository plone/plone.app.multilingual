import martian
from martian.error import GrokImportError

from zope.interface import alsoProvides

from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.dx.directives import languageindependent
from plone.directives.form import Schema


class MultilingualGrokker(martian.InstanceGrokker):
    martian.component(Schema.__class__)
    martian.directive(languageindependent)

    def execute(self, interface, config, **kw):

        languageindependentfields = interface.queryTaggedValue(
            languageindependent.dotted_name(), [])

        for fieldName in languageindependentfields:
            try:
                alsoProvides(interface[fieldName], ILanguageIndependentField)
            except KeyError:
                errmsg = "Field %s set in languageindependent() directive " + \
                         "on %s not found"

                raise GrokImportError(errmsg % (fieldName, interface,))
        return True

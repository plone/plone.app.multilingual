# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from interfaces import ILanguageIndependentField
from plone.app.multilingual.manager import TranslationManager
from z3c.form.interfaces import IValue
from z3c.form.interfaces import NO_VALUE
from zope.interface import implementer


def isLanguageIndependent(field):
    if field.interface is None:
        return False

    if ILanguageIndependentField.providedBy(field):
        return True
    else:
        return False


@implementer(IValue)
class ValueBase(object):

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.field = field
        self.form = form
        self.widget = widget

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')


class AddingLanguageIndependentValue(ValueBase):
    # XXX Deprecated ???
    def getTranslationUuid(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if 'tg' in session.keys():
            return session['tg']

    def get(self):
        print "get AddingLanguageIndependentValue", self.field
        uuid = self.getTranslationUuid()

        if isLanguageIndependent(self.field) and uuid:
            manager = TranslationManager(uuid)
            result = manager.get_translations()

            if len(result) >= 1:

                orig_lang = result.keys()[0]
                obj = result[orig_lang]
                name = self.field.__name__
                print "-> field name ", name
                # XXX
                # this does not work with behaviors, if other than direct
                # attribute storage was used.
                try:
                    value = getattr(aq_base(obj), name)
                except AttributeError:
                    print "-> AttributeError: ", name
                    pass
                else:
                    print "-> attribute value ", value
                    return value

        if self.field.default is None:
            print "-> no value"
            return NO_VALUE

        print "-> default"
        return self.field.default

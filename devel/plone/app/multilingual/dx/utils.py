# -*- coding: utf-8 -*-
from zope import interface
from zope.component import getUtility

from plone.dexterity import utils
from plone.dexterity.interfaces import IDexterityFTI

from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager

from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from z3c.relationfield.interfaces import IRelationValue

from plone.app.multilingual.interfaces import ILanguage
from zope.component import queryAdapter
from plone.app.multilingual.interfaces import ITranslationManager

from zope.app.intid.interfaces import IIntIds
from zope import component
from z3c.relationfield import RelationValue

_marker = object()


class LanguageIndependentFieldsManager(object):
    interface.implements(ILanguageIndependentFieldsManager)

    def __init__(self, context):
        self.context = context

    def has_independent_fields(self):
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schemas = []
        schemas.append(fti.lookupSchema())

        for behavior_schema in \
                utils.getAdditionalSchemata(self.context,
                                            self.context.portal_type):
            if behavior_schema is not None:
                schemas.append(behavior_schema)

        for schema in schemas:
            for field_name in schema:
                if ILanguageIndependentField.providedBy(schema[field_name]):
                    return True
        return False

    def copy_fields(self, translation):

        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        schemas = []
        schemas.append(fti.lookupSchema())

        for behavior_schema in \
                utils.getAdditionalSchemata(self.context,
                                            self.context.portal_type):
            if behavior_schema is not None:
                schemas.append(behavior_schema)

        doomed = False
        for schema in schemas:
            for field_name in schema:
                if ILanguageIndependentField.providedBy(schema[field_name]):
                    doomed = True

                    value = getattr(schema(self.context), field_name, _marker)
                    if IRelationValue.providedBy(value):
                        obj = value.to_object
                        adapter = queryAdapter(translation, ILanguage)
                        trans_obj = ITranslationManager(obj)\
                            .get_translation(adapter.get_language())
                        if trans_obj:
                            intids = component.getUtility(IIntIds)
                            value = RelationValue(intids.getId(trans_obj))
                    if not (value == _marker):
                        # We check if not (value == _marker) because
                        # z3c.relationfield has an __eq__
                        setattr(schema(translation), field_name, value)

        # If at least one field has been copied over to the translation
        # we need to inform subscriber to trigger an ObjectModifiedEvent
        # on that translation.
        return doomed

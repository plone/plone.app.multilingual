# -*- coding: utf-8 -*-
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ITranslationCloner
from plone.app.multilingual.interfaces import ITranslationManager
from plone.dexterity.utils import iterSchemata
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.interfaces import IRelationValue
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface import implementer
import pkg_resources
try:
    # pkg_resources.get_distribution('zope.initd')
    from zope.intid.interfaces import IIntIds
except pkg_resources.DistributionNotFound:
    from zope.app.intid.interfaces import IIntIds

_marker = object()


@implementer(ITranslationCloner)
class Cloner(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, obj):
        ILanguageIndependentFieldsManager(self.context).copy_fields(obj)


@implementer(ILanguageIndependentFieldsManager)
class LanguageIndependentFieldsManager(object):

    def __init__(self, context):
        self.context = context

    def has_independent_fields(self):
        for schema in iterSchemata(self.context):
            for field_name in schema:
                if ILanguageIndependentField.providedBy(schema[field_name]):
                    return True
        return False

    def copy_relation(self, relation_value, target_language):
        obj = relation_value.to_object
        intids = getUtility(IIntIds)
        translation = ITranslationManager(obj).get_translation(target_language)
        if translation:
            return RelationValue(intids.getId(translation))
        else:
            return RelationValue(intids.getId(obj))

    def copy_fields(self, translation):
        doomed = False

        target_language = queryAdapter(translation, ILanguage).get_language()

        def relation_copier(rel, lang=target_language, fun=self.copy_relation):
            return fun(rel, lang)

        for schema in iterSchemata(self.context):
            for field_name in schema:
                if ILanguageIndependentField.providedBy(schema[field_name]):
                    value = getattr(schema(self.context), field_name, _marker)

                    if value == _marker:
                        continue
                    elif IRelationValue.providedBy(value):
                        value = self.copy_relation(value, target_language)
                    elif IRelationList.providedBy(schema[field_name]):
                        value = map(relation_copier, value or [])

                    doomed = True
                    setattr(schema(translation), field_name, value)

        # If at least one field has been copied over to the translation
        # we need to inform subscriber to trigger an ObjectModifiedEvent
        # on that translation.
        return doomed

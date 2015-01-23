# -*- coding: utf-8 -*-
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ITranslationManager
from plone.dexterity.utils import iterSchemata
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.validator import StrictSimpleFieldValidator
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.interfaces import IRelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface import implementer
from zope.pagetemplate.interfaces import IPageTemplate

_marker = object()


class LanguageIndependentFieldValidator(StrictSimpleFieldValidator):
    """Override validator so we can ignore language independent fields,
       these will be automatically filled later on by subscriber.createdEvent
    """
    def validate(self, value, force=False):
        # always pass
        pass


class LanguageIndependentFieldInputTemplate(object):
    """Override input template for language independent fields with
       display widget, because values will be automatically filled
       by later on by subscriber.createdEvent.
    """
    def __init__(self, context, request, view, field, widget):
        self.context = context
        self.request = request
        self.view = view
        self.field = field
        self.widget = widget

    def __call__(self, widget):
        template = getMultiAdapter(
            (self.context, self.request, self.view, self.field, self.widget,),
            IPageTemplate, name=DISPLAY_MODE)
        return template(widget)


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
        relation_copier =\
            lambda r, l=target_language, f=self.copy_relation: f(r, l)

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

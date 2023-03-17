from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ITranslationCloner
from plone.app.multilingual.interfaces import ITranslationManager
from plone.base.interfaces import ILanguage
from plone.dexterity.utils import iterSchemata
from plone.base.utils import safe_text
from z3c.relationfield import RelationValue
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.interfaces import IRelationValue
from zope.component import getUtility
from zope.component import queryAdapter
from zope.interface import implementer
from zope.intid.interfaces import IIntIds


_marker = object()


@implementer(ITranslationCloner)
class Cloner:
    def __init__(self, context):
        self.context = context

    def __call__(self, obj):
        ILanguageIndependentFieldsManager(self.context).copy_fields(obj)


@implementer(ILanguageIndependentFieldsManager)
class LanguageIndependentFieldsManager:
    def __init__(self, context):
        self.context = context

    def has_independent_fields(self):
        for schema in iterSchemata(self.context):
            for field_name in schema:
                if ILanguageIndependentField.providedBy(schema[field_name]):
                    return True
        return False

    def copy_relation(self, relation_value, target_language):
        if not relation_value or relation_value.isBroken():
            return

        obj = relation_value.to_object
        intids = getUtility(IIntIds)
        translation = ITranslationManager(obj).get_translation(target_language)
        if translation:
            return RelationValue(intids.getId(translation))
        return RelationValue(intids.getId(obj))

    def copy_fields(self, translation):
        changed = False

        target_language = queryAdapter(translation, ILanguage).get_language()

        for schema in iterSchemata(self.context):
            context_adapter = None
            translation_adapter = None
            for field_name in schema:
                if ILanguageIndependentField.providedBy(schema[field_name]):
                    if context_adapter is None:
                        context_adapter = schema(self.context)
                    value = getattr(context_adapter, field_name, _marker)
                    field_changed = None
                    if value == _marker:
                        continue
                    elif IRelationValue.providedBy(value):
                        field_changed = True
                        value = self.copy_relation(value, target_language)
                    elif IRelationList.providedBy(schema[field_name]):
                        field_changed = True
                        if not value:
                            value = []
                        else:
                            new_value = []
                            for relation in value:
                                copied_relation = self.copy_relation(
                                    relation, target_language
                                )
                                if copied_relation:
                                    new_value.append(copied_relation)
                            value = new_value

                    if translation_adapter is None:
                        translation_adapter = schema(translation)

                    # We only want to store a new value if it has changed.
                    # In general we can compare equality of the new value to the one on the translation.
                    # But RelationValue.__eq__ is broken if the relation doesn't have a from_object,
                    # so for now we force field_changed to True for relations above.
                    if field_changed is None:
                        translation_value = getattr(
                            translation_adapter, field_name, _marker
                        )
                        field_changed = value != translation_value
                    if field_changed:
                        changed = True
                        setattr(translation_adapter, field_name, safe_text(value))

        # If at least one field has been copied over to the translation
        # we need to inform subscriber to trigger an ObjectModifiedEvent
        # on that translation.
        return changed

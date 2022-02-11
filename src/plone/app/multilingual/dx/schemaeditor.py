from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.schemaeditor.interfaces import IFieldEditorExtender
from plone.schemaeditor.interfaces import ISchemaContext
from zope import schema
from zope.component import adapter
from zope.component import provideAdapter
from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides
from zope.schema import interfaces
from zope.schema.interfaces import IField


PMF = MessageFactory("plone.app.multilingual")


class IFieldLanguageIndependent(Interface):
    languageindependent = schema.Bool(
        title=PMF("Language independent field"),
        description=PMF(
            "The field is going to be copied on all "
            "translations when you edit the content"
        ),
        required=False,
    )


@implementer(IFieldLanguageIndependent)
@adapter(interfaces.IField)
class FieldLanguageIndependentAdapter:
    def __init__(self, field):
        self.field = field

    def _read_languageindependent(self):
        return ILanguageIndependentField.providedBy(self.field)

    def _write_languageindependent(self, value):
        if value:
            alsoProvides(self.field, ILanguageIndependentField)
        else:
            noLongerProvides(self.field, ILanguageIndependentField)

    languageindependent = property(
        _read_languageindependent, _write_languageindependent
    )


# IFieldLanguageIndependent could be registered directly as a named adapter
# providing IFieldEditorExtender for ISchemaContext and IField. But we can
# also register a separate callable which returns the schema only if
# additional conditions pass:
@adapter(ISchemaContext, IField)
def get_li_schema(schema_context, field):
    fti = getattr(schema_context, "fti", None)
    lang_behavior = {
        "plone.app.multilingual.dx.interfaces.IDexterityTranslatable",
        "plone.translatable",
    }
    fti_behaviors = set(getattr(fti, "behaviors", []))
    if lang_behavior.intersection(fti_behaviors):
        return IFieldLanguageIndependent


# Register the callable which makes the field edit form know about the
# new schema:
provideAdapter(
    get_li_schema,
    provides=IFieldEditorExtender,
    name="plone.schemaeditor.languageindependent",
)


# And the adapter for getting/setting the value.
provideAdapter(FieldLanguageIndependentAdapter, provides=IFieldLanguageIndependent)

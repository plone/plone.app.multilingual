from .interfaces import ILanguageIndependentField
from Acquisition import aq_base
from plone.app.multilingual.manager import TranslationManager
from Products.CMFCore.utils import getToolByName
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IValue
from z3c.form.interfaces import NO_VALUE
from z3c.form.validator import StrictSimpleFieldValidator
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.pagetemplate.interfaces import IPageTemplate


def isLanguageIndependent(field):
    return field.interface is not None and ILanguageIndependentField.providedBy(field)


class LanguageIndependentFieldValidator(StrictSimpleFieldValidator):
    """Override validator so we can ignore language independent fields,
    these will be automatically filled later on by subscriber.createdEvent
    """

    def validate(self, value, force=False):
        # always pass
        pass


class LanguageIndependentFieldInputTemplate:
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
            (
                self.context,
                self.request,
                self.view,
                self.field,
                self.widget,
            ),
            IPageTemplate,
            name=DISPLAY_MODE,
        )
        return template(widget)


@implementer(IValue)
class ValueBase:
    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.field = field
        self.form = form
        self.widget = widget

    @property
    def catalog(self):
        return getToolByName(self.context, "portal_catalog")


class AddingLanguageIndependentValue(ValueBase):
    # XXX Deprecated ???
    def getTranslationUuid(self):
        translation_info = getattr(self.request, "translation_info", {})
        if "tg" in translation_info.keys():
            return translation_info["tg"]

    def get(self):
        uuid = self.getTranslationUuid()

        if isLanguageIndependent(self.field) and uuid:
            manager = TranslationManager(uuid)
            result = manager.get_translations()

            if len(result) >= 1:

                orig_lang = list(result.keys())[0]
                obj = result[orig_lang]
                name = self.field.__name__
                # XXX
                # this does not work with behaviors, if other than direct
                # attribute storage was used.
                try:
                    value = getattr(aq_base(obj), name)
                except AttributeError:
                    pass
                else:
                    return value

        if self.field.default is None:
            return NO_VALUE

        return self.field.default

from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.validator import StrictSimpleFieldValidator
from zope.component import getMultiAdapter
from zope.pagetemplate.interfaces import IPageTemplate


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

from z3c.form.validator import StrictSimpleFieldValidator


class LanguageIndependentFieldValidator(StrictSimpleFieldValidator):
    """Override validator so we can ignore language independent fields,
       these will be automatically filled later on by subscriber.createdEvent
    """

    def validate(self, value, force=False):
        # always pass
        pass

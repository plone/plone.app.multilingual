from plone.dexterity.browser.view import DefaultView
from z3c.form.interfaces import IEditForm
from zope.interface import implementer


@implementer(IEditForm)
class DexterityBabelView(DefaultView):
    # By claiming that we implement IEditForm, we also get the TaggedValues of
    # that interface. This is important, because this view is displayed side
    # by side with the edit from, and the DefaultView itself has some tagged
    # values to hide fields.
    pass

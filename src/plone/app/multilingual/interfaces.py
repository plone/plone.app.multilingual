from zope.interface import Interface
from zope import schema
from plone.app.multilingual import _


class IPloneAppMultilingualInstalled(Interface):
    """ layer """


class IMultilinguaSettings(Interface):

    show_selector_always = schema.Bool(
        title=_(u"show selector always"),
    )

from zope.interface import Interface
from zope import schema
from plone.app.multilingual import _


class IPloneAppMultilingualInstalled(Interface):
    """ layer """


class IMultilinguaSettings(Interface):

    show_selector_always = schema.Bool(
        title=_(u"show selector always"),
    )


class IMultilinguaRootFolder(Interface):

    default_layout_languages = schema.Dict(
        min_length=0, max_length=10,
        key_type=schema.ASCII(title=u"Key"),
        value_type=schema.TextLine(title=u"Value"),
        title=_(u"Select diferent urls for each differnt language"),
    )

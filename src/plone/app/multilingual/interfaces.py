from zope.interface import Interface
from zope import schema
from plone.app.multilingual import _
from plone.registry import field


class IPloneAppMultilingualInstalled(Interface):
    """ layer """


class IMultilinguaSettings(Interface):
    """ Selector at plone.registry
    """

    show_selector_always = field.Bool(
        title=_(u"show selector always"),
    )

    default_layout_languages = field.Dict(
        min_length=0, max_length=10,
        key_type=field.ASCII(title=u"Key"),
        value_type=field.TextLine(title=u"Value"),
        title=_(u"Select diferent urls for each differnt language"),
    )



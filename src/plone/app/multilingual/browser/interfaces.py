# -*- coding: utf-8 -*-
from plone.app.multilingual import _
from plone.app.multilingual.browser.vocabularies import deletable_languages
from plone.app.multilingual.browser.vocabularies import untranslated_languages
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from zope import interface
from zope import schema
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IBrowserSubMenuItem


class IMultilingualLayer(interface.Interface):
    """ browser layer """


class ITranslateSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the translate menu.
    """


class ITranslateMenu(IBrowserMenu):
    """The translate menu.
    """


class ICreateTranslation(interface.Interface):

    language = schema.Choice(
        title=_(u"title_language", default=u"Language"),
        source=untranslated_languages,
    )


class IUpdateLanguage(interface.Interface):

    language = schema.Choice(
        title=_(u"title_available_languages", default=u"Available languages"),
        description=_(
            u"description_update_language",
            default=u"Untranslated languages from the current content"
        ),
        source=untranslated_languages,
        required=True,
    )


class IAddTranslation(model.Schema):

    language = schema.Choice(
        title=_(u"title_language", default=u"Language"),
        source=untranslated_languages,
        required=True,
    )
    content = RelationChoice(
        title=_(u"content"),
        vocabulary="plone.app.vocabularies.Catalog",
        required=True,
    )


class IRemoveTranslation(model.Schema):

    languages = schema.List(
        title=_(u"title_languages"),
        value_type=schema.Choice(
            title=_(u"title_language", default=u"Language"),
            source=deletable_languages,
        ),
        required=True,
    )
    directives.widget(languages='z3c.form.browser.select.SelectFieldWidget')

interface.alsoProvides(IUpdateLanguage, IFormFieldProvider)
interface.alsoProvides(IAddTranslation, IFormFieldProvider)
interface.alsoProvides(IRemoveTranslation, IFormFieldProvider)

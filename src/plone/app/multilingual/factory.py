# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import ITranslationCloner
from plone.app.multilingual.interfaces import ITranslationFactory
from plone.app.multilingual.interfaces import ITranslationIdChooser
from plone.app.multilingual.interfaces import ITranslationLocator
from plone.app.multilingual.interfaces import ITranslationManager
from zope.interface import implementer


@implementer(ILanguageIndependentFieldsManager)
class DefaultLanguageIndependentFieldsManager(object):
    """ Default language independent fields manager.
    """

    def __init__(self, context):
        self.context = context

    def get_field_names(self):
        return []

    def copy_fields(self, translation):
        return


@implementer(ITranslationLocator)
class DefaultTranslationLocator(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, language):
        """
        Look for the closest translated folder or siteroot
        """
        parent = aq_parent(self.context)
        translated_parent = parent
        found = False
        while not (IPloneSiteRoot.providedBy(parent)
                   and not ILanguageRootFolder.providedBy(parent))\
                and not found:
            parent_translation = ITranslationManager(parent)
            if parent_translation.has_translation(language):
                translated_parent =\
                    parent_translation.get_translation(language)
                found = True
            parent = aq_parent(parent)
        return translated_parent


@implementer(ITranslationCloner)
class DefaultTranslationCloner(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, obj):
        return


@implementer(ITranslationIdChooser)
class DefaultTranslationIdChooser(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, parent, language):
        content_id = self.context.getId()
        splitted = content_id.split('-')
        # ugly heuristic (searching for something like 'de', 'en' etc.)
        if len(splitted) > 1 and len(splitted[-1]) == 2:
            content_id = '-'.join(splitted[:-1])
        while content_id in parent.objectIds():
            content_id = "%s-%s" % (content_id, language)
        return content_id


@implementer(ITranslationFactory)
class DefaultTranslationFactory(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, language):
        content_type = self.context.portal_type
        # parent for translation
        locator = ITranslationLocator(self.context)
        parent = locator(language)
        # id for translation
        name_chooser = ITranslationIdChooser(self.context)
        content_id = name_chooser(parent, language)
        # creating the translation
        new_id = parent.invokeFactory(
            type_name=content_type,
            id=content_id,
            language=language)
        new_content = getattr(parent, new_id)
        # clone language-independent content
        cloner = ITranslationCloner(self.context)
        cloner(new_content)
        return new_content

from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from zope import interface


# Patch for hiding 'language' field from the edit form
ICategorization['language'].readonly = True


class Language(object):

    def __init__(self, context):
        self.context = context

    interface.implements(ILanguage)

    def get_language(self):
        language = self.context.language
        if not language:
            language = LANGUAGE_INDEPENDENT
        return language

    def set_language(self, language):
        self.context.language = language
        self.context.reindexObject(idxs=['Language'])

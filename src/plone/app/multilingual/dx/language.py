# from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from Products.CMFPlone.interfaces import ILanguage
from zope.interface import implementer


# Patch for hiding 'language' field from the edit form
# ICategorization['language'].readonly = True


@implementer(ILanguage)
class Language:
    def __init__(self, context):
        self.context = context

    def get_language(self):
        return self.context.language or LANGUAGE_INDEPENDENT

    def set_language(self, language):
        self.context.language = language
        self.context.reindexObject(idxs=["Language"])

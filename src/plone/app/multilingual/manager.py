from plone.app.multilingual.events import ObjectTranslatedEvent
from plone.app.multilingual.events import ObjectWillBeTranslatedEvent
from plone.app.multilingual.events import TranslationRegisteredEvent
from plone.app.multilingual.events import TranslationRemovedEvent
from plone.app.multilingual.events import TranslationUpdatedEvent
from plone.app.multilingual.interfaces import IMutableTG
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslationFactory
from plone.app.multilingual.interfaces import ITranslationLocator
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import NOTG
from plone.app.multilingual.itg import addAttributeTG
from plone.app.uuid.utils import uuidToObject
from plone.protect.interfaces import IDisableCSRFProtection
from plone.uuid.handlers import addAttributeUUID
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguage
from zope.component.hooks import getSite
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import implementer


@implementer(ITranslationManager)
class TranslationManager:
    def __init__(self, context):
        self.context = context
        if isinstance(context, str):
            self.tg = context
        else:
            self.tg = self.get_tg(context)
        site = getSite()
        self.pcatalog = getToolByName(site, "portal_catalog", None)

    def get_id(self, context):
        """If an object is created via portal factory we don't get a id, we
        have to wait till the object is really created.
        TODO: a better check if we are in the portal factory!
        """
        try:
            context_id = IUUID(context)
        # We must ensure that this case can't happen, any object translatable
        # will have an UUID (in any case we can be at the portal factory!)
        except KeyError:
            alsoProvides(getRequest(), IDisableCSRFProtection)
            addAttributeUUID(context, None)
            context.reindexObject(idxs=["UID"])
            context_id = IUUID(context)
        return context_id

    def get_tg(self, context):
        """If an object is created via portal factory we don't get a id, we
        have to wait till the object is really created.
        TODO: a better check if we are in the portal factory!
        """
        try:
            context_id = ITG(context)
        # We must ensure that this case can't happen, any object translatable
        # will have an TG (in any case we can be at the portal factory!)
        except TypeError:
            alsoProvides(getRequest(), IDisableCSRFProtection)
            addAttributeTG(context, None)
            context.reindexObject(idxs=["TranslationGroup"])
            context_id = ITG(context)
        return context_id

    def query_canonical(self):
        return self.tg

    def register_translation(self, language, content):
        """register a translation for an existing content"""
        if not language and language != "":
            raise KeyError("There is no target language")

        if type(content) == str:
            content = uuidToObject(content)

        # Check if exists and is not myself
        brains = self.pcatalog.unrestrictedSearchResults(
            TranslationGroup=self.tg, Language=language
        )
        if len(brains) > 0 and brains[0].UID != self.get_id(content):
            raise KeyError("Translation already exists")

        # register the new translation in the canonical
        IMutableTG(content).set(self.tg)
        content.reindexObject(idxs=("Language", "TranslationGroup"))
        notify(TranslationRegisteredEvent(self.context, content, language))

    def update(self):
        """Update the adapted item.

        If unregistered, register a Translation-Grouup (TG) for it and exit.

        Check that there aren't two translations on the same language
        This is to be used for changing the contexts language.
        If there is already an item in the same language,
        Remove the other items TG information and make the current adapted
        context the active language for the current TG.

        """
        language = ILanguage(self.context).get_language()
        brains = self.pcatalog.unrestrictedSearchResults(
            TranslationGroup=self.tg,
            Language=language,
        )
        if len(brains) == 0:
            # There is no translation within current TG for this language.
            self.register_translation(language, self.context)
            return
        # In case the language is already within the translated languages we are
        # going to orphan the old translation.
        brain = brains[0]
        content_id = self.get_id(self.context)
        if brain.UID == content_id:
            return

        # It is a different object -> remove the old one
        # We get the old uuid
        old_object = brain.getObject()
        IMutableTG(old_object).set(NOTG)
        old_object.reindexObject(idxs=("TranslationGroup",))
        notify(TranslationUpdatedEvent(self.context, old_object, language))

    def add_translation(self, language):
        """see interfaces"""
        if not language and language != "":
            raise KeyError("There is no target language")
        # event
        notify(ObjectWillBeTranslatedEvent(self.context, language))
        # create the translated object
        translation_factory = ITranslationFactory(self.context)
        translated_object = translation_factory(language)
        ILanguage(translated_object).set_language(language)
        # reindex the translated object
        translated_object.reindexObject()
        # register the new translation
        self.register_translation(language, translated_object)
        # event
        notify(ObjectTranslatedEvent(self.context, translated_object, language))

    def add_translation_delegated(self, language):
        """
        Creation is delegated to factory/++add++
        Lets return the url where we are going to create the translation
        """
        if not language and language != "":
            raise KeyError("There is no target language")
        # event
        notify(ObjectWillBeTranslatedEvent(self.context, language))
        # localize where we need to store the new object
        locator = ITranslationLocator(self.context)
        parent = locator(language)
        return parent

    def remove_translation(self, language):
        """see interfaces"""
        translation = self.get_translation(language)
        IMutableTG(translation).set(NOTG)
        translation.reindexObject(idxs=("TranslationGroup",))
        notify(TranslationRemovedEvent(self.context, translation, language))

    def get_translation(self, language):
        """see interfaces"""
        brains = self.pcatalog.unrestrictedSearchResults(
            TranslationGroup=self.tg, Language=language
        )
        if len(brains) != 1:
            return None
        return brains[0].getObject()

    def get_restricted_translation(self, language):
        """see interfaces"""
        brains = self.pcatalog.searchResults(
            TranslationGroup=self.tg, Language=language
        )
        if len(brains) != 1:
            return None
        return brains[0].getObject()

    def get_translations(self):
        """see interfaces"""
        translations = {}
        brains = self.pcatalog.unrestrictedSearchResults(
            TranslationGroup=self.tg,
        )
        for brain in brains:
            translations[brain.Language] = brain.getObject()
        return translations

    def get_restricted_translations(self):
        """see interfaces"""
        translations = {}
        brains = self.pcatalog.searchResults(TranslationGroup=self.tg)
        for brain in brains:
            translations[brain.Language] = brain.getObject()
        return translations

    def get_translated_languages(self):
        """see interfaces"""
        languages = []
        brains = self.pcatalog.unrestrictedSearchResults(TranslationGroup=self.tg)
        for brain in brains:
            if brain.Language not in languages:
                languages.append(brain.Language)
        return languages

    def has_translation(self, language):
        """see interfaces"""
        return language in self.get_translated_languages()

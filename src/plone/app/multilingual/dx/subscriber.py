# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser
from Products.CMFCore.utils import getToolByName
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITranslationManager
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryAdapter
from zope.event import notify
from zope.globalrequest import getRequest
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class LanguageIndependentModifier(object):
    """Class to handle dexterity editions."""

    def __call__(self, content, event):
        """Called by the event system."""
        request = getattr(event.object, 'REQUEST', getRequest())
        translation_info = getattr(request, 'translation_info', {})

        if 'tg' in translation_info.keys():
            # In case it's a on the fly translation avoid
            return

        if IDexterityTranslatable.providedBy(content):
            self.canonical = ITranslationManager(content).query_canonical()

            if event.descriptions \
               and len(event.descriptions) > 1 \
               and event.descriptions[1] == self.canonical:
                return

            if IObjectModifiedEvent.providedBy(event):
                self.handle_modified(content)

    def bypass_security_checks(self):
        registry = getUtility(IRegistry)

        # BBB for lrf-branch
        field = registry.records.get(
            IMultiLanguageExtraOptionsSchema.__identifier__ +
            '.bypass_languageindependent_field_permission_check')

        return field and field.value or False

    def handle_modified(self, content):

        fieldmanager = ILanguageIndependentFieldsManager(content)
        if not fieldmanager.has_independent_fields():
            return

        sm = getSecurityManager()
        try:
            # Do we have permission to sync language independent fields?
            if self.bypass_security_checks():
                # Clone the current user and assign a new editor role to
                # allow edition of all translated objects even if the
                # current user whould not have permission to do that.
                tmp_user = UnrestrictedUser(
                    sm.getUser().getId(), '', ['Editor', ], '')

                # Wrap the user in the acquisition context of the portal
                # and finally switch the user to our new editor
                acl_users = getToolByName(content, 'acl_users')
                tmp_user = tmp_user.__of__(acl_users)
                newSecurityManager(None, tmp_user)

            # Copy over all language independent fields
            transmanager = ITranslationManager(content)
            for translation in self.get_all_translations(content):
                trans_obj = transmanager.get_translation(translation)
                if fieldmanager.copy_fields(trans_obj):
                    self.reindex_translation(trans_obj)
        finally:
            # Restore the old security manager
            setSecurityManager(sm)

    def reindex_translation(self, translation):
        """Once the modification is done, reindex translation"""
        translation.reindexObject()

        fti = getUtility(IDexterityFTI, name=translation.portal_type)
        schema = fti.lookupSchema()
        descriptions = Attributes(schema)
        # where is this information needed?
        # XXX behaviors need to be considered here
        # use plone.dexterity.utils.iterSchemata or similiar

        # Pass the canonical object as a event description
        notify(ObjectModifiedEvent(translation, descriptions, self.canonical))

    def get_all_translations(self, content):
        """Return all translations excluding the just modified content"""
        content_lang = queryAdapter(content, ILanguage).get_language()
        translations = ITranslationManager(content).get_translated_languages()
        translations.remove(content_lang)
        return translations

handler = LanguageIndependentModifier()

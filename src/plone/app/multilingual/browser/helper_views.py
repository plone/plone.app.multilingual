from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility
from plone.multilingual.interfaces import IMultilingualStorage
from plone.app.uuid.utils import uuidToObject
from plone.app.multilingual.browser.selector import NOT_TRANSLATED_YET_TEMPLATE
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.multilingual.interfaces import ITranslationManager


class universal_link(BrowserView):
    """ Redirects the user to the negotiated translated page
        based on the user preferences in the user's browser.
    """

    def __call__(self):
        uid = ''
        if 'uid' in self.request:
            uid = self.request['uid']
        else:
            # If no uid parameter redirect to root
            root = getToolByName(self.context, 'portal_url')
            self.request.RESPONSE.redirect(root.url())
        # Look for the element
        storage = getUtility(IMultilingualStorage)
        if storage.get_canonical(uid):
            canonical = storage.get_canonical(uid)
            # The negotiated language
            ltool = getToolByName(self.context, 'portal_languages')
            if len(ltool.getRequestLanguages()) > 0:
                language = ltool.getRequestLanguages()[0]
                target_uuid = canonical.get_item(language)
                if target_uuid:
                    target_object = uuidToObject(target_uuid)
                    self.request.RESPONSE.redirect(target_object.absolute_url())
                else:
                    target_object = uuidToObject(uid)
                    self.request.RESPONSE.redirect(target_object.absolute_url() + NOT_TRANSLATED_YET_TEMPLATE)
        else:
            # If no uid parameter redirect to root
            root = getToolByName(self.context, 'portal_url')
            self.request.RESPONSE.redirect(root.url())


class not_translated_yet(BrowserView):
    """ View to inform user that the view requested is not translated yet,
        and shows the already translated related content.
    """
    __call__ = ViewPageTemplateFile('templates/not_translated_yet.pt')

    def already_translated(self):
        return ITranslationManager(self.context).get_translations().items()

    def has_any_translation(self):
        return len(ITranslationManager(self.context).get_translations().items()) > 1

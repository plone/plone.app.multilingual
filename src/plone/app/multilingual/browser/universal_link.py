from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility
from plone.multilingual.interfaces import IMultilingualStorage
from plone.app.uuid.utils import uuidToObject


class universal_link(BrowserView):
    """ Redirects the user to the negotiated translated page """

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
            language = ltool.getRequestLanguages()[0]
            target_uuid = canonical.get_item(language)
            if target_uuid:
                target_object = uuidToObject(target_uuid)
                self.request.RESPONSE.redirect(target_object.absolute_url())
        else:
            # If no uid parameter redirect to root
            root = getToolByName(self.context, 'portal_url')
            self.request.RESPONSE.redirect(root.url())

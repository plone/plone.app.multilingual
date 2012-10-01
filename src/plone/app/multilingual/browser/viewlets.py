from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


class oneLanguageConfiguredNoticeViewlet(ViewletBase):
    """ Notice the user that PAM is installed and only one language
        is configured.
    """
    available = False

    def render(self):
        if self.available:
            return self.index()

        return u""

    def update(self):
        lt = getToolByName(self.context, 'portal_languages')
        supported = lt.getSupportedLanguages()
        self.available = len(supported) <= 1

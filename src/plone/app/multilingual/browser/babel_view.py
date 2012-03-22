from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.multilingual.interfaces import ITranslationManager
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from Products.Archetypes.browser.edit import Edit

class BabelView(BrowserView):
    template = ViewPageTemplateFile('babel_view.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state=getMultiAdapter((context, request), name="plone_portal_state")
        self.portal_url = portal_state.portal_url()
        self.group = ITranslationManager(self.context)
   
    def getGroup(self):
        return self.group

    def getPortal(self):
        portal_url = getToolByName(self.context, 'portal_url')
        return portal_url

    def objToTranslate(self):
        return self.context()

    def languages(self):
        return {}

class BabelEdit(Edit):
    __call__ = ViewPageTemplateFile('babel_edit.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.group = ITranslationManager(self.context)
   
    def getTranslatedLanguages(self):
        return self.group.get_translated_languages()

    def getGroup(self):
        return self.group

    def getPortal(self):
        portal_url = getToolByName(self.context, 'portal_url')
        return portal_url

    def objToTranslate(self):
        return self.context

    def languages(self):
        return {}
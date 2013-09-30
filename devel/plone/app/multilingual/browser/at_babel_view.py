from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ATBabelView(BrowserView):
    __call__ = ViewPageTemplateFile('templates/at_babel_view.pt')


class ATBabelEdit(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.RESPONSE.redirect(self.context.absolute_url() +
                                       '/at_babel_edit')

import zope.schema
import zope.interface
from zope.i18nmessageid import MessageFactory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile

from plone.app.multilingual.browser.interfaces import IUpdateLanguage
from plone.app.multilingual import _
from plone.app.multilingual.browser.utils import multilingualMoveObject

import z3c.form

import plone.app.z3cform
import plone.z3cform.templates


class UpdateLanguageForm(z3c.form.form.Form):
    """ A form to change language """

    fields = z3c.form.field.Fields(IUpdateLanguage)

    ignoreContext = True

    output = None

    @z3c.form.button.buttonAndHandler(_(u"update_language",
                               default=u"Update Language"))
    def handle_update(self, action):
        data, errors = self.extractData()
        new_object = self.context

        if not errors:
            language = data['language']
            # We need to move the object to its place!!
            new_object = multilingualMoveObject(self.context, language)

        return self.request.response.redirect(new_object.absolute_url() + '?set_language=' + language)


# IF you want to customize form frame you need to make a custom FormWrapper view around it
# (default plone.z3cform.layout.FormWrapper is supplied automatically with form.py templates)
# update_language_form = plone.z3cform.layout.wrap_form(UpdateLanguageForm, index=FiveViewPageTemplateFile("templates/reporter.pt"))
update_language_form = plone.z3cform.layout.wrap_form(UpdateLanguageForm)


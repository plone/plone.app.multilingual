from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import IUpdateLanguage
from plone.app.multilingual.browser.utils import multilingualMoveObject
from plone.z3cform.layout import wrap_form
from z3c.form import button
from z3c.form import field
from z3c.form import form


class UpdateLanguageForm(form.Form):
    """A form to change language"""

    fields = field.Fields(IUpdateLanguage)

    ignoreContext = True

    output = None

    @button.buttonAndHandler(_("update_language", default="Update Language"))
    def handle_update(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        new_object = self.context
        language = data["language"]
        # We need to move the object to its place!!
        new_object = multilingualMoveObject(self.context, language)

        return self.request.response.redirect(
            new_object.absolute_url() + "?set_language=" + language
        )


update_language_form = wrap_form(UpdateLanguageForm)

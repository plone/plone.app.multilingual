from Acquisition import aq_inner
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.dexterity.browser.edit import DefaultEditForm
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility


class MultilingualEditForm(DefaultEditForm):

    babel = ViewPageTemplateFile("templates/dexterity_edit.pt")

    def languages(self):
        """Deprecated"""
        context = aq_inner(self.context)

        ls = LanguageSelector(context, self.request, None, None)
        ls.update()
        results = ls.languages()

        supported_langs = [v["code"] for v in results]
        missing = {str(c) for c in supported_langs}

        lsv = LanguageSelectorViewlet(context, self.request, None, None)
        translations = lsv._translations(missing)

        # We want to see the babel_view
        append_path = (
            "",
            "babel_view",
        )

        non_viewable = set()
        for data in results:
            code = str(data["code"])
            data["translated"] = code in translations.keys()

            appendtourl = "/".join(append_path)

            if data["translated"]:
                trans, direct, has_view_permission = translations[code]
                if not has_view_permission:
                    # shortcut if the user cannot see the item
                    non_viewable.add(data["code"])
                    continue
                data["url"] = trans.absolute_url() + appendtourl
            else:
                non_viewable.add(data["code"])

        # filter out non-viewable items
        results = [r for r in results if r["code"] not in non_viewable]
        return results

    def portal_url(self):
        portal_tool = getToolByName(self.context, "portal_url", None)
        if portal_tool is not None:
            return portal_tool.getPortalObject().absolute_url()
        return None

    def render(self):
        self.request["disable_border"] = True
        self.request["disable_plone.leftcolumn"] = True
        self.request["disable_plone.rightcolumn"] = True

        for field in self.fields.keys():
            if field in self.schema:
                if ILanguageIndependentField.providedBy(self.schema[field]):
                    self.widgets[field].addClass("languageindependent")
            # With plone.autoform, fieldnames from additional schematas
            # reference their schema by prefixing their fieldname
            # with schema.__identifier__ and then a dot as a separator
            # See autoform.txt in the autoform package
            if "." in field:
                schemaname, fieldname = field.split(".")
                for schema in self.additionalSchemata:
                    if schemaname == schema.__identifier__ and fieldname in schema:
                        if ILanguageIndependentField.providedBy(
                            schema[fieldname]
                        ):  # noqa
                            self.widgets[field].addClass("languageindependent")
        self.babel_content = super().render()
        return self.babel()

    @property
    def max_nr_of_buttons(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMultiLanguageExtraOptionsSchema, prefix="plone"
        )
        return settings.buttons_babel_view_up_to_nr_translations


DefaultMultilingualEditView = layout.wrap_form(MultilingualEditForm)

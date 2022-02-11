from plone.app.multilingual import api
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.relationfield.behavior import IRelatedItems
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IValidator
from z3c.relationfield import RelationValue
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent import ObjectModifiedEvent
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema._bootstrapinterfaces import RequiredMissing

import unittest


class TestLanguageIndependentFieldOnAddTranslationForm(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, IDefaultBrowserLayer)
        alsoProvides(self.request, IPloneAppMultilingualInstalled)

        fti = DexterityFTI("Feedback")
        fti.behaviors = (
            "plone.basic",
            "plone.namefromtitle",
            "plone.translatable",
        )
        fti.model_source = """\
<model xmlns="http://namespaces.plone.org/supermodel/schema"
       xmlns:lingua="http://namespaces.plone.org/supermodel/lingua">
  <schema>
    <field name="mandatory_feedback" type="zope.schema.Text"
           lingua:independent="true">
      <description />
      <required>True</required>
      <title>Mandatory feedback</title>
    </field>
  </schema>
</model>"""
        portal_types = getToolByName(self.portal, "portal_types")
        portal_types._setObject("Feedback", fti)

        self.document = createContentInContainer(
            self.portal["en"],
            "Feedback",
            checkConstraints=False,
            title="Test feedback",
            mandatory_feedback="This is a test",
        )

        # Call 'create_translation' to annotate request
        self.request.form["language"] = "ca"
        self.redirect = getMultiAdapter(
            (self.document, self.request), name="create_translation"
        )
        self.redirect()

        # Look up the ++addtranslation++ with annotated request in place
        self.view = self.portal["ca"].restrictedTraverse(
            "++addtranslation++" + IUUID(self.document)
        )
        self.view.update()
        self.field = self.view.form_instance.fields["mandatory_feedback"].field
        self.widget = self.view.form_instance.widgets["mandatory_feedback"]

    def test_field_is_required(self):
        self.assertTrue(self.field.required)

    def test_field_is_independent(self):
        self.assertTrue(ILanguageIndependentField.providedBy(self.field))

    def test_default_validator_raise_exception_on_independent_field(self):
        # Remove browser layer to get the default validator
        noLongerProvides(self.request, IPloneAppMultilingualInstalled)
        ###
        validator = getMultiAdapter(
            (
                self.view.context,
                self.view.request,
                self.view.form_instance,
                self.field,
                self.widget,
            ),
            IValidator,
        )
        self.assertNotEqual(
            str(validator.__class__.__name__), "LanguageIndependentFieldValidator"
        )
        self.assertRaises(RequiredMissing, validator.validate, None)

    def test_validator_pass_on_required_independent_field(self):
        validator = getMultiAdapter(
            (
                self.view.context,
                self.view.request,
                self.view.form_instance,
                self.field,
                self.widget,
            ),
            IValidator,
        )
        self.assertEqual(
            str(validator.__class__.__name__), "LanguageIndependentFieldValidator"
        )
        self.assertIsNone(validator.validate(None))

    def test_input_widget_renders_textarea(self):
        # Remove browser layer to get the default validator
        noLongerProvides(self.request, IPloneAppMultilingualInstalled)
        ###
        widget_template = getMultiAdapter(
            (
                self.view.context,
                self.view.request,
                self.view.form_instance,
                self.field,
                self.widget,
            ),
            IPageTemplate,
            name="input",
        )
        self.assertIn("<textarea", widget_template(self.widget))

    def test_input_widget_does_not_render_textarea_but_span(self):
        widget_template = getMultiAdapter(
            (
                self.view.context,
                self.view.request,
                self.view.form_instance,
                self.field,
                self.widget,
            ),
            IPageTemplate,
            name="input",
        )
        self.assertNotIn("<textarea", widget_template(self.widget))


class TestLanguageIndependentRelationField(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.request, IDefaultBrowserLayer)
        alsoProvides(self.request, IPloneAppMultilingualInstalled)

        self.a_en = createContentInContainer(
            self.portal["en"], "Document", title="Test Document"
        )

        self.b_en = createContentInContainer(
            self.portal["en"], "Document", title="Another Document"
        )

        adapted = IRelatedItems(self.a_en)
        dm = getMultiAdapter((adapted, IRelatedItems["relatedItems"]), IDataManager)
        dm.set([self.b_en])

    def test_has_relation_list(self):
        adapted = IRelatedItems(self.a_en)

        bound = IRelatedItems["relatedItems"].bind(adapted)
        self.assertEqual(len(bound.get(adapted)), 1)

        value = bound.get(adapted)
        self.assertEqual(type(value[0]), RelationValue)

        dm = getMultiAdapter((adapted, IRelatedItems["relatedItems"]), IDataManager)
        self.assertEqual(dm.get(), [self.b_en])

    def test_relation_list_gets_copied(self):
        a_ca = api.translate(self.a_en, "ca")

        adapted = IRelatedItems(a_ca)

        bound = IRelatedItems["relatedItems"].bind(adapted)
        self.assertEqual(len(bound.get(adapted)), 1)

        value = bound.get(adapted)
        self.assertEqual(type(value[0]), RelationValue)

        dm = getMultiAdapter((adapted, IRelatedItems["relatedItems"]), IDataManager)
        self.assertEqual(dm.get(), [self.b_en])

    def test_relation_list_gets_translated(self):
        b_ca = api.translate(self.b_en, "ca")
        a_ca = api.translate(self.a_en, "ca")

        adapted = IRelatedItems(a_ca)

        bound = IRelatedItems["relatedItems"].bind(adapted)
        self.assertEqual(len(bound.get(adapted)), 1)

        value = bound.get(adapted)
        self.assertEqual(type(value[0]), RelationValue)

        dm = getMultiAdapter((adapted, IRelatedItems["relatedItems"]), IDataManager)
        self.assertEqual(dm.get(), [b_ca])

    def test_relation_list_gets_cleared(self):
        a_ca = api.translate(self.a_en, "ca")

        adapted = IRelatedItems(self.a_en)
        dm = getMultiAdapter((adapted, IRelatedItems["relatedItems"]), IDataManager)
        dm.set([])

        notify(ObjectModifiedEvent(self.a_en))

        adapted = IRelatedItems(a_ca)
        dm = getMultiAdapter((adapted, IRelatedItems["relatedItems"]), IDataManager)
        self.assertEqual(dm.get(), [])

    def test_copied_relation_list_gets_translated(self):
        a_ca = api.translate(self.a_en, "ca")
        b_ca = api.translate(self.b_en, "ca")

        # But only after self.a_en is modified (this is a feature, not a bug):
        notify(ObjectModifiedEvent(self.a_en))

        adapted = IRelatedItems(a_ca)

        bound = IRelatedItems["relatedItems"].bind(adapted)
        self.assertEqual(len(bound.get(adapted)), 1)

        value = bound.get(adapted)
        self.assertEqual(type(value[0]), RelationValue)

        dm = getMultiAdapter((adapted, IRelatedItems["relatedItems"]), IDataManager)
        self.assertEqual(dm.get(), [b_ca])

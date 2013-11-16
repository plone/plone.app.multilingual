# -*- coding: utf-8 -*-
import unittest
from Products.CMFCore.utils import getToolByName
from z3c.form.interfaces import IValidator
from zope.component import getMultiAdapter
from zope.interface import alsoProvides, noLongerProvides
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema._bootstrapinterfaces import RequiredMissing
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer


class TestLanguageIndependentFieldOnAddTranslationForm(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IDefaultBrowserLayer)
        alsoProvides(self.request, IPloneAppMultilingualInstalled)

        fti = DexterityFTI('Feedback')
        fti.behaviors = (
            'plone.app.dexterity.behaviors.metadata.IBasic',
            'plone.app.content.interfaces.INameFromTitle',
            'plone.app.multilingual.dx.interfaces.IDexterityTranslatable',
        )
        fti.model_source = u"""\
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
        portal_types = getToolByName(self.portal, 'portal_types')
        portal_types._setObject('Feedback', fti)

        self.document = createContentInContainer(
            self.portal['en'], 'Feedback', checkConstraints=False,
            title=u'Test feedback', mandatory_feedback=u'This is a test')

        # Call 'create_translation' to annotate request
        self.request.form['language'] = 'ca'
        self.redirect = getMultiAdapter(
            (self.document, self.request),
            name="create_translation"
        )
        self.redirect()

        # Look up the ++addtranslation++ with annotated request in place
        self.view = self.portal['ca'].restrictedTraverse(
            '++addtranslation++Feedback'
        )
        self.view.update()
        self.field = self.view.form_instance.fields['mandatory_feedback'].field
        self.widget = self.view.form_instance.widgets['mandatory_feedback']

    def test_field_is_required(self):
        self.assertTrue(self.field.required)

    def test_field_is_independent(self):
        self.assertTrue(ILanguageIndependentField.providedBy(self.field))

    def test_default_validator_raise_exception_on_independent_field(self):
        # Remove browser layer to get the default validator
        noLongerProvides(self.request, IPloneAppMultilingualInstalled)
        ###
        validator = getMultiAdapter(
            (self.view.context, self.view.request,
             self.view.form_instance, self.field, self.widget),
            IValidator
        )
        self.assertNotEqual(
            str(validator.__class__.__name__),
            'LanguageIndependentFieldValidator'
        )
        self.assertRaises(
            RequiredMissing,
            validator.validate,
            None
        )

    def test_validator_pass_on_required_independent_field(self):
        validator = getMultiAdapter(
            (self.view.context, self.view.request,
             self.view.form_instance, self.field, self.widget),
            IValidator
        )
        self.assertEqual(
            str(validator.__class__.__name__),
            'LanguageIndependentFieldValidator'
        )
        self.assertIsNone(validator.validate(None))

    def test_input_widget_renders_textarea(self):
        # Remove browser layer to get the default validator
        noLongerProvides(self.request, IPloneAppMultilingualInstalled)
        ###
        widget_template = getMultiAdapter(
            (self.view.context, self.view.request,
             self.view.form_instance, self.field, self.widget),
            IPageTemplate,
            name='input'
        )
        self.assertIn('<textarea', widget_template(self.widget))

    def test_input_widget_does_not_render_textarea_but_span(self):
        widget_template = getMultiAdapter(
            (self.view.context, self.view.request,
             self.view.form_instance, self.field, self.widget),
            IPageTemplate,
            name='input'
        )
        self.assertNotIn('<textarea', widget_template(self.widget))

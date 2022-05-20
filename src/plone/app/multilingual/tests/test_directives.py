from plone.app.multilingual.dx.directives import languageindependent
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.testing import PAM_INTEGRATION_TESTING
from plone.supermodel import model
from plone.supermodel.utils import mergedTaggedValueList
from zope import schema
from zope.interface import Interface

import unittest


class TestDirectives(unittest.TestCase):

    layer = PAM_INTEGRATION_TESTING

    def test_schema_directives_store_tagged_values(self):
        """Test, if the schema directive values are stored as tagged values."""

        class IDummy(model.Schema):
            """Dummy schema class."""

            languageindependent("foo")
            foo = schema.TextLine(title="Foo")

        self.assertEqual(
            [(Interface, "foo", "true")],
            mergedTaggedValueList(IDummy, languageindependent.key),
        )

        self.assertTrue(ILanguageIndependentField.providedBy(IDummy["foo"]))

    def test_inherited_schema_still_has_tagged_value(self):
        """An inherited schema should still have the tagged value information
        inherited from its superclass.
        """

        class IFoo(model.Schema):
            """Class with a searchable field"""

            languageindependent("baz")
            baz = schema.TextLine(title="baz")

        class IBar(IFoo):
            """Schema class which inherits a field from IFoo."""

        self.assertEqual(
            [(Interface, "baz", "true")],
            mergedTaggedValueList(IFoo, languageindependent.key),
        )
        self.assertTrue(ILanguageIndependentField.providedBy(IFoo["baz"]))

        self.assertEqual(
            [(Interface, "baz", "true")],
            mergedTaggedValueList(IBar, languageindependent.key),
        )
        self.assertTrue(ILanguageIndependentField.providedBy(IBar["baz"]))

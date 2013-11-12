from plone.app.multilingual.dx.directives import languageindependent
from plone.directives import form
from plone.supermodel.utils import mergedTaggedValueList
from zope import schema
from zope.interface import Interface
import unittest
import zope.component.testing


class TestDirectives(unittest.TestCase):

    def tearDown(self):
        """Tear down the testing setup.
        """
        zope.component.testing.tearDown()

    def test_schema_directives_store_tagged_values(self):
        """Test, if the schema directive values are stored as tagged values.
        """

        class IDummy(form.Schema):
            """Dummy schema class.
            """
            languageindependent('foo')
            foo = schema.TextLine(title=u'Foo')

        self.assertEquals([(Interface, 'foo', 'true')],
                          mergedTaggedValueList(IDummy,
                                                languageindependent.key))

    def test_inherited_schema_still_has_tagged_value(self):
        """An inherited schema should still have the tagged value information
        inherited from its superclass.
        """

        class IFoo(form.Schema):
            """Class with a searchable field
            """
            languageindependent('baz')
            baz = schema.TextLine(title=u'baz')

        class IBar(IFoo):
            """Schema class which inherits a field from IFoo.
            """

        self.assertEquals([(Interface, 'baz', 'true')],
                          mergedTaggedValueList(IFoo, languageindependent.key))
        self.assertEquals([(Interface, 'baz', 'true')],
                          mergedTaggedValueList(IBar, languageindependent.key))
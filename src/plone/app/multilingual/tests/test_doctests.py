import unittest2 as unittest
import doctest
from plone.testing import layered
from plone.app.multilingual.testing import (
    PLONEAPPMULTILINGUAL_INTEGRATION_TESTING,
    PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING,
    optionflags,
)
integration_tests = [
    'vocabularies.txt'
]
functional_tests = [
    'form.txt',
    'menu.txt',
    'catalog.txt',
    'language_independent.txt',
]


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite('tests/%s' % f,
                                      package='plone.app.multilingual',
                                      optionflags=optionflags),
                 layer=PLONEAPPMULTILINGUAL_INTEGRATION_TESTING)
            for f in integration_tests]
        +
        [layered(doctest.DocFileSuite('tests/%s' % f,
                                      package='plone.app.multilingual',
                                      optionflags=optionflags),
                 layer=PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING)
            for f in functional_tests]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

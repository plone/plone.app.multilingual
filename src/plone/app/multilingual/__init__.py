# make this a package

import pkg_resources

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.multilingual')

from Products.PloneLanguageTool.LanguageTool import LanguageBinding
from languagetool import setLanguageBindingsCookieWins
LanguageBinding.setLanguageBindings = setLanguageBindingsCookieWins

try:
    from Products.LinguaPlone import patches
    isLPinstalled = True
except ImportError:
    isLPinstalled = False


try:
    pkg_resources.get_distribution('plone.dexterity')
    isDexterityInstalled = True
except pkg_resources.DistributionNotFound:
    isDexterityInstalled = False

from plone.app.multilingual import catalog
catalog  # pyflakes

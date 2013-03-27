# make this a package

import pkg_resources

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.multilingual')

from Products.PloneLanguageTool.LanguageTool import LanguageBinding
from languagetool import setLanguageBindingsCookieWins
LanguageBinding.setLanguageBindings = setLanguageBindingsCookieWins

try:
    pkg_resources.get_distribution('Products.LinguaPlone')
except pkg_resources.DistributionNotFound:
    isLPinstalled = False
else:
    isLPinstalled = True

# Instead of check for Dexterity, check if p.multilingualbehavior is installed.
# If it's installed, then Dexterity is installed too.
try:
    pkg_resources.get_distribution('plone.multilingualbehavior')
except pkg_resources.DistributionNotFound:
    isDexterityInstalled = False
else:
    isDexterityInstalled = True

from plone.app.multilingual import catalog
catalog  # pyflakes

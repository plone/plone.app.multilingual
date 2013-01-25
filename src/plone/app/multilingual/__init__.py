# make this a package

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
    from plone.dexterity import *
    isDexterityInstalled = True
except ImportError:
    isDexterityInstalled = False

from plone.app.multilingual import catalog
catalog  # pyflakes

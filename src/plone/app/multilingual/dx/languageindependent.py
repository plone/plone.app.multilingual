from .interfaces import ILanguageIndependentField
from plone.app.event.dx.behaviors import IEventBasic
from zope.interface import alsoProvides

# configure existing behaviors to be language independent
alsoProvides(IEventBasic["start"], ILanguageIndependentField)
alsoProvides(IEventBasic["end"], ILanguageIndependentField)
alsoProvides(IEventBasic["whole_day"], ILanguageIndependentField)
alsoProvides(IEventBasic["open_end"], ILanguageIndependentField)

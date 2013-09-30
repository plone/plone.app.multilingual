
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import queryUtility

from zope import interface
from zope import component
# XXX
from zope.component import adapter

from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent

from plone.uuid.interfaces import IUUIDGenerator

from plone.app.multilingual.interfaces import ATTRIBUTE_NAME
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import NOTG
from plone.app.multilingual.interfaces import IMutableTG

try:
    from Acquisition import aq_base
except ImportError:
    aq_base = lambda v: v  # soft-dependency on Zope2, fallback


@interface.implementer(ITG)
@component.adapter(ITranslatable)
def attributeTG(context):
    return getattr(context, ATTRIBUTE_NAME, None)


class MutableAttributeTG(object):
    interface.implements(IMutableTG)
    component.adapts(ITranslatable)

    def __init__(self, context):
        self.context = context

    def get(self):
        return getattr(self.context, ATTRIBUTE_NAME, None)

    def set(self, tg):
        if tg == NOTG:
            generator = queryUtility(IUUIDGenerator)
            tg = generator()
        tg = str(tg)
        setattr(self.context, ATTRIBUTE_NAME, tg)


@adapter(ITranslatable, IObjectCreatedEvent)
def addAttributeTG(obj, event):

    if not IObjectCopiedEvent.providedBy(event):
        if getattr(aq_base(obj), ATTRIBUTE_NAME, None):
            return  # defensive: keep existing TG on non-copy create

    generator = queryUtility(IUUIDGenerator)
    if generator is None:
        return

    tg = generator()
    if not tg:
        return

    setattr(obj, ATTRIBUTE_NAME, tg)

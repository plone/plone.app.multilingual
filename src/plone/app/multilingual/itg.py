# -*- coding: utf-8 -*-
from Acquisition import aq_base
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import adapter, queryUtility
from zope.interface import implementer
from zope.lifecycleevent.interfaces import (IObjectCopiedEvent,
                                            IObjectCreatedEvent)

from plone.app.multilingual.interfaces import (ATTRIBUTE_NAME, ITG, NOTG,
                                               IMutableTG, ITranslatable)


@implementer(ITG)
@adapter(ITranslatable)
def attributeTG(context):
    return getattr(context, ATTRIBUTE_NAME, None)


@implementer(IMutableTG)
@adapter(ITranslatable)
class MutableAttributeTG(object):
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

    if not IObjectCopiedEvent.providedBy(event) and getattr(
        aq_base(obj), ATTRIBUTE_NAME, None
    ):
        return  # defensive: keep existing TG on non-copy create

    generator = queryUtility(IUUIDGenerator)
    if generator is None:
        return

    tg = generator()
    if not tg:
        return

    setattr(obj, ATTRIBUTE_NAME, tg)

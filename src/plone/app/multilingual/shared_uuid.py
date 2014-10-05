# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_chain
from plone.app.multilingual.content.lrf import ILanguageRootFolder
from plone.app.multilingual.interfaces import ILanguageIndependentFolder
from plone.uuid.interfaces import ATTRIBUTE_NAME
from plone.uuid.interfaces import IAttributeUUID
from plone.uuid.interfaces import IUUID
from zope.component import adapter
from zope.interface import implementer


@implementer(IUUID)
@adapter(ILanguageRootFolder)
def lrfUUID(context):
    return getattr(aq_base(context), ATTRIBUTE_NAME, None)


@implementer(IUUID)
@adapter(ILanguageIndependentFolder)
def lifUUID(context):
    return getattr(aq_base(context), ATTRIBUTE_NAME, None)


@implementer(IUUID)
@adapter(IAttributeUUID)
def attributeUUID(context):
    is_language_independent = False
    for element in aq_chain(context):
        if ILanguageIndependentFolder.providedBy(element):
            is_language_independent = True
        if ILanguageRootFolder.providedBy(element) and is_language_independent:
            uid = getattr(aq_base(context), ATTRIBUTE_NAME, None) or ''
            return uid + '-' + element.id if uid is not None else None
    return getattr(context, ATTRIBUTE_NAME, None)

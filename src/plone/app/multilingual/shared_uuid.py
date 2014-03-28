from Acquisition import aq_base
from Acquisition import aq_chain
from plone.app.multilingual.content.lrf import ILanguageRootFolder
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
@adapter(IAttributeUUID)
def attributeUUID(context):
    child = context
    for element in aq_chain(context):
        if hasattr(child, '_v_is_shared_content') \
           and child._v_is_shared_content \
           and ILanguageRootFolder.providedBy(element):
            uid = getattr(aq_base(context), ATTRIBUTE_NAME, None)
            return uid + '-' + element.id if uid is not None else None
        child = element
    return getattr(context, ATTRIBUTE_NAME, None)

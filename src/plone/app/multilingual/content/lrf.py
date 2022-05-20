from plone.app.content.namechooser import NormalizingNameChooser
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import ITranslationIdChooser
from plone.dexterity.content import Container
from zope.component import adapter
from zope.container.interfaces import INameChooser
from zope.deprecation import deprecated
from zope.interface import implementer


_marker = object()


@implementer(INameChooser)
@adapter(ILanguageRootFolder)
class LRFNameChooser(NormalizingNameChooser):
    """Special name chooser to fix issue where createContentInContainer is
    used to create a new content into LRF with an id, which exists already
    in the parent folder.

    """

    def chooseName(self, name, object):
        chosen = super().chooseName(name, object)
        if chosen in self.context.objectIds():
            old_id = getattr(object, "id", None)
            object.id = chosen
            chooser = ITranslationIdChooser(object)
            chosen = chooser(self.context, self.context.getId())
            object.id = old_id
        return chosen


@implementer(ILanguageRootFolder, INavigationRoot)
class LanguageRootFolder(Container):
    """Deprecated LanguageRootFolder custom base class"""


deprecated(
    "LanguageRootFolder", "LanguageRootFolders should be migrate to DexterityContainers"
)

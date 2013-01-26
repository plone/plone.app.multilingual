from plone.app.upgrade.utils import installOrReinstallProduct


def installPloneMultilingual(portal):
    # Make sure plone.app.discussion is properly installed.
    installOrReinstallProduct(
        portal,
        "plone.multilingual",
        out=None,
        hidden=True)

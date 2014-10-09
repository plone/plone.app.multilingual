# -*- coding: utf-8 -*-
"""Legacy install/uninstall-methods to guard from re-installing/uninstalling"""
from Products.CMFCore.utils import getToolByName


# def install(context):
#     # When 'install' is defined, QuickInstaller doesn't apply the default
#     # GenericSetups-profile automaticlaly, but it has to be imported
#     # manually.
#     setup_tool = getToolByName(context, 'portal_setup')
#     setup_tool.runAllImportStepsFromProfile(
#         'profile-plone.app.multilingual:default', purge_old=False)


# def beforeUninstall(self, reinstall, product, cascade):
#     # 'beforeUninstall' can be used to prevent automatic execution of named
#     # GS steps from the default profile, e.g. 'utilities'
#     if 'utilities' in cascade:
#         cascade.remove('utilities')
#     return None, cascade


def uninstall(context, reinstall=False):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-plone.app.multilingual:uninstall', purge_old=False)

# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4:


def setLanguageBindingsCookieWins(self, usePath=1, useContent=1, useCookie=1,
                                  useRequest=1, useDefault=1,
                                  useCcTLD=0, useSubdomain=0, authOnly=0):
    """Setup the current language stuff."""
    langs = []
    if usePath:
        # This one is set if there is an allowed language in the current path
        langsPath = [self.tool.getPathLanguage()]
    else:
        langsPath = []

    if useContent:
        langsContent = [self.tool.getContentLanguage()]
    else:
        langsContent = []

    if useCookie and not (authOnly and self.tool.isAnonymousUser()):
        # If we are using the cookie stuff we provide the setter here
        set_language = self.tool.REQUEST.get('set_language', None)
        if set_language:
            langsCookie = [self.tool.setLanguageCookie(set_language)]
        else:
            # Get from cookie
            langsCookie = [self.tool.getLanguageCookie()]
    else:
        langsCookie = []

    if useSubdomain:
        langsSubdomain = self.tool.getSubdomainLanguages()
    else:
        langsSubdomain = []

    if useCcTLD:
        langsCcTLD = self.tool.getCcTLDLanguages()
    else:
        langsCcTLD = []

    # Get langs from request
    if useRequest:
        langsRequest = self.tool.getRequestLanguages()
    else:
        langsRequest = []

    # Get default
    if useDefault:
        langsDefault = [self.tool.getDefaultLanguage()]
    else:
        langsDefault = []

    # Build list
    # patched here - cookie should win
    langs = langsPath + langsCookie + langsContent + langsSubdomain + \
        langsCcTLD + langsRequest + langsDefault

    # Filter None languages
    langs = [lang for lang in langs if lang is not None]

    # Set cookie language to language
    if useCookie and langs[0] not in langsCookie:
        self.tool.setLanguageCookie(langs[0], noredir=True)

    self.DEFAULT_LANGUAGE = langs[-1]
    self.LANGUAGE = langs[0]
    self.LANGUAGE_LIST = langs[1:-1]

    return self.LANGUAGE

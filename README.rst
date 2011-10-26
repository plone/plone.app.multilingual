======================
plone.app.multilingual
======================

Introduction
============

This module provides the user interface for managing content translations. It's the app package of the next generation Plone multilingual engine. It's designed to work with Dexterity content types and the *old fashioned* Archetypes based content types as well. It only works with Plone 4.1 and above due to the use of UUIDs to reference the translations.


Usage
=====

For using this package with Dexterity content types you should add to your *eggs* buildout section::

    eggs =
        plone.app.multilingual [dexterity]

If you want to use it with Archetypes based content types::

    eggs =
        plone.app.multilingual [archetypes]

[...] (WIP)


Translation Engine Design
=========================

See plone.multilingual README:

http://github.com/plone/plone.multilingual


Roadmap
=======

Feature list for paml:

1.0
---
    1. Improved display of the current content language and which translations are already available
    2. Traversal using /en /es /ca URLs
    3. Initial reimplementation of the UX in translation views in Plone UI
    4. Initial implementation of language independent fields using marker interfaces on fields

2.0
---
    1. Add support for Deco layouts and content types
    2. Pluggable translation policies
    3. Pluggable language policies negotiations

3.0
---
    1. plone.app.cmsui support

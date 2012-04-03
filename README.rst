======================
plone.app.multilingual
======================

Introduction
============

This module provides the user interface for managing content translations. It's the app package of the next generation Plone multilingual engine. It's designed to work with Dexterity content types and the *old fashioned* Archetypes based content types as well. It only works with Plone 4.1 and above due to the use of UUIDs to reference the translations.


Usage
=====

To use this package with both Dexterity and Archetypes based content types you should add the following two lines to your *eggs* buildout section:

	eggs =
		plone.app.multilingual [archetypes]
		plone.app.multilingual [dexterity]

Alternatively, you can write it like this:

	eggs =
    	plone.app.multilingual
    	plone.multilingualbehavior

(plone.multilingualbehavior adds multilingual functionality for Dexterity content types)

If you need to use this package only with Archetypes based content types you only need the following line:
	eggs =
		plone.app.multilingual [archetypes]

Whichever of the above changes you make to your *eggs* section, you also need to add the following to your *zcml* buildout section:
	zcml =
    	plone.app.multilingual


After re-running your buildout and installing the newly available add-ons, go to the languages section of your Site Setup and select two or more languages for your site. You will now be able to create translations of Plone's default content types, or to link existing content as translations.

plone.app.multilingual will create folders for each of your site's languages and put translated content into the appropriate folders.

For information about making your Dexterity content type translatable, see the plone.multilingualbehavior documentation.


Translation Engine Design
=========================

See plone.multilingual README:

http://github.com/plone/plone.multilingual


License
=======

GNU General Public License, version 2


Sponsoring
==========

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

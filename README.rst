======================
plone.app.multilingual
======================

Introduction
============

Talking about multi-language support in Plone is talk about
Products.LinguaPlone. It has been the defacto standard for managing translations
of Archetypes-based content types in Plone through the years. Somehow its
functionality never made its way into the Plone core and today is in legacy
status. Nowadays, Plone faces the rising of Dexterity content types and its
incoming adoption into the Plone core in the near future (4.3) and complete the
transition to Plone as default content types in Plone 5.

plone.app.multilingual was designed originally to provide Plone a whole
multilingual story. Using ZCA technologies, enables translations to Dexterity
and Archetypes content types as well managed via an unified UI.

This module provides the user interface for managing content translations. It's
the app package of the next generation Plone multilingual engine. It's designed
to work with Dexterity content types and the *old fashioned* Archetypes based
content types as well. It only works with Plone 4.1 and above due to the use of
UUIDs to reference the translations.

After more than 7 years, a GSOC, redesigns, reimplementations due to deprecated
libraries, two major Plone versions finally we are able to say that
plone.app.multilingual is finally here.

Components
==========

PAM is composed of four packages, two are mandatory:

    * plone.app.multilingual (UI)
    * plone.multilingual (core)

and two optionals (at least one should be installed):

    * plone.multilingualbehavior (enable Dexterity support via a behavior)
    * archetypes.multilingual (enable Archetypes support)

Usage
=====

To use this package with both Dexterity and Archetypes based content types you
should add the following two lines to your *eggs* buildout section::

    eggs =
        plone.app.multilingual
        plone.multilingualbehavior

If you need to use this package only with Archetypes based content types you
only need the following line::

    eggs =
        plone.app.multilingual


Setup
=====

After re-running your buildout and installing the newly available add-ons, you
should go to the `Languages` section of your `Site Setup` and select at least
two or more languages for your site. You will now be able to create translations
of Plone's default content types, or to link existing content as translations.

Features
========

These are the most important features PAM provides.

Root Language folders
---------------------

After the setup, PAM will create root folders for each of your site's languages
and put translated content into the appropriate folders. A language folder
implements INavigation Root, so from the user's point of view, each language is
"jailed" inside its correspondent language folder. There are subscribers in
place to capture user interaction with content and update the language in
contents, for example when user moves or copy content between language folders.

Babel view
----------

An evolution of the LP `translate` view, unified for either Archetypes and
Dexterity content types. It features an already translated content viewer for
the current content being edited via an ajaxified dinamic selector that shows
them on the fly on user request.

Translation locator policy
--------------------------

Language selector policy
------------------------

Neutral root folder support
---------------------------

Translation map
---------------

Google Translation Service integration
--------------------------------------

LinguaPlone migration
---------------------

Backup
------


For information about making your Dexterity content type translatable, see the
plone.multilingualbehavior documentation.


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

This is the planned feature list for PAM:

1.0
---

    * Babel view
    * Root language folders
    * Translation locator policy
    * Language selector policy
    * Neutral root folder support
    * Translation map
    * Google Translation Service integration
    * LinguaPlone migration
    * Backup

2.0
---

    * XLIFF export/import
    * Iterate support: we know there are some needs about iterate integration
    * LinguaPlus/linguatools set of useful tools
    * Outdated translations alerts and translation workflows support

3.0
---

    * plone.app.toolbar/plone.app.cmsui support
    * Add support for Deco layouts and content types
    * Pluggable translation policies
    * Pluggable language policies negotiations

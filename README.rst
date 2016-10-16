.. image:: https://travis-ci.org/plone/plone.app.multilingual.png?branch=master
    :target: http://travis-ci.org/plone/plone.app.multilingual

.. contents::


Introduction
============

In the old days before Plone 4.3, talking about multi-language support in Plone
is talk about Products.LinguaPlone. It has been the *defacto* standard for
managing translations of Archetypes-based content types in Plone through the
years. Somehow its functionality never made its way into the Plone core and
today it is in legacy status. Nowadays, Plone faces the rising of Dexterity
content types and its adoption into the core since Plone 4.3. With Plone 5
released, the transition is completed and Dexterity is shipped as its default
content type story.

plone.app.multilingual was designed originally to provide Plone a whole
multilingual story. Using ZCA technologies, enables translations to Dexterity
and Archetypes content types as well managed via an unified UI.

This module provides the user interface for managing content translations. It's
the app package of the next generation Plone multilingual engine. It's designed
to work with Dexterity content types and the *old fashioned* Archetypes based
content types as well. It only works with Plone 4.1 and above due to the use of
UUIDs for referencing the translations.

After more than 7 years, a GSOC, redesigns, reimplementations due to deprecated
libraries, two major Plone versions finally we are able to say that
plone.app.multilingual is finally here.


Versions
========

* ``1.x`` - Plone 4.x with Archetypes and Dexterity

* ``2.x`` - Plone >= 4.x, < 5.0 with plone.app.contenttypes (Dexterity) and
  real shared content

* ``3.x`` - Plone >= 5.x.  3.0.17 will likely be the latest release on this branch.  You are encouraged to use 4.x.

* ``4.x`` - Plone >= 5.x (5.0.3 minimum, due to GenericSetup dependency)

Components
==========

PAM is composed of two packages, one is mandatory:

    * plone.app.multilingual (core, UI, enables Dexterity support via a behavior)

and one optional:

    * archetypes.multilingual (enables Archetypes support)

Usage
=====

To use this package with both Dexterity and Archetypes based content types you
should add the following line to your *eggs* buildout section::

    eggs =
        plone.app.multilingual[archetypes]

To use this package with plone.app.contenttypes you should add the following
line to your *eggs* buildout section::

    eggs =
        plone.app.multilingual

Setup
=====

After re-running your buildout and installing the newly available add-ons, you
should go to the *Languages* section of your site's control panel and select
at least two or more languages for your site. You will now be able to create
translations of Plone's default content types, or to link existing content as
translations.

Features
========

These are the most important features PAM provides.

Root Language folders
---------------------

After the setup, PAM will create root folders for each of your site's
languages and put translated content into the appropriate folders. A language
folder implements INavigationRoot, so from the user's point of view, each
language is "jailed" inside its correspondent language folder. There are event
subscribers in place to capture user interaction with content and update the
language in contents accordingly, for example when user moves or copy content
between language folders.


Babel view
----------

An evolution of the LP *translate* view, unified for either Archetypes and
Dexterity content types. It features an already translated content viewer for
the current content being edited via an ajaxified dynamic selector that shows
them on the fly on user request.


Language independent fields
---------------------------

PAM has support for language independent fields, but with a twist respect the
LP implementation. As PAM does design does not give more relevance to one
translated object above the others siblings (has no canonical object), fields
marked as language independent get copied over all the members of the
translation group always. The PAM UI will warn you about this behavior by
reminding you that the values in the field on the other group participants
will be overwritten.


Translation locator policy
--------------------------

When translating content, this policy decides how it would be placed in the
site's structure. There are two policies in place:

    * LP way, the translation gets placed in the nearest translated folder in
      parent's hierarchy

    * Ask user where to place the translated element in the destination
      language root folder


Language selector policy
------------------------

While browsing the site, the language selector viewlet allows users to switch
site's content language and ease access between translations of the current
content. There are two policies in place in case the translation of a specific
language does not exist (yet):

    * LP way, the selector shows the nearest translated container.
    * Shows the user an informative view that shows the current available
      translations for the current content.


The "Media" folder - a shared "Language Independent Folder"
-----------------------------------------------------------

The root language folders are used to house the content tree for the
corresponding language. However, there are some use cases where we need
content that does not belong to any language. For example, for assets or side
resources like images, videos and documents. For this reason PAM supplies a
special Language Independent Folder to house these kind of objects.
After PAM setup, there is a special folder called "Media", which can be
accessed through the "Go to shared folder" item of the "Translate" menu. All
items placed in this folder will have neutral as their default language and
will be visible from the other root language folders as if they were placed
there as well.

Note: Language Independent Folder's have also been historically known as
"Neutral root folder", "language neutral folder" and
"language shared (folder)".  Also don't confuse Language Independent Folders
with Language Independent Fields


Translation map
---------------

In order to ease the translation tasks, we devised a tool that displays in a
useful way all the current translated objects and its current translation
information. The map also shows a list of missing translations in case you
want to build a *mirrored* (completely) translated site.


Google Translation Service integration
--------------------------------------

If you are subscriber of the Google Translation service (a paid service), you
can setup your API key on *Languages* site setup. Then, you will notice a new
icon in the babel view that takes the original field on the left side and
using Google Translations service, translates its contents and fill the right
side field.


LinguaPlone migration
---------------------

You can migrate your existing LP powered sites to PAM using the *Migration* tab
in the *Languages* control panel. The migration has been divided into 4 steps
for separation of concerns and for improving the success of each of the required
procedures.

Step 0 (optional) - Reindex the language index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The migration of LinguaPlone content depends on an up-to-date Language index.
Use this step to refresh this index. **Warning:** Depending on the number of
items in your site, this can take a considerable amount of time. This step is
not destructive and can be executed as many times as needed.

Step 1 - Relocate content to the proper root language folder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step will move the site's content to its correspondent root language folder
and previously will make a search for misplaced content through the site's
content tree and will move them to its nearest translated parent. **Warning:**
This step is destructive as it will alter your content tree structure. Make sure
you have previously configured your site's languages properly in the 'Site
Languages' tab of the 'Languages' control panel. It's advisable that you do not
perform this step on production servers having not tried it in
development/preproduction servers previously. Depending on the distribution of
your site's content and the accuracy of the language information on each content
object you may need to relocate manually some misplaced content after this step.
Despite the fact that this step is 'destructive' it can be executed as times as
needed if some problem is detected and afterwards you fix the problem. Please,
refer to the procedure log when it finishes.

Step 2 - Transfer multilingual catalog information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step will transfer the relations between translations stored by LinguaPlone
to the PAM catalog. This step is not destructive and can be executed as many
times as needed.

Step 3 - Cleanup after migration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step will search and fix some lost dependencies to the ITranslatable
interface hidden in the relation catalog and it gets rid of them. It must be run
only when LinguaPlone is already uninstalled, so this step is hidden until then.


Marking objects as translatables
================================

Archetypes
----------

By default, if PAM is installed, Archetypes-based content types are marked as
translatables


Dexterity
---------

Users should mark a dexterity content type as translatable by assigning a the
multilingual behavior to the definition of the content type either via file
system, supermodel or through the web.


Marking fields as language independant
======================================

Archetypes
----------

The language independent fields on Archetype-based content are marked the same
way as in LinguaPlone::

    atapi.StringField(
        'myField',
        widget=atapi.StringWidget(
        ....
        ),
        languageIndependent=True
    ),

.. note::

    If you want to completely remove LinguaPlone of your installation, you
    should make sure that your code are dependant in any way of LP.


Dexterity
---------

There are four ways of achieve it.

Directive
~~~~~~~~~

In your content type class declaration::

    from plone.app.multilingual.dx import directives
    directives.languageindependent('field')

Supermodel
~~~~~~~~~~

In your content type XML file declaration::

    <field name="myField" type="zope.schema.TextLine" lingua:independent="true">
        <description />
        <title>myField</title>
    </field>

Native
~~~~~~

In your code::

    from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
    alsoProvides(ISchema['myField'], ILanguageIndependentField)

Through the web
~~~~~~~~~~~~~~~

Via the content type definition in the *Dexterity Content Types* control panel.


Internal design of plone.app.multilingual
=========================================

All the internal features are implemented on the package plone.app.multilingual.

The key points are:

    1. Each translation is a content object
    2. There is no canonical object
    3. The translation reference storage is external to the content
       object
    4. Adapt all the steps on translation
    5. Language get/set via an unified adapter
    6. Translatable marker interface(s)


There is no canonical content object
------------------------------------

Having a canonical object on the content space produces a dependency which is
not orthogonal with the normal behavior of Plone. Content objects should be
autonomous and you should be able to remove it. This is the reason because we
removed the canonical content object. There is a canonical object on the
translation infrastructure but is not on the content space.


Translation reference storage
-----------------------------

In order to maintain the relations between the different language objects we
designed a common object called a *translation group*. This translation group
has an UUID on its own and each object member of the group stores it in the
object catalog register. You can use the ITranslationManager utility to access
and manipulate the members of a translation group given one object of the group.


Adapt all the steps on translation
----------------------------------

The different aspects involved on a translation are adapted, so it's possible
to create different policies for different types, sites, etc.

  * ITranslationFactory - General factory used to create a new content

    * ITranslationLocator - Where we are going to locate the new translated content

        Default : If the parent folder is translated create the content on the
        translated parent folder, otherwise create on the parent folder.

    * ITranslationCloner - Method to clone the original object to the new one

        Default : Nothing

    * ITranslationIdChooser - Which id is the translation

        Default : The original id + lang code-block

  * ILanguageIndependentFieldsManager - Manager for language independent fields

    Default: Nothing


Language get/set via an unified adapter
---------------------------------------

In order to access and modify the language of a content type regardless the
type (Archetypes/Dexterity) there is a interface/adapter::

    Products.CMFPlone.interfaces.ILanguage

You can use::

    from Products.CMFPlone.interfaces import ILanguage
    language = ILanguage(context).get_language()

or in case you want to set the language of a content::

    language = ILanguage(context).set_language('ca')


Translatable marker interface
-----------------------------

In order to know if a content can be translated there is a marker interface::

    plone.app.multilingual.interfaces.ITranslatable

Source Code
===========

Contributors please read the document `Process for Plone core's development <http://docs.plone.org/develop/plone-coredev/index.html>`_

Sources are at the `Plone code repository hosted at Github <https://github.com/plone/plone.app.multilingual>`_.

License
=======

GNU General Public License, version 2


Roadmap
=======

This is the planned feature list for PAM:

1.0
---

    * Babel view
    * Root language folders
    * Non invasive language selector
    * Universal link
    * Language selector policy
    * Neutral root folder support
    * Catalog based storage
    * Translation map
    * Google Translation Service integration
    * LinguaPlone migration


2.0 (PLIP 13091)
----------------

    * The first version compatible with PLIP 13091
      (https://dev.plone.org/ticket/13091)
    * Update, get rid of legacy code and transfer some of the PAM logic to the
      Plone core (plone.app.i18n)
    * Perform the same for other parts of Plone core to integrate some monkey
      patches and update legacy code from Products.PloneLanguageTool


3.0
---

    * XLIFF export/import
    * Iterate support: we know there are some needs about iterate integration
    * LinguaPlus/linguatools set of useful tools
    * Outdated translations alerts and translation workflows support
    * plone.app.toolbar/plone.app.cmsui support
    * Add support for Deco layouts and content types
    * Pluggable translation policies
    * Pluggable language policies negotiations

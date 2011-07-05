======================
plone.app.multilingual
======================

Introduction
============

This module provides the user-interface to manager content-translations


Usage
=====

To use this package with dexterity:

    plone.app.multilingual [dexterity]

Archetypes:
    
    plone.app.multilingual [archetypes]

Translation Engine Design
=========================

* see plone.multilingual 

Use Cases
=========

1. Configuring languages
------------------------

Deciding which languages the site is going to be on. This use case includes :

* The default language is the one that is going to be used when creating a new object on the site.

* The 

Test :

tests/01-ConfigureMulitlingual.txt

2. Translate a AT object 
------------------------

In order to translate AT objects they need to implement ITranslatable interface. This is done throw ZCML and the Products.Archetypes.atapi.BaseObject object. 

This use case is divided in:

* Defining which AT object can be translated

* Creating a new AT object and translating it to another language

Test :


3. Translate a dexterity object
-------------------------------


4. Edit a AT translated object using a babel_view
-------------------------------------------------

5. Edit a dexterity translated object using a babel_view
--------------------------------------------------------


6. Clean utility translation dictionary
---------------------------------------



7. Policy language URL
----------------------

When a user decide to use the policy language URL, it can be possible to accés to translated object using /ca-es/Compra where Compra is the "canonical name" of the object

8. Policy language GET var
--------------------------

When a user decide to use the policy language GET var, it can be possible to accés to the translated object /path/to/object?language=ca-es 


9. Policy to store the new translated object
--------------------------------------------


10. 


URL Policies
============

* Enable Tiny URL : in this case the tiny url will redirect you to the correct language depending on your cockie
* Force redirecto to coockie language
* Fallback to default language

Edit Policies
=============

* Use babel_view on edit
* Don't use babel_view as default

Default Language
================

We get the default language from the PloneLanguageTool or in the future use local utility plone.app.i18n.locales.languages 
We use PloneLanguageTool with getToolByName 
TODO : XXX change to use localutility languages

There is a plone.app.layout.navigation that set the default DefaultView and we can define

Local utility that handles all the translations object 

Atributs no traduibles

Una traducció d'una altra

policies :

FULL - all duplicated

PARTIAL - not on mother site

PRESS RELEASE 

----------------------------------------------------

revision at anotation

---------------------------------------------------

* Translate default page and the folder

* Neutral folders and content ExtendedExtendedPath create neutral content inside translated tree

* workflow 

* default language on creating

* URL

* PloneLanguageTool

* List of languages not defined

* Events 

* Creating portal_url -> /es/

Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

6.0.0a11 (2022-05-24)
---------------------

Bug fixes:


- Add icon expressions to types.
  [agitator] (#401)


6.0.0a10 (2022-05-15)
---------------------

Bug fixes:


- Make compatible with robotframework 3-5.
  [maurits] (#5)


6.0.0a9 (2022-04-04)
--------------------

Bug fixes:


- Connect translations: always set basePath pattern option.
  In the supported Plone versions this always works.
  [maurits] (#6)


6.0.0a8 (2022-02-24)
--------------------

Bug fixes:


- Fix issue with wrong redirection URL if a language selector viewlet was rendered in a subrequest, like with Mosaic. 
  [jensens] (397-2)
- isort, black, pyupgrade, remove six usages.
  [jensens] (#397)


6.0.0a7 (2022-01-19)
--------------------

Bug fixes:


- In CMFPlone the ILanguage schema was moved to plone.i18n and is referenced as such there, here the change was missing.
  [jensens] (#394)


6.0.0a6 (2021-12-29)
--------------------

Bug fixes:


- Fix typos in documentation.  [telshock] (#340)


6.0.0a5 (2021-10-16)
--------------------

Bug fixes:


- Manage Translations view should not call translation objects. [mliebischer] (#384)


6.0.0a4 (2021-10-13)
--------------------

Bug fixes:


- Disable CSRF protection during the setting of TG attribute. [mamico] (#375)


6.0.0a3 (2021-09-15)
--------------------

Bug fixes:


- Remove cyclic dependency with Products.CMFPlone
  [ericof] (#391)


6.0.0a2 (2021-09-01)
--------------------

Bug fixes:


- Force view_methods to be a tuple on setup and uninstall (#337)
- Fix deleting items with broken relation in languageindependent field
  [pbauer] (#390)


6.0.0a1 (2021-04-28)
--------------------

Breaking changes:


- Bootstrapify for barceloneta-lts (#380)

      * Init add to own branch

      * Add back missing html tag

      * Fix double msgs & add full width

      * Fix headings

      * Init add to own branch

      * Add back missing html tag

      * Fix headings

      * fix test, use string from footer

      * fix test, check h1 not documentFirstHeading

      * fix test, use contains text

      * update icons

      * Jquery load is removed with jq3.

      * major version bump

      Co-authored-by: Peter Holzer <peter.holzer@agitator.com>
      Co-authored-by: Peter Mathis <peter.mathis@kombinat.at> (#380)


Bug fixes:


- Force view_methods to be a tuple on setup and uninstall (#337)


5.6.2 (2020-09-26)
------------------

Bug fixes:


- Fixed deprecation warning for ComponentLookupError.
  Fixed deprecation warning for ILanguageSchema, depend on ``plone.i18n`` 4.0.4.
  Fixed deprecation warning for IObjectEvent from zope.component.
  Fixed deprecation warning for zope.site.hooks.
  [maurits] (#3130)


5.6.1 (2020-06-24)
------------------

Bug fixes:


- Hide left and right portlet columns on babel add view. Fixes #373 [iham] (#373)


5.6.0 (2020-05-06)
------------------

New features:


- Inherit IPloneAppMultilingualInstalled layer from IPloneFormLayer for better
  LIF widget overriding.
  [petschki] (#371)


Bug fixes:


- Move metadata to setup.cfg in order to avoid encoding problems in CHANGES.rst running Plone 6.0 on Python 3.6, see #372.
  [jensens] (#372)


5.5.1 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


5.5.0 (2019-12-11)
------------------

New features:


- Remove the 'set_language' parameter when 'always_set_cookie' is enabled in language control panel. See #362
  [erral] (#362)


5.4.2 (2019-11-25)
------------------

Bug fixes:


- Use the shared 'Plone test setup' and 'Plone test teardown' keywords in Robot tests.
  [Rotonen] (#349)


5.4.1 (2019-08-23)
------------------

Bug fixes:


- fix adding new language when Language Independent Folder has content
  [petschki] (#358)
- add/update translation forms doesn't show error return from z3c form validation
  [mamico] (#360)


5.4.0 (2019-07-18)
------------------

New features:


- Add low level events and notifies:
  on register, update and remove of a translation to a translation groups.
  [jensens] (#256)


Bug fixes:


- Remove deprecation warnings in tests.
  Increase readability
  Add code comments.
  Remove superfluos reindex of "Language" in manager.
  [jensens] (#256)
- wrong check for default addview in addtranslation traverser
  [mauro] (#355)
- Remove any dependency to ``archetypes.multilingual``, since this is a indirection.
  Remove all dependencies that are already part of ``Products.CMFPlone``.
  All version specifications were reduced to use a recent ``Products.CMFPlone``.
  The ``decorator`` dependency is no longer used.
  [jensens] (#357)


5.3.5 (2019-05-21)
------------------

Bug fixes:


- Setting named behavior instead of dotted on fti during install. [iham] (#345)


5.3.4 (2019-05-04)
------------------

Bug fixes:

- Avoid browser to permanently cache first redirection to negotiated lang (#347)
  [laulaz]

- Moved to named behaviors. [iham] (#342)


5.3.3 (2019-04-29)
------------------

Bug fixes:


- Fix toolbar icon
  [agitator] (#338)
- Fix DeprecationWarning ``ILanguageSchema`` was moved to ``plone.i18n``. [jensens] (#339)


5.3.2 (2019-02-08)
------------------

Bug fixes:


- a11y: Added role attribute for portalMessage [nzambello] (#332)


5.3.1 (2018-12-11)
------------------

Bug fixes:

- Hide left and right portlet columns on babel_edit. Fixes #327
  [erral]


5.3.0 (2018-11-05)
------------------

New features:

- Add compatibility with python 3.
  [pbauer]


5.2.3 (2018-09-26)
------------------

Bug fixes:

- Rerelease, as 5.2.1 was somehow released twice, once in June, once in September.
  [maurits]


5.2.2 (2018-09-25)
------------------

New features:

- Make plone.app.controlpanel optional (no longer there in Plone 5.2).
  [jensens]

Bug fixes:

- Upgrade step to profile version 3 was lost and now recreated.
  [jensens, 2silver]

- Do not show deprecation warning when loading migrator code,
  as it is intended to load old LRF there.
  [jensens]

- Don't fail, if multilingual selector is called without query
  [tomgross]

- Fix connecting of documents
  [tomgross]


5.2.1 (2018-06-20)
------------------

Bug fixes:

- Fixed tests now that Catalan has translated ‘assets’ into ‘recursos’.
  [maurits]

- Run addAttributeTG for the site root when installing. This prevents
  triggering plone.protect.
  [jaroel]


5.2.0 (2018-04-04)
------------------

New features:

- Move translations to plone.app.locales. Fixes #191
  [erral]

Bug fixes:

- Fix Python 3 import.
  [pbauer]

- Remove `language-switcher` from available view methods when uninstalling
  [erral]

- Fix i18n markup in multilingual map to avoid ${DYNAMIC_CONTENT} strings in po files
  [erral]

- Fix i18n markup of the viewlet shown in the translation creation view.
  [erral]


5.1.4 (2018-02-02)
------------------

Bug fixes:

- Removed ``Extensions/Install.py``.  This was only there as wrapper for
  applying our uninstall profile, but that wrapper is no longer needed.
  [maurits]

- Marked 'Scenario: As an editor I can translate a document' as noncritical.
  This is a 'robot' test that has been unstable for a long time.
  [maurits]

- Fix issue where rendering translation menu did write on get when translations
  were enabled on old site with existing content
  [datakurre]

- Fix issue where DX multilingual subscriber was executed even multilingual
  was not installed
  [Asko Soukka]

- Fix edge case where ValueError was raised from DX translatable subscriber
  when no translations were yet available for the content
  [datakurre]

- Fix issue where rendering universal link failed when translation information
  was not yet available for the content
  [datakurre]


5.1.3 (2017-11-25)
------------------

New features:

- Set shortname ``plone.translatable`` to behavior ``plone.app.multilingual.dx.interfaces.IDexterityTranslatable``.
  [jensens]

Bug fixes:

- Imports are Python3 compatible
  [ale-rt, jensens]

- Fix serialization of query variables for selector links in Zope 4.
  [davisagli]


5.1.2 (2017-08-05)
------------------

New features:

- Complete basque translation
  [erral]

- Complete spanish translation
  [erral]


5.1.1 (2017-07-20)
------------------

Bug fixes:

- Safely convert field value to unicode
  [agitator, GerardRodes]


5.1 (2017-07-18)
----------------

New features:

- Rebuilt po files
  [erral]

- Rename ``media`` folder to a more generic name ``assets`` by default and
  add i18nize it to be localization aware
  [agitator, datakurre]
- When viewing a folder with a default page, the translation menu shows all
  options for both the folder and then the default page in the
  same order and with the same titles. The option to edit the current page in
  babel view have been merged with the options to edit the other translations
  to make the menu more consistent
  [datakurre]

- Translation menu show the title of the language independent folder on
  the language independent folder link in translation menu as
  "Open ${title} folder"
  [datakurre]

- Translation menu no longer includes "Set content language"-menuitem, which
  was redundant (but less transparent in its behavior) to just cutting and
  pasting a content under the desired language folder
  [datakurre]

Bug fixes:

- Add missing i18n:translate tags
  [erral]


5.0.8 (2017-07-03)
------------------

Bug fixes:

- Fixed language alternate viewlet #153 [erral]

- Notify ObjectTranslatedEvent if translating with babel view
  #277 [tomgross]

- Fixed issue where delete action on modify translations view deleted
  the current page instead of the selected translation
  [datakurre]


5.0.7 (2017-05-31)
------------------

Bug fixes:

- removed unittest2 dependency
  [kakshay21]


5.0.6 (2017-05-09)
------------------

Bug fixes:

- Update import of UnauthorizedUser. [davisagli]


5.0.5 (2017-04-27)
------------------

Bug fixes:

- Remove travis integration because plone.app.mutlilingual is part of plonecore and should be tested there.
- Fix bug where formcontrols were overlaped by fields.
  [agitator]

- Fix robot tests to work with improved related items widget.
  [thet]


5.0.4 (2017-03-26)
------------------

New features:

- Add a new view ``@@tg`` for translatable content. It will return the
  current translation group of the content, matching the bahavior of ``@@uuid``
  of ``plone.app.uuid`` returning UUID of the content.  [datakurre]


5.0.3 (2017-02-12)
------------------

New features:

- Show Translate menu in INavigationRoot items and hide in ILanguageRootFolders
  [erral]

Bug fixes:

- Remove deprecated __of__ calls on BrowserViews
  [MrTango]


5.0.2 (2017-01-04)
------------------

Bug fixes:

- Add new tests for sitemap.xml.gz (it is currently not listing any content)
  [djowett]


5.0.1 (2017-01-02)
------------------

Bug fixes:

- Allow to work in an Archtypes free Plone 5.1.
  [jensens]

- Replace unittest2 with unittest.
  [jensens]


5.0 (2016-11-17)
----------------

Breaking changes:

- Support for Archetypes content is only installed if you install `archetypes.multilingual.
  For Archetypes support, there is a new ``archetypes`` ``extras_require``, which you can depend upon.
  [davisagli]

New features:

- Replaced add_translations and remove_translations with combined modify_translations.
  Modify translations page gives you an overview of existing translations and has actions
  to connect, disconnect existing translations, as well as actions to create or delete a translation for you content item.
  [agitator]

- Moved stylesheet from legacy bundle to logged-in bundle
  [agitator]

Bug fixes:

- Made robot tests more robust, I hope.
  Before using 'Wait until element is visible',
  first call   'Wait until page contains element'.
  The first one only works reliably when the element was already on the page initially.
  If the element was created dynamically, you need to use the 'page contains' call first,
  otherwise you sometimes get an error:
  'Element not found in the cache - perhaps the page has changed since it was looked up.'
  [maurits]


4.0.4 (2016-09-16)
------------------

Bug fixes:

- Change RelatedItemsFieldWidget configuration from ``@@add_translations`` view to support Mockup 2.4.0, so that the widget is able to navigate beyond the INavigationRoot boundary and to access other translation trees.
  This change keeps compatibility with older versions of Mockup or Mockup-less setups.
  [thet]


4.0.3 (2016-08-15)
------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


4.0.2 (2016-06-12)
------------------

Bug fixes:

- Fixed unstable robot test by waiting until the expected text is on the page.  [maurits]


4.0.1 (2016-06-07)
------------------

Bug fixes:

- Correct event subscribers so that content cut from one LRF & pasted into the
  Media folder is shown there when I switch to a second language.
  [djowett]


4.0.0 (2016-05-25)
------------------

Breaking changes:

- No more compatible with GenericSetup below 1.8.2.
  [iham]

New features:

- Creating language folder(s) on installation.
  (fixes https://github.com/plone/plone.app.multilingual/issues/214)
  [iham]


3.0.17 (2016-05-03)
-------------------

Fixes:

- Wait for visibility of select2 result, instead of time.
  [jensens]

- Workaroud in robot test for TinyMCE overlap bug see
  https://github.com/plone/plone.app.multilingual/issues/227
  for details
  [jensens]


3.0.16 (2016-03-31)
-------------------

Fixes:

- Fixed compatibility issue with archetypes contents: wrong URL were generated.
  [keul, hvelarde]

- Really don't show the Google Translate button when no API key set
  [djowett]


3.0.15 (2016-03-01)
-------------------

Fixes:

- Clarify naming of Language Independent Folders
  [djowett]



3.0.14 (2016-02-25)
-------------------

New:

- Updated Traditional Chinese translations.

Fixes:

- Use custom catalog vocabulary for translation content mapping widget,
  which searches all site content.
  [alecm]

- Update Site Setup link in all control panels (fixes https://github.com/plone/Products.CMFPlone/issues/1255)
  [davilima6]


3.0.13 (2015-10-27)
-------------------

New:

- Updated Traditional Chinese translations.
  [l34marr]

Fixes:

- Fixed typo in Italian translation
  [ale-rt]


3.0.12 (2015-09-27)
-------------------

- Disable csrf protection with multilingual.
  [vangheem]

- Resolve deprecation warning for isDefaultPage.
  [fulv]


3.0.11 (2015-09-20)
-------------------

- Fix the old fixed fake tabbing with the back to Site Setup link.
  [sneridagh]

- update French translations
  [enclope]


3.0.10 (2015-09-15)
-------------------

- Fix migration-view, lp-migration-after and after-migration-cleanup.
  [pbauer]

- Fix translation-map.
  Fixes https://github.com/plone/plone.app.multilingual/issues/175
  [pbauer]


3.0.9 (2015-09-14)
------------------

- Add auth-key to pam-migration.
  [pbauer]


3.0.8 (2015-09-14)
------------------

- Fix @@relocate-content.
  [pbauer]


3.0.7 (2015-09-12)
------------------

- Updated basque translation
  [erral]


3.0.6 (2015-08-20)
------------------

- Rerelease due to possible brown bag release.  Jenkins complains
  about 3.0.5.
  [maurits]


3.0.5 (2015-08-20)
------------------

- Move @@multilingual-selector registration from PloneRoot to Navigation root
  This allows to hide language folders in nginx and to use different domains.
  [do3cc]

- Update Traditional Chinese translation.
  [l34marr]


3.0.4 (2015-07-18)
------------------

- Adapt to plone.protect in case its old content.
  [bloodbare]

- Waiting for patterns to test the add translation on robot framework.
  [bloodbare]

- Remove superfluous 'for'.
  [fulv]


3.0.3 (2015-06-05)
------------------

- Remove CMFDefault dependency
  [tomgross]


3.0.2 (2015-05-13)
------------------

- Fix ``containsobjects`` field, renamed to contains_objects
  [gforcada]


3.0.1 (2015-05-04)
------------------

- Japanese translations.
  [terapyon]

- Update version information for Plone 5 in ``README.rst``.
  [saily]


3.0.0 (2015-03-26)
------------------

- Adaptation of plone.app.multilingual for Plone 5. Moved ILanguage to CMFPlone,
  events only executed when browserlayer is installed, control panel integrated
  on z3cform with Plone5.
  [bloodbare]


2.0.0 (2015-03-24)
------------------

- Add Traditional Chinese translation.
  [l34marr]

2.0a4 (2015-03-04)
------------------

- Remove dependency on zope.app.container and zope.app.initd
  [joka]

- Add more common api functions and test them.
  [jensens]

- Refactor locations of code in dx to bundle stuff at a sane place.
  [jensens]

- Remove BLACKLIST_IDS, with LIF this is superfluos.
  [jensens]

- Remove LanguageTool patch, meanwhile superfluos.
  [jensens]

- Add new ``bootstrap.py`` to support new parameter ``--setuptools-version``.
  [saily]

- Fixed language independent fields in ++addtranslation++
  requires ``plone.z3cform >= 0.8.1``
  [jensens, agitator]

- Add uninstall hook to run uninstall profile on deactivation
  [datakurre]

- Fix behavior registration on activation for all Dexterity types
  without dependency to ``plone.app.contenttypes``.
  [datakurre]

- Do not block acquisition on LRF for acl_users, portal_url (both broke login
  form) and portal_catalog any more.
  [jensens]

- Feature: Introduce a set variable BLACK_LIST_IDS which is used as a central
  place for blacklisted object ids not to take into account as neutral
  content or in LRF. It unifies the formerly cluttered different combinations
  of tests with same goal.
  [jensens]

- Cleanup: Pep8, utf8-headers, readability, ..., code-analysis now runs.
  [jensens]

- Fix issue where universal link ignored the language cookie
  [datakurre]

- Fix Plone 5 compatibility issues
  [martior]

- Add a manual folder to LRF migration view
  [datakurre]

- Fix schema editor plugin to not break schema editors outside FTI (e.g.
  ``collective.easyform``)
  [datakurre]

2.0a3 (2014-05-30)
------------------

- Show 'Translate into' menu in plone-contentmenu only when having permission
  to translate.
  [saily]

- Use *Modify portal content* permission for *Edit* action on Language Root
  Folders.
  [saily]

- Move ``devel`` to ``src`` folder, update ``MANIFEST.in``,
  ``setup.py``, ``buildout.cfg`` and ``.gitignore`` to fit that new structure.
  Updated docs.
  [saily]

- Prepare tests to Plone 5
  [saily]


2.0a2 (2014-03-27)
------------------

- Fix alternate language viewlet
  [saily]

- Fix tests. Don't rely on translateable strings in functional tests,
  translations may change.
  [saily]

- Add uninstall profile.
  [thet]


2.0a1 (2014-03-25)
------------------

- In the findContent method of the migrator script, do a more explicit test if
  a content is a real, Dexterity or Archetypes based content object.
  [thet]

- ``createdEvent`` subscriber works now in request-free environments too.
  [jensens]

- Download latest v1 ``bootstrap.py``
  [saily]

- Fix an import issue in ``upgrades.py``
  [saily]

- Add code analysis to ``plone-test-4.x.cfg`` and ``plone-test-5.x.cfg``
  [saily]

- Huge PEP8 and Flake8 cleanup. Please run ``bin/code-analysis`` before
  commiting. A git pre-commit hook should be added automatically through
  buildout.
  [saily]

- Ensure ``plone.app.controlpanel.Language`` permission is present.
  [saily]

- Merge ``add.py`` and ``add_translation_form.py`` into one file
  [saily]

- Rename ``update_translation_form.py`` to ``update.py``
  [saily]

- Rename ``remove_translation_form.py`` to ``remove.py``
  [saily]

- Remove ``five.grok`` in browser directory.
  [saily]


1.2 - 2013-09-24
----------------

- Better testsetup for robot tests using it's own layer.
  [saily]

- Revert translation: display of default pages of folders (it doesn't show
  content which doesn't have 'is_default_page' attributes).
  [bogdangi]

- Add new option to allow users to bypass permission checks when updating
  objects with language independent fields.
  [saily]

- Add a new alternate languages viewlet, see:
  https://support.google.com/webmasters/answer/189077
  [saily]

- Remove Twitter-Bootstrap css code from ``multilingual.css`` and set
  stylesheet rendering to authenticated users only.
- Remove twitter bootstrap styles and make style rendered for authenticated
  users only.  [saily]

- Add an upgrade step to reimport css_registry
  [saily]


1.1 - 2013-06-19
----------------

- Add translation: widget missing
- Translating folder with default_page: menu items added
- Add translation: display of default pages of folders
  [ksuess]

- Bugfix: p.a.contentmenu fails if access to translation is not permitted.
  Solution: Introduce restricted access and use it in vocabulary for menu.
  [jensens]

- Added ++add++ and factory support using session var to store where it comes
  from. It maintains the old programatic way so it's possible to create
  translations using code.
  [ramon]

- Extend travis integration to test against Plone 4.1, 4.2, 4.3 and
  include following dependencies into tests:
  - ``plone.multilingual``
  - ``plone.multilingualbehavior``
  - ``archetypes.multilingual``
  [saily]

- plone.app.contenttypes compatibility on setup
  [sneridagh]

- Added French translation
  [bouchardsyl]

- take care to filter out translated contents
  wich do no have supported language information
  [kiorky]

- added support for language neutral objects with country specific language codes
  by checking _combinedlanguagelist too
  [agitator]


1.0 - 2013-04-16
----------------

- Remove ITG usage to ITranslationManager usage
  [ramon]

- Shared folder working on old collections
  [fgrcon]

- Shared folder correct name and reference on setup
  [ramon]

- Instead of check for Dexterity, check if p.multilingualbehavior is installed.
  If it's installed, then Dexterity is installed too
  [sneridagh]

- Fixed travis integration, extend from plone buildout-cache.
  [saily]

- Clean the migration template [erral]

- Don't assume a transition called 'publish' will exist [erral]

- Show language name if no native language information is available.
  [saily]

- Added Ukrainian translation
  [kroman0]

- Add to travis-ci
  [saily]

- Use drop-down instead of buttons on babel view if there are more than X
  translations [pysailor]


1.0rc1 - 2013-01-26
-------------------

- Improve and finish migration code and related 'Languages' configlet tab
  [pysailor, sneridagh]
- Testing of migration code on production sites [pysailor, erralin, sneridagh]
- Fix broken tests and new ones [pysailor, erralin, bloodbare, sneridagh]
- New re-designed language selector and related helper views [erralin,
  bloodbare]
- Not translated view improvements [erralin, bloodbare]
- fixed getClosestDestination when translation doesn't exist [gborelli]
- Update deprecated imports to work with Plone 4.3
  [saily]


1.0b3 2012-10-04
----------------

- Select the original language in the dexterity babel edit form.
  [maurits]

- Add after migration action on view
  [do3cc]

- Multilingual Map
  [ramon]

- Univeral link
  [ramon]

- Catalog patch bug solving
  [ramon]

- Language selector bug solving
  [sneridagh]

- Babel view javascripts unification and optimization
  [ramon]

- Neutral language folder and menu options added
  [ramon]

- New tests
  [sneridagh]

- Moving templates to templates folder
  [ramon]

- Updating language options
  [ramon]

- Menu refactoring
  [ramon]

- Allow to see all content on adding translation
  [ramon]


1.0b2 - 2012-07-08
------------------

- change language index to Language to LinguaPlone coexistance
  [ramon]

- don't rebuild the complete catalog on installing
  [pbauer]

- add indexes via setuphandler instead of xml to prevents purging on reinstall
  [pbauer]

- make babel-view align fields next to each other
  [do3cc]

- updated .po files
  [gborelli]

- Added rebuild.sh script in order to simplify updating translations
  [gborelli]

- Added italian translation
  [gborelli]

- Do not fail when the front-page cannot be moved to a new folder
  during setup.
  [maurits]

- Make it possible to override the portal_type that is used when
  creating a root language folder.
  [maurits]


1.0b1 - 2012-04-03
------------------

- Added Google Translation Service ajax service [ramon]

- Added babel view on AT [sneridagh]

- Added babel view on dexterity [ramon]

- Added the option to not filter language on folder_contents view
  [ramon]

- Added to translation menu to edit a translated language [ramon]

- Initial setup of a site moving content to language folders [ramon]


0.1a2 - 2011-12-04
------------------

- Improved Control Panel [ramon]

- Improved Language Control Panel site languages selector widget to be
  more usable.

- Setup the root folder layout for each configured site languages on
  languages control panel save settings [ramon, sneridagh]

- Adapt languageselector viewlet from LP [ramon]

- Re-enable and adapt the searchResults patch again [ramon]

- Cleaning description of packages and registerProfile of paml
  [sneridagh]


0.1a1 - 2011-10-03
------------------

- Initial version [ramon, awello, sneridagh]

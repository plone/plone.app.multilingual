Changelog
=========

5.0.1 (2017-01-02)
------------------

Bug fixes:

- Allow to work in an Archtypes free Plone 5.1.
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

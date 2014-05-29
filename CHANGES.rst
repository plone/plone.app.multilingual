Changelog
=========

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

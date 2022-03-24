*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot
Resource  Products/CMFPlone/tests/robot/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown

*** Test Cases ***

Scenario: As an editor I can add new translation
    Given a site owner
      and a document in English
      and a document in Catalan
     When I view the Catalan document
      and I link the document in English as a translation
      and I switch to English
     Then I can view the document in English


*** Keywords ***

Setup test browser
  Set Selenium speed  0.5s
  Open test browser
  Set window size  1200  900

# Given

a site owner
  Enable autologin as  Manager

a document in English
  Create content  type=Document
  ...  container=/${PLONE_SITE_ID}/en/
  ...  id=an-english-document
  ...  title=An English Document

a document in Catalan
  Create content  type=Document
  ...  container=/${PLONE_SITE_ID}/ca/
  ...  id=a-catalan-document
  ...  title=A Catalan Document

# When

I view the Catalan document
  Go to  ${PLONE_URL}/ca/a-catalan-document
  Wait until page contains  A Catalan Document

I link the document in English as a translation
  Page should contain element  css=#plone-contentmenu-multilingual a
  Capture page screenshot
  Element should be visible  css=#plone-contentmenu-multilingual a
  Click Element  css=#plone-contentmenu-multilingual a
  Wait until page contains element  css=#_modify_translations
  Wait until element is visible  css=#_modify_translations

  Click Element  css=#_modify_translations
  Given patterns are loaded
  Wait until page contains element  css=#translations-overview .connectTranslationAction

  Click Element  css=#translations-overview .connectTranslationAction
  Wait until page contains element  css=.select2-choices
  Wait until element is visible  css=.select2-choices
  Click Element  css=#formfield-form-widgets-content .pat-relateditems-container button.mode.search
  Input Text  css=#formfield-form-widgets-content .select2-input  en
  Wait until page contains element  xpath=(//span[contains(., 'An English Document')])
  Wait until element is visible  xpath=(//span[contains(., 'An English Document')])
  Click Element  xpath=(//span[contains(., 'An English Document')])
  Wait until page contains  An English Document

  # We need a complicated xpath, because for some reason a button with this id is there twice.
  # The first one is hidden.
  Click Element  xpath=(//*[contains(@class, 'modal-footer')]//button[@id='form-buttons-connect_translation'])
  Wait until page contains element  xpath=(//h3[@class="translationTitle"])
  Sleep  5
  Wait until element is visible  xpath=(//h3[@class="translationTitle"])
  Focus  xpath=(//*[@id="translations-overview"]//a[contains(@href,"a-catalan-document")])
  Click Element  xpath=(//*[@id="translations-overview"]//a[contains(text(),'/plone/ca/a-catalan-document')])
  Wait until page contains  A Catalan Document

I switch to English
  Click Link  xpath=//a[@title='English']
  Wait until page contains  An English Document

# Then

I can view the document in English
  Wait until page contains element
  ...  xpath=//h1[1][contains(text(),'English Document')]
  Wait until page contains element
  ...  xpath=//ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='English']

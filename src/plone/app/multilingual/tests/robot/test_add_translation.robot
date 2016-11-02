*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  Products/CMFPlone/tests/robot/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers
Suite setup  Set Selenium speed  0.5s

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
  Click Element  css=#plone-contentmenu-multilingual a
  Wait until page contains element  css=#_modify_translations
  Wait until element is visible  css=#_modify_translations

  Click Element  css=#_modify_translations
  Given patterns are loaded
  Wait until page contains element
  ...  css=#translations-overview .connectTranslationAction

  Click Element  css=#translations-overview .connectTranslationAction
  Wait until page contains element  css=.select2-choices
  Wait until element is visible  css=.select2-choices
  Click Element  css=#formfield-form-widgets-content .select2-choices
  Wait until page contains element  xpath=(//span[contains(., 'An English Document')])
  Wait until element is visible  xpath=(//span[contains(., 'An English Document')])
  Click Element  xpath=(//span[contains(., 'An English Document')])
  Wait until page contains  An English Document

  Click Element  xpath=(//*[contains(@class, 'plone-modal-footer')]//input[@id='form-buttons-connect_translation'])
  Wait until page contains element  xpath=(//h3[@class="translationTitle"])
  Sleep  5
  Wait until element is visible  xpath=(//h3[@class="translationTitle"])
  Focus  xpath=(//*[@class="odd"]//a[contains(@href,"a-catalan-document")])
  Click Element  xpath=(//*[@class="odd"]//a[contains(@href,"a-catalan-document")])
  Wait until page contains  A Catalan Document

I switch to English
  Click Link  xpath=//a[@title='English']
  Wait until page contains  An English Document

# Then

I can view the document in English
  Wait until page contains element
  ...  xpath=//*[contains(@class, 'documentFirstHeading')][./text()='An English Document']
  Wait until page contains element
  ...  xpath=//ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='English']

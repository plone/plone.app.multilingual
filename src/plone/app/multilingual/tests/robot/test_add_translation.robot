*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  Products/CMFPlone/tests/robot/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: As an editor I can add new translation
    Given a site owner
      and a document in English
      and a document in Catalan
     When I view the Catalan document
      and I add the document in English as a translation
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

I add the document in English as a translation
  Click Element  css=#plone-contentmenu-multilingual a
  Wait until element is visible  css=#_add_translations

  Click Element  css=#_add_translations
  Given patterns are loaded
  Wait until page contains element
  ...  css=#formfield-form-widgets-content .select2-choices

  Click Element  css=#formfield-form-widgets-content .select2-choices
  Wait until element is visible  css=#select2-drop
  Wait until element is visible  xpath=(//span[contains(., 'An English Document')])
  Click Element  xpath=(//span[contains(., 'An English Document')])
  Wait until page contains  An English Document

  Select From List  name=form.widgets.language:list  en
  Click Element  css=#form-buttons-add_translations
  Click Element  css=#contentview-view a
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

*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: As an editor I can translate a document
    Given a site owner
      and a document in English
     When I translate the document into Catalan
     Then I can view the document in Catalan

Scenario: As a visitor I can view the translation
    Given a site owner
      and a document in English with Catalan translation
     When I switch to Catalan
     Then I can view the document in Catalan


*** Keywords ***

# Given

a site owner
  Enable autologin as  Manager

a visitor
  Disable autologin

a document in English
  Create content  type=Document
  ...  container=/${PLONE_SITE_ID}/en/
  ...  id=an-english-document
  ...  title=An English Document

a document in English with Catalan translation
  ${uid} =  Create content  type=Document
  ...  container=/${PLONE_SITE_ID}/en/
  ...  id=an-english-document
  ...  title=An English Document
  Create translation  ${uid}  ca
  ...  title=A Catalan Document
  Go to  ${PLONE_URL}/resolveuid/${uid}
  Wait until page contains  An English Document

# When

I translate the document into Catalan
  Go to  ${PLONE_URL}/en/an-english-document/@@create_translation?language=ca
  Input Text  form.widgets.IDublinCore.title  A Catalan Document
  Click Link  Dates  # workaround for of TinyMCE editor field problem
  Click Button  Guardar
  Wait until page contains  Element creat
  Wait until page contains  A Catalan Document

I switch to Catalan
  Click Link  xpath=//a[@title='Català']
  Wait until page contains  A Catalan Document

# Then

I can view the document in Catalan
  Page Should Contain Element
  ...  xpath=//*[contains(@class, 'documentFirstHeading')][./text()='A Catalan Document']
  Page Should Contain Element
  ...  xpath=//ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='Català']

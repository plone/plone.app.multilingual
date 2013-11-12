*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Variables  plone/app/testing/interfaces.py
Variables  plone/app/multilingual/tests/robot/variables.py


Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: As an editor I can translate a document
    Given a site owner
      and a document in English
     When I translate the document into Catalan
     Then I can view the document in Catalan

Scenario: As a vistor I can view the translation
    Given a site owner
      and a document in English with Catalan translation
     When I switch to Catalan
     Then I can view the document in Catalan


*** Keywords ***

# Given

a site owner
  Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

a visitor
  Go To  ${PLONE_URL}

a document in English
  Go to  ${PLONE_URL}/en/++add++Document
  Input Text  form.widgets.IDublinCore.title  An English Document
  Click Button  Save

a document in English with Catalan translation
  Go to  ${PLONE_URL}/en/++add++Document
  Input Text  form.widgets.IDublinCore.title  An English Document
  Click Button  Save
  Go to  ${PLONE_URL}/en/an-english-document/@@create_translation?language=ca
  Input Text  form.widgets.IDublinCore.title  A Catalan Document
  Click Button  Save
  Wait until page contains  Item created

# When

I translate the document into Catalan
  Go to  ${PLONE_URL}/en/an-english-document/@@create_translation?language=ca
  Input Text  form.widgets.IDublinCore.title  A Catalan Document
  Click Button  Save
  Wait until page contains  Item created

I switch to Catalan
  Click Link  Català
  Wait until page contains  A Catalan Document

# Then

I can view the document in Catalan
  Page Should Contain Element  xpath=//*[contains(@class, 'documentFirstHeading')][./text()='A Catalan Document']
  Page Should Contain Element  xpath=//ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='Català']

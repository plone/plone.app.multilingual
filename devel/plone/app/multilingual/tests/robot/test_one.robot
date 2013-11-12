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


*** Keywords ***

a site owner
  Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

a document in English
  Go to  ${PLONE_URL}/en/++add++Document
  Input Text  form.widgets.IDublinCore.title  An English Document
  Click Button  Save

I translate the document into Catalan
  Go to  ${PLONE_URL}/en/an-english-document/@@create_translation?language=ca
  Pause
  Input Text  form.widgets.IDublinCore.title  A Catalan Document
  Click Button  Save
  Wait until page contains  Item created

I can view the document in Catalan
  Page Should Contain Element  xpath=//*[contains(@class, 'documentFirstHeading')][./text()='A Catalan Document']
  Page Should Contain Element  xpath=//ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='Català']

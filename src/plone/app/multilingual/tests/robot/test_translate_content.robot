*** Settings ***

Resource    plone/app/robotframework/browser.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords    Plone test teardown

*** Test cases ***

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

a document in English
  Create content    type=Document    container=/${PLONE_SITE_ID}/en/    id=an-english-document    title=An English Document

a document in English with Catalan translation
  ${uid}=    Create content    type=Document    container=/${PLONE_SITE_ID}/en/    id=an-english-document    title=An English Document
  Create translation    ${uid}    ca    title=A Catalan Document
  Go to    ${PLONE_URL}/resolveuid/${uid}
  Get Element    //h1[1][text()='An English Document']

# When

I translate the document into Catalan
  Go to    ${PLONE_URL}/en/an-english-document/@@create_translation?language=ca
  Take screenshot
  Type Text    //input[@name="form.widgets.IDublinCore.title"]    A Catalan Document
  Take screenshot
  Click    //button[@id="form-buttons-save"]

I switch to Catalan
  Click    //a[@title='Català']
  Get Element    //h1[1][text()='A Catalan Document']

# Then

I can view the document in Catalan
  Get Element    //h1[1][text()='A Catalan Document']
  Get Element    //ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='Català']

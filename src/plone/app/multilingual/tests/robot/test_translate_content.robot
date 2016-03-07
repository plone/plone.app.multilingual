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

Scenario: As an editor when I create a translation I see information on what I am translating
    Given a site owner
      and a document in English with Catalan translation
     When I start to translate the document into French
     Then I see information on the other existing translations


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
  Click Button  Save
  Wait until page contains  Item created

I start to translate the document into French
  Go to  ${PLONE_URL}/en/an-english-document/@@create_translation?language=fr

I switch to Catalan
  Click Link  Català
  Wait until page contains  A Catalan Document

# Then

I can view the document in Catalan
  Page Should Contain Element
  ...  xpath=//*[contains(@class, 'documentFirstHeading')][./text()='A Catalan Document']
  Page Should Contain Element
  ...  xpath=//ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='Català']

I see information on the other existing translations
  Element should be visible  css=.portalMessage.info #multilingual-add-form-is-translation
  # Element should contain  css=.portalMessage.info  This object is going to be a translation to Français
  Element should contain  css=.portalMessage.info  Cette élément est sur le point d'être traduit en Français à partir de :
  # Element should contain  css=.portalMessage.info  If you want to create this object without being a translation press here
  Element should contain  css=.portalMessage.info  Si vous souhaité créer cet élément sans rentrer dans le processus de traduction cliquez ici
  Element should contain  css=.portalMessage.info  English An English Document
  Element should contain  css=.portalMessage.info  Català A Catalan Document

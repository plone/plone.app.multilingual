*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: As a site owner I can see language independent field setting
    Given a site owner
      and a dexterity content type field settings form
     When I open the field settings
     Then I can see the language independent field setting

Scenario: As a site owner I can set field language independent
    Given a site owner
      and a dexterity content type field settings form
     When I select language independent field setting
      and I save the form
      and I open the form again
     Then the language independent field setting is selected

Scenario: As a site owner I can unset field from being language independent
    Given a site owner
      and a dexterity content type with a language independent field
      and a dexterity content type field settings form
     When I unselect language independent field setting
      and I save the form
      and I open the form again
     Then the language independent field setting is not selected


*** Keywords ***

# Given

a site owner
  Enable autologin as  Manager

a dexterity content type open in schema editor
  Go to  ${PLONE_URL}/dexterity-types/Document/@@fields
  Element should be visible  css=a.fieldSettings

a dexterity content type field settings form
  Go to  ${PLONE_URL}/dexterity-types/Document/@@fields
  Element should be visible  css=a.fieldSettings
  Click link  css=a.fieldSettings
  Wait until page contains  Edit Field 'text'

a dexterity content type with a language independent field
  Set field language independent  Document  text  on

# When

I Open the field settings
  Click link  css=a.fieldSettings
  Wait until page contains  Edit Field 'text'

I select language independent field setting
  Select checkbox  form-widgets-IFieldLanguageIndependent-languageindependent-0
  Checkbox should be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

I save the form
  Click button  form-buttons-save

I open the form again
  Click link  css=a.fieldSettings
  Wait until page contains  Edit Field 'text'

I unselect language independent field setting
  Unselect checkbox  form-widgets-IFieldLanguageIndependent-languageindependent-0
  Checkbox should not be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

# Then

I can see the language independent field setting
  Element should be visible  form-widgets-IFieldLanguageIndependent-languageindependent-0

the language independent field setting is selected
  Checkbox should be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

the language independent field setting is not selected
  Checkbox should not be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

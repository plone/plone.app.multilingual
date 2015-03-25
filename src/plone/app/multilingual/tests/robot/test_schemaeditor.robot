*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: As a site owner I can see language independent field setting
    Given a site owner
      and a dexterity content type with a TTW field
     When I open the field settings
     Then I can see the language independent field setting

Scenario: As a site owner I can set field language independent
    Given a site owner
      and a dexterity content type with a TTW field
     When I open the field settings
      and I select the language independent field setting
      and I save the form
      and I open the form again
     Then the language independent field setting is selected

Scenario: As a site owner I can unset field from being language independent
    Given a site owner
      and a dexterity content type with a language independent TTW field
     When I open the field settings
      and I unselect the language independent field setting
      and I save the form
      and I open the form again
     Then the language independent field setting is not selected


*** Keywords ***

# Given

a site owner
  Enable autologin as  Manager

a dexterity content type with a TTW field
  Create content type  Custom
  Go to  ${PLONE_URL}/dexterity-types/Custom/@@fields
  Wait until page contains element  css=body.template-fields

a dexterity content type field settings form
  Go to  ${PLONE_URL}/dexterity-types/Custom/@@fields
  Go to  ${PLONE_URL}/dexterity-types/Custom/custom
  Wait until page contains  Language independent field

a dexterity content type with a language independent TTW field
  Create content type  Custom
  Set field language independent  Custom  custom  on
  Go to  ${PLONE_URL}/dexterity-types/Custom/@@fields
  Wait until page contains element  css=body.template-fields

# When

I open the field settings
  Go to  ${PLONE_URL}/dexterity-types/Custom/custom
  Page should contain  Language independent field

I select the language independent field setting
  Select checkbox  form-widgets-IFieldLanguageIndependent-languageindependent-0
  Checkbox should be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

I save the form
  Wait until page contains element  css=#form-buttons-save
  Click button  css=#form-buttons-save
  Wait until keyword succeeds  1  10  Element should not be visible  .plone-modal-wrapper

I open the form again
  Go to  ${PLONE_URL}/dexterity-types/Custom/custom
  Wait until page contains  Language independent field

I unselect the language independent field setting
  Unselect checkbox  form-widgets-IFieldLanguageIndependent-languageindependent-0
  Checkbox should not be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

# Then

I can see the language independent field setting
  Wait until page contains element  id=form-widgets-IFieldLanguageIndependent-languageindependent-0

the language independent field setting is selected
  Checkbox should be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

the language independent field setting is not selected
  Checkbox should not be selected  form-widgets-IFieldLanguageIndependent-languageindependent-0

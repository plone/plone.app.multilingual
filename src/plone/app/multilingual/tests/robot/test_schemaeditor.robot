*** Settings ***

Resource    plone/app/robotframework/browser.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords    Plone test teardown

*** Test cases ***

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
    Enable autologin as    Manager

a dexterity content type with a TTW field
    Create content type    Custom
    Go to    ${PLONE_URL}/dexterity-types/Custom/@@fields
    Get Element    //body[contains(@class, "template-fields")]

a dexterity content type field settings form
    Go to    ${PLONE_URL}/dexterity-types/Custom/@@fields
    Go to    ${PLONE_URL}/dexterity-types/Custom/custom
    Get Text    //div[@id="form-widgets-IFieldLanguageIndependent-languageindependent"]    contains    Language independent field

a dexterity content type with a language independent TTW field
    Create content type    Custom
    Set field language independent    Custom    custom    on
    Go to    ${PLONE_URL}/dexterity-types/Custom/@@fields
    Get Element    //body[contains(@class, "template-fields")]

# When

I open the field settings
    Go to    ${PLONE_URL}/dexterity-types/Custom/custom
    Get Text    //div[@id="form-widgets-IFieldLanguageIndependent-languageindependent"]    contains    Language independent field

I select the language independent field setting
    Check Checkbox    //input[@id="form-widgets-IFieldLanguageIndependent-languageindependent-0"]
    Get Checkbox State    //input[@id="form-widgets-IFieldLanguageIndependent-languageindependent-0"]    ==    checked

I save the form
    Get Element    //*[@id="form-buttons-save"]
    Click    //*[@id="form-buttons-save"]
    Get Element Count    //div[contains(@class,"plone-modal-wrapper")]    should be    0

I open the form again
    Go to  ${PLONE_URL}/dexterity-types/Custom/custom
    Get Text    //div[@id="form-widgets-IFieldLanguageIndependent-languageindependent"]    contains    Language independent field

I unselect the language independent field setting
    Uncheck Checkbox    //input[@id="form-widgets-IFieldLanguageIndependent-languageindependent-0"]
    Get Checkbox State    //input[@id="form-widgets-IFieldLanguageIndependent-languageindependent-0"]    ==    unchecked

# Then

I can see the language independent field setting
    Get Element    //*[@id="form-widgets-IFieldLanguageIndependent-languageindependent-0"]

the language independent field setting is selected
    Get Checkbox State    //input[@id="form-widgets-IFieldLanguageIndependent-languageindependent-0"]    ==    checked

the language independent field setting is not selected
    Get Checkbox State    //input[@id="form-widgets-IFieldLanguageIndependent-languageindependent-0"]    ==    unchecked

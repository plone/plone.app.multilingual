*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: Babel View for DX content
    Given a site owner
     When I translate the content 'en/dxdoc' to 'es'
      And I switch the available translations language to 'Catalan'
     Then I get the 'CA doc' as title of the available translation information for DX


Scenario: Babel View for AT content
    Given a site owner
     When I translate the content 'en/atdoc' to 'es'
      And I switch the available translations language to 'Catalan'
     Then I get the 'CA doc' as title of the available translation information for AT


*** Keywords ***

a site owner
    Enable autologin as  Manager

I translate the content '${content_id}' to '${lang}'
    Go to  ${PLONE_URL}/${content_id}/@@create_translation?language=${lang}

I switch the available translations language to '${lang}'
    Click Element  name=button-${lang}

I get the '${lang-title}' as title of the available translation information for AT
    Wait Until Keyword Succeeds  5 sec  1 sec  Element Should Contain  xpath=//*[contains(@id, 'parent-fieldname-title')]  ${lang-title}

I get the '${lang-title}' as title of the available translation information for DX
    Wait Until Keyword Succeeds  5 sec  1 sec  Element Should Contain  id=form-widgets-IDublinCore-title  ${lang-title}

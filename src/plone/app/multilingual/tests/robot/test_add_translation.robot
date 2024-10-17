*** Settings ***

Resource    plone/app/robotframework/browser.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords    Plone test teardown

*** Test Cases ***

Scenario: As an editor I can add new translation
    Given a site owner
      and a document in English
      and a document in Catalan
     When I view the Catalan document
      and I link the document in English as a translation
      and I switch to English
     Then I can view the document in English


*** Keywords ***

# Given

a site owner
    Enable autologin as    Manager

a document in English
    Create content    type=Document    container=/${PLONE_SITE_ID}/en/    id=an-english-document    title=An English Document

a document in Catalan
    Create content    type=Document    container=/${PLONE_SITE_ID}/ca/    id=a-catalan-document    title=A Catalan Document

# When

I view the Catalan document
    Go to    ${PLONE_URL}/ca/a-catalan-document
    Get Element    //h1[1][text()='A Catalan Document']

I link the document in English as a translation
    Get Element    //li[@id="plone-contentmenu-multilingual"]/a
    Take Screenshot
    Get Element States    //li[@id="plone-contentmenu-multilingual"]/a     contains    visible
    Click    //li[@id="plone-contentmenu-multilingual"]/a
    Get Element States    //a[@id="_modify_translations"]     contains    visible
    Click    //a[@id="_modify_translations"]
    Click    //table[@id="translations-overview"]/tbody/tr[1]/td[3]/a[contains(@class,"connectTranslationAction")]
    Click    //div[@id="formfield-form-widgets-content"]//div[contains(@class,"pat-relateditems-container")]//button[contains(@class,"mode") and contains(@class,"search")]
    Type Text    //div[@id="formfield-form-widgets-content"]//input[contains(@class,"select2-input")]    en
    Click    //span[contains(., 'An English Document')]
    Click    //*[contains(@class, 'modal-footer')]//button[@id='form-buttons-connect_translation']
    Get Text    //table[@id="translations-overview"]/tbody/tr[1]/td[2]/h3[@class="translationTitle"]    should be    An English Document
    Click    //table[@id="translations-overview"]//a[contains(text(),'/plone/ca/a-catalan-document')]
    Get Text    //*[@id="content"]/header/h1    should be    A Catalan Document

I switch to English
    Click    //a[@title='English']
    Get Element    //h1[1][contains(text(),'An English Document')]

# Then

I can view the document in English
    Get Element    //h1[1][contains(text(),'English Document')]
    Get Element    //ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='English']

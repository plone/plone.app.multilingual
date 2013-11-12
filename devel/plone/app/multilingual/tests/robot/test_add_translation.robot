*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Add translation
    [Tags]  Plone5

    Given a site owner
     When I add new avaliable lang 'uk'
      And I go to 'en' catalog
   Create a document with  en  It is a test document
      And I go to 'uk' catalog
   Create a document with  uk  Це тестовий документ
    Click Element  css=#plone-contentmenu-multilingual .actionMenuHeader a
    Click Element  css=#_add_translations
    Click Element  css=#formfield-form-widgets-content-widgets-query .searchButton
    Wait until element is visible  css=#form-widgets-content-contenttree a[href$='/plone/en']
    Click Element  css=#form-widgets-content-contenttree a[href$='/plone/en']
    Wait until page contains  It is a test document
    Click link  xpath=//*[contains(text(), 'It is a test document')]/parent::a
    Click Element  css=.contentTreeAdd
    Select From List  name=form.widgets.language:list  en
    Click Element  css=#form-buttons-add_translations
    Click Element  css=#contentview-view a
    Click Element  css=.language-en a
    Wait until page contains  It is a test document
    Click Element  css=.language-uk a
    Wait until page contains  Це тестовий документ


*** Keywords ***

I add new avaliable lang '${lang}'
    Go to  ${PLONE_URL}/@@language-controlpanel
    Select From List  name=form.available_languages.from  ${lang}
    Click Element  name=from2toButton
    Click Element  name=form.actions.save

Create a document with
  [Arguments]  ${lang}  ${title}
  Go to  ${PLONE_URL}/${lang}/createObject?type_name=Document
  Element should be visible  form.widgets.IDublinCore.title
  Input text  form.widgets.IDublinCore.title  ${title}
  Click Button  Save

I go to '${lang}' catalog
    Go to  ${PLONE_URL}/${lang}

a site owner
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

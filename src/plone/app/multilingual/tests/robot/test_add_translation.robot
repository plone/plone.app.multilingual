*** Settings ***

Variables  plone/app/testing/interfaces.py
Variables  plone/app/multilingual/tests/robot/variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

# Resource  library-settings.txt
Resource  plone/app/multilingual/tests/robot/keywords.txt

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown

*** Test Cases ***

Add translation
    Given a site owner
     When I add new avaliable lang 'uk'
      And I go to 'en' catalog
   Create a document with  en  It is a test document
      And I go to 'uk' catalog
   Create a document with  uk  Це тестовий документ
    Click Element  css=#plone-contentmenu-multilingual .actionMenuHeader a
    Click Element  css=#_add_translations
    Click Element  css=#formfield-form-widgets-content-widgets-query .searchButton 
    Click Element  css=#form-widgets-content-contenttree a[href$='/plone/en']
    Wait until page contains  It is a test document
    Click Element  css=#form-widgets-content-contenttree a[href$='it-is-a-test-document']
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
  Input text  css=#title  ${title}
  Click Button  Save

I go to '${lang}' catalog
    Go to  ${PLONE_URL}/${lang}

a site owner
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

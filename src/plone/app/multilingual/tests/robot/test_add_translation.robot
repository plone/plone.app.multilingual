*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Scenario: As an editor I can add new translation
    Given a site owner
      and a document in English
      and a document in Catalan
     When I view the Catalan document
      and I add the document in English as a translation
      and I switch to English
     Then I can view the document in English


*** Keywords ***

# Given

a site owner
  Enable autologin as  Manager

a document in English
  Create content  type=Document
  ...  container=/${PLONE_SITE_ID}/en/
  ...  id=an-english-document
  ...  title=An English Document

a document in Catalan
  Create content  type=Document
  ...  container=/${PLONE_SITE_ID}/ca/
  ...  id=a-catalan-document
  ...  title=A Catalan Document

# When

I view the Catalan document
  Go to  ${PLONE_URL}/ca/a-catalan-document
  Wait until page contains  A Catalan Document

I add the document in English as a translation
  Click Element  css=#plone-contentmenu-multilingual .actionMenuHeader a
  Wait until element is visible  css=#_add_translations

  Click Element  css=#_add_translations
  Wait until page contains element
  ...  css=#formfield-form-widgets-content-widgets-query .searchButton

  Click Element  css=#formfield-form-widgets-content-widgets-query .searchButton
  Wait until element is visible  css=#form-widgets-content-contenttree a[href$='/plone/en']

  # Record whether contenttree loads expanded or collapsed in case the Click Link below fails (see #204) 
  Capture Page Screenshot
  # contenttree could load expanded or collapsed - so only try to open if it's collapsed
  Run Keyword And Ignore Error
  ...  Click Element  css=#form-widgets-content-contenttree .navTreeItem.collapsed a[href$='/plone/en']

  Wait until page contains  An English Document
  Wait until element is visible  xpath=//*[contains(text(), 'An English Document')]/parent::a
  # Record what the above keyword passed in case the Click Link below fails (see #204)
  Capture Page Screenshot

  Click link  xpath=//*[contains(text(), 'An English Document')]/parent::a
  Click Element  css=.contentTreeAdd

  Select From List  name=form.widgets.language:list  en
  Click Element  css=#form-buttons-add_translations
  Click Element  css=#contentview-view a
  Wait until page contains  A Catalan Document

I switch to English
  Click Link  xpath=//a[@title='English']
  Wait until page contains  An English Document

# Then

I can view the document in English
  Wait until page contains element
  ...  xpath=//*[contains(@class, 'documentFirstHeading')][./text()='An English Document']
  Wait until page contains element
  ...  xpath=//ul[@id='portal-languageselector']/li[contains(@class, 'currentLanguage')]/a[@title='English']

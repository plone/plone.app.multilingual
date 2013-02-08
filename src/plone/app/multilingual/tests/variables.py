import os

from plone.app.testing.interfaces import PLONE_SITE_ID

PORT = 55001
if 'ZSERVER_PORT' in os.environ:
    PORT = os.environ["ZSERVER_PORT"]

ZOPE_URL = "http://localhost:%s" % PORT
PLONE_URL = "%s/%s" % (ZOPE_URL, PLONE_SITE_ID)
BROWSER = "Firefox"
REMOTE_URL = ""
DESIRED_CAPABILITIES = ""
TEST_FOLDER = "%s/acceptance-test-folder"

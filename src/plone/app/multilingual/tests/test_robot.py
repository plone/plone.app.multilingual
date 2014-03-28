# -*- coding: utf-8 -*-
import unittest

import robotsuite

from plone.app.multilingual.testing import PAM_ROBOT_TESTING
from plone.testing import layered


UNIT_TEST_LEVEL = 1
INTEGRATION_TEST_LEVEL = 2
FUNCTIONAL_TEST_LEVEL = 3
ROBOT_TEST_LEVEL = 5


def test_suite():
    suite = unittest.TestSuite()
    suite.level = ROBOT_TEST_LEVEL
    suite.addTests([
        layered(robotsuite.RobotTestSuite('robot'), layer=PAM_ROBOT_TESTING),
    ])
    return suite

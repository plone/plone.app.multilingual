from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_ROBOT_TESTING
from plone.testing import layered

import os
import robotsuite
import unittest

UNIT_TEST_LEVEL = 1
INTEGRATION_TEST_LEVEL = 2
FUNCTIONAL_TEST_LEVEL = 3
ROBOT_TEST_LEVEL = 5


def test_suite():
    suite = unittest.TestSuite()
    suite.level = ROBOT_TEST_LEVEL
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in
        os.listdir(robot_dir) if doc.endswith('.robot') and
        doc.startswith('test_')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(test),
                    layer=PLONEAPPMULTILINGUAL_ROBOT_TESTING),
        ])
    return suite

# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_ROBOT_TESTING

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('robot'),
                layer=PLONEAPPMULTILINGUAL_ROBOT_TESTING),
    ])
    return suite

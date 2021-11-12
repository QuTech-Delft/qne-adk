import re
import unittest

from adk import version

class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertTrue(re.match(r"^\d+\.\d+\.\d+$", version.__version__))

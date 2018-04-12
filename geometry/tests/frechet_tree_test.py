import json
import unittest

from geometry.utils.tree_reader import create_tree


class TestFrechetTree(unittest.TestCase):

    def setUp(self):
        self.error = 1.0
        self.delta = 1.0
        self.tree = create_tree(json.load(open('trees/tree_a.json')))

    def test_nothing(self):
        pass

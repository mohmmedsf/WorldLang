import unittest
from next_syntax.analyzer import analyze

class AnalyzerTests(unittest.TestCase):
    def codes(self, source):
        return [item.code for item in analyze(source)]

    def test_valid_function(self):
        self.assertEqual(self.codes('دالة جمع(أ، ب)\n    أرجع أ + ب\nاطبع جمع(1، 2)'), [])

    def test_unknown_function(self):
        self.assertIn('E_UNKNOWN_FUNCTION', self.codes('اطبع غير_موجود(1)'))

    def test_wrong_arity(self):
        self.assertIn('E_ARITY', self.codes('دالة جمع(أ، ب)\n    أرجع أ + ب\nاطبع جمع(1)'))

    def test_duplicate_function(self):
        self.assertIn('E_DUPLICATE_FUNCTION', self.codes('دالة عمل()\n    أرجع 1\nدالة عمل()\n    أرجع 2'))

    def test_return_outside(self):
        self.assertIn('E_RETURN_OUTSIDE', self.codes('أرجع 3'))

if __name__ == '__main__':
    unittest.main()

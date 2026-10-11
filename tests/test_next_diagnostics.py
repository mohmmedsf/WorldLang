import unittest
from next_syntax.diagnostics import syntax_diagnostic

class DiagnosticsTests(unittest.TestCase):
    def test_valid_source(self):
        self.assertIsNone(syntax_diagnostic('اطبع 1'))

    def test_unexpected_token(self):
        d = syntax_diagnostic('اطبع @')
        self.assertIsNotNone(d)
        self.assertEqual(d.line, 1)
        self.assertIn('اطبع @', d.render())

    def test_indentation_error(self):
        d = syntax_diagnostic('إذا صحيح\n    اطبع 1\n  اطبع 2')
        self.assertIsNotNone(d)
        self.assertEqual(d.line, 3)

    def test_missing_expression(self):
        d = syntax_diagnostic('اطبع')
        self.assertIsNotNone(d)
        self.assertEqual(d.code, 'E_SYNTAX')

if __name__ == '__main__':
    unittest.main()

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from next_syntax.__main__ import main
from next_syntax.runtime import run, RuntimeErrorNext

class IntegrationHardeningTests(unittest.TestCase):
    def cli(self, command, source):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'test.wln'
            path.write_text(source, encoding='utf-8')
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = main([command, str(path)])
            return status, stdout.getvalue(), stderr.getvalue()

    def test_index_after_binary_expression(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'Invalid operation'):
            run('اطبع [1، 2] + [3، 4][0]')

    def test_index_after_parenthesized_binary(self):
        self.assertEqual(run('اطبع ([1، 2] + [3، 4])[2]').output, ['3'])

    def test_check_rejects_unknown_function(self):
        status, out, err = self.cli('check', 'اطبع مجهولة(1)')
        self.assertEqual(status, 1)
        self.assertIn('E_UNKNOWN_FUNCTION', err)

    def test_lint_rejects_wrong_arity(self):
        status, out, err = self.cli('lint', 'دالة جمع(أ، ب)\n    أرجع أ + ب\nاطبع جمع(1)')
        self.assertEqual(status, 1)
        self.assertIn('E_ARITY', err)

    def test_lint_valid(self):
        status, out, err = self.cli('lint', 'اطبع 2 + 3')
        self.assertEqual(status, 0)
        self.assertIn('OK:', out)

    def test_check_syntax_pointer(self):
        status, out, err = self.cli('check', 'اطبع @')
        self.assertEqual(status, 1)
        self.assertIn('E_SYNTAX', err)
        self.assertIn('^', err)

if __name__ == '__main__':
    unittest.main()

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from next_syntax.__main__ import main

class CliTests(unittest.TestCase):
    def run_cli(self, command, source):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'example.wln'
            file.write_text(source, encoding='utf-8')
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                status = main([command, str(file)])
            return status, out.getvalue(), err.getvalue()

    def test_run(self):
        status, out, err = self.run_cli('run', 'اطبع 2 + 3')
        self.assertEqual((status, out), (0, '5\n'))

    def test_check(self):
        status, out, err = self.run_cli('check', 'اطبع 1')
        self.assertEqual(status, 0)
        self.assertIn('OK:', out)

    def test_tokens(self):
        status, out, err = self.run_cli('tokens', 'اطبع 1')
        self.assertEqual(status, 0)
        self.assertIn('PRINT', out)

    def test_invalid_source(self):
        status, out, err = self.run_cli('run', 'اطبع مجهول')
        self.assertEqual(status, 1)
        self.assertIn('Undefined variable', err)

if __name__ == '__main__':
    unittest.main()

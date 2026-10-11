import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from next_syntax.__main__ import main

class VMCLITests(unittest.TestCase):
    def test_compile_and_execute_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'sample.wl'
            source.write_text('اجعل س = [1، 2]\nلكل عنصر في س:\n    اطبع عنصر', encoding='utf-8')
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(['compile', str(source)]), 0)
            artifact = source.with_suffix('.wbc.json')
            self.assertTrue(artifact.exists())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(['vm', str(artifact)]), 0)
            self.assertEqual(output.getvalue().splitlines(), ['1', '2'])

    def test_vm_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'sample.wl'
            source.write_text('اطبع 2 + 3', encoding='utf-8')
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(['vm', str(source)]), 0)
            self.assertEqual(out.getvalue().strip(), '5')

if __name__ == '__main__':
    unittest.main()

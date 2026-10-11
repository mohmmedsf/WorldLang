import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from next_syntax.__main__ import main

class JSONToolingTests(unittest.TestCase):
    def invoke(self, command, source):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'program.wl'
            path.write_text(source, encoding='utf-8')
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = main([command, str(path)])
            return status, json.loads(output.getvalue())

    def test_ast_json(self):
        status, payload = self.invoke('ast-json', 'اطبع 2')
        self.assertEqual(status, 0)
        self.assertEqual(payload['schema'], 'worldlang.next.ast')

    def test_clean_diagnostics(self):
        status, payload = self.invoke('diagnostics-json', 'اطبع 2')
        self.assertEqual(status, 0)
        self.assertEqual(payload['diagnostics'], [])

    def test_syntax_diagnostics(self):
        status, payload = self.invoke('diagnostics-json', 'اطبع @')
        self.assertEqual(status, 1)
        self.assertEqual(payload['diagnostics'][0]['code'], 'SYNTAX')

if __name__ == '__main__':
    unittest.main()

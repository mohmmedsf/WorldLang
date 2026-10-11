import unittest
from next_syntax.bytecode import Bytecode, compile_source, execute, validate
from next_syntax.runtime import RuntimeErrorNext
from next_syntax.editor import diagnostics
from next_syntax.lsp import diagnostic_items

class LimitsAndRangesTests(unittest.TestCase):
    def test_bytecode_invalid_json(self):
        with self.assertRaises(ValueError):
            Bytecode.from_json('{broken')

    def test_bytecode_size_limit(self):
        with self.assertRaisesRegex(ValueError, 'large'):
            Bytecode.from_json(' ' * 4_000_001)

    def test_instruction_limit(self):
        with self.assertRaisesRegex(ValueError, 'many'):
            validate(Bytecode(1, (('PUSH', 1),) * 100_001))

    def test_output_limit(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'Output'):
            execute(compile_source('اطبع 1\nاطبع 2'), max_output_lines=1)

    def test_call_depth_validation(self):
        with self.assertRaises(ValueError):
            execute(compile_source('اطبع 1'), max_call_depth=1)

    def test_source_error_line_and_column(self):
        source = 'اطبع 1\nاطبع @'
        item = diagnostics(source)[0]
        self.assertEqual(item['line'], 2)
        self.assertEqual(item['column'], 6)
        lsp = diagnostic_items(source)[0]['range']['start']
        self.assertEqual(lsp, {'line': 1, 'character': 5})

if __name__ == '__main__':
    unittest.main()

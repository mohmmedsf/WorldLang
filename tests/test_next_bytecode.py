import unittest
from next_syntax.bytecode import Bytecode, compile_source, execute, validate
from next_syntax.runtime import run, RuntimeErrorNext

class BytecodeTests(unittest.TestCase):
    def test_arithmetic_matches_interpreter(self):
        source = 'اجعل س = 2 + 3 * 4\nاطبع س'
        self.assertEqual(execute(compile_source(source))['output'], run(source).output)

    def test_roundtrip_json_arabic(self):
        module = compile_source('اجعل قيمة = 7\nاطبع قيمة')
        decoded = Bytecode.from_json(module.to_json())
        self.assertEqual(execute(decoded)['output'], ['7'])

    def test_reject_unknown_opcode(self):
        with self.assertRaises(ValueError):
            validate(Bytecode(1, (('EVAL', None),)))

    def test_reject_stack_underflow(self):
        with self.assertRaises(ValueError):
            validate(Bytecode(1, (('PRINT', None),)))

    def test_reject_unbalanced_stack(self):
        with self.assertRaises(ValueError):
            validate(Bytecode(1, (('PUSH', 1),)))

    def test_reject_unsupported_function(self):
        with self.assertRaises(ValueError):
            compile_source('دالة فحص():\n    أرجع 1')

    def test_reject_unsupported_boolean_short_circuit(self):
        with self.assertRaises(ValueError):
            compile_source('اطبع صحيح و خطأ')

    def test_step_limit(self):
        with self.assertRaises(RuntimeErrorNext):
            execute(compile_source('اطبع 1\nاطبع 2'), max_steps=1)

    def test_undefined_variable(self):
        with self.assertRaises(RuntimeErrorNext):
            execute(compile_source('اطبع مجهول'))

if __name__ == '__main__':
    unittest.main()

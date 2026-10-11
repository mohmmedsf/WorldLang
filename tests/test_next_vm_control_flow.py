import unittest
from next_syntax.bytecode import Bytecode, compile_source, execute, validate
from next_syntax.runtime import run, RuntimeErrorNext

class VMControlFlowTests(unittest.TestCase):
    def parity(self, source):
        module = Bytecode.from_json(compile_source(source).to_json())
        self.assertEqual(execute(module)['output'], run(source).output)

    def test_if_else(self):
        self.parity('اجعل س = 3\nإذا س > 2:\n    اطبع "yes"\nوإلا:\n    اطبع "no"')

    def test_if_elif(self):
        self.parity('اجعل س = 2\nإذا س > 3:\n    اطبع 1\nوإلا إذا س > 1:\n    اطبع 2\nوإلا:\n    اطبع 3')

    def test_while(self):
        self.parity('اجعل س = 0\nطالما س < 3:\n    اطبع س\n    س = س + 1')

    def test_repeat(self):
        self.parity('كرر 3 مرات:\n    اطبع 7')

    def test_nested(self):
        self.parity('اجعل س = 0\nكرر 2 مرات:\n    طالما س < 2:\n        اطبع س\n        س = س + 1')

    def test_loop_limit(self):
        module = compile_source('طالما صحيح:\n    اطبع 1')
        with self.assertRaisesRegex(RuntimeErrorNext, 'step limit'):
            execute(module, max_steps=20)

    def test_reject_invalid_jump(self):
        with self.assertRaisesRegex(ValueError, 'jump target'):
            validate(Bytecode(1, (('JUMP', 100),)))

    def test_roundtrip(self):
        source = 'كرر 2 مرات:\n    اطبع "مرحبا"'
        module = Bytecode.from_json(compile_source(source).to_json())
        self.assertEqual(execute(module)['output'], ['مرحبا', 'مرحبا'])

if __name__ == '__main__':
    unittest.main()

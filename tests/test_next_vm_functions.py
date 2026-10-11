import unittest
from next_syntax.bytecode import Bytecode, compile_source, execute
from next_syntax.runtime import run, RuntimeErrorNext

class VMFunctionTests(unittest.TestCase):
    def parity(self, source):
        module = Bytecode.from_json(compile_source(source).to_json())
        self.assertEqual(execute(module)['output'], run(source).output)

    def test_simple_function(self):
        self.parity('دالة جمع(س، ص):\n    أرجع س + ص\nاطبع جمع(3، 4)')

    def test_local_scope(self):
        self.parity('اجعل س = 10\nدالة ف(س):\n    س = س + 1\n    أرجع س\nاطبع ف(2)\nاطبع س')

    def test_nested_calls(self):
        self.parity('دالة ضعف(س):\n    أرجع س * 2\nدالة مجموع(س):\n    أرجع ضعف(س) + 1\nاطبع مجموع(4)')

    def test_zero_args(self):
        self.parity('دالة رقم():\n    أرجع 42\nاطبع رقم()')

    def test_wrong_arity(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'Incorrect argument count'):
            execute(compile_source('دالة ف(س):\n    أرجع س\nاطبع ف()'))

    def test_undefined_function(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'Undefined function'):
            execute(compile_source('اطبع غير_معروفة(2)'))

    def test_recursion_depth_limit(self):
        source = 'دالة ف(س):\n    أرجع ف(س + 1)\nاطبع ف(1)'
        with self.assertRaisesRegex(RuntimeErrorNext, 'depth limit'):
            execute(compile_source(source), max_steps=100000)

if __name__ == '__main__':
    unittest.main()

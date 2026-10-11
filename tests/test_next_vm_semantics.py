import unittest
from next_syntax.bytecode import Bytecode, compile_source, execute
from next_syntax.runtime import run

class VMSemanticsTests(unittest.TestCase):
    def parity(self, source):
        module = Bytecode.from_json(compile_source(source).to_json())
        self.assertEqual(execute(module)['output'], run(source).output)

    def test_and_true(self):
        self.parity('اطبع صحيح و صحيح')

    def test_and_false_skips_undefined(self):
        self.parity('اطبع خطأ و غير_معروف')

    def test_or_true_skips_undefined(self):
        self.parity('اطبع صحيح أو غير_معروف')

    def test_or_false(self):
        self.parity('اطبع خطأ أو صحيح')

    def test_nested_short_circuit(self):
        self.parity('اطبع (خطأ أو صحيح) و صحيح')

    def test_function_implicit_none(self):
        self.parity('دالة ف():\n    اجعل س = 3\nاطبع ف()')

    def test_json_null_roundtrip(self):
        module = Bytecode(1, (('PUSH', None), ('PRINT', None)))
        self.assertEqual(execute(Bytecode.from_json(module.to_json()))['output'], ['None'])

if __name__ == '__main__':
    unittest.main()

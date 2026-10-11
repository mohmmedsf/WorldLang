import unittest
from next_syntax.parser import parse
from next_syntax.runtime import run
from next_syntax.bytecode import compile_source, execute, Bytecode

class DifferentialMatrixTests(unittest.TestCase):
    CASES = [
        'اطبع 1 + 2 * 3',
        'اطبع (1 + 2) * 3',
        'اطبع صحيح و خطأ',
        'اطبع خطأ أو صحيح',
        'اطبع خطأ و غير_موجود',
        'اطبع صحيح أو غير_موجود',
        'اجعل س = [1، 2، 3]\nاطبع س[1]',
        'لكل س في [1، 2، 3]:\n    اطبع س * 2',
        'اجعل س = 0\nطالما س < 3:\n    اطبع س\n    س = س + 1',
        'دالة مربع(س):\n    أرجع س * س\nاطبع مربع(5)',
        'كرر 3 مرات:\n    اطبع 7',
        'إذا صحيح:\n    اطبع 1\nوإلا:\n    اطبع 2',
    ]
    def test_ast_vs_json_vm(self):
        for source in self.CASES:
            with self.subTest(source=source):
                parse(source)
                expected = run(source).output
                bytecode = Bytecode.from_json(compile_source(source).to_json())
                self.assertEqual(execute(bytecode)['output'], expected)

if __name__ == '__main__':
    unittest.main()

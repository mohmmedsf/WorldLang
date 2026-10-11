import unittest
from next_syntax.bytecode import Bytecode, compile_source, execute, validate

class CFGVerifierTests(unittest.TestCase):
    def test_reject_branch_join_stack_mismatch(self):
        code = (('PUSH', True), ('JUMP_IF_FALSE', 4), ('PUSH', 7), ('JUMP', 5), ('JUMP', 5), ('PRINT', None))
        with self.assertRaisesRegex(ValueError, 'stack'):
            validate(Bytecode(1, code))

    def test_reject_back_edge_stack_growth(self):
        with self.assertRaisesRegex(ValueError, 'stack'):
            validate(Bytecode(1, (('PUSH', 1), ('JUMP', 0))))

    def test_reject_underflow_on_branch(self):
        code = (('PUSH', False), ('JUMP_IF_FALSE', 3), ('PUSH', 1), ('PRINT', None))
        with self.assertRaisesRegex(ValueError, 'Stack underflow'):
            validate(Bytecode(1, code))

    def test_valid_nested_control_flow(self):
        src = 'اجعل س = 0\nكرر 2 مرات:\n    طالما س < 2:\n        اطبع س\n        س = س + 1'
        self.assertEqual(execute(compile_source(src))['output'], ['0', '1'])

    def test_valid_foreach_function(self):
        src = 'دالة ضعف(س):\n    أرجع س * 2\nلكل س في [1، 2]:\n    اطبع ضعف(س)'
        self.assertEqual(execute(compile_source(src))['output'], ['2', '4'])

if __name__ == '__main__':
    unittest.main()

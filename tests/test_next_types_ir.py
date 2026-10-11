import unittest
from next_syntax.typesys import check_types
from next_syntax.ir import IRModule, IRInstruction, lower, validate

class TypesAndIRTests(unittest.TestCase):
    def codes(self, source):
        return [issue.code for issue in check_types(source)]

    def test_valid_numeric(self):
        self.assertEqual(self.codes('اجعل س = 2 + 3\nاطبع س'), [])

    def test_invalid_string_plus_int(self):
        self.assertIn('E_BINARY_TYPE', self.codes('اطبع "x" + 2'))

    def test_invalid_index(self):
        self.assertIn('E_INDEX_TYPE', self.codes('اطبع [1، 2]["x"]'))

    def test_non_indexable(self):
        self.assertIn('E_NOT_INDEXABLE', self.codes('اطبع 10[0]'))

    def test_boolean_is_not_integer(self):
        self.assertIn('E_BINARY_TYPE', self.codes('اطبع صحيح + 2'))

    def test_ir_lower(self):
        module = lower('اطبع 3')
        self.assertEqual(module.version, 1)
        self.assertEqual(module.instructions[0].opcode, 'PRINT')
        self.assertTrue(validate(module))

    def test_invalid_ir_version(self):
        with self.assertRaisesRegex(ValueError, 'version'):
            validate(IRModule(99, ()))

    def test_invalid_opcode(self):
        with self.assertRaisesRegex(ValueError, 'instruction'):
            validate(IRModule(1, (IRInstruction('EVAL', (1,)),)))

if __name__ == '__main__':
    unittest.main()

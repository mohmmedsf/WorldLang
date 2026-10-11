import unittest
from next_syntax.bytecode import Bytecode, validate

class BytecodeHardeningTests(unittest.TestCase):
    def test_reject_unknown_boolean_binary(self):
        with self.assertRaises(ValueError):
            validate(Bytecode(1, (('PUSH', 1), ('PUSH', 2), ('BINARY', 'AND'), ('PRINT', None))))

    def test_reject_unhashable_opcode(self):
        with self.assertRaises(ValueError):
            Bytecode.from_json('{"version":1,"code":[[[],null]]}')

    def test_reject_malformed_instruction(self):
        with self.assertRaises(ValueError):
            Bytecode.from_json('{"version":1,"code":[42]}')

    def test_reject_unhashable_binary_operator(self):
        with self.assertRaises(ValueError):
            Bytecode.from_json('{"version":1,"code":[["PUSH",1],["PUSH",2],["BINARY",[]],["PRINT",null]]}')

if __name__ == '__main__':
    unittest.main()

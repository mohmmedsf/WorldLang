import unittest
from next_syntax.typed_ir import lower, dumps, loads, to_bytecode
from next_syntax.bytecode import execute

class TypedIRTests(unittest.TestCase):
    def test_roundtrip_and_execution(self):
        source = 'دالة ضعف(س):\n    أرجع س * 2\nاطبع ضعف(3)'
        module = loads(dumps(lower(source)))
        self.assertEqual(execute(to_bytecode(module))['output'], ['6'])

    def test_reject_invalid_opcode(self):
        with self.assertRaises(ValueError):
            loads('{"schema":"worldlang.next.typed-stack-ir","version":1,"instructions":[{"opcode":"EVAL","operand_kind":"none","operand":null}]}')

    def test_reject_wrong_version(self):
        with self.assertRaises(ValueError):
            loads('{"schema":"worldlang.next.typed-stack-ir","version":2,"instructions":[]}')

    def test_reject_wrong_operand_kind(self):
        with self.assertRaises(ValueError):
            loads('{"schema":"worldlang.next.typed-stack-ir","version":1,"instructions":[{"opcode":"PRINT","operand_kind":"address","operand":null}]}')

if __name__ == '__main__':
    unittest.main()

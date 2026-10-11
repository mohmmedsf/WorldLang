import unittest
from next_syntax.parser import parse
from next_syntax.ast_json import dumps, loads

class ASTJSONTests(unittest.TestCase):
    def test_roundtrip_nested_program(self):
        source = 'دالة ضعف(س):\n    أرجع س * 2\nلكل س في [1، 2]:\n    اذا س > 1:\n        اطبع ضعف(س)'
        program = parse(source)
        self.assertEqual(loads(dumps(program)), program)

    def test_deterministic_serialization(self):
        program = parse('اطبع 3 + 4')
        self.assertEqual(dumps(program), dumps(loads(dumps(program))))

    def test_reject_unknown_node(self):
        with self.assertRaises(ValueError):
            loads('{"schema":"worldlang.next.ast","version":1,"program":{"node":"EVAL","fields":{}}}')

    def test_reject_wrong_version(self):
        with self.assertRaises(ValueError):
            loads('{"schema":"worldlang.next.ast","version":2,"program":null}')

    def test_reject_non_program_root(self):
        with self.assertRaises(ValueError):
            loads('{"schema":"worldlang.next.ast","version":1,"program":7}')

if __name__ == '__main__':
    unittest.main()

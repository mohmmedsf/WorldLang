import unittest
from next_syntax.bytecode import Bytecode, compile_source, execute
from next_syntax.runtime import run, RuntimeErrorNext

class VMCollectionsTests(unittest.TestCase):
    def parity(self, source):
        module = Bytecode.from_json(compile_source(source).to_json())
        self.assertEqual(execute(module)['output'], run(source).output)

    def test_list_literal(self):
        self.parity('اطبع [1، 2، 3]')

    def test_indexing(self):
        self.parity('اجعل س = [3، 4، 5]\nاطبع س[1]')

    def test_nested_index(self):
        self.parity('اطبع [[1، 2]، [3، 4]][1][0]')

    def test_foreach_sum(self):
        self.parity('اجعل مجموع = 0\nلكل عنصر في [1، 2، 3]:\n    مجموع = مجموع + عنصر\nاطبع مجموع')

    def test_foreach_string(self):
        self.parity('لكل حرف في "abc":\n    اطبع حرف')

    def test_foreach_nested(self):
        self.parity('لكل س في [1، 2]:\n    لكل ص في [3، 4]:\n        اطبع س * ص')

    def test_foreach_empty(self):
        self.parity('لكل س في []:\n    اطبع س\nاطبع 9')

    def test_bad_index(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'Index must be an integer'):
            execute(compile_source('اطبع [1، 2]["a"]'))

    def test_bad_iterable(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'For-each requires'):
            execute(compile_source('لكل س في 5:\n    اطبع س'))

if __name__ == '__main__':
    unittest.main()

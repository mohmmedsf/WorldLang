import unittest
from next_syntax.runtime import run, RuntimeErrorNext
from next_syntax.lexer import SyntaxErrorNext

class ForeachIndexingTests(unittest.TestCase):
    def test_foreach_sum(self):
        result = run('قيم = [2، 3، 5]\nمجموع = 0\nلكل عنصر في قيم\n    مجموع = مجموع + عنصر\nاطبع مجموع')
        self.assertEqual(result.output, ['10'])

    def test_index_zero(self):
        self.assertEqual(run('قيم = [7، 8]\nاطبع قيم[0]').output, ['7'])

    def test_negative_index(self):
        self.assertEqual(run('قيم = [7، 8]\nاطبع قيم[-1]').output, ['8'])

    def test_string_index(self):
        self.assertEqual(run('اطبع "abc"[1]').output, ['b'])

    def test_index_out_of_range(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'out of range'):
            run('اطبع [1][5]')

    def test_index_type(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'integer'):
            run('اطبع [1]["x"]')

    def test_foreach_non_iterable(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'list or string'):
            run('لكل عنصر في 10\n    اطبع عنصر')

    def test_foreach_step_limit(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'step limit'):
            run('لكل عنصر في [1، 2، 3]\n    اطبع عنصر', max_steps=4)

    def test_missing_for_in(self):
        with self.assertRaises(SyntaxErrorNext):
            run('لكل عنصر [1، 2]\n    اطبع عنصر')

    def test_nested_indexing(self):
        self.assertEqual(run('قيم = [[1، 2]، [3، 4]]\nاطبع قيم[1][0]').output, ['3'])

if __name__ == '__main__':
    unittest.main()

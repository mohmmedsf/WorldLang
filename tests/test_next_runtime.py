import unittest
from next_syntax.runtime import run, RuntimeErrorNext

class NextRuntimeTests(unittest.TestCase):
    def test_natural_and_compact_execute_equally(self):
        natural = 'اجعل العمر يساوي 20\nإذا كان العمر أكبر من أو يساوي 18\n    اطبع "بالغ"\nوإلا\n    اطبع "قاصر"'
        compact = 'العمر = 20\nإذا العمر >= 18\n    اطبع "بالغ"\nوإلا\n    اطبع "قاصر"'
        self.assertEqual(run(natural), run(compact))
        self.assertEqual(run(natural).output, ['بالغ'])

    def test_else_branch(self):
        result = run('العمر = 16\nإذا العمر >= 18\n    اطبع "بالغ"\nوإلا\n    اطبع "قاصر"')
        self.assertEqual(result.output, ['قاصر'])

    def test_arithmetic_precedence(self):
        result = run('س = 10 + 5 * 2\nص = (10 + 5) * 2\nاطبع س\nاطبع ص')
        self.assertEqual(result.output, ['20', '30'])

    def test_nested_conditions(self):
        result = run('س = 7\nإذا س > 3\n    إذا س < 9\n        اطبع "وسط"')
        self.assertEqual(result.output, ['وسط'])

    def test_elif_branch(self):
        result = run('س = 3\nإذا س > 5\n    اطبع "أ"\nوإلا إذا س > 2\n    اطبع "ب"\nوإلا\n    اطبع "ج"')
        self.assertEqual(result.output, ['ب'])

    def test_undefined_variable(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'Undefined variable'):
            run('اطبع غير_معرف')

    def test_divide_by_zero(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'Invalid operation'):
            run('اطبع 1 / 0')

    def test_short_circuit_or(self):
        result = run('إذا 1 == 1 أو غير_معرف > 0\n    اطبع "نجح"')
        self.assertEqual(result.output, ['نجح'])

    def test_step_limit(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'step limit'):
            run('اطبع 1', max_steps=1)

    def test_strings_preserved(self):
        self.assertEqual(run('اطبع "إذا كان العمر أكبر من"').output, ['إذا كان العمر أكبر من'])

if __name__ == '__main__':
    unittest.main()

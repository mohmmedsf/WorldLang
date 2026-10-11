import unittest
from next_syntax.runtime import run, RuntimeErrorNext
from next_syntax.parser import parse
from next_syntax.lexer import SyntaxErrorNext

class ExtendedRuntimeTests(unittest.TestCase):
    def test_function_return(self):
        source = 'دالة جمع(أ، ب)\n    أرجع أ + ب\nاطبع جمع(4، 6)'
        self.assertEqual(run(source).output, ['10'])

    def test_local_parameters(self):
        result = run('س = 8\nدالة ضاعف(س)\n    أرجع س * 2\nاطبع ضاعف(3)\nاطبع س')
        self.assertEqual(result.output, ['6', '8'])

    def test_while_loop(self):
        result = run('س = 0\nطالما س < 3\n    س = س + 1\nاطبع س')
        self.assertEqual(result.output, ['3'])

    def test_repeat_loop(self):
        result = run('س = 0\nكرر 4 مرات\n    س = س + 2\nاطبع س')
        self.assertEqual(result.output, ['8'])

    def test_list_literal(self):
        result = run('قيم = [1، 2، 3]')
        self.assertEqual(result.variables['قيم'], [1, 2, 3])

    def test_boolean_literal(self):
        self.assertEqual(run('إذا صحيح\n    اطبع "نعم"').output, ['نعم'])

    def test_wrong_arity(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'argument count'):
            run('دالة جمع(أ، ب)\n    أرجع أ + ب\nاطبع جمع(1)')

    def test_return_outside_function(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'outside function'):
            run('أرجع 1')

    def test_repeat_negative(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'nonnegative'):
            run('كرر -1 مرات\n    اطبع 1')

    def test_while_step_limit(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'step limit'):
            run('طالما صحيح\n    اطبع 1', max_steps=30)

    def test_function_recursion_limit(self):
        with self.assertRaisesRegex(RuntimeErrorNext, 'depth limit'):
            run('دالة دور(س)\n    أرجع دور(س)\nاطبع دور(1)', max_call_depth=4)

    def test_duplicate_parameter(self):
        with self.assertRaisesRegex(SyntaxErrorNext, 'Duplicate'):
            parse('دالة خطأ(س، س)\n    أرجع س')

if __name__ == '__main__':
    unittest.main()

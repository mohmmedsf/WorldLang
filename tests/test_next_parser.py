import unittest
from next_syntax.parser import parse, Program, Assign, Print, If, Binary, Literal
from next_syntax.lexer import SyntaxErrorNext

class HybridParserTests(unittest.TestCase):
    def test_equivalent_natural_and_compact(self):
        natural = 'اجعل العمر يساوي 20\nإذا كان العمر أكبر من أو يساوي 18\n    اطبع "بالغ"'
        compact = 'العمر = 20\nإذا العمر >= 18\n    اطبع "بالغ"'
        self.assertEqual(parse(natural), parse(compact))

    def test_arithmetic_precedence(self):
        ast = parse('الناتج = 10 + 5 * 2')
        self.assertEqual(ast.statements[0].value.op, 'PLUS')
        self.assertEqual(ast.statements[0].value.right.op, 'MUL')

    def test_grouping_changes_precedence(self):
        ast = parse('الناتج = (10 + 5) * 2')
        self.assertEqual(ast.statements[0].value.op, 'MUL')

    def test_elif_else(self):
        ast = parse('إذا س > 5\n    اطبع "أ"\nوإلا إذا س > 2\n    اطبع "ب"\nوإلا\n    اطبع "ج"')
        self.assertEqual(len(ast.statements[0].branches), 2)
        self.assertEqual(len(ast.statements[0].otherwise), 1)

    def test_missing_indentation(self):
        with self.assertRaises(SyntaxErrorNext):
            parse('إذا س > 5\nاطبع "أ"')

    def test_unknown_statement(self):
        with self.assertRaises(SyntaxErrorNext):
            parse('استورد شيء')

    def test_chained_comparison_rejected(self):
        with self.assertRaises(SyntaxErrorNext):
            parse('اطبع 1 < 2 < 3')

    def test_parenthesized_print(self):
        self.assertEqual(parse('اطبع (2 + 3)'), Program((Print(Binary('PLUS', Literal(2), Literal(3))),)))

if __name__ == '__main__':
    unittest.main()

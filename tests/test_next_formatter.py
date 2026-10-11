import unittest
from next_syntax.formatter import format_source
from next_syntax.parser import parse
from next_syntax.runtime import run

class FormatterTests(unittest.TestCase):
    CASES = (
        'اطبع 2+3*4',
        'اجعل س=[1,2]\nلكل عنصر في س:\n  اطبع عنصر',
        'دالة ضعف(س):\n  أرجع س*2\nاطبع ضعف(4)',
        'اذا صحيح:\n  اطبع 1\nوالا:\n  اطبع 2',
        'كرر 2 مرات:\n  اطبع 3',
        'اطبع (1+2)*3',
    )
    def test_idempotent_and_ast_equivalent(self):
        for source in self.CASES:
            with self.subTest(source=source):
                formatted = format_source(source)
                self.assertEqual(format_source(formatted), formatted)
                self.assertEqual(parse(formatted), parse(source))
                self.assertEqual(run(formatted).output, run(source).output)

if __name__ == '__main__':
    unittest.main()

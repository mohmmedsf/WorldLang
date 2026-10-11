"""Small deterministic AST parser for the opt-in Arabic hybrid syntax.

Supports declarations, assignments, printing, arithmetic, comparisons, if/elif/else.
Does not execute code or change the Classic WorldLang parser.
"""
from dataclasses import dataclass
from .lexer import lex, SyntaxErrorNext

@dataclass(frozen=True)
class Literal:
    value: object

@dataclass(frozen=True)
class Name:
    value: str

@dataclass(frozen=True)
class Unary:
    op: str
    operand: object

@dataclass(frozen=True)
class Binary:
    op: str
    left: object
    right: object

@dataclass(frozen=True)
class Assign:
    name: str
    value: object

@dataclass(frozen=True)
class Print:
    value: object

@dataclass(frozen=True)
class If:
    branches: tuple
    otherwise: tuple

@dataclass(frozen=True)
class Program:
    statements: tuple

PRECEDENCE = {
    'OR': 1, 'AND': 2, 'EQ': 3, 'NE': 3,
    'GT': 3, 'LT': 3, 'GE': 3, 'LE': 3,
    'PLUS': 4, 'MINUS': 4, 'MUL': 5, 'DIV': 5,
}
COMPARISONS = {'EQ', 'NE', 'GT', 'LT', 'GE', 'LE'}

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    @property
    def current(self):
        return self.tokens[self.i]

    def accept(self, kind):
        if self.current.kind == kind:
            token = self.current
            self.i += 1
            return token
        return None

    def expect(self, kind):
        token = self.accept(kind)
        if token is None:
            t = self.current
            raise SyntaxErrorNext(
                f'Line {t.line}, column {t.column}: expected {kind}, got {t.kind}'
            )
        return token

    def parse(self):
        statements = self.statements('EOF')
        self.expect('EOF')
        return Program(tuple(statements))

    def statements(self, end):
        result = []
        while self.current.kind != end:
            if self.current.kind == 'EOF':
                self.expect(end)
            if self.accept('NEWLINE'):
                continue
            if self.current.kind in ('DEDENT', 'ELSE', 'ELIF'):
                self.expect(end)
            result.append(self.statement())
        return result

    def block(self):
        self.expect('NEWLINE')
        self.expect('INDENT')
        statements = self.statements('DEDENT')
        if not statements:
            t = self.current
            raise SyntaxErrorNext(f'Line {t.line}: empty block')
        self.expect('DEDENT')
        return tuple(statements)

    def statement(self):
        if self.accept('LET'):
            name = self.expect('IDENT').value
            self.expect('ASSIGN')
            value = self.expression()
            self.expect('NEWLINE')
            return Assign(name, value)
        if self.current.kind == 'IDENT' and self.tokens[self.i + 1].kind == 'ASSIGN':
            name = self.expect('IDENT').value
            self.expect('ASSIGN')
            value = self.expression()
            self.expect('NEWLINE')
            return Assign(name, value)
        if self.accept('PRINT'):
            value = self.expression()
            self.expect('NEWLINE')
            return Print(value)
        if self.accept('IF'):
            branches = [(self.expression(), self.block())]
            while self.accept('ELIF'):
                branches.append((self.expression(), self.block()))
            otherwise = self.block() if self.accept('ELSE') else ()
            return If(tuple(branches), otherwise)
        t = self.current
        raise SyntaxErrorNext(f'Line {t.line}, column {t.column}: unsupported statement {t.kind}')

    def expression(self, min_precedence=0):
        token = self.current
        if self.accept('MINUS'):
            left = Unary('NEG', self.expression(6))
        elif self.accept('LPAREN'):
            left = self.expression()
            self.expect('RPAREN')
        elif self.accept('NUMBER'):
            left = Literal(float(token.value) if '.' in token.value else int(token.value))
        elif self.accept('STRING'):
            left = Literal(token.value[1:-1])
        elif self.accept('IDENT'):
            left = Name(token.value)
        else:
            raise SyntaxErrorNext(f'Line {token.line}, column {token.column}: expected expression, got {token.kind}')

        while self.current.kind in PRECEDENCE and PRECEDENCE[self.current.kind] >= min_precedence:
            operator = self.current.kind
            if operator in COMPARISONS and isinstance(left, Binary) and left.op in COMPARISONS:
                raise SyntaxErrorNext(f'Line {self.current.line}: chained comparisons require explicit AND')
            self.i += 1
            right = self.expression(PRECEDENCE[operator] + 1)
            left = Binary(operator, left, right)
        return left

def parse(source: str) -> Program:
    return Parser(lex(source)).parse()

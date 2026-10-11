"""Early, opt-in static diagnostics for the WorldLang Next AST.

Scope: duplicate function declarations, unknown function calls, call arity,
and returns outside function bodies. Does not replace runtime checks.
"""
from dataclasses import dataclass
from .parser import (Assign, Binary, Call, ForEach, Function, If, Index,
                     ListLiteral, Literal, Name, Print, Program, Repeat, Return,
                     Unary, While, parse)

@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str

def analyze(source: str) -> list[Diagnostic]:
    program = parse(source)
    signatures = {}
    errors = []
    def register(statements):
        for node in statements:
            if isinstance(node, Function):
                if node.name in signatures:
                    errors.append(Diagnostic('E_DUPLICATE_FUNCTION', f'Duplicate function: {node.name}'))
                else:
                    signatures[node.name] = len(node.parameters)
            if isinstance(node, If):
                for _, body in node.branches:
                    register(body)
                register(node.otherwise)
            if isinstance(node, (While, Repeat, ForEach)):
                register(node.body)
    register(program.statements)
    def expression(node):
        if isinstance(node, Call):
            if node.name not in signatures:
                errors.append(Diagnostic('E_UNKNOWN_FUNCTION', f'Unknown function: {node.name}'))
            elif len(node.arguments) != signatures[node.name]:
                errors.append(Diagnostic('E_ARITY', f'Incorrect argument count: {node.name}'))
            for arg in node.arguments:
                expression(arg)
        elif isinstance(node, Binary):
            expression(node.left); expression(node.right)
        elif isinstance(node, Unary):
            expression(node.operand)
        elif isinstance(node, ListLiteral):
            for item in node.elements:
                expression(item)
        elif isinstance(node, Index):
            expression(node.target); expression(node.index)
    def statements(nodes, in_function=False):
        for node in nodes:
            if isinstance(node, Assign):
                expression(node.value)
            elif isinstance(node, Print):
                expression(node.value)
            elif isinstance(node, Return):
                if not in_function:
                    errors.append(Diagnostic('E_RETURN_OUTSIDE', 'Return outside function'))
                expression(node.value)
            elif isinstance(node, Function):
                statements(node.body, True)
            elif isinstance(node, If):
                for condition, body in node.branches:
                    expression(condition)
                    statements(body, in_function)
                statements(node.otherwise, in_function)
            elif isinstance(node, (While, Repeat, ForEach)):
                expression(node.condition if isinstance(node, While) else node.count if isinstance(node, Repeat) else node.iterable)
                statements(node.body, in_function)
    statements(program.statements)
    return errors

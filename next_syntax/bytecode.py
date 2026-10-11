"""Portable, JSON-serializable stack bytecode for a safe Next subset.

Supports literals, variables, arithmetic/comparisons, print and simple assignment.
Unsupported syntax fails closed rather than silently falling back to AST execution.
"""
import json
from dataclasses import dataclass
from .parser import Assign, Binary, Literal, Name, Print, Unary, parse
from .runtime import RuntimeErrorNext, OPERATORS

VERSION = 1
OPS = {'PUSH', 'LOAD', 'STORE', 'BINARY', 'NEG', 'PRINT'}
BINARY = set(OPERATORS) | {'AND', 'OR'}

@dataclass(frozen=True)
class Bytecode:
    version: int
    code: tuple

    def to_json(self):
        validate(self)
        return json.dumps({'version': self.version, 'code': [list(i) for i in self.code]}, ensure_ascii=False)

    @classmethod
    def from_json(cls, source):
        obj = json.loads(source)
        if not isinstance(obj, dict) or set(obj) != {'version', 'code'}:
            raise ValueError('Invalid bytecode document')
        if not isinstance(obj['code'], list):
            raise ValueError('Invalid code')
        result = cls(obj['version'], tuple(tuple(i) for i in obj['code']))
        validate(result)
        return result

def validate(module):
    if not isinstance(module, Bytecode) or type(module.version) is not int or module.version != VERSION:
        raise ValueError('Unsupported bytecode version')
    if not isinstance(module.code, tuple):
        raise ValueError('Invalid bytecode instructions')
    depth = 0
    for instruction in module.code:
        if not isinstance(instruction, tuple) or len(instruction) != 2:
            raise ValueError('Invalid instruction format')
        op, arg = instruction
        if op not in OPS:
            raise ValueError('Invalid opcode')
        if op == 'PUSH':
            if type(arg) not in (int, float, str, bool):
                raise ValueError('Invalid constant')
            depth += 1
        elif op == 'LOAD':
            if not isinstance(arg, str) or not arg:
                raise ValueError('Invalid name')
            depth += 1
        elif op == 'BINARY':
            if arg not in BINARY or depth < 2:
                raise ValueError('Invalid binary operation or stack underflow')
            depth -= 1
        elif op == 'NEG':
            if arg is not None or depth < 1:
                raise ValueError('Invalid negation or stack underflow')
        else:
            if op == 'STORE' and (not isinstance(arg, str) or not arg):
                raise ValueError('Invalid store name')
            if op == 'PRINT' and arg is not None:
                raise ValueError('Invalid print argument')
            if depth < 1:
                raise ValueError('Stack underflow')
            depth -= 1
    if depth != 0:
        raise ValueError('Unbalanced stack')
    return True

def compile_source(source):
    code = []
    def emit_expr(node):
        if isinstance(node, Literal):
            code.append(('PUSH', node.value))
        elif isinstance(node, Name):
            code.append(('LOAD', node.value))
        elif isinstance(node, Unary) and node.op == 'NEG':
            emit_expr(node.operand)
            code.append(('NEG', None))
        elif isinstance(node, Binary):
            if node.op in ('AND', 'OR'):
                raise ValueError('Short-circuit boolean expressions are not yet supported in bytecode')
            emit_expr(node.left)
            emit_expr(node.right)
            code.append(('BINARY', node.op))
        else:
            raise ValueError(f'Unsupported bytecode expression: {type(node).__name__}')
    for stmt in parse(source).statements:
        if isinstance(stmt, Assign):
            emit_expr(stmt.value)
            code.append(('STORE', stmt.name))
        elif isinstance(stmt, Print):
            emit_expr(stmt.value)
            code.append(('PRINT', None))
        else:
            raise ValueError(f'Unsupported bytecode statement: {type(stmt).__name__}')
    module = Bytecode(VERSION, tuple(code))
    validate(module)
    return module

def execute(module, *, max_steps=100000):
    validate(module)
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError('max_steps must be positive')
    stack, variables, output = [], {}, []
    for step, (op, arg) in enumerate(module.code, 1):
        if step > max_steps:
            raise RuntimeErrorNext('Execution step limit exceeded')
        if op == 'PUSH':
            stack.append(arg)
        elif op == 'LOAD':
            if arg not in variables:
                raise RuntimeErrorNext(f'Undefined variable: {arg}')
            stack.append(variables[arg])
        elif op == 'STORE':
            variables[arg] = stack.pop()
        elif op == 'PRINT':
            output.append(str(stack.pop()))
        elif op == 'NEG':
            try:
                stack.append(-stack.pop())
            except (TypeError, ValueError) as exc:
                raise RuntimeErrorNext(f'Invalid negation: {exc}') from exc
        elif op == 'BINARY':
            right, left = stack.pop(), stack.pop()
            try:
                stack.append(OPERATORS[arg](left, right))
            except (ArithmeticError, TypeError, ValueError) as exc:
                raise RuntimeErrorNext(f'Invalid operation {arg}: {exc}') from exc
    return {'output': output, 'variables': variables}

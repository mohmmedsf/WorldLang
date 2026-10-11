"""Portable, JSON-serializable stack bytecode for a safe Next subset.

Supports literals, variables, arithmetic/comparisons, print and simple assignment.
Unsupported syntax fails closed rather than silently falling back to AST execution.
"""
import json
from dataclasses import dataclass
from .parser import Assign, Binary, If, While, Repeat, Literal, Name, Print, Unary, parse
from .runtime import RuntimeErrorNext, OPERATORS

VERSION = 1
OPS = {'PUSH', 'LOAD', 'STORE', 'BINARY', 'NEG', 'PRINT', 'JUMP', 'JUMP_IF_FALSE', 'DUP', 'POP', 'CHECK_REPEAT'}
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
    for pc, instruction in enumerate(module.code):
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
        elif op in ('JUMP', 'JUMP_IF_FALSE'):
            if type(arg) is not int or not 0 <= arg <= len(module.code):
                raise ValueError('Invalid jump target')
            if op == 'JUMP_IF_FALSE':
                if depth < 1:
                    raise ValueError('Stack underflow')
                depth -= 1
        elif op == 'CHECK_REPEAT':
            if arg is not None or depth < 1:
                raise ValueError('Invalid repeat count check')
        elif op == 'DUP':
            if arg is not None or depth < 1:
                raise ValueError('Invalid DUP')
            depth += 1
        elif op == 'POP':
            if arg is not None or depth < 1:
                raise ValueError('Invalid POP')
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
    counter = 0
    def emit_block(statements):
        for statement in statements:
            emit_statement(statement)
    def emit_statement(stmt):
        nonlocal counter
        if isinstance(stmt, Assign):
            emit_expr(stmt.value)
            code.append(('STORE', stmt.name))
        elif isinstance(stmt, Print):
            emit_expr(stmt.value)
            code.append(('PRINT', None))
        elif isinstance(stmt, If):
            exits = []
            for condition, body in stmt.branches:
                emit_expr(condition)
                jump = len(code)
                code.append(('JUMP_IF_FALSE', -1))
                emit_block(body)
                exits.append(len(code))
                code.append(('JUMP', -1))
                code[jump] = ('JUMP_IF_FALSE', len(code))
            emit_block(stmt.otherwise)
            for jump in exits:
                code[jump] = ('JUMP', len(code))
        elif isinstance(stmt, While):
            start = len(code)
            emit_expr(stmt.condition)
            jump = len(code)
            code.append(('JUMP_IF_FALSE', -1))
            emit_block(stmt.body)
            code.append(('JUMP', start))
            code[jump] = ('JUMP_IF_FALSE', len(code))
        elif isinstance(stmt, Repeat):
            counter += 1
            name = f'\\x00repeat_{counter}'
            emit_expr(stmt.count)
            code.append(('CHECK_REPEAT', None))
            code.append(('STORE', name))
            start = len(code)
            code.append(('LOAD', name))
            code.append(('PUSH', 0))
            code.append(('BINARY', 'GT'))
            jump = len(code)
            code.append(('JUMP_IF_FALSE', -1))
            emit_block(stmt.body)
            code.append(('LOAD', name))
            code.append(('PUSH', 1))
            code.append(('BINARY', 'MINUS'))
            code.append(('STORE', name))
            code.append(('JUMP', start))
            code[jump] = ('JUMP_IF_FALSE', len(code))
        else:
            raise ValueError(f'Unsupported bytecode statement: {type(stmt).__name__}')
    emit_block(parse(source).statements)
    module = Bytecode(VERSION, tuple(code))
    validate(module)
    return module

def execute(module, *, max_steps=100000):
    validate(module)
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError('max_steps must be positive')
    stack, variables, output = [], {}, []
    pc = 0
    steps = 0
    while pc < len(module.code):
        op, arg = module.code[pc]
        pc += 1
        steps += 1
        if steps > max_steps:
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
        elif op == 'JUMP':
            pc = arg
        elif op == 'JUMP_IF_FALSE':
            if not stack.pop():
                pc = arg
        elif op == 'CHECK_REPEAT':
            count = stack[-1]
            if type(count) is not int or count < 0:
                raise RuntimeErrorNext('Repeat count must be a nonnegative integer')
        elif op == 'DUP':
            stack.append(stack[-1])
        elif op == 'POP':
            stack.pop()
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

"""Portable, JSON-serializable stack bytecode for a safe Next subset.

Supports literals, variables, arithmetic/comparisons, print and simple assignment.
Unsupported syntax fails closed rather than silently falling back to AST execution.
"""
import json
from dataclasses import dataclass
from .parser import Assign, Binary, If, While, Repeat, ForEach, Index, ListLiteral, Function, Call, Return, Literal, Name, Print, Unary, parse
from .runtime import RuntimeErrorNext, OPERATORS

VERSION = 1
MAX_INSTRUCTIONS = 100_000
MAX_JSON_BYTES = 4_000_000
OPS = {'PUSH', 'LOAD', 'STORE', 'TO_BOOL', 'BINARY', 'NEG', 'PRINT', 'JUMP', 'JUMP_IF_FALSE', 'DUP', 'POP', 'CHECK_REPEAT', 'BUILD_LIST', 'INDEX', 'ITER_INIT', 'ITER_NEXT', 'DEFINE', 'CALL', 'RETURN'}
BINARY = set(OPERATORS)

@dataclass(frozen=True)
class Bytecode:
    version: int
    code: tuple

    def to_json(self):
        validate(self)
        return json.dumps({'version': self.version, 'code': [list(i) for i in self.code]}, ensure_ascii=False)

    @classmethod
    def from_json(cls, source):
        if not isinstance(source, str) or len(source.encode('utf-8')) > MAX_JSON_BYTES:
            raise ValueError('Bytecode document too large')
        try:
            obj = json.loads(source)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError('Invalid bytecode JSON') from exc
        if not isinstance(obj, dict) or set(obj) != {'version', 'code'}:
            raise ValueError('Invalid bytecode document')
        if not isinstance(obj['code'], list):
            raise ValueError('Invalid code')
        if not all(isinstance(i, list) and len(i) == 2 for i in obj['code']):
            raise ValueError('Invalid instruction format')
        result = cls(obj['version'], tuple(tuple(i) for i in obj['code']))
        validate(result)
        return result

def validate(module):
    if not isinstance(module, Bytecode) or type(module.version) is not int or module.version != VERSION:
        raise ValueError('Unsupported bytecode version')
    if not isinstance(module.code, tuple):
        raise ValueError('Invalid bytecode instructions')
    if len(module.code) > MAX_INSTRUCTIONS:
        raise ValueError('Too many bytecode instructions')
    # Validate instruction shapes before control-flow analysis.
    for pc, instruction in enumerate(module.code):
        if not isinstance(instruction, tuple) or len(instruction) != 2:
            raise ValueError('Invalid instruction format')
        op, arg = instruction
        if not isinstance(op, str) or op not in OPS:
            raise ValueError('Invalid opcode')
        if op == 'PUSH':
            if arg is not None and type(arg) not in (int, float, str, bool):
                raise ValueError('Invalid constant')
        elif op in ('LOAD', 'STORE'):
            if not isinstance(arg, str) or not arg:
                raise ValueError('Invalid variable name')
        elif op == 'BINARY':
            if not isinstance(arg, str) or arg not in BINARY:
                raise ValueError('Invalid binary operation')
        elif op in ('JUMP', 'JUMP_IF_FALSE'):
            if type(arg) is not int or not 0 <= arg <= len(module.code):
                raise ValueError('Invalid jump target')
        elif op == 'BUILD_LIST':
            if type(arg) is not int or arg < 0:
                raise ValueError('Invalid list size')
        elif op == 'ITER_NEXT':
            if not isinstance(arg, (list, tuple)) or len(arg) != 2 or not isinstance(arg[0], str) or not arg[0] or type(arg[1]) is not int or not 0 <= arg[1] <= len(module.code):
                raise ValueError('Invalid iterator operands')
        elif op == 'DEFINE':
            if not isinstance(arg, (list, tuple)) or len(arg) != 3:
                raise ValueError('Invalid function definition')
            name, params, address = arg
            if not isinstance(name, str) or not name or not isinstance(params, (list, tuple)) or not all(isinstance(p, str) and p for p in params) or len(set(params)) != len(params) or type(address) is not int or not 0 <= address < len(module.code):
                raise ValueError('Invalid function metadata')
        elif op == 'CALL':
            if not isinstance(arg, (list, tuple)) or len(arg) != 2 or not isinstance(arg[0], str) or not arg[0] or type(arg[1]) is not int or arg[1] < 0:
                raise ValueError('Invalid call')
        elif arg is not None:
            raise ValueError('Unexpected instruction argument')

    # Worklist dataflow: every reachable PC must have one consistent stack height.
    # Function entry points start with empty stacks and RETURN terminates each path.
    entries = {0}
    entries.update(arg[2] for op, arg in module.code if op == 'DEFINE')
    heights = {}
    pending = [(pc, 0) for pc in entries]
    n = len(module.code)
    while pending:
        pc, depth = pending.pop()
        if pc in heights:
            if heights[pc] != depth:
                raise ValueError('Inconsistent stack height at control-flow join')
            continue
        heights[pc] = depth
        if pc == n:
            if depth != 0:
                raise ValueError('Unbalanced stack at program exit')
            continue
        op, arg = module.code[pc]
        pops, pushes = {
            'PUSH': (0, 1), 'LOAD': (0, 1), 'STORE': (1, 0),
            'BINARY': (2, 1), 'NEG': (1, 1), 'TO_BOOL': (1, 1), 'PRINT': (1, 0),
            'JUMP': (0, 0), 'JUMP_IF_FALSE': (1, 0),
            'DUP': (1, 2), 'POP': (1, 0), 'CHECK_REPEAT': (1, 1),
            'BUILD_LIST': (arg if op == 'BUILD_LIST' else 0, 1),
            'INDEX': (2, 1), 'ITER_INIT': (1, 1),
            'ITER_NEXT': (1, 1), 'DEFINE': (0, 0),
            'CALL': (arg[1] if op == 'CALL' else 0, 1),
            'RETURN': (1, 0),
        }[op]
        if depth < pops:
            raise ValueError('Stack underflow')
        next_depth = depth - pops + pushes
        if op == 'RETURN':
            if next_depth != 0:
                raise ValueError('Unbalanced function return stack')
            continue
        if op == 'JUMP':
            successors = (arg,)
        elif op == 'JUMP_IF_FALSE':
            successors = (pc + 1, arg)
        elif op == 'ITER_NEXT':
            successors = (pc + 1, arg[1])
        else:
            successors = (pc + 1,)
        for target in successors:
            pending.append((target, next_depth if op != 'ITER_NEXT' or target == pc + 1 else depth))

    return True

def compile_source(source):
    code = []
    def emit_expr(node):
        if isinstance(node, Literal):
            code.append(('PUSH', node.value))
        elif isinstance(node, Name):
            code.append(('LOAD', node.value))
        elif isinstance(node, Call):
            for item in node.arguments:
                emit_expr(item)
            code.append(('CALL', (node.name, len(node.arguments))))
        elif isinstance(node, ListLiteral):
            for item in node.elements:
                emit_expr(item)
            code.append(('BUILD_LIST', len(node.elements)))
        elif isinstance(node, Index):
            emit_expr(node.target)
            emit_expr(node.index)
            code.append(('INDEX', None))
        elif isinstance(node, Unary) and node.op == 'NEG':
            emit_expr(node.operand)
            code.append(('NEG', None))
        elif isinstance(node, Binary):
            if node.op == 'AND':
                emit_expr(node.left)
                code.append(('TO_BOOL', None))
                code.append(('DUP', None))
                jump = len(code)
                code.append(('JUMP_IF_FALSE', -1))
                code.append(('POP', None))
                emit_expr(node.right)
                code.append(('TO_BOOL', None))
                code[jump] = ('JUMP_IF_FALSE', len(code))
                return
            if node.op == 'OR':
                emit_expr(node.left)
                code.append(('TO_BOOL', None))
                code.append(('DUP', None))
                jump = len(code)
                code.append(('JUMP_IF_FALSE', -1))
                end = len(code)
                code.append(('JUMP', -1))
                code[jump] = ('JUMP_IF_FALSE', len(code))
                code.append(('POP', None))
                emit_expr(node.right)
                code.append(('TO_BOOL', None))
                code[end] = ('JUMP', len(code))
                return
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
        elif isinstance(stmt, Function):
            skip = len(code)
            code.append(('JUMP', -1))
            start = len(code)
            emit_block(stmt.body)
            code.append(('PUSH', None))
            code.append(('RETURN', None))
            code[skip] = ('JUMP', len(code))
            code.append(('DEFINE', (stmt.name, stmt.parameters, start)))
        elif isinstance(stmt, Return):
            emit_expr(stmt.value)
            code.append(('RETURN', None))
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
        elif isinstance(stmt, ForEach):
            emit_expr(stmt.iterable)
            code.append(('ITER_INIT', None))
            start = len(code)
            jump = len(code)
            code.append(('ITER_NEXT', (stmt.name, -1)))
            emit_block(stmt.body)
            code.append(('JUMP', start))
            code[jump] = ('ITER_NEXT', (stmt.name, len(code)))
            code.append(('POP', None))
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

def execute(module, *, max_steps=100000, max_call_depth=100, max_output_lines=10000):
    validate(module)
    if type(max_steps) is not int or max_steps < 1:
        raise ValueError('max_steps must be positive')
    if type(max_call_depth) is not int or max_call_depth < 2:
        raise ValueError('max_call_depth must be >= 2')
    if type(max_output_lines) is not int or max_output_lines < 1:
        raise ValueError('max_output_lines must be positive')
    stack, variables, output = [], {}, []
    functions = {}
    frames = [variables]
    calls = []
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
            if arg in frames[-1]:
                stack.append(frames[-1][arg])
            elif arg in variables:
                stack.append(variables[arg])
            else:
                raise RuntimeErrorNext(f'Undefined variable: {arg}')
        elif op == 'STORE':
            frames[-1][arg] = stack.pop()
        elif op == 'DEFINE':
            name, params, address = arg
            functions[name] = (params, address)
        elif op == 'CALL':
            name, argc = arg
            if name not in functions:
                raise RuntimeErrorNext(f'Undefined function: {name}')
            params, address = functions[name]
            if len(params) != argc:
                raise RuntimeErrorNext(f'Incorrect argument count for {name}')
            if len(frames) >= max_call_depth:
                raise RuntimeErrorNext('Function call depth limit exceeded')
            args = stack[-argc:] if argc else []
            if argc:
                del stack[-argc:]
            calls.append((pc, len(stack)))
            frames.append(dict(zip(params, args)))
            pc = address
        elif op == 'RETURN':
            if not calls:
                raise RuntimeErrorNext('Return outside function')
            result = stack.pop()
            pc, base = calls.pop()
            del stack[base:]
            frames.pop()
            stack.append(result)
        elif op == 'BUILD_LIST':
            items = stack[-arg:] if arg else []
            if arg:
                del stack[-arg:]
            stack.append(items)
        elif op == 'INDEX':
            index, target = stack.pop(), stack.pop()
            if not isinstance(target, (list, str)):
                raise RuntimeErrorNext('Indexing requires a list or string')
            if type(index) is not int:
                raise RuntimeErrorNext('Index must be an integer')
            try:
                stack.append(target[index])
            except IndexError as exc:
                raise RuntimeErrorNext('Index out of range') from exc
        elif op == 'ITER_INIT':
            target = stack.pop()
            if not isinstance(target, (list, str)):
                raise RuntimeErrorNext('For-each requires a list or string')
            stack.append(iter(target))
        elif op == 'ITER_NEXT':
            name, end = arg
            try:
                frames[-1][name] = next(stack[-1])
            except StopIteration:
                pc = end
        elif op == 'PRINT':
            if len(output) >= max_output_lines:
                raise RuntimeErrorNext('Output line limit exceeded')
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
        elif op == 'TO_BOOL':
            stack.append(bool(stack.pop()))
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

"""Experimental opt-in AST interpreter. Not a security sandbox."""
import operator
from dataclasses import dataclass, field
from .parser import (Assign, Binary, Call, Function, If, ListLiteral, Literal,
                     Name, Print, Program, Repeat, Return, Unary, While, parse)

class RuntimeErrorNext(Exception):
    pass

class _ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

OPERATORS = {
    'PLUS': operator.add, 'MINUS': operator.sub,
    'MUL': operator.mul, 'DIV': operator.truediv,
    'EQ': operator.eq, 'NE': operator.ne,
    'GT': operator.gt, 'LT': operator.lt,
    'GE': operator.ge, 'LE': operator.le,
}

@dataclass
class ExecutionResult:
    output: list[str] = field(default_factory=list)
    variables: dict = field(default_factory=dict)

class Interpreter:
    def __init__(self, max_steps=100000, max_call_depth=100):
        self.result = ExecutionResult()
        self.max_steps = max_steps
        self.steps = 0
        self.functions = {}
        self.frames = [self.result.variables]
        self.max_call_depth = max_call_depth

    def tick(self):
        self.steps += 1
        if self.steps > self.max_steps:
            raise RuntimeErrorNext('Execution step limit exceeded')

    def lookup(self, name):
        if name in self.frames[-1]:
            return self.frames[-1][name]
        if name in self.result.variables:
            return self.result.variables[name]
        raise RuntimeErrorNext(f'Undefined variable: {name}')

    def evaluate(self, node):
        self.tick()
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, ListLiteral):
            return [self.evaluate(element) for element in node.elements]
        if isinstance(node, Name):
            return self.lookup(node.value)
        if isinstance(node, Unary):
            if node.op == 'NEG':
                return -self.evaluate(node.operand)
            raise RuntimeErrorNext(f'Unsupported unary operator: {node.op}')
        if isinstance(node, Call):
            function = self.functions.get(node.name)
            if function is None:
                raise RuntimeErrorNext(f'Undefined function: {node.name}')
            if len(node.arguments) != len(function.parameters):
                raise RuntimeErrorNext(f'Incorrect argument count for {node.name}')
            values = [self.evaluate(arg) for arg in node.arguments]
            if len(self.frames) >= self.max_call_depth:
                raise RuntimeErrorNext('Function call depth limit exceeded')
            self.frames.append(dict(zip(function.parameters, values)))
            try:
                try:
                    self.execute_block(function.body)
                except _ReturnSignal as returned:
                    return returned.value
                return None
            finally:
                self.frames.pop()
        if isinstance(node, Binary):
            if node.op == 'AND':
                return bool(self.evaluate(node.left)) and bool(self.evaluate(node.right))
            if node.op == 'OR':
                return bool(self.evaluate(node.left)) or bool(self.evaluate(node.right))
            operation = OPERATORS.get(node.op)
            if operation is None:
                raise RuntimeErrorNext(f'Unsupported operator: {node.op}')
            try:
                return operation(self.evaluate(node.left), self.evaluate(node.right))
            except (ArithmeticError, TypeError, ValueError) as exc:
                raise RuntimeErrorNext(f'Invalid operation {node.op}: {exc}') from exc
        raise RuntimeErrorNext(f'Unsupported expression: {type(node).__name__}')

    def execute_block(self, statements):
        for statement in statements:
            self.tick()
            if isinstance(statement, Assign):
                self.frames[-1][statement.name] = self.evaluate(statement.value)
            elif isinstance(statement, Print):
                self.result.output.append(str(self.evaluate(statement.value)))
            elif isinstance(statement, If):
                for condition, body in statement.branches:
                    if self.evaluate(condition):
                        self.execute_block(body)
                        break
                else:
                    self.execute_block(statement.otherwise)
            elif isinstance(statement, While):
                while self.evaluate(statement.condition):
                    self.tick()
                    self.execute_block(statement.body)
            elif isinstance(statement, Repeat):
                count = self.evaluate(statement.count)
                if type(count) is not int or count < 0:
                    raise RuntimeErrorNext('Repeat count must be a nonnegative integer')
                for _ in range(count):
                    self.tick()
                    self.execute_block(statement.body)
            elif isinstance(statement, Function):
                self.functions[statement.name] = statement
            elif isinstance(statement, Return):
                if len(self.frames) == 1:
                    raise RuntimeErrorNext('Return outside function')
                raise _ReturnSignal(self.evaluate(statement.value))
            else:
                raise RuntimeErrorNext(f'Unsupported statement: {type(statement).__name__}')

    def run(self, program):
        if not isinstance(program, Program):
            raise TypeError('Expected Program AST')
        self.execute_block(program.statements)
        return self.result

def run(source: str, *, max_steps: int = 100000, max_call_depth: int = 100) -> ExecutionResult:
    if max_steps < 1 or max_call_depth < 2:
        raise ValueError('Limits must be positive (max_call_depth >= 2)')
    return Interpreter(max_steps=max_steps, max_call_depth=max_call_depth).run(parse(source))

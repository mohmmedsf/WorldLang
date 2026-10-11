"""Minimal opt-in AST interpreter for WorldLang Next.

No eval/exec, filesystem, network, imports, or Classic interpreter modifications.
This is a prototype, not a security sandbox for hostile inputs.
"""
import operator
from dataclasses import dataclass, field
from .parser import Assign, Binary, If, Literal, Name, Print, Program, Unary, parse

class RuntimeErrorNext(Exception):
    """Evaluation error in Next syntax."""

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
    def __init__(self, max_steps=100000):
        self.result = ExecutionResult()
        self.max_steps = max_steps
        self.steps = 0

    def tick(self):
        self.steps += 1
        if self.steps > self.max_steps:
            raise RuntimeErrorNext('Execution step limit exceeded')

    def evaluate(self, node):
        self.tick()
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, Name):
            if node.value not in self.result.variables:
                raise RuntimeErrorNext(f'Undefined variable: {node.value}')
            return self.result.variables[node.value]
        if isinstance(node, Unary):
            if node.op == 'NEG':
                return -self.evaluate(node.operand)
            raise RuntimeErrorNext(f'Unsupported unary operator: {node.op}')
        if isinstance(node, Binary):
            if node.op == 'AND':
                left = self.evaluate(node.left)
                return bool(left) and bool(self.evaluate(node.right))
            if node.op == 'OR':
                left = self.evaluate(node.left)
                return bool(left) or bool(self.evaluate(node.right))
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
                self.result.variables[statement.name] = self.evaluate(statement.value)
            elif isinstance(statement, Print):
                self.result.output.append(str(self.evaluate(statement.value)))
            elif isinstance(statement, If):
                for condition, body in statement.branches:
                    if self.evaluate(condition):
                        self.execute_block(body)
                        break
                else:
                    self.execute_block(statement.otherwise)
            else:
                raise RuntimeErrorNext(f'Unsupported statement: {type(statement).__name__}')

    def run(self, program):
        if not isinstance(program, Program):
            raise TypeError('Expected Program AST')
        self.execute_block(program.statements)
        return self.result

def run(source: str, *, max_steps: int = 100000) -> ExecutionResult:
    """Parse and execute opt-in Next syntax, returning output and variables."""
    if max_steps < 1:
        raise ValueError('max_steps must be positive')
    return Interpreter(max_steps=max_steps).run(parse(source))

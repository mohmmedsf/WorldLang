"""Conservative type inference for Next expressions; no implicit coercion claims."""
from dataclasses import dataclass
from .parser import (Assign, Binary, Call, ForEach, Function, If, Index,
                     ListLiteral, Literal, Name, Print, Repeat, Return, Unary,
                     While, parse)

@dataclass(frozen=True)
class TypeIssue:
    code: str
    message: str

def infer_literal(value):
    if isinstance(value, bool):
        return 'Bool'
    if isinstance(value, int):
        return 'Int'
    if isinstance(value, float):
        return 'Float'
    if isinstance(value, str):
        return 'String'
    return 'Unknown'

def check_types(source):
    program = parse(source)
    env = {}
    issues = []
    def expression(node, scope):
        if isinstance(node, Literal):
            return infer_literal(node.value)
        if isinstance(node, Name):
            return scope.get(node.value, env.get(node.value, 'Unknown'))
        if isinstance(node, ListLiteral):
            types = [expression(item, scope) for item in node.elements]
            inner = types[0] if types and len(set(types)) == 1 else 'Unknown'
            return f'List[{inner}]'
        if isinstance(node, Index):
            target = expression(node.target, scope)
            index = expression(node.index, scope)
            if index not in ('Int', 'Unknown'):
                issues.append(TypeIssue('E_INDEX_TYPE', 'Index must be Int'))
            if target.startswith('List['):
                return target[5:-1]
            if target == 'String':
                return 'String'
            if target != 'Unknown':
                issues.append(TypeIssue('E_NOT_INDEXABLE', f'Cannot index {target}'))
            return 'Unknown'
        if isinstance(node, Unary):
            inner = expression(node.operand, scope)
            if node.op == 'NEG' and inner not in ('Int', 'Float', 'Unknown'):
                issues.append(TypeIssue('E_UNARY_TYPE', f'Cannot negate {inner}'))
            return inner
        if isinstance(node, Binary):
            left = expression(node.left, scope)
            right = expression(node.right, scope)
            if node.op in ('EQ', 'NE', 'GT', 'LT', 'GE', 'LE', 'AND', 'OR'):
                return 'Bool'
            if node.op == 'PLUS' and left == right == 'String':
                return 'String'
            if node.op == 'PLUS' and left.startswith('List[') and left == right:
                return left
            numeric = ('Int', 'Float')
            if left in numeric and right in numeric:
                return 'Float' if node.op == 'DIV' or 'Float' in (left, right) else 'Int'
            if 'Unknown' not in (left, right):
                issues.append(TypeIssue('E_BINARY_TYPE', f'Cannot apply {node.op} to {left} and {right}'))
            return 'Unknown'
        if isinstance(node, Call):
            for arg in node.arguments:
                expression(arg, scope)
            return 'Unknown'
        return 'Unknown'
    def walk(nodes, scope):
        for node in nodes:
            if isinstance(node, Assign):
                scope[node.name] = expression(node.value, scope)
            elif isinstance(node, Print):
                expression(node.value, scope)
            elif isinstance(node, Return):
                expression(node.value, scope)
            elif isinstance(node, Function):
                walk(node.body, dict.fromkeys(node.parameters, 'Unknown'))
            elif isinstance(node, If):
                for condition, body in node.branches:
                    expression(condition, scope)
                    walk(body, scope.copy())
                walk(node.otherwise, scope.copy())
            elif isinstance(node, (While, Repeat, ForEach)):
                condition = node.condition if isinstance(node, While) else node.count if isinstance(node, Repeat) else node.iterable
                expression(condition, scope)
                inner = scope.copy()
                if isinstance(node, ForEach):
                    inner[node.name] = 'Unknown'
                walk(node.body, inner)
    walk(program.statements, env)
    return issues

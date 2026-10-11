"""Deterministic formatter for the supported WorldLang Next AST subset."""
from .parser import (parse, Literal, Name, Unary, Binary, ListLiteral, Index, Call,
                     Assign, Print, If, ForEach, While, Repeat, Function, Return, PRECEDENCE)

def expression(node, parent=0):
    if isinstance(node, Literal):
        if node.value is True: return 'صحيح'
        if node.value is False: return 'خطأ'
        if isinstance(node.value, str):
            import json
            return json.dumps(node.value, ensure_ascii=False)
        return str(node.value)
    if isinstance(node, Name): return node.value
    if isinstance(node, Unary): return '-' + expression(node.operand, 6)
    if isinstance(node, ListLiteral): return '[' + '، '.join(expression(x) for x in node.elements) + ']'
    if isinstance(node, Index): return expression(node.target, 6) + '[' + expression(node.index) + ']'
    if isinstance(node, Call): return node.name + '(' + '، '.join(expression(x) for x in node.arguments) + ')'
    if isinstance(node, Binary):
        prec = PRECEDENCE[node.op]
        ops = {'OR':'أو','AND':'و','EQ':'==','NE':'!=','GT':'>','LT':'<','GE':'>=','LE':'<=',
               'PLUS':'+','MINUS':'-','MUL':'*','DIV':'/'}
        value = expression(node.left, prec) + ' ' + ops[node.op] + ' ' + expression(node.right, prec + 1)
        return '(' + value + ')' if prec < parent else value
    raise ValueError('Unsupported expression')

def format_source(source):
    program = parse(source)
    lines = []
    def block(statements, depth):
        pad = '    ' * depth
        for stmt in statements:
            if isinstance(stmt, Assign):
                lines.append(pad + 'اجعل ' + stmt.name + ' = ' + expression(stmt.value))
            elif isinstance(stmt, Print):
                lines.append(pad + 'اطبع ' + expression(stmt.value))
            elif isinstance(stmt, Return):
                lines.append(pad + 'أرجع ' + expression(stmt.value))
            elif isinstance(stmt, Function):
                lines.append(pad + 'دالة ' + stmt.name + '(' + '، '.join(stmt.parameters) + '):')
                block(stmt.body, depth + 1)
            elif isinstance(stmt, ForEach):
                lines.append(pad + 'لكل ' + stmt.name + ' في ' + expression(stmt.iterable) + ':')
                block(stmt.body, depth + 1)
            elif isinstance(stmt, While):
                lines.append(pad + 'طالما ' + expression(stmt.condition) + ':')
                block(stmt.body, depth + 1)
            elif isinstance(stmt, Repeat):
                lines.append(pad + 'كرر ' + expression(stmt.count) + ' مرات:')
                block(stmt.body, depth + 1)
            elif isinstance(stmt, If):
                for index, (condition, body) in enumerate(stmt.branches):
                    lines.append(pad + ('إذا ' if index == 0 else 'وإلا إذا ') + expression(condition) + ':')
                    block(body, depth + 1)
                if stmt.otherwise:
                    lines.append(pad + 'وإلا:')
                    block(stmt.otherwise, depth + 1)
            else:
                raise ValueError('Unsupported statement')
    block(program.statements, 0)
    return '\n'.join(lines) + ('\n' if lines else '')

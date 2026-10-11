"""Portable, JSON-safe AST transport for WorldLang Next.

This is an AST exchange format, not the final typed control-flow IR ABI.
"""
import json
from dataclasses import fields, is_dataclass
from . import parser as ast

SCHEMA = 'worldlang.next.ast'
VERSION = 1
NODE_TYPES = {name: getattr(ast, name) for name in (
    'Program', 'Literal', 'Name', 'Unary', 'Binary', 'Assign', 'Print',
    'If', 'ListLiteral', 'Index', 'ForEach', 'Call', 'Function', 'Return',
    'While', 'Repeat'
)}

def encode(node):
    if is_dataclass(node) and type(node).__name__ in NODE_TYPES and type(node) is NODE_TYPES[type(node).__name__]:
        return {'node': type(node).__name__, 'fields': {
            f.name: encode(getattr(node, f.name)) for f in fields(node)
        }}
    if isinstance(node, tuple):
        return {'tuple': [encode(value) for value in node]}
    if node is None or type(node) in (str, int, float, bool):
        return node
    raise ValueError('Unsupported AST value')

def decode(value):
    if isinstance(value, dict):
        if set(value) == {'tuple'} and isinstance(value['tuple'], list):
            return tuple(decode(item) for item in value['tuple'])
        if set(value) != {'node', 'fields'} or not isinstance(value['node'], str):
            raise ValueError('Invalid AST node')
        cls = NODE_TYPES.get(value['node'])
        if cls is None or not isinstance(value['fields'], dict):
            raise ValueError('Unknown AST node')
        expected = {f.name for f in fields(cls)}
        if set(value['fields']) != expected:
            raise ValueError('Invalid AST fields')
        return cls(**{name: decode(value['fields'][name]) for name in expected})
    if value is None or type(value) in (str, int, float, bool):
        return value
    raise ValueError('Invalid AST value')

def dumps(program):
    if not isinstance(program, ast.Program):
        raise ValueError('Expected Program')
    return json.dumps({'schema': SCHEMA, 'version': VERSION, 'program': encode(program)}, ensure_ascii=False, allow_nan=False, sort_keys=True)

def loads(document):
    try:
        data = json.loads(document)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid AST document') from exc
    if not isinstance(data, dict) or set(data) != {'schema', 'version', 'program'} or data['schema'] != SCHEMA or type(data['version']) is not int or data['version'] != VERSION:
        raise ValueError('Unsupported AST document')
    result = decode(data['program'])
    if not isinstance(result, ast.Program):
        raise ValueError('Expected Program root')
    return result

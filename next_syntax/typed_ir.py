"""Portable typed instruction listing for WorldLang Next.

A deliberately conservative, versioned representation of compiled bytecode.
This is a typed stack IR, not SSA or a Mojo ABI.
"""
import json
from dataclasses import dataclass
from .bytecode import Bytecode, compile_source, validate as validate_bytecode

SCHEMA = 'worldlang.next.typed-stack-ir'
VERSION = 1
ARG_KINDS = {
    'PUSH':'constant', 'LOAD':'symbol', 'STORE':'symbol', 'TO_BOOL':'none',
    'BINARY':'operator', 'NEG':'none', 'PRINT':'none', 'JUMP':'address',
    'JUMP_IF_FALSE':'address', 'DUP':'none', 'POP':'none',
    'CHECK_REPEAT':'none', 'BUILD_LIST':'count', 'INDEX':'none',
    'ITER_INIT':'none', 'ITER_NEXT':'iterator', 'DEFINE':'function',
    'CALL':'call', 'RETURN':'none'
}

@dataclass(frozen=True)
class TypedInstruction:
    opcode: str
    operand_kind: str
    operand: object

@dataclass(frozen=True)
class TypedModule:
    version: int
    instructions: tuple

def from_bytecode(module):
    validate_bytecode(module)
    return TypedModule(VERSION, tuple(TypedInstruction(op, ARG_KINDS[op], arg) for op, arg in module.code))

def lower(source):
    return from_bytecode(compile_source(source))

def to_bytecode(module):
    if not isinstance(module, TypedModule) or type(module.version) is not int or module.version != VERSION:
        raise ValueError('Unsupported typed IR version')
    code = []
    for instruction in module.instructions:
        if not isinstance(instruction, TypedInstruction) or instruction.operand_kind != ARG_KINDS.get(instruction.opcode):
            raise ValueError('Invalid typed IR instruction')
        code.append((instruction.opcode, instruction.operand))
    result = Bytecode(1, tuple(code))
    validate_bytecode(result)
    return result

def dumps(module):
    bytecode = to_bytecode(module)
    return json.dumps({'schema': SCHEMA, 'version': VERSION,
                       'instructions': [{'opcode': op, 'operand_kind': ARG_KINDS[op], 'operand': arg}
                                        for op, arg in bytecode.code]}, ensure_ascii=False, sort_keys=True, allow_nan=False)

def loads(document):
    try:
        payload = json.loads(document)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError('Invalid typed IR JSON') from exc
    if not isinstance(payload, dict) or set(payload) != {'schema', 'version', 'instructions'} or payload['schema'] != SCHEMA or type(payload['version']) is not int or payload['version'] != VERSION or not isinstance(payload['instructions'], list):
        raise ValueError('Invalid typed IR document')
    instructions = []
    for item in payload['instructions']:
        if not isinstance(item, dict) or set(item) != {'opcode', 'operand_kind', 'operand'}:
            raise ValueError('Invalid typed IR instruction')
        instructions.append(TypedInstruction(item['opcode'], item['operand_kind'], item['operand']))
    module = TypedModule(VERSION, tuple(instructions))
    to_bytecode(module)
    return module

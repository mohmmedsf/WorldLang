"""Minimal versioned, serializable Next IR for audit and future backends.

This IR is a structural representation of parsed statements, not executable
bytecode or a compiled native artifact.
"""
from dataclasses import dataclass
from .parser import parse

IR_VERSION = 1

@dataclass(frozen=True)
class IRInstruction:
    opcode: str
    operands: tuple

@dataclass(frozen=True)
class IRModule:
    version: int
    instructions: tuple

def lower(source):
    program = parse(source)
    instructions = tuple(IRInstruction(type(statement).__name__.upper(), (statement,))
                         for statement in program.statements)
    return IRModule(IR_VERSION, instructions)

def validate(module):
    if not isinstance(module, IRModule) or module.version != IR_VERSION:
        raise ValueError('Unsupported IR version')
    allowed = {'ASSIGN', 'PRINT', 'IF', 'FOREACH', 'FUNCTION', 'RETURN', 'WHILE', 'REPEAT'}
    for instruction in module.instructions:
        if not isinstance(instruction, IRInstruction) or instruction.opcode not in allowed:
            raise ValueError('Invalid IR instruction')
        if len(instruction.operands) != 1:
            raise ValueError('Invalid IR operands')
    return True

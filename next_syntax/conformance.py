"""Shared source-to-output conformance runner for Next backends.

The Mojo backend can consume the JSON corpus independently when its API is ready.
"""
import json
from pathlib import Path
from .runtime import run
from .bytecode import Bytecode, compile_source, execute

CORPUS_SCHEMA = 'worldlang.next.conformance'
VERSION = 1

def evaluate_case(case):
    if not isinstance(case, dict) or set(case) != {'name', 'source', 'expected_output'}:
        raise ValueError('Invalid conformance case')
    if not isinstance(case['name'], str) or not isinstance(case['source'], str) or not isinstance(case['expected_output'], list) or not all(isinstance(line, str) for line in case['expected_output']):
        raise ValueError('Invalid conformance fields')
    reference = run(case['source']).output
    portable = execute(Bytecode.from_json(compile_source(case['source']).to_json()))['output']
    expected = case['expected_output']
    return {'name': case['name'], 'reference': reference, 'bytecode': portable, 'passed': reference == portable == expected}

def run_corpus(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'schema', 'version', 'cases'} or data['schema'] != CORPUS_SCHEMA or type(data['version']) is not int or data['version'] != VERSION or not isinstance(data['cases'], list):
        raise ValueError('Invalid conformance corpus')
    return [evaluate_case(case) for case in data['cases']]

# WorldLang Next bytecode and Mojo conformance draft

**Status:** experimental v1 format, not an agreed Mojo ABI.

## Build and execute

```bash
python -m next_syntax check examples/demo.wl
python -m next_syntax compile examples/demo.wl
python -m next_syntax vm examples/demo.wbc.json
python -m next_syntax vm examples/demo.wl
```

The `compile` command writes `<input-stem>.wbc.json` alongside the source. Only explicitly supported Next syntax is compiled; unsupported constructs fail rather than falling back to the AST interpreter.

## Bytecode document

```json
{"version":1,"code":[["PUSH",2],["PUSH",3],["BINARY","PLUS"],["PRINT",null]]}
```

- Each instruction is a two-element array: opcode and operand.
- Instruction addresses are zero-based indexes into `code`; a jump to `len(code)` exits.
- Stack execution is deterministic for supported pure expressions.
- `PUSH` accepts JSON strings, numbers, booleans and null.
- `LOAD` and `STORE` resolve variables; `CALL`, `DEFINE` and `RETURN` implement function frames.
- `ITER_INIT` and `ITER_NEXT` implement foreach over strings and lists.
- `TO_BOOL` converts a value to its Python-style truthiness; `AND` and `OR` compile to short-circuit jumps.
- The verifier analyzes stack height along reachable CFG edges. This is not a security sandbox and does not validate every possible runtime type.

## Proposed cross-runtime fixture format

```json
{
  "case": "arithmetic-001",
  "source": "اطبع 2 + 3",
  "expected_stdout": ["5"],
  "expected_error": null,
  "bytecode_version": 1
}
```

Before integrating Mojo, agree on numeric overflow, float precision, truthiness, Unicode indexing, errors, function declaration visibility, recursion limits and resource accounting. Python's `str()` rendering and arbitrary precision integers should not silently become a permanent ABI contract.

## Required before production
- Define stable typed IR independent of Python AST.
- Add a Python/Mojo shared conformance corpus and run it in both CI pipelines.
- Harden CFG validation further (function entry boundaries, dynamic types, malicious bytecode, resource exhaustion).
- Verify Classic compatibility with explicit regression cases.
- Agree on a migration/versioning policy with the upstream maintainer.

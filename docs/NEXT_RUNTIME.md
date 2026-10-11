# WorldLang Next — opt-in runtime prototype

This module extends the experimental lexer and parser in RFC #13.

## Example

```python
from next_syntax.runtime import run

source = """اجعل العمر = 20
إذا كان العمر أكبر من أو يساوي 18
    اطبع "بالغ"
وإلا
    اطبع "قاصر"
"""
result = run(source)
assert result.output == ["بالغ"]
```

## Tests

```sh
python -m unittest discover -s tests -v
```

## Explicit limitations

- This is a **separate** Next prototype; it does not integrate with Classic WorldLang runtime or language packs.
- Only assignments, print, conditions, numbers, strings, comparisons, arithmetic, boolean AND/OR and parentheses are supported.
- No loops, functions, imports, user input, type system, bytecode or native compiler.
- Output is collected in a list rather than printed to stdout.
- Execution step counting is a defensive limit, **not** a security sandbox.
- Classic backward compatibility is structural (no Classic files changed), not yet demonstrated through a comprehensive regression suite.
- CI and real execution must be verified before merging.

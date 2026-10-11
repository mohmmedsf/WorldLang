# WorldLang Next — staged architecture

## Current experimental pipeline
`source -> phrase lexer -> tokens -> Next AST parser -> optional static analyzer -> Python AST interpreter`

## Planned production pipeline
`source -> Unicode-aware lexer -> versioned parser -> typed AST -> semantic analysis -> language-neutral IR -> interpreter/bytecode/native backends`

## Design boundaries
- Arabic is a surface language; the IR must be language-neutral.
- A deterministic grammar is required: do not interpret arbitrary prose as executable code.
- Reserve keyword phrases and document identifier escaping before stabilizing syntax.
- Preserve source spans on all tokens and AST nodes for reliable diagnostics.
- Version syntax and language packs; do not silently translate Classic programs.
- Memory safety and native performance require separate ownership/lifetime or GC design, IR validation, and benchmarking; not implied by the Python prototype.

## Proposed next engineering milestones
1. Baseline Classic regression fixtures and translation smoke tests.
2. First-class source span model and diagnostics, not regex extraction.
3. Typed AST and explicit variable binding rules.
4. Canonical IR with validation and deterministic execution.
5. Benchmarks against a documented baseline before making performance claims.

**This document is an architecture roadmap, not an implemented compiler.**

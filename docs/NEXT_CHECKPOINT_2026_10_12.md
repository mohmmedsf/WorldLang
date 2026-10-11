# WorldLang Next — implementation checkpoint

## Delivered in this batch
- Formatter and `format` CLI with AST/idempotence tests.
- Basic LSP server with document lifecycle and syntax diagnostics using actual line/column.
- Differential interpreter/VM regression matrix and shared golden conformance corpus.
- Bytecode JSON and instruction count bounds, configurable call-depth/output-line quotas.
- Versioned AST interchange and a typed **stack** IR transport with round-trip validation.
- CLI `typed-ir` export.

## Not yet complete
- Full Classic regression and cross-version compatibility matrix.
- Typed SSA/CFG IR independent of VM opcodes.
- Robust LSP spans for static diagnostics, completion/hover/definition, incremental sync.
- Full hostile-code isolation, memory/time limits and complete fuzzing.
- Mojo integration, upstream approval, native packaging.

## Validation
Run `python -m unittest discover -s tests -p 'test_next_*.py' -v`.
The last previously confirmed green CI was run 101, prior to the latest batch. Check CI for the current head before treating this checkpoint as validated.

## CLI
```bash
python -m next_syntax format program.wl
python -m next_syntax typed-ir program.wl
python -m next_syntax.lsp
```
All features are opt-in; Classic remains unchanged by these changes.

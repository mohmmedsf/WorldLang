# WorldLang Next Developer Tools (experimental)

## Formatter
```bash
python -m next_syntax format example.wl
```
Prints canonical Arabic source to stdout without overwriting files. The formatter parses first; invalid source fails.

## LSP server
```bash
python -m next_syntax.lsp
```
Communicates over standard input/output using LSP Content-Length framing. Current capabilities:
- `initialize`, `shutdown`, `exit`
- Full document synchronization (`didOpen`, `didChange`, `didClose`)
- `publishDiagnostics` for syntax/static-analysis errors

Current limitations: diagnostics use a placeholder document range (0:0–0:1), not accurate source spans; no hover, completion, symbols, incremental edits or cancellation. The server is an editor integration prototype, not yet a production LSP.

## JSON toolchain
```bash
python -m next_syntax ast-json example.wl
python -m next_syntax diagnostics-json example.wl
python -m next_syntax compile example.wl
python -m next_syntax vm example.wbc.json
```

`ast-json` exports a versioned transport AST. It is **not** a typed SSA/CFG IR or the finalized Mojo interface.

## Tests
```bash
python -m unittest discover -s tests -p 'test_next_*.py' -v
```

All commands are opt-in and do not replace the Classic WorldLang interpreter.

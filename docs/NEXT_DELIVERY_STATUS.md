# WorldLang Next integration delivery status

This document records **implemented** work separately from proposed work. Do not treat it as a release announcement.

## Implemented on this branch
- Hybrid Arabic Next lexer/parser, AST interpreter, analysis and type prototype.
- Experimental stack bytecode VM with CFG stack-height analysis, functions, lists, loops and boolean short-circuit.
- CLI commands: run, check, lint, tokens, compile, vm, ast-json, diagnostics-json.
- Versioned AST JSON exchange format (not a typed IR).
- JSON diagnostics adapter for editor integrations (not an LSP server).
- Shared JSON golden conformance corpus and Python interpreter-vs-VM differential runner.
- Automated GitHub Actions Next test suite.

## Not implemented / not verified
- Stable language-neutral typed SSA/CFG IR, full optimizer and native backend.
- Mojo interpreter integration, Linux Mojo smoke tests or an agreed upstream bytecode ABI.
- Full LSP server, formatter, VS Code extension and offline installer.
- Full Classic compatibility, malicious bytecode isolation and comprehensive resource budgets.
- Upstream merge approval.

## Integration requirements
1. Obtain @ZiadRabea's Mojo runtime entry points and preferred interface.
2. Agree on grammar and semantics and turn the corpus into cross-engine golden fixtures.
3. Run both backends against the same corpus in CI.
4. Review source-level compatibility and all security/resource limits.
5. Open upstream review only when those gates pass.

This branch is an experimental integration prototype; avoid enabling it as Classic's default.

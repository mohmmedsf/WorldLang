# WorldLang Next — Quantum Leap Integration Plan (v0.2 proposal)

**Owner review required.** This is an engineering execution plan, not a claim of production readiness or an approved Mojo integration.

## Definition of done
- One opt-in Next frontend with documented grammar, source spans and deterministic diagnostics.
- A language-neutral, versioned IR with explicit serialization and round-trip fixtures.
- Verified bytecode lowering and an execution engine with deterministic error handling and configurable resource budgets.
- CLI compile/run/check/lint/vm plus machine-readable diagnostics and stable exit codes.
- Automated Classic/Next compatibility, AST/VM differential tests and malformed-bytecode adversarial tests.
- A conformance bundle ready for the upstream maintainer's Mojo runtime to consume.
- A green integration CI and a reviewed, mergeable upstream PR **only after** maintainer approval.

## Workstreams (parallelizable)

### A. Language semantics and grammar
- Freeze hybrid syntax in an RFC with Arabic/English token aliases and whitespace/indentation rules.
- Document precedence, implicit delimiters, functions, closures, scopes, lists, indexing and truthiness.
- Add golden parser tests, Unicode/RTL edge cases and error-recovery fixtures.
- Compatibility gate: Classic remains default, Next opt-in.

### B. Typed IR and backend architecture
- Define `worldlang.ir.v1` schema: module/functions/basic blocks/instructions/types/source spans.
- Lower AST to IR, verify dominance/terminators and consistent symbol resolution.
- Keep bytecode as a backend of the IR, not the long-term frontend interface.
- Generate canonical fixtures to be consumed by Python and Mojo.

### C. VM and safety
- CFG stack verification, function-region isolation, malformed-JSON bounds, operand type checks.
- Fix semantic drift between interpreter and VM, including implicit returns, boolean short circuit, Unicode and arithmetic.
- Configurable instruction, call-depth, memory and output limits.
- Property-based or generative bytecode fuzz cases and differential execution tests.

### D. Developer experience
- CLI `compile`, `vm`, `run`, `check`, `lint`, `tokens`, `format` and machine-readable diagnostics.
- Language Server Protocol prototype (diagnostics, symbols, completion, hover).
- VS Code syntax highlighting, snippets and integration documentation.
- Offline release artifacts and platform smoke tests.

### E. CI, Classic compatibility and maintainer handoff
- Matrix for Python versions and supported OSes; smoke tests for Classic entry points.
- Golden source/AST/IR/bytecode/output conformance corpus.
- Reproducible integration artifacts, changelog, migration guide and version policy.
- Discuss IR/Mojo interface with @ZiadRabea before declaring cross-runtime compatibility.

## Execution gates

| Gate | Required evidence |
| --- | --- |
| G0 | Existing CI green, no regressions |
| G1 | Grammar RFC and parser/semantic golden tests |
| G2 | Versioned IR schema + verified round-trip |
| G3 | AST/VM parity and hardened bytecode verifier |
| G4 | Developer CLI/LSP + packaging smoke tests |
| G5 | Classic compatibility + Mojo fixture contract reviewed |
| G6 | Upstream maintainer review and integration decision |

## Current baseline
- Hybrid lexer/parser/interpreter, analyzer, type prototype, structural IR, bytecode VM, CLI and CI are present.
- Short-circuit boolean VM, CFG verification and JSON bytecode CLI were added in this integration branch.
- Last CI run before this plan: 125/126 passed; an obsolete rejection test has been updated and must be rerun.
- **Not yet delivered:** true portable typed IR, LSP, formatter, Mojo backend, full adversarial verifier and verified Classic compatibility.

## Contribution policy
Develop in `feature/worldlang-next-foundation` with small testable commits; present one consolidated draft PR for review. Do not force-merge, rename upstream's main branch, or claim Mojo compatibility before running its tests.

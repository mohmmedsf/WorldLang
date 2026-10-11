# WorldLang Next Foundation — integration proposal

Status: **experimental, review requested**. This branch is a consolidated snapshot of the stacked Next prototypes. It does not replace Classic or imply upstream acceptance.

## Scope
- Opt-in hybrid Arabic syntax, lexer, parser, AST and interpreter.
- Source diagnostics, static analysis, initial type inference and structural IR.
- CLI and compatibility test prototypes.
- JSON-serializable stack bytecode and experimental Python VM: arithmetic, variables, conditionals, loops, collections, foreach and scoped function calls.

## Compatibility and adoption
1. Keep the existing Classic entry points and default behavior unchanged.
2. Introduce Next as an explicitly selected mode until grammar and semantics are approved.
3. Treat JSON bytecode as an **experimental versioned transport**, not a frozen cross-runtime ABI.
4. Do not merge into upstream main without maintainer review and compatibility verification.
5. This branch is intentionally based on the fork's stacked implementation, so its full diff must be reviewed before upstream merge.

## Proposed Mojo interoperability contract (NOT YET AGREED)
- Separate frontend (source -> typed IR) from backend (IR -> bytecode/VM).
- Document primitive values, numeric operations, truthiness, string indexing, list behavior, errors, evaluation order, function scope, recursion and resource limits.
- Publish canonical JSON fixtures: source, expected diagnostics, normalized IR, bytecode and expected output.
- Add cross-engine conformance tests (Python reference vs Mojo interpreter) **after** the Mojo format and APIs are shared.
- Keep IR/bytecode versioning explicit; reject unknown versions and invalid control flow.

## Open engineering blockers
- Bytecode verifier is currently linear; it must be replaced with control-flow-aware stack analysis and stronger validation of malformed modules.
- The IR is structural and not yet a language-independent lowering contract.
- Bytecode and reference interpreter have not been proven semantically equivalent for every language feature.
- Mojo integration cannot be implemented or verified without the maintainer's Mojo interpreter interface.
- Classic compatibility, security limits and release packaging need a broader regression matrix.

## Suggested upstream review sequence
1. Approve the opt-in syntax and backwards-compatibility policy.
2. Agree on typed IR and Mojo/Python boundary.
3. Review conformance fixtures and safety/verification requirements.
4. Merge reviewed components incrementally; keep experimental VM opt-in.

## Maintainer coordination
@ZiadRabea: Thanks for your encouraging feedback. This consolidated branch is prepared for review, not a request to merge all experimental changes blindly. Could you share the planned Mojo frontend/IR interface or bytecode shape, and the preferred target branch? We can then align the compatibility fixtures before proposing a production pipeline integration.

# WorldLang Classic → Next compatibility assessment (initial)

**Status: inventory and migration design, not proof of behavioral equivalence.**

The upstream Classic lexer uses Python modules under `bin/`, loads language-specific keyword JSON via `KWLoader.get_keywords_for(language)`, ignores leading whitespace during ordinary tokenization, and recognizes `;` and newlines as statement boundaries. Its parser defines nodes including `IfNode`, `ForNode`, `WhileNode`, `FuncDefNode`, `CallNode`, `ReturnNode` and `ListNode`.

The experimental Next implementation is in `next_syntax/`. It uses indentation to delimit blocks and a separate AST and runtime. It is **not** a drop-in replacement.

| Capability | Classic (observed implementation) | Next (prototype) | Migration status |
|---|---|---|---|
| Variable assignment | VarAssignNode | Assign | Semantics not formally compared |
| If/else | IfNode | If | Different block syntax |
| While | WhileNode | While | Runtime parity unverified |
| Functions | FuncDefNode/CallNode | Function/Call | Scope and return semantics may differ |
| Lists | ListNode | ListLiteral | Partial |
| For | ForNode (range-style) | ForEach/Repeat | Not equivalent |
| Keyword localization | JSON language packs | Arabic phrases in lexer | Not integrated |
| Blocks | Explicit do/end keywords | Indentation | Migration required |
| Classic programs | Existing interpreter | Not supported as-is | Do not route automatically |

## Safe integration strategy

1. Keep the Classic entry point as default and add an explicit Next CLI flag or command.
2. Capture golden Classic execution outputs for representative examples **before** any bridging.
3. Build a compatibility table of Classic token/node semantics and errors.
4. Introduce a versioned language mode with no automatic guessing based on whitespace.
5. Add differential tests against Classic for the overlapping subset; record intentional differences.
6. Only then consider shared IR or language-pack adapters.

No Classic files are modified by this branch.

"""Command line entry point for the experimental WorldLang Next interpreter."""
import argparse
import sys
from pathlib import Path
from .lexer import lex, SyntaxErrorNext
from .parser import parse
from .analyzer import analyze
from .diagnostics import syntax_diagnostic
from .runtime import run, RuntimeErrorNext
from .bytecode import Bytecode, compile_source, execute

def main(argv=None):
    parser = argparse.ArgumentParser(prog='python -m next_syntax')
    parser.add_argument('command', choices=('run', 'check', 'tokens', 'lint', 'compile', 'vm'))
    parser.add_argument('file', type=Path)
    parser.add_argument('--max-steps', type=int, default=100000)
    args = parser.parse_args(argv)
    try:
        source = args.file.read_text(encoding='utf-8-sig')
        if args.command == 'compile':
            module = compile_source(source)
            target = args.file.with_suffix('.wbc.json')
            target.write_text(module.to_json(), encoding='utf-8')
            print(target)
        elif args.command == 'vm':
            if args.file.name.endswith('.wbc.json'):
                module = Bytecode.from_json(source)
            else:
                module = compile_source(source)
            result = execute(module, max_steps=args.max_steps)
            for line in result['output']:
                print(line)
        elif args.command in ('check', 'lint'):
            syntax_error = syntax_diagnostic(source)
            if syntax_error is not None:
                print(syntax_error.render(), file=sys.stderr)
                return 1
            issues = analyze(source)
            if issues:
                for issue in issues:
                    print(f'{issue.code}: {issue.message}', file=sys.stderr)
                return 1
            ast = parse(source)
            print(f'OK: {len(ast.statements)} top-level statements')
        elif args.command == 'tokens':
            for token in lex(source):
                print(f'{token.line}:{token.column} {token.kind} {token.value}')
        else:
            result = run(source, max_steps=args.max_steps)
            for line in result.output:
                print(line)
        return 0
    except (OSError, UnicodeError, SyntaxErrorNext, RuntimeErrorNext, ValueError) as exc:
        print(f'WorldLang Next: {exc}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())

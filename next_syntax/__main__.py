"""Command line entry point for the experimental WorldLang Next interpreter."""
import argparse
import json
import sys
from pathlib import Path
from .lexer import lex, SyntaxErrorNext
from .parser import parse
from .runtime import run, RuntimeErrorNext

def main(argv=None):
    parser = argparse.ArgumentParser(prog='python -m next_syntax')
    parser.add_argument('command', choices=('run', 'check', 'tokens'))
    parser.add_argument('file', type=Path)
    parser.add_argument('--max-steps', type=int, default=100000)
    args = parser.parse_args(argv)
    try:
        source = args.file.read_text(encoding='utf-8-sig')
        if args.command == 'check':
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

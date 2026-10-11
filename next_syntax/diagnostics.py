"""Source-aware diagnostic formatter for the opt-in Next frontend."""
from dataclasses import dataclass
from .lexer import SyntaxErrorNext, lex
from .parser import parse

@dataclass(frozen=True)
class SourceDiagnostic:
    code: str
    message: str
    line: int
    column: int
    snippet: str

    def render(self):
        pointer = ' ' * (max(self.column, 1) - 1) + '^'
        return f'{self.code} at {self.line}:{self.column}: {self.message}\n{self.snippet}\n{pointer}'

def syntax_diagnostic(source: str):
    """Return first lexical or parsing error with best available source position."""
    try:
        parse(source)
        return None
    except SyntaxErrorNext as exc:
        import re
        message = str(exc)
        match = re.search(r'Line (\d+)(?:, column (\d+))?', message)
        line = int(match.group(1)) if match else 1
        column = int(match.group(2)) if match and match.group(2) else 1
        lines = source.splitlines()
        snippet = lines[line-1] if 0 < line <= len(lines) else ''
        return SourceDiagnostic('E_SYNTAX', message, line, column, snippet)

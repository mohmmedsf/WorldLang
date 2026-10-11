"""Editor diagnostics with source ranges where available."""
from .diagnostics import syntax_diagnostic
from .analyzer import analyze

def diagnostics(source):
    syntax = syntax_diagnostic(source)
    if syntax is not None:
        return [{'severity': 'error', 'code': syntax.code, 'message': syntax.message,
                 'line': syntax.line, 'column': syntax.column}]
    return [{'severity': 'error', 'code': issue.code, 'message': issue.message,
             'line': 1, 'column': 1} for issue in analyze(source)]

"""JSON diagnostics for editor integrations (experimental protocol)."""
from .diagnostics import syntax_diagnostic
from .analyzer import analyze

def diagnostics(source):
    syntax = syntax_diagnostic(source)
    if syntax is not None:
        return [{'severity': 'error', 'code': 'SYNTAX', 'message': syntax.render()}]
    return [{'severity': 'error', 'code': issue.code, 'message': issue.message} for issue in analyze(source)]

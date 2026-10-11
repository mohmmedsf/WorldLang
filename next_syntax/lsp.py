"""Minimal JSON-RPC Language Server Protocol server for WorldLang Next.

Provides document synchronization and diagnostics. No external dependencies.
"""
import json
import sys
from .editor import diagnostics

def read_message(stream):
    headers = {}
    while True:
        line = stream.readline()
        if not line:
            return None
        if line in (b'\r\n', b'\n'):
            break
        key, sep, value = line.decode('ascii').partition(':')
        if not sep:
            raise ValueError('Malformed LSP header')
        headers[key.lower()] = value.strip()
    length = int(headers.get('content-length', '-1'))
    if length < 0 or length > 4_000_000:
        raise ValueError('Invalid LSP content length')
    return json.loads(stream.read(length).decode('utf-8'))

def send(stream, payload):
    raw = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    stream.write(b'Content-Length: ' + str(len(raw)).encode('ascii') + b'\r\n\r\n' + raw)
    stream.flush()

def diagnostic_items(source):
    return [{'range': {'start': {'line': 0, 'character': 0}, 'end': {'line': 0, 'character': 1}},
             'severity': 1, 'source': 'worldlang-next', 'code': d['code'], 'message': d['message']}
            for d in diagnostics(source)]

def serve(inp=None, out=None):
    inp = inp or sys.stdin.buffer
    out = out or sys.stdout.buffer
    documents = {}
    while True:
        message = read_message(inp)
        if message is None:
            return
        method = message.get('method')
        params = message.get('params') or {}
        if method == 'initialize':
            send(out, {'jsonrpc':'2.0', 'id':message['id'], 'result': {
                'capabilities': {'textDocumentSync': 1},
                'serverInfo': {'name': 'worldlang-next-lsp', 'version': '0.1.0'}}})
        elif method == 'shutdown':
            send(out, {'jsonrpc':'2.0', 'id':message['id'], 'result':None})
        elif method == 'exit':
            return
        elif method in ('textDocument/didOpen', 'textDocument/didChange', 'textDocument/didClose'):
            doc = params['textDocument']
            uri = doc['uri']
            if method == 'textDocument/didOpen':
                documents[uri] = doc['text']
            elif method == 'textDocument/didChange':
                documents[uri] = params['contentChanges'][-1]['text']
            else:
                documents.pop(uri, None)
            send(out, {'jsonrpc':'2.0', 'method':'textDocument/publishDiagnostics',
                       'params': {'uri': uri, 'diagnostics': diagnostic_items(documents[uri]) if uri in documents else []}})
        elif 'id' in message:
            send(out, {'jsonrpc':'2.0', 'id':message['id'],
                       'error': {'code': -32601, 'message': 'Method not found'}})

if __name__ == '__main__':
    serve()

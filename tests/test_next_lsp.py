import io
import json
import unittest
from next_syntax.lsp import read_message, send, serve

class LSPTests(unittest.TestCase):
    def message(self, payload):
        stream = io.BytesIO()
        send(stream, payload)
        return stream.getvalue()

    def test_unicode_framing(self):
        data = {'jsonrpc':'2.0', 'method':'test', 'params':{'text':'أهلا'}}
        self.assertEqual(read_message(io.BytesIO(self.message(data))), data)

    def test_initialize_open_close(self):
        uri = 'file:///example.wl'
        commands = [
            {'jsonrpc':'2.0', 'id':1, 'method':'initialize', 'params':{}},
            {'jsonrpc':'2.0', 'method':'textDocument/didOpen', 'params':{'textDocument':{'uri':uri, 'text':'اطبع @'}}},
            {'jsonrpc':'2.0', 'method':'textDocument/didClose', 'params':{'textDocument':{'uri':uri}}},
            {'jsonrpc':'2.0', 'id':2, 'method':'shutdown'},
            {'jsonrpc':'2.0', 'method':'exit'},
        ]
        incoming = io.BytesIO(b''.join(self.message(cmd) for cmd in commands))
        outgoing = io.BytesIO()
        serve(incoming, outgoing)
        outgoing.seek(0)
        replies = [read_message(outgoing) for _ in range(4)]
        self.assertEqual(replies[0]['result']['capabilities']['textDocumentSync'], 1)
        self.assertEqual(replies[1]['params']['diagnostics'][0]['code'], 'SYNTAX')
        self.assertEqual(replies[2]['params']['diagnostics'], [])
        self.assertIsNone(replies[3]['result'])

    def test_reject_oversized_payload(self):
        with self.assertRaises(ValueError):
            read_message(io.BytesIO(b'Content-Length: 5000000\r\n\r\n'))

if __name__ == '__main__':
    unittest.main()

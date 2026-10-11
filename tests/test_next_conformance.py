import unittest
from pathlib import Path
from next_syntax.conformance import run_corpus

class ConformanceTests(unittest.TestCase):
    def test_reference_and_vm_match_golden_cases(self):
        path = Path(__file__).resolve().parents[1] / 'conformance' / 'next-v1.json'
        results = run_corpus(path)
        self.assertGreaterEqual(len(results), 6)
        self.assertTrue(all(item['passed'] for item in results), results)

if __name__ == '__main__':
    unittest.main()

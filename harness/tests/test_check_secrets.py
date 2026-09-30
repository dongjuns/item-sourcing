"""비밀 검사에서 테스트 예시와 실제 설정 값을 구분한다."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_secrets import contains_secret


class SecretTests(unittest.TestCase):
    def test_configured_secret_always_blocks(self) -> None:
        self.assertTrue(contains_secret(b"prefix private-value suffix", [b"private-value"], "app.py"))
        self.assertFalse(contains_secret(b"safe content", [b"private-value"], "app.py"))

    def test_example_exception_is_limited_to_one_test_file(self) -> None:
        content = b"https://" + b"user:" + b"password@" + b"www.domeggook.com/63749955"
        path = "backend/tests/adapters/test_domeggook.py"
        self.assertFalse(contains_secret(content, [], path))
        self.assertTrue(contains_secret(content, [], "README.md"))
        self.assertTrue(contains_secret(content, [b"password"], path))

    def test_token_and_private_key_patterns_block(self) -> None:
        self.assertTrue(contains_secret(b"sk-" + b"x" * 32, [], "app.py"))
        self.assertTrue(contains_secret(b"-----BEGIN " + b"PRIVATE KEY-----", [], "app.py"))


if __name__ == "__main__":
    unittest.main()

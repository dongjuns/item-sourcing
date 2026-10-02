"""언어 규칙과 비밀 파일 검사 제외 동작을 검증한다."""

from __future__ import annotations

import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path

from harness.check_language import check_files, find_violations, repository_files


class LanguageTests(unittest.TestCase):
    def test_english_korean_and_symbols_are_allowed(self) -> None:
        content = "# 설계 Design v1\n가격 10,000원 → 확인 · ≤ 3\n\u1100\u1161\n"
        self.assertEqual(find_violations(content), [])

    def test_other_language_letters_are_rejected(self) -> None:
        for character in ("\u4e2d", "\u3042", "\u30a2", "\uff71", "\u0410", "\u03b1"):
            with self.subTest(codepoint=ord(character)):
                self.assertEqual(len(find_violations(character)), 1)

    def test_extended_ideographs_and_radicals_are_rejected(self) -> None:
        for character in ("\U00020000", "\ufa11", "\u2f00", "\u3007"):
            with self.subTest(codepoint=ord(character)):
                self.assertEqual(len(find_violations(character)), 1)

    def test_mixed_text_reports_exact_location(self) -> None:
        issues = find_violations("문서\n제목\u65e5")
        self.assertEqual((issues[0].line, issues[0].column), (2, 3))
        self.assertEqual(issues[0].codepoint, "U+65E5")

    def test_combining_language_marks_are_rejected(self) -> None:
        self.assertEqual(len(find_violations("e\u0301")), 1)

    def test_error_output_does_not_contain_original_line(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            document = root / "sample.md"
            document.write_text("sensitive-example-\u4e2d", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                self.assertEqual(check_files(root, [document]), 1)
            self.assertNotIn("sensitive-example", output.getvalue())
            self.assertNotIn("\u4e2d", output.getvalue())

    def test_non_utf8_source_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            document = root / "sample.py"
            document.write_bytes(b"\xff")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(check_files(root, [document]), 1)


class RepositoryTests(unittest.TestCase):
    def test_tracked_untracked_ignored_deleted_and_symlink_files(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            (root / ".gitignore").write_text(".env\nignored.md\n", encoding="utf-8")
            (root / "tracked.md").write_text("문서", encoding="utf-8")
            (root / "deleted.md").write_text("삭제 예정", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.md", "deleted.md"], cwd=root, check=True)
            (root / "deleted.md").unlink()
            (root / "untracked.py").write_text("pass", encoding="utf-8")
            (root / "ignored.md").write_text("\u4e2d", encoding="utf-8")
            (root / ".env").write_text("SAMPLE_SECRET=example", encoding="utf-8")
            (root / ".env.example").write_text("SAMPLE_SECRET=", encoding="utf-8")
            (root / "linked.md").symlink_to(root / "ignored.md")
            names = {path.name for path in repository_files(root)}
            self.assertEqual(names, {"tracked.md", "untracked.py", ".env.example", ".gitignore"})


if __name__ == "__main__":
    unittest.main()

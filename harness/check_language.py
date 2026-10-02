"""코드와 문서에서 영어·한글 외 언어 문자를 검사한다."""

from __future__ import annotations

import argparse
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path


SOURCE_SUFFIXES = frozenset(
    {
        ".md", ".mdx", ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx",
        ".mjs", ".cjs", ".json", ".yaml", ".yml", ".toml", ".ini",
        ".sql", ".sh", ".bash", ".zsh", ".html", ".htm", ".css",
        ".scss", ".svg", ".xml", ".txt", ".conf",
    }
)
SOURCE_NAMES = frozenset({"Makefile", "Dockerfile", ".env.example", ".gitignore", ".dockerignore"})
HANGUL_RANGES = (
    (0x1100, 0x11FF), (0x3130, 0x318F), (0xA960, 0xA97F),
    (0xAC00, 0xD7AF), (0xD7B0, 0xD7FF), (0xFFA0, 0xFFDC),
)
CJK_SYMBOL_RANGES = ((0x2E80, 0x2FFF),)


@dataclass(frozen=True)
class Violation:
    line: int
    column: int
    codepoint: str
    name: str


def is_allowed(character: str) -> bool:
    """영어·한글과 일반 숫자·기호·공백만 허용한다."""
    point = ord(character)
    if point < 128:
        return True
    if any(start <= point <= end for start, end in HANGUL_RANGES):
        return True
    if any(start <= point <= end for start, end in CJK_SYMBOL_RANGES):
        return False
    category = unicodedata.category(character)
    if category[0] in {"L", "M"} or category == "Nl":
        return False
    return True


def find_violations(content: str) -> list[Violation]:
    """문자 자체나 원문을 출력하지 않고 위치·문자 코드만 반환한다."""
    violations: list[Violation] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for column, character in enumerate(line, start=1):
            if not is_allowed(character):
                violations.append(
                    Violation(
                        line_number, column, f"U+{ord(character):04X}",
                        unicodedata.name(character, "UNKNOWN"),
                    )
                )
    return violations


def repository_files(root: Path) -> list[Path]:
    """Git 추적·미추적 파일을 검사하되 ignored 파일과 삭제 파일은 제외한다."""
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, capture_output=True, check=True,
    )
    paths = {Path(name.decode("utf-8")) for name in result.stdout.split(b"\0") if name}
    return [
        root / path
        for path in sorted(paths)
        if (path.suffix.lower() in SOURCE_SUFFIXES or path.name in SOURCE_NAMES)
        and (root / path).is_file()
        and not (root / path).is_symlink()
    ]


def check_files(root: Path, paths: list[Path]) -> int:
    errors = 0
    for path in paths:
        relative = path.relative_to(root)
        try:
            violations = find_violations(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            print(f"{relative}: UTF-8 파일 읽기 실패", file=sys.stderr)
            errors += 1
            continue
        for violation in violations:
            print(
                f"{relative}:{violation.line}:{violation.column}: "
                f"허용하지 않는 언어 문자 {violation.codepoint} {violation.name}",
                file=sys.stderr,
            )
        errors += len(violations)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="코드·문서의 영어·한글 규칙 검사")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root.resolve()
    try:
        paths = repository_files(root)
    except (OSError, UnicodeError, subprocess.CalledProcessError):
        print("Git 파일 목록을 읽을 수 없습니다.", file=sys.stderr)
        return 2
    errors = check_files(root, paths)
    if errors:
        print(f"언어 검사 실패: {errors}건", file=sys.stderr)
        return 1
    print(f"언어 검사 통과: {len(paths)}개 파일")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

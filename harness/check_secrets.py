"""공유 대상에서 실제 설정된 비밀과 주요 토큰 형식을 검사한다."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = re.compile(
    rb"(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    rb"github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|"
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
)
AUTH_URL = re.compile(rb"https?://[^\s/@:]+:[^\s/@]+@")


def contains_secret(data: bytes, values: list[bytes], path: str) -> bool:
    if any(value and value in data for value in values) or TOKENS.search(data):
        return True
    for match in AUTH_URL.finditer(data):
        fixture = (
            path == "backend/tests/adapters/test_domeggook.py"
            and match.group() == b"https://" + b"user:" + b"password@"
        )
        if not fixture:
            return True
    return False


def configured_secrets() -> list[bytes]:
    sys.path.insert(0, str(ROOT / "backend"))
    from app.core.config import Config

    config = Config()
    return [
        value.get_secret_value().encode()
        for value in (
            config.domeggook_api_key,
            config.openai_api_key,
        )
        if value.get_secret_value()
    ]


def main() -> int:
    try:
        values = configured_secrets()
    except Exception:
        print("비밀 검사 설정 실패. 백엔드 의존성과 환경설정을 확인하세요.")
        return 2
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    ).split(b"\0")
    findings = []
    count = 0
    for encoded in paths:
        if not encoded:
            continue
        name = encoded.decode()
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            continue
        count += 1
        if contains_secret(path.read_bytes(), values, name):
            findings.append(name)
    if findings:
        print("비밀 검사 실패. 파일 경로만 표시:")
        print("\n".join(findings))
        return 1
    print(f"비밀 검사 통과: {count}개 파일. 비밀 값은 출력하지 않음.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

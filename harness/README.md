# 코드와 문서 언어 검사

코드와 Markdown은 영어와 한글만 사용한다. 일반 숫자·공백·문장부호·수식·화살표 등 기호는 허용한다. 영어 알파벳과 한글 이외의 언어 문자, 결합 언어 문자, CJK 부수는 검사 실패로 처리한다. UTF-8을 읽을 수 없는 코드·문서도 실패다.

## 실행

```bash
make check-design
```

Python 표준 라이브러리와 Git만 사용하며 별도 패키지를 설치하지 않는다. 다른 디렉터리를 검사하려면 python3 harness/check_language.py --root <경로>를 실행한다.

| 명령 | 동작 |
| --- | --- |
| make check-language | 코드·문서 문자 검사 |
| make test-harness | 검사 허용·차단·Git 제외 규칙 테스트 |
| make check-design | 검사기 테스트와 저장소 언어 검사 모두 실행 |

## 검사 범위와 비밀 보호

Git의 추적 파일과 ignore되지 않은 미추적 파일 중 Markdown·Python·TypeScript·JavaScript·JSON·YAML·SQL·셸·웹 소스·설정·일반 텍스트, Makefile·Dockerfile·.env.example·.gitignore·.dockerignore를 검사한다. 목록은 check_language.py의 SOURCE_SUFFIXES·SOURCE_NAMES에서 관리한다. 삭제 파일과 심볼릭 링크는 제외한다.

ignore된 .env·의존성·로컬 산출물은 검사 목록에 들어가지 않는다. 이미 추적한 파일은 .gitignore만으로 제외되지 않는다. 이 검사기는 비밀 탐지 도구가 아니므로 비밀을 추적하지 않는 규칙은 별도로 지킨다.

오류는 파일 경로·행·열·Unicode 코드와 영문 문자 이름만 출력한다. 잘못된 문자나 주변 원문을 출력하지 않는다. 올바른 문구로 수정한 뒤 다시 실행하며 자동 치환은 하지 않는다.

## 적용 기준

문서 수정 후 make check-design을 통과해야 한다. 향후 개발 골격의 make lint와 CI에도 이 명령을 포함한다. 현재는 로컬 검사 명령과 테스트를 제공하며 Git 훅이나 원격 CI가 자동 적용된 상태는 아니다. 이 검사는 번역 품질·내용 정확성·화면 렌더링을 보장하지 않으므로 문서 검토도 수행한다.

## 비밀 검사

make check-secrets는 백엔드 config에서 읽은 실제 키·비밀번호와 주요 토큰 형식을 공유 대상 파일에서 찾는다. 키 값이나 해당 줄은 출력하지 않는다. make lint에도 포함했다. 실행 전에 backend/.venv를 준비한다. 거부 URL 테스트의 가짜 인증정보 예외는 해당 파일의 고정 예시만 허용하고 실제 설정된 값이 포함되면 예외 없이 실패한다.

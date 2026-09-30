# 상품 소싱과 AI 콘텐츠 검토 도구

사용자가 입력한 도매꾹 상품 상세 URL에서 상품 정보와 이미지를 수집하고, AI 상세페이지·썸네일을 생성한 뒤 사람이 검토·편집·확정하는 1인용 도구다. 판매 채널 등록은 후속 범위로 보류했다.

현재는 개발 중인 초안이다. 백엔드·프론트 핵심 코드가 작성됐지만 기능 테스트, 프론트 API 타입 생성·빌드, 화면 통합 검증은 아직 완료하지 않았다. 실제 도매꾹 수집·유료 AI 호출·PostgreSQL 실실행도 검증 전이다. 자세한 상태는 [할 일](docs/TASKS.md)과 [문제 기록](docs/development-issues.md)을 따른다.

## 구성

- `backend/app/adapters/sources/`: 소싱처의 URL 판별·조회·표준화. 도매꾹은 상품 조회만 수행한다.
- `backend/app/adapters/ai/`: 텍스트·이미지 생성 API와 명시적인 연습용 구현.
- `backend/app/services/`: 수집, 이미지 저장, 생성, 예산 관리, 검토·확정.
- `backend/app/db/migrations/`: 초기 DB 마이그레이션. 로컬 SQLite 검증 경로와 PostgreSQL 타입을 포함한다.
- `frontend/src/`: 로그인, 상품 입력·목록·수집 결과, 생성·검토, 설정 화면.
- `backend/prompts/`: 생성 프롬프트. 문구 수정은 여기서 한다.
- `harness/`: 코드·문서의 영어·한글 사용 검사와 테스트.

## 로컬 백엔드 개발

Python 3.12 이상과 uv가 필요하다. `.env.example`을 참고해 저장소 루트의 `.env`를 설정한다. 이미 있는 `.env`를 덮어쓰지 않는다.

환경설정은 `backend/app/core/config.py`를 따른다. 인증에는 `BASIC_AUTH_PASSWORD` 설정이 필요하다. `SOURCE_MODE=mock`, `AI_MODE=mock`에서는 연습용 데이터와 콘텐츠를 사용한다. 실제 도매꾹 조회는 `SOURCE_MODE=live`와 `DOMEGGOOK_API_KEY`를 사용한다. 실제 AI 호출에는 `OPENAI_API_KEY`, `AI_TEXT_MODEL`, `AI_IMAGE_MODEL`, `AI_MODE=live`와 DB의 일·월 예산 및 가격 근거 설정이 필요하다.

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run python -m app.db.seed
uv run uvicorn app.main:app --reload
```

기본 DB는 로컬 SQLite다. 운영용 PostgreSQL·Docker 실행 구성은 아직 완성되지 않았다. 프론트의 `npm run gen:api`에 필요한 스크립트와 생성 타입도 후속 작업으로 남아 있어 현재 프론트 빌드 성공을 보장하지 않는다.

## 현재 실행 가능한 검사

```bash
make check-design
cd backend
uv run ruff check app
uv run ruff format --check app
uv run mypy app
```

언어 검사와 ruff 검사는 통과를 확인했다. mypy는 모듈 경로 중복 오류로 중단되며 수정 중이다. 기능 테스트와 루트 `make lint`, `make test` 명령은 아직 준비되지 않았다. 초안 PR은 검토용이며 머지 전 해당 검증을 완료해야 한다.

## 비밀과 문제 기록

실제 키·비밀번호·DB 접속 정보는 `.env`에만 두며 커밋하지 않는다. `.env`, 로컬 DB, 이미지 파일, 로컬 로그는 Git 제외 대상이다. 실제 수집 응답을 fixture로 보관할 때는 인증정보를 제거한다. 현재 도매꾹 fixture는 실제 녹화 응답이 아닌 예시임을 표시했다.

발생 문제는 `logs/development-issues.log`와 [개발 문제 문서](docs/development-issues.md)에 같은 ID로 기록한다. 로그는 로컬에만 보관한다. [설계](docs/PLAN.md), [요구사항](docs/requirements.md), [DB 설계](docs/db-schema.md), [인수인계](docs/handover.md)를 함께 참고한다.

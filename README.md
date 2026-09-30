# 상품 소싱과 AI 콘텐츠 검토 도구

사용자가 입력한 도매꾹 상품 상세 URL에서 상품 정보와 이미지를 수집하고, AI 상세페이지·썸네일을 생성한 뒤 사람이 검토·편집·확정하는 1인용 도구다. 판매 채널 등록은 후속 범위로 보류했다.

현재는 개발 중인 초안이다. 주신 상품 URL의 실제 수집·이미지 다운로드·본문 텍스트 추출·수량별 금액 계산을 검증했다. 백엔드 기능 테스트, API 타입 생성, 프론트 빌드와 정적 검사도 통과했다. 브라우저 화면 동작, 실제 유료 AI 호출, PostgreSQL 실실행은 아직 검증 전이다. 자세한 상태는 [검증 기록](docs/verification.md), [할 일](docs/TASKS.md), [문제 기록](docs/development-issues.md)을 따른다.

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

기본 DB는 로컬 SQLite다. 운영용 PostgreSQL·Docker 실행 구성은 아직 완성되지 않았다.

Node.js 22.12 이상을 사용해 프론트를 준비한다. 저장소 루트에서 아래 명령을 실행한다.

```bash
cd frontend
npm ci
npm run gen:api
npm run dev
```

기본 접속 주소는 프론트 `http://127.0.0.1:5173`, API `http://127.0.0.1:8000`이다. 로그인 계정은 기본 `owner`, 비밀번호는 `.env`의 `BASIC_AUTH_PASSWORD`다. 별도 API 포트는 프론트 실행 시 `API_PROXY_TARGET`으로 지정한다.

수집 결과 화면에서 대표·본문 사진, HTML에서 추출한 설명 텍스트, 수량별 단가·상품금액·배송비·합계를 확인한다. 수량 기본값은 최소 주문 수량과 구매 단위를 따른다. 일반 지역 기본 배송비를 계산하며 지역 추가금·다른 상품 묶음배송·할인은 제외한다. 옵션 단가나 배송 규칙이 미확인이면 합계는 null이다. 이미지 안의 글자를 읽는 OCR은 아직 구현하지 않았다.

## 현재 실행 가능한 검사

```bash
make check-design
make lint
make test
cd frontend
npm run build
```

자동 테스트는 외부 호출을 차단하고 실제 수집 응답 fixture와 fake 어댑터를 사용한다. 수집·금액·이미지 저장·연습 생성·편집·확정·버전 충돌·예산·재시작 복구를 검증한다. 초안 PR에는 별도로 남은 화면·실제 AI·운영 DB 검증 항목을 표시한다.

## 비밀과 문제 기록

실제 키·비밀번호·DB 접속 정보는 `.env`에만 두며 커밋하지 않는다. `.env`, 로컬 DB, 이미지 파일, 로컬 로그는 Git 제외 대상이다. 실제 수집 응답을 fixture로 보관할 때는 인증정보를 제거한다. 도매꾹 fixture는 작성한 예시와 실제 조회에서 발췌한 응답을 구분해 표시했다.

발생 문제는 `logs/development-issues.log`와 [개발 문제 문서](docs/development-issues.md)에 같은 ID로 기록한다. 로그는 로컬에만 보관한다. [설계](docs/PLAN.md), [요구사항](docs/requirements.md), [DB 설계](docs/db-schema.md), [인수인계](docs/handover.md)를 함께 참고한다.

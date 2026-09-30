# AGENTS.md

이 문서는 이 저장소에서 작업하는 AI 코딩 에이전트(Claude Code 등)와 개발자를 위한 규칙입니다.
작업 전 `PLAN.md`(설계)와 `TASKS.md`(할 일)를 먼저 읽으세요.

## 프로젝트 한 줄 요약

도매몰 상품 URL → 상품 정보 수집 → AI 상세페이지·썸네일 생성 → 사람이 검토 → 쿠팡·네이버 스마트스토어 등록.
1인 사업자용 개인 도구. 대량 처리, 멀티 유저, 주문 관리는 범위 밖.

**우선순위 (발주자 확정): 1 수집 > 2 AI 생성 > 3 채널 등록.**
- 수집은 도매꾹이 필수이고, 소싱처를 계속 늘릴 수 있는 구조가 이 프로젝트의 핵심 가치다. 소싱처 어댑터 코드와 "소싱처 추가 절차" 문서의 품질을 최우선으로 본다.
- 수동 입력은 보류(스키마만), 후보 필터링은 있으면 좋음(P1).
- 작업 충돌 시 번호가 큰 쪽(등록)을 먼저 줄인다.

## 저장소 구조

```
backend/
  app/
    api/            # FastAPI 라우터 (얇게: 검증 + 서비스 호출만)
    services/       # 유스케이스: collect, generate, register, discover
    adapters/
      sources/      # 도매몰별 1파일: ownerclan.py, domeggook.py, base.py (수동 입력은 스키마만)
      channels/     # 채널별 1파일: coupang.py, smartstore.py, base.py
      ai/           # text.py, image.py, base.py  ← 모델 교체는 여기서만
      market/       # naver_shopping.py, kamis.py
    models/         # SQLAlchemy 모델
    db/             # 세션, Alembic
    workers/        # 백그라운드 작업
    core/           # 설정, 로깅, 예외
  prompts/          # AI 프롬프트 템플릿 (.md) — 코드 밖에서 수정 가능
  tests/
    fixtures/       # 외부 API 녹화 응답 (json)
frontend/
  src/
    pages/          # 후보탐색, 상품입력, 생성검토, 등록, 이력, 설정
    components/
    api/            # 백엔드 호출 클라이언트
docs/               # requirements, screens, db-schema, handover, ops-manual
docker-compose.yml
Makefile
```

## 명령어

```bash
make up          # docker compose up (api :8000, web :5173, db :5432)
make down
make migrate     # alembic upgrade head
make migration m="설명"   # alembic revision --autogenerate
make test        # pytest (backend) + vitest (frontend)
make lint        # ruff + mypy + eslint
make seed        # 기본 settings(수수료율·배송비·톤) 투입
```

- 백엔드 단독: `cd backend && uvicorn app.main:app --reload`
- 프론트 단독: `cd frontend && npm run dev`
- 설계·언어 검사: `make check-design` (현재 사용 가능. 앱 실행·lint·test 명령은 골격 구현 후 사용)
- 환경변수: `.env.example`을 복사해 `.env` 생성. 실제 키는 절대 커밋하지 않음.

## 아키텍처 규칙 (반드시 지킬 것)

1. **어댑터 패턴**: 도매몰·채널·AI·외부 데이터는 `adapters/*/base.py`의 Protocol을 구현한 파일 하나로 추가한다. 서비스 계층은 Protocol만 알고 구체 클래스를 import하지 않는다. 등록은 `adapters/registry.py`에서만. **특히 소싱처 어댑터는 비개발자 가족이 복사해서 새 도매몰을 붙일 수 있을 만큼 단순·균일하게** 유지한다 (파일 1개, 함수 3개, fixture 1폴더). P1 검색은 선택 SearchSourceAdapter Protocol로 분리해 기본 3함수를 유지한다.
2. **표준 모델 경유**: 수집 결과는 반드시 `Product` 표준 모델로 정규화한 뒤 다음 단계로 넘긴다. 원본은 `raw` jsonb에 그대로 보존.
3. **외부 호출 실패 격리**: 모든 외부 호출은 예외를 잡아 `RegisterResult`/`FetchResult` 같은 결과 객체로 반환한다. 예외를 라우터까지 올리지 않는다. 한 채널 실패가 다른 채널을 막으면 안 된다.
4. **사람 확인 필수**: AI 생성물은 `listings.status = confirmed`가 된 뒤에만 등록 가능. 생성 즉시 등록하는 코드 경로를 만들지 않는다.
5. **채널 규격 의존 코드 표시**: 채널·도매몰의 필드명, 규격, URL, 카테고리 코드에 의존하는 코드 블록 위에 `# [CHANNEL-SPEC] 쿠팡 상품등록 API v2 — 규격 변경 시 이 함수만 수정` 형태의 주석을 단다.
6. **비밀 관리**: API 키·토큰·비밀번호는 `core/config.py`(env) 또는 `settings` 테이블 암호화 컬럼에서만 읽는다. 로그에 출력 금지.
7. **AI 호출은 한 곳**: LLM/이미지 API 호출은 `adapters/ai/`에서만. 프롬프트 본문은 `backend/prompts/*.md`에 두고 코드에 문자열로 박지 않는다.
8. **비용 상한**: AI 호출 전 `settings.daily_ai_limit` 확인, 초과 시 명확한 메시지로 거부.
9. **1인 사용 전제**: 인증은 단일 비밀번호(basic auth). 권한 모델·조직·팀 개념을 추가하지 않는다.
10. **YAGNI**: 대량 처리, 큐 클러스터, 캐시 계층, 마이크로서비스 분리 금지. 하루 수십 건이 상한이다.

## 코드 스타일

- Python: ruff(기본 + isort), mypy strict-ish, 함수·변수 snake_case, 타입 힌트 필수, Pydantic v2 스키마.
- TypeScript: eslint + prettier, 컴포넌트 PascalCase, 훅 `use*`, API 타입은 백엔드 OpenAPI에서 생성(`npm run gen:api`).
- **주석·문서·커밋 메시지·UI 문구는 한국어**. 식별자는 영어. 코드와 Markdown에는 영어·한글만 사용한다. 일반 숫자·공백·문장부호·수식 기호는 허용한다.
- 문서·코드 수정 후 `make check-design`으로 언어 harness를 통과한다. 구현 골격에서는 이 검사를 `make lint`와 CI에 포함한다. 검사 범위·실행 방법은 `harness/README.md`를 따른다.
- 한 함수 40줄 이내, 한 파일 400줄 이내를 목표. 넘으면 분리.
- 매직 넘버 금지: 채널 규격 수치(이미지 크기, 글자 수 제한)는 각 어댑터 상단 상수로.

## 테스트 규칙

- 어댑터마다 `tests/adapters/test_<name>.py` 필수. 외부 응답은 `tests/fixtures/<name>/*.json`으로 녹화해 사용. 테스트에서 실제 네트워크 호출 금지.
- `normalize()`는 fixture 입력 → 기대 `Product` 스냅샷 비교.
- `build_payload()`는 `Listing` → 기대 dict 스냅샷 비교. 채널 규격이 바뀌면 이 스냅샷을 갱신하는 것이 수정 절차의 일부.
- 서비스 계층은 Protocol을 fake 어댑터로 대체해 테스트.
- PR 머지 전 `make lint && make test` 통과.

## 새 소싱처(도매몰) 어댑터 추가 절차 — 가장 자주 하게 될 작업 (인수인계 문서에도 동일하게 기록)

1. `adapters/<kind>/base.py`의 Protocol 확인
2. 기존 파일(예: `ownerclan.py`) 복사 → 이름 변경
3. `matches / fetch / normalize`(또는 `validate / build_payload / register`) 구현, `[CHANNEL-SPEC]` 주석
4. `tests/fixtures/<name>/`에 응답 샘플 저장, 테스트 작성
5. `adapters/registry.py`에 등록
6. `docs/handover.md` 어댑터 목록 갱신

## 작업 방식

- 작업은 `TASKS.md`의 항목 단위로. 시작 시 해당 항목을 브랜치명으로(`feat/p2-ownerclan-adapter`), 완료 시 체크.
- PR 설명에 "무엇을 / 왜 / 테스트 방법 / 채널 규격 의존 여부" 4줄.
- DB 변경은 반드시 Alembic 마이그레이션과 `docs/db-schema.md` 갱신을 함께.
- 스코프 밖 기능(2차 후보, 주문 관리 등)을 발견해도 구현하지 말고 `TASKS.md` "2차 후보"에 한 줄 추가만.
- 확실하지 않은 채널 규격(필드명·제한값)은 추측으로 코딩하지 말고 `docs/channel-fields.md`에 "확인 필요" 표시 후 mock으로 진행.

## 하지 말 것

- 실제 키로 테스트 등록 자동 실행 (테스트 등록은 사람이 화면에서 버튼을 눌러야 함)
- 도매몰·채널 사이트에 과도한 요청 (Playwright 사용 시 요청 간격 ≥ 2초, 동시 1개)
- 생성 이미지에 타사 브랜드·로고·캐릭터 삽입
- `raw` 원본 삭제, 등록 이력(`registrations`) 삭제
- 발주자 승인 없는 의존성 대량 추가(라이선스 GPL 계열 주의)

## 참고 문서

- `PLAN.md` — 설계·일정·리스크
- `TASKS.md` — 단계별 할 일
- `docs/channel-fields.md` — 채널별 필수 필드·제한값 (확인 필요 항목 포함)
- `docs/handover.md` — 인수인계(자주 하는 수정 5가지)
- `docs/ops-manual.md` — 운영·장애 대응

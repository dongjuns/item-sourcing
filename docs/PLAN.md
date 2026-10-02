# PLAN.md — AI 상품 소싱·상세페이지 생성·판매채널 자동 등록 프로그램

> 2026-10-02 최신 확정: 현재 작업은 **사용자가 입력한 도매꾹 URL의 상품 정보·사진·설명 수집과 수집 화면 버튼 검증**이다. AI 상세페이지·썸네일 생성과 관련 연동·유료 검증은 보류하며 OpenAI 키·비용 상한을 요구하지 않는다. 로그인·Basic Auth는 제거하고 바로 상품 화면을 연다. PostgreSQL 실실행·Docker·CI·운영 백업·판매 채널 등록도 보류한다.

> 이전 구현 목표(현재 범위는 위 최신 확정을 따름): 사용자가 입력한 도매꾹 상품 상세 URL → 상품 정보·이미지 수집 → AI 상세페이지·썸네일 생성 → 사람의 검토·편집·확정까지. 판매 채널 등록은 후속 단계로 보류한다. 아래 등록 범위와 일정은 초기 장기 계획이며 현재 구현 대상이 아니다. 도매꾹은 수집 소싱처이며 등록 대상이 아니다. AI 계정은 개발 계정을 먼저 사용하고 이후 클라이언트 계정으로 설정을 교체한다.

> 제안서(2026-09-30) 1차 필수 범위 기준. 착수 2026-10-20, 완료 2026-11-30.
> 대량 처리 아님. 1인 사업자가 하루 몇 건 등록하는 개인용 도구.

> 2026-09-30 설계 v1: [요구사항](requirements.md), [화면 설계](screens/README.md), [DB와 ERD](db-schema.md), [어댑터 계약](adapter-contracts.md), [규격 확인 목록](channel-fields.md)을 작성했다. 내부 상세 설계는 이 문서들을 따른다. 외부 규격·발주자 검수·실연동은 별도 확인한다.

## 0. 우선순위 (발주자 확정, 2026-09-30)

시간·예산이 부족하면 **아래 번호가 큰 것부터 줄인다.** 개발 순서도 이 순서를 따른다.

| 순위 | 항목 | 세부 |
| --- | --- | --- |
| **1** | **도매몰 상품 정보 수집** | 도매꾹 **필수**. 이후 오너클랜 등 소싱처를 계속 늘릴 수 있는 구조가 중요 (어댑터 1파일 = 1소싱처) |
| 1-보류 | 수동 입력 | 요청 스키마만 예약. 수집 실패 시 원본 링크·사유·재시도 안내, 입력 폼과 저장 API는 보류 |
| 1-선택 | 상품 후보 자동 필터링 | 있으면 좋음. "어디에 어떤 상품이 있고 무엇이 좋은지" 찾는 일을 줄이는 기능 |
| **2** | **AI 상세페이지·썸네일 생성** | 채널별 형식에 맞춰 생성, 사람이 검토·확정 |
| **3** | **판매 채널 자동 등록** | 쿠팡, 스마트스토어 순. 가장 마지막 단계, 일정 부족 시 반자동(등록용 파일 내보내기)으로 축소 가능 |

## 1. 목표

URL 하나를 넣으면 `수집 → AI 상세/썸네일 생성 → 검토·수정 → 쿠팡·스마트스토어 등록`이 한 화면에서 끝나고,
후보 필터링 화면에서 고른 상품을 같은 흐름으로 넘길 수 있다. 소싱처는 파일 하나 추가로 늘어난다.

## 2. 1차 범위 (In / Out)

| In | Out (2차 또는 제외) |
| --- | --- |
| 도매몰 수집: **도매꾹(필수)** → 오너클랜 → 여유 시 1곳 추가 | 농수산물 B2B 도매몰(2차) |
| 소싱처 확장 구조(어댑터 레지스트리, 추가 절차 문서) | 수동 입력 전체 구현(보류) |
| AI 상세페이지 + 썸네일 3안 생성, 화면에서 수정·확정 | 카카오 톡딜, 토스 등록 |
| 채널 등록: 쿠팡 Open API, 네이버 커머스 API | 후보 탐색 고급(판매량 추정·AI 점수화) |
| (선택) 후보 필터링 기본: 조건 검색 + 마진 계산 + 경쟁 최저가 | 주문 통합, 다중 계정, 대량 등록, 권한/멀티유저 |
| Docker 배포, 인수인계 문서, DB 스키마, 운영 매뉴얼 | |

## 3. 아키텍처

```
┌─────────────── frontend (React + TS, Vite) ───────────────┐
│ 후보탐색(P1) │ 상품입력(URL) │ 생성·검토 │ 등록·이력 │ 설정 │
└──────────────────────────┬────────────────────────────────┘
                           │ REST (JSON)
┌──────────────────────────▼────────────────────────────────┐
│ backend (Python 3.12, FastAPI)                             │
│  api/            라우터                                    │
│  services/       유스케이스 (수집·생성·등록·탐색)           │
│  adapters/                                                 │
│    sources/      오너클랜, 도매꾹           ← 도매몰별 1파일 │
│    channels/     coupang, smartstore        ← 채널별 1파일  │
│    ai/           text (LLM), image           ← 모델 교체점  │
│    market/       naver_shopping(P1), kamis(P2)             │
│  models/ + db/   SQLAlchemy + Alembic                       │
│  workers/        단일 프로세스 백그라운드 작업              │
└──────────────────────────┬────────────────────────────────┘
                 PostgreSQL │ 파일 저장(로컬/S3 호환)
```

### 핵심 설계 원칙

1. **어댑터 분리**: 도매몰·채널·AI는 각각 공통 인터페이스를 구현한 파일 하나. 추가/수정은 그 파일만.
2. **정규화된 중간 모델**: 어디서 수집하든 `Product` 표준 스키마로 변환한 뒤 이후 흐름은 동일.
3. **실패 격리**: 외부 호출은 모두 try/except + 결과 레코드 저장. 한 채널 실패가 다른 채널을 막지 않는다.
4. **사람 확인 단계**: AI 생성물은 반드시 화면에서 확정 후 등록. 자동 즉시 등록 없음.
5. **비밀 분리**: API 키·계정은 `.env` / 설정 테이블. 코드에 하드코딩 금지.
6. **한국어 주석 + "정책 변경 시 여기" 표시**: 외부 규격 의존 코드에 `# [CHANNEL-SPEC]` 주석.

## 4. 어댑터 인터페이스

```python
# adapters/sources/base.py
class SourceAdapter(Protocol):
    name: str
    def matches(self, url: str) -> bool: ...
    async def fetch(self, url: str) -> FetchResult: ...  # 원본과 오류 격리
    def normalize(self, raw: RawProduct) -> NormalizeResult: ...  # 표준 모델과 누락

# adapters/channels/base.py
class ChannelAdapter(Protocol):
    name: str
    def validate(self, listing: Listing) -> list[Issue]: ...   # 등록 전 검사
    def build_payload(self, listing: Listing) -> dict[str, object]: ...  # 채널 규격 변환
    async def register(self, payload: dict[str, object]) -> RegisterResult: ...
    async def categories(self, query: str) -> CategoryResult: ...  # 검색 오류 격리

# adapters/ai/base.py
class TextGenerator(Protocol):
    async def generate_detail(self, product: Product, channel: str, tone: str) -> DetailResult: ...
class ImageGenerator(Protocol):
    async def generate_thumbnails(self, product: Product, n: int = 3) -> ImageResult: ...
```

## 5. 데이터 모델

상세 컬럼·제약·상태 전이는 [DB 설계](db-schema.md)와 [어댑터 계약](adapter-contracts.md)에 정의한다. listings는 검토 상태를, registrations는 시도 결과를 관리한다. 등록 실패 시 listing은 confirmed를 유지하고 시도 이력만 failed가 된다. 수정·재생성은 재확정을 요구한다.

| 테이블 | 용도 | 주요 컬럼 |
| --- | --- | --- |
| `products` | 표준화된 상품 원본 | id, source, source_url, collection_status, name, wholesale_price, options, images, shipping, detail_html, raw, issues |
| `listings` | 채널별 등록용 콘텐츠 | id, product_id, channel, content_mode, title, detail_html, thumbnail_ids, sale_price, category_code, status(draft/confirmed/registered), content_version, confirmed_version |
| `assets` | 생성·수집 이미지 | id, product_id, listing_id(nullable), kind, status, path, prompt |
| `registrations` | 채널 등록 시도 이력 | id, listing_id, content_version, listing_snapshot, mode, external_id, request, response, status, resolution |
| `settings` | 일반 설정과 암호화 비밀 | key, value, encrypted_value |
| `jobs` | 백그라운드 작업 | id, kind, target_key, payload, result, status, log |
| `ai_calls` | 호출별 비용 예약·정산 | id, job_id, budget_day, budget_month, reserved_cost_krw, actual_cost_krw, status, pricing_snapshot, resolution |
| `candidates` / `candidate_queries` | P1 후보 탐색 | 조건, 결과, 출처·시각, 비용 반영 잔액·잔액률. P0 DB 생성에서 제외 |

## 6. 기술 스택 및 선택 이유

| 영역 | 선택 | 이유 |
| --- | --- | --- |
| Backend | Python 3.12 / FastAPI / SQLAlchemy 2 / Alembic | 수집·AI 라이브러리 풍부, 읽기 쉬움 |
| Frontend | React 18 / TypeScript / Vite / Tailwind | 참고자료 많음, 수정 인력 구하기 쉬움 |
| DB | PostgreSQL 16 | 무료·안정·jsonb |
| 수집 | httpx(API) → 없으면 Playwright | API 우선, 화면 변경 내성 |
| AI | 텍스트: Anthropic/OpenAI API, 이미지: 이미지 생성 API | 한 파일에서만 호출, 교체 용이, 비용 상한 |
| 백그라운드 작업 | FastAPI BackgroundTasks + PostgreSQL jobs | 단일 프로세스 직렬 실행, 중단 작업은 사람이 재시도 |
| 배포 | Docker Compose (api, web, db) 소형 VM 1대 | 명령 한 줄 재시작·이전 |
| 테스트 | pytest, 어댑터별 fixture(녹화된 응답) | 외부 서비스 없이 재현 |

## 7. 단계별 일정 (6주)

| 주차 | 기간 | 목표 | 산출물 / 검수 |
| --- | --- | --- | --- |
| W1 | 10/20–10/24 | 기획 확정, 저장소·CI·Docker 골격, DB 초안, 어댑터 레지스트리 | 화면 설계(6~8), ERD v1 |
| W2 | 10/27–10/31 | **도매꾹 수집** 완성, 상품 목록 화면 | **10/31 화면 설계 확정 + 도매꾹 URL 수집 시연** |
| W3 | 11/03–11/07 | 오너클랜 수집, 소싱처 추가 절차 문서화, (선택) 후보 필터링 기본 | 소싱처 2곳 수집 확인 |
| W4 | 11/10–11/14 | AI 텍스트·썸네일 생성, 검토·수정 화면 | **11/14 수집→생성 시연, 톤 확정** |
| W5 | 11/17–11/21 | 쿠팡·스마트스토어 어댑터, 카테고리 매핑, 등록 화면·이력 | **11/21 실계정 테스트 등록 1건** |
| W6 | 11/24–11/28 | 배포, 문서, 버그 수정, 남는 시간에 후보 필터링 보강, 인수인계 세션 | **11/30 최종 검수** |

> 일정이 밀리면 W5(등록)를 "채널 규격 검증 + 등록용 데이터 내보내기"까지로 줄이고 API 등록은 12월 안정화 기간으로 넘긴다. 수집(W2–W3)은 줄이지 않는다.
| 12월 | 12/01–12/31 | 안정화·지원사업 서류 마무리 | 결과보고 산출물 |

## 8. 착수 전 선행 조건 (블로커)

- [ ] 쿠팡 Wing Open API 승인 + Access/Secret Key
- [ ] 네이버 커머스 API 애플리케이션 승인 + Client ID/Secret
- [ ] 오너클랜·도매꾹 계정 등급 및 API 이용 가능 여부 (도매꾹 env 키 설정 존재 확인, 권한·실조회는 미확인)
- [ ] 생성형 AI API 키 발급 및 월 비용 상한 합의
- [ ] 기존 등록 상품 2~3건 샘플(채널별 카테고리·옵션 구조)
- [ ] 도매몰 이미지 저작권 사용 범위 확인

> API 승인 지연 시: 어댑터는 mock 응답으로 먼저 개발하고, 키 도착 즉시 실연동 전환.

## 9. 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 채널 API 승인 지연 | W5 등록 지연 | mock 기반 선개발, 승인은 계약 전 신청 |
| 도매몰 API 없음/제한 | 수집 불안정 | 허용되는 Playwright 대체, 실패 시 원본 링크·사유·재시도 안내 |
| 채널 정책·규격 변경 | 등록 실패 | 어댑터 격리, `[CHANNEL-SPEC]` 주석, 검증 단계에서 사전 오류 표시 |
| AI 생성 품질·비용 | 재작업 | 프롬프트 템플릿 파일화, 생성 수 제한, 토큰 사용량 로그 |
| 1인 검수 병목 | 일정 | 주 1회 고정 검수 시점(7항) |

## 10. 인수인계 결과물

- Git 저장소(발주자 소유) + 한국어 README
- `docs/handover.md` 구조 설명, 자주 하는 수정 5가지 따라하기
- `docs/db-schema.md` + ERD + Alembic 마이그레이션
- `docs/ops-manual.md` 재시작·백업·키 갱신·채널 공지 확인 순서·오류별 대처
- 인수인계 화상 세션 2회 녹화본

# 상품 소싱 도구 인수인계

작성일: 2026-09-30. 상태: 설계 단계 인수인계 초안. 아래 backend 경로·명령은 구현 예정이며 현재 실행할 수 있는 코드가 아니다. 실제 어댑터가 구현되면 파일과 샘플을 연결해 따라하기를 검증한다.

## 소싱처 추가 절차

소싱처는 도매몰마다 파일 1개, matches·fetch·normalize 3함수, fixture 폴더 1개로 추가한다. 이후 생성·검토·등록은 같은 Product를 사용하므로 소싱처마다 다시 만들지 않는다.

1. backend/app/adapters/sources/base.py의 SourceAdapter와 [계약 문서](adapter-contracts.md)를 읽는다.
2. 기존 domeggook.py 또는 ownerclan.py를 복사하고 새 소싱처 이름으로 바꾼다. 계정·키는 복사하지 않는다.
3. matches에서 실제 호스트와 상품 URL을 판별한다. fetch에서 API 우선 조회와 FetchResult 반환을 구현한다. normalize에서 원본을 Product로 변환하고 누락 필드를 Issue로 남긴다.
4. URL·필드·규격 의존 블록 위에 [CHANNEL-SPEC] 주석을 달고 [확인 목록](channel-fields.md)에 공식 근거를 기록한다. 불명확한 규격은 mock으로 남긴다.
5. backend/tests/fixtures/<name>/에 비밀을 제거한 정상·누락·옵션·실패 응답을 저장한다. 실제 녹화본과 작성한 mock을 구분한다.
6. backend/tests/adapters/test_<name>.py에서 matches와 fetch 오류 격리, normalize Product 스냅샷을 검증한다. 테스트에서는 네트워크를 호출하지 않는다.
7. backend/app/adapters/registry.py에 등록한다. 서비스에서 구체 소싱처 클래스를 import하지 않는다.
8. 아래 어댑터 목록을 갱신하고 make lint와 make test를 실행한다. UI에서는 수집 출처·누락·원본 링크까지 확인한다.

공통 요청 간격·이미지 다운로드·비밀 제거 도우미는 수정하지 않고 사용한다. 새 소싱처를 붙이기 위해 서비스나 생성 코드를 고쳐야 한다면 표준 Product 계약과 레지스트리 의존 관계를 먼저 점검한다.

## 소싱처 목록

| 소싱처 | 파일 | 현재 상태 | 계정·규격 확인 |
| --- | --- | --- | --- |
| 도매꾹 | backend/app/adapters/sources/domeggook.py | 구현 예정, 필수 | DOMEGGOOK_API_KEY 설정 존재, API 권한·규격 미확인 |
| 오너클랜 | backend/app/adapters/sources/ownerclan.py | 구현 예정, 필수 | 미확인 |
| 수동 입력 | 요청 스키마만 예약 | 보류, 어댑터 등록하지 않음 | 해당 없음 |

## 채널 필드 변경

공식 변경 내용을 channel-fields.md에 기록한 뒤 channels/<name>.py의 상수·validate·build_payload를 수정한다. 이미지 업로드·인증 변경은 register 경계에서 격리한다. Listing 입력 → 기대 payload 스냅샷을 함께 갱신한다. 모르는 필드를 추측해 기본값으로 넣지 않는다. 실계정 테스트 등록은 화면에서 사람이 실행한다.

## AI 문구와 톤 변경

backend/prompts/detail_<channel>.md를 수정한다. 공급자·모델 교체는 adapters/ai만 변경한다. 생성 전에 가격·호출 상한 설정을 확인한다. 변경 뒤 mock 테스트와 사람이 보는 샘플 검수를 수행한다. 재생성 결과는 draft이며 이전 확정은 해제된다. registered 상품은 1차에서 재생성하지 않는다.

## 수수료와 배송비 변경

설정 화면에서 채널 수수료·부과 기준·배송비를 확인한 값으로 변경한다. 설정값에는 확인일과 근거를 둔다. 미확인 비용은 null로 두고 잔액을 확정값으로 표시하지 않는다. 기본 seed에 예시 수수료를 실제값으로 넣지 않는다.

## 카테고리 변경

채널 카테고리 검색으로 실제 코드를 선택하고 해당 상품의 고시·인증 필수값을 다시 검사한다. 저장 시 draft로 돌아가므로 재확정한다. 카테고리 검색 규격 변경은 채널 어댑터에만 반영하고 스냅샷을 갱신한다.

## 키 취급

도매꾹 키는 프로젝트 루트 .env의 DOMEGGOOK_API_KEY에서 core/config.py가 읽는다. 키를 문서·명령 인자·프론트엔드 변수·테스트 fixture·등록 스냅샷에 복사하지 않는다. 공급자 URL에 인증 인자가 포함되면 로그 전에 제거한다. .env.example에는 변수명과 빈 값만 둔다.

.env는 Git에서 제외한다. 비밀 파일은 git add -f로 추가하지 않는다. 커밋 전에는 추적 파일 이름과 diff를 검사한다. .gitignore는 과거에 이미 커밋한 비밀을 제거해 주지 않으므로 실제 노출이 확인되면 키를 교체하고 저장소 이력을 별도로 처리한다.

## 최종 인수인계에서 보강할 내용

실행·백업·복구·키 교체·unknown 등록 확인 순서는 docs/ops-manual.md에 작성한다. 실제 어댑터 코드로 소싱처 추가 실습을 수행하고, 설치·실행 명령과 DB 복원 결과를 검증한다. 이 문서 작성만으로 Phase 3 소싱처 확장이나 Phase 6 인수인계 TASK를 완료 처리하지 않는다.

# 도매꾹 응답 fixture

product.json은 공식 상품상세정보 4.6 필드를 참고해 작성한 mock이며 실제 계정 조회 녹화본이 아니다. 샘플 상품번호·이미지 URL은 실상품으로 사용하지 않는다.

product_recorded.json은 사용자가 지정한 상품 63749955의 실제 조회에서 수집 관련 필드만 발췌한 응답이다. API 키·요청 URL·공급자 계정·연락처는 포함하지 않는다. 전체 원본은 Git 제외 로컬 DB와 assets/verification에 보존한다. product_recorded.expected.json은 조회 시각을 고정한 Product 정규화 스냅샷이다.

녹화 시기: 2026-09-30~2026-10-01. 상품 URL: https://www.domeggook.com/63749955. 상품상세정보 getItemView 4.6을 사용했다. 테스트는 이 파일을 읽으며 실제 URL이나 이미지 주소를 요청하지 않는다. 재고·가격은 녹화 시점 값이고 현재 값으로 간주하지 않는다. 옵션 단가 해석은 별도 검증이 필요하다.

"""비밀과 DB 조회 없이 프론트 타입 생성용 OpenAPI만 출력한다."""

import json

from app.main import app

if __name__ == "__main__":
    print(json.dumps(app.openapi(), ensure_ascii=False))

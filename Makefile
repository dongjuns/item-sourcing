# 설계 단계 검사. 애플리케이션 실행·lint·test는 개발 골격에서 추가한다.
.PHONY: check-language test-harness check-design

check-language:
	python3 harness/check_language.py

test-harness:
	python3 -m unittest discover -s harness/tests -v

check-design: test-harness check-language

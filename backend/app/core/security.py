"""기본 인증과 외부 응답의 비밀 제거."""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import JsonValue

from app.core.config import Config, get_config

basic_auth = HTTPBasic(auto_error=False)
SECRET_FIELDS = {"aid", "apikey", "api_key", "token", "authorization", "password", "secret"}


def require_auth(
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic_auth)],
    config: Annotated[Config, Depends(get_config)],
) -> None:
    password = config.basic_auth_password.get_secret_value()
    if not password:
        raise HTTPException(503, "BASIC_AUTH_PASSWORD를 .env에 설정하세요.")
    user_ok = credentials is not None and secrets.compare_digest(
        credentials.username.encode(), config.basic_auth_username.encode()
    )
    password_ok = credentials is not None and secrets.compare_digest(
        credentials.password.encode(), password.encode()
    )
    if not (user_ok and password_ok):
        raise HTTPException(401, "비밀번호를 확인하세요.", headers={"WWW-Authenticate": "Basic"})


def redact(value: JsonValue, secret_values: tuple[str, ...] = ()) -> JsonValue:
    if isinstance(value, dict):
        return {
            key: "[REDACTED_SECRET]"
            if key.lower() in SECRET_FIELDS
            else redact(item, secret_values)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item, secret_values) for item in value]
    if isinstance(value, str):
        for secret in secret_values:
            if secret:
                value = value.replace(secret, "[REDACTED_SECRET]")
    return value

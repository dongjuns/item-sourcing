"""외부 응답에서 비밀 값을 제거한다."""

from pydantic import JsonValue

SECRET_FIELDS = {
    "aid",
    "apikey",
    "api_key",
    "token",
    "authorization",
    "password",
    "secret",
    "access_token",
    "refresh_token",
    "client_secret",
    "sid",
}


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

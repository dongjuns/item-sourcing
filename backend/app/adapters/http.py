"""읽기 전용 소싱 요청의 간격과 이미지 다운로드 호스트를 제한한다."""

import asyncio
import ipaddress
import socket
import time
from urllib.parse import urlsplit

import httpx

from app.core.config import Config


class SourceHTTP:
    def __init__(self, config: Config, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.config = config
        self.transport = transport
        self.lock = asyncio.Lock()
        self.last_request = 0.0

    async def get(self, url: str, params: dict[str, str] | None = None) -> httpx.Response:
        async with self.lock:
            delay = self.config.source_interval_seconds - (time.monotonic() - self.last_request)
            if delay > 0:
                await asyncio.sleep(delay)
            self.last_request = time.monotonic()
            async with httpx.AsyncClient(
                timeout=self.config.request_timeout_seconds,
                transport=self.transport,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                return await client.get(url, params=params)

    async def download(self, url: str) -> bytes:
        await self.validate_image_url(url)
        async with self.lock:
            delay = self.config.source_interval_seconds - (time.monotonic() - self.last_request)
            if delay > 0:
                await asyncio.sleep(delay)
            self.last_request = time.monotonic()
            async with (
                httpx.AsyncClient(
                    timeout=self.config.request_timeout_seconds,
                    transport=self.transport,
                    follow_redirects=False,
                    trust_env=False,
                ) as client,
                client.stream("GET", url) as response,
            ):
                response.raise_for_status()
                chunks = bytearray()
                async for chunk in response.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > self.config.max_image_bytes:
                        raise ValueError("이미지 파일 크기 제한 초과")
                return bytes(chunks)

    async def validate_image_url(self, url: str) -> None:
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        if parsed.scheme not in {"https", "http"} or parsed.username or parsed.password:
            raise ValueError("허용하지 않는 이미지 URL")
        if parsed.port not in {None, 80, 443} or not any(
            host == domain or host.endswith("." + domain)
            for domain in self.config.image_allowed_domains
        ):
            raise ValueError("허용하지 않는 이미지 호스트")
        if self.transport is not None:
            return
        addresses = await asyncio.to_thread(socket.getaddrinfo, host, None)
        if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
            raise ValueError("공개 주소가 아닌 이미지 호스트")

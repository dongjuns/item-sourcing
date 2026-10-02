"""수집 화면 검증 서버를 터미널 세션과 분리해 실행한다."""

import argparse
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOGS = ROOT / "logs"
STATE = LOGS / "local-dev.json"
URLS = {
    "api": "http://127.0.0.1:8001/health",
    "web": "http://127.0.0.1:5174/",
    "proxy": "http://127.0.0.1:5174/api/products?page=1",
}


def ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def status() -> bool:
    checks = {name: ready(url) for name, url in URLS.items()}
    print(json.dumps(checks, ensure_ascii=False))
    return all(checks.values())


def start() -> bool:
    # 사용 중인 포트의 프로세스는 교체하거나 종료하지 않는다.
    for port in (8001, 5174):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                print(f"포트 {port}가 사용 중입니다. make local-status로 확인하세요.")
                return False
    python = ROOT / "backend/.venv/bin/python"
    vite = ROOT / "frontend/node_modules/vite/bin/vite.js"
    node = shutil.which("node")
    if not python.exists() or not vite.exists() or not node:
        print("backend의 uv sync와 frontend의 npm ci를 먼저 실행하세요.")
        return False

    LOGS.mkdir(exist_ok=True)
    processes: dict[str, subprocess.Popen[bytes]] = {}
    commands = {
        "api": [
            str(python),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
        ],
        "web": [node, str(vite), "--host", "127.0.0.1", "--port", "5174", "--strictPort"],
    }
    env = {
        **os.environ,
        "AI_MODE": "mock",
        "SOURCE_MODE": "live",
        "API_PROXY_TARGET": "http://127.0.0.1:8001",
    }
    try:
        for name, command in commands.items():
            with (LOGS / f"local-{name}.log").open("ab") as output:
                processes[name] = subprocess.Popen(
                    command,
                    cwd=ROOT / ("backend" if name == "api" else "frontend"),
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if any(process.poll() is not None for process in processes.values()):
                break
            if all(ready(url) for url in URLS.values()):
                STATE.write_text(
                    json.dumps({name: process.pid for name, process in processes.items()})
                )
                print("상품 화면: http://127.0.0.1:5174/")
                print("서버 PID: " + STATE.read_text())
                return True
            time.sleep(0.25)
    except OSError:
        pass
    # 실패 시 이번 호출이 만든 프로세스만 정리한다.
    for process in processes.values():
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    print("기동 실패. logs/local-api.log와 logs/local-web.log를 확인하세요.")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="로컬 수집 검증 서버 실행·상태 확인")
    parser.add_argument("action", choices=("start", "status"))
    action = parser.parse_args().action
    raise SystemExit(0 if (start() if action == "start" else status()) else 1)

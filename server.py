# -*- coding: utf-8 -*-
"""
치공구 R&D Hub - Python Server v1.0
1차 서버 버전

역할
- 현재 HTML Hub를 Python HTTP 서버에서 제공
- 팀 PC에서 브라우저로 접속할 수 있는 기본 서버 구축
- 향후 SQLite DB / API를 연결하기 위한 기본 구조 제공

현재 1차 버전에서는 기존 HTML의 기능을 변경하지 않습니다.
데이터 저장은 아직 localStorage 방식이며, 다음 단계에서 SQLite DB로 연결합니다.

실행:
    python server.py

기본 접속:
    http://localhost:8080

다른 PC에서 접속:
    http://서버PC의IP:8080

예:
    http://192.168.0.100:8080
"""

from __future__ import annotations

import json
import os
import socket
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


# ============================================================
# 기본 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# 현재 확정된 HTML 파일명
HTML_FILE = "치공구_RD_요청관리_Hub_v5.6_진행담당자분리_치공구점수관리.html"

# 서버 포트
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8080))

SERVER_VERSION = "1.0"
HUB_VERSION = "v5.1"


# ============================================================
# 서버 PC IP 확인
# ============================================================

def get_local_ip() -> str:
    """현재 PC의 LAN IP를 확인합니다."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


# ============================================================
# JSON 응답
# ============================================================

def send_json(handler: SimpleHTTPRequestHandler, data: dict, status=200):
    body = json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


# ============================================================
# HTTP Handler
# ============================================================

class HubRequestHandler(SimpleHTTPRequestHandler):
    """
    현재 HTML을 그대로 제공하면서
    향후 /api/... 형태의 중앙 서버 API를 추가하기 위한 Handler입니다.
    """

    def log_message(self, format, *args):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} - {format % args}")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # ----------------------------------------------------
        # 서버 상태 확인
        # ----------------------------------------------------
        if path == "/api/health":
            send_json(self, {
                "success": True,
                "server": "치공구 R&D Hub Server",
                "server_version": SERVER_VERSION,
                "hub_version": HUB_VERSION,
                "status": "running",
                "time": datetime.now().isoformat(timespec="seconds")
            })
            return

        # ----------------------------------------------------
        # 서버 정보
        # ----------------------------------------------------
        if path == "/api/info":
            send_json(self, {
                "success": True,
                "server": "치공구 R&D Hub Server",
                "server_version": SERVER_VERSION,
                "hub_version": HUB_VERSION,
                "database": "not_connected",
                "storage": "browser localStorage",
                "next_step": "SQLite DB connection"
            })
            return

        # ----------------------------------------------------
        # 루트 접속 → 현재 Hub HTML
        # ----------------------------------------------------
        if path in ("", "/"):
            html_path = BASE_DIR / HTML_FILE

            if not html_path.exists():
                send_json(self, {
                    "success": False,
                    "error": "Hub HTML file not found",
                    "expected_file": HTML_FILE,
                    "server_directory": str(BASE_DIR)
                }, 404)
                return

            self.path = "/" + HTML_FILE

        return super().do_GET()


# ============================================================
# 서버 실행
# ============================================================

def main():
    html_path = BASE_DIR / HTML_FILE

    print()
    print("=" * 70)
    print("  치공구 R&D Hub - Python Server v1.0")
    print("=" * 70)
    print()

    print(f"[서버 폴더]  {BASE_DIR}")
    print(f"[Hub HTML]   {HTML_FILE}")

    if not html_path.exists():
        print()
        print("[오류] Hub HTML 파일을 찾을 수 없습니다.")
        print()
        print("server.py와 아래 HTML 파일을 같은 폴더에 넣어주세요.")
        print(f"  {HTML_FILE}")
        print()
        input("Enter를 누르면 종료합니다...")
        return

    local_ip = get_local_ip()

    print()
    print("[서버 상태] 정상")
    print()
    print("브라우저 접속 주소")
    print(f"  PC 내부:    http://localhost:{PORT}")
    print(f"  서버 PC:    http://127.0.0.1:{PORT}")
    print(f"  팀 PC 접속: http://{local_ip}:{PORT}")
    print()
    print("서버 상태 확인:")
    print(f"  http://{local_ip}:{PORT}/api/health")
    print()
    print("종료하려면 이 창에서 Ctrl + C")
    print()
    print("-" * 70)

    server = ThreadingHTTPServer((HOST, PORT), HubRequestHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("[서버 종료] Ctrl + C 입력으로 서버를 종료합니다.")
    finally:
        server.server_close()
        print("[서버] 종료 완료")


if __name__ == "__main__":
    main()

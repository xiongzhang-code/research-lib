#!/usr/bin/env python3
"""Smoke test dependency-free MCP wrappers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SERVERS = [
    "admlq_mcp.py",
    "nio_mcp.py",
    "optq_mcp.py",
    "dpvcfg_mcp.py",
    "gpu_monitor_mcp.py",
    "submission_mcp.py",
    "history_index_mcp.py",
]


def run(cmd: list[str], input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, input=input_text, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)


def main() -> int:
    failures = []
    for server in SERVERS:
        path = ROOT / server
        listed = run([sys.executable, str(path), "--list-tools"])
        if listed.returncode != 0:
            failures.append((server, "list-tools", listed.stderr))
            continue
        try:
            tools = json.loads(listed.stdout)
            assert tools and all("name" in t for t in tools)
        except Exception as exc:
            failures.append((server, "list-tools-json", str(exc)))
            continue
        init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        called = run([sys.executable, str(path)], json.dumps(init) + "\n")
        if called.returncode != 0:
            failures.append((server, "initialize", called.stderr))
            continue
        try:
            payload = json.loads(called.stdout.splitlines()[0])
            assert payload["result"]["capabilities"]["tools"] == {}
        except Exception as exc:
            failures.append((server, "initialize-json", f"{exc}: {called.stdout}"))
    if failures:
        print(json.dumps({"ok": False, "failures": failures}, indent=2, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "servers": SERVERS}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

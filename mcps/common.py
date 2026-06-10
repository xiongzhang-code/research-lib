#!/usr/bin/env python3
"""Small dependency-free MCP stdio runtime for local research tools."""

from __future__ import annotations

import argparse
import glob
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


TMP_ROOT = Path(os.environ.get("RESEARCH_TMP", "/dat/workspace/xiongzhang/tmp"))
VENV_ACTIVATE = Path(os.environ.get("RESEARCH_VENV_ACTIVATE", "/home/xiongzhang/venv_lgb/bin/activate"))
PYTHON = os.environ.get("RESEARCH_BIN_PYTHON") or os.environ.get("RESEARCH_MCP_PYTHON", sys.executable)


def env_path(name: str, default: str) -> str:
    return os.environ.get(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any] | str]

    def spec(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


def text_response(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def json_response(data: Any) -> dict[str, Any]:
    return text_response(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))


def clamp_output(text: str, max_chars: int = 20000) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-max_chars // 2 :]
    return f"{head}\n\n... <truncated {len(text) - max_chars} chars> ...\n\n{tail}"


def ensure_tmp() -> Path:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    return TMP_ROOT


def existing(paths: list[str]) -> list[str]:
    return [p for p in paths if Path(p).exists()]


def first_existing(paths: list[str]) -> str | None:
    found = existing(paths)
    return found[0] if found else None


def glob_count(pattern: str) -> int:
    return len(glob.glob(pattern))


def list_paths(pattern: str, limit: int = 100) -> list[str]:
    return sorted(glob.glob(pattern))[:limit]


def run_command(
    argv: list[str],
    cwd: str | None = None,
    timeout: int = 120,
    env: dict[str, str] | None = None,
    max_chars: int = 20000,
) -> dict[str, Any]:
    start = time.time()
    proc = subprocess.run(
        argv,
        cwd=cwd,
        timeout=timeout,
        env={**os.environ, **(env or {})},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "argv": argv,
        "cwd": cwd or os.getcwd(),
        "returncode": proc.returncode,
        "elapsed_sec": round(time.time() - start, 3),
        "stdout": clamp_output(proc.stdout, max_chars),
        "stderr": clamp_output(proc.stderr, max_chars),
    }


def run_shell(
    command: str,
    cwd: str | None = None,
    timeout: int = 120,
    max_chars: int = 20000,
    use_venv: bool = False,
) -> dict[str, Any]:
    shell_cmd = command
    if use_venv and VENV_ACTIVATE.exists():
        shell_cmd = f"source {shlex.quote(str(VENV_ACTIVATE))} && {command}"
    return run_command(["bash", "-lc", shell_cmd], cwd=cwd, timeout=timeout, max_chars=max_chars)


def python_script(script: str, args: list[str] | None = None, timeout: int = 120, cwd: str | None = None) -> dict[str, Any]:
    if not Path(script).exists():
        return {"error": "script_not_found", "script": script}
    return run_command([PYTHON, script, *(args or [])], cwd=cwd or str(Path(script).parent), timeout=timeout)


def queue_counts(queue_dir: str) -> dict[str, Any]:
    q = Path(queue_dir)
    data: dict[str, Any] = {"queue_dir": str(q), "exists": q.exists()}
    for name in ["cfgdir", "donedir", "retrydir", "faildir", "logdir"]:
        d = q / name
        data[name] = {
            "path": str(d),
            "exists": d.exists(),
            "xml": glob_count(str(d / "*.xml")) if d.exists() else 0,
            "done_xml": glob_count(str(d / "*.done.xml")) if d.exists() else 0,
            "err": glob_count(str(d / "*.err")) if d.exists() else 0,
            "log": glob_count(str(d / "*.log")) if d.exists() else 0,
        }
    return data


def describe_files(paths: list[str], limit: int = 50) -> dict[str, Any]:
    out = []
    for p in paths[:limit]:
        path = Path(p)
        try:
            stat = path.stat()
            out.append({"path": str(path), "size": stat.st_size, "mtime": stat.st_mtime})
        except OSError as exc:
            out.append({"path": str(path), "error": str(exc)})
    return {"count": len(paths), "shown": out}


def dry_run_or_exec(
    argv: list[str],
    dry_run: bool = True,
    timeout: int = 120,
    cwd: str | None = None,
    allow_env: str | None = None,
    confirmation_token: str | None = None,
) -> dict[str, Any]:
    if dry_run:
        return {"dry_run": True, "argv": argv, "cwd": cwd or os.getcwd()}
    if allow_env and not env_bool(allow_env):
        return {
            "dry_run": False,
            "blocked": True,
            "reason": f"{allow_env} is not enabled in the selected research_lib cluster profile",
            "argv": argv,
            "cwd": cwd or os.getcwd(),
        }
    if confirmation_token is None or len(confirmation_token.strip()) < 16:
        return {
            "dry_run": False,
            "blocked": True,
            "reason": "dry_run=false requires a non-empty confirmation_token that identifies the target and timestamp",
            "argv": argv,
            "cwd": cwd or os.getcwd(),
        }
    return run_command(argv, cwd=cwd, timeout=timeout)


class MCPServer:
    def __init__(self, name: str, tools: list[Tool]):
        self.name = name
        self.tools = {tool.name: tool for tool in tools}

    def handle(self, msg: dict[str, Any]) -> dict[str, Any] | None:
        method = msg.get("method")
        msg_id = msg.get("id")
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": self.name, "version": "0.1.0"},
                    },
                }
            if method == "notifications/initialized":
                return None
            if method == "tools/list":
                return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [t.spec() for t in self.tools.values()]}}
            if method == "tools/call":
                params = msg.get("params") or {}
                name = params.get("name")
                args = params.get("arguments") or {}
                if name not in self.tools:
                    raise ValueError(f"unknown tool: {name}")
                result = self.tools[name].handler(args)
                if isinstance(result, str):
                    result = text_response(result)
                return {"jsonrpc": "2.0", "id": msg_id, "result": result}
            raise ValueError(f"unsupported method: {method}")
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": str(exc)},
            }

    def serve(self) -> None:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = self.handle(json.loads(line))
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()


def main(server_name: str, tools: list[Tool]) -> None:
    parser = argparse.ArgumentParser(description=f"{server_name} MCP server")
    parser.add_argument("--list-tools", action="store_true")
    parser.add_argument("--call", help="Call one tool outside MCP stdio mode")
    parser.add_argument("--args", default="{}", help="JSON arguments for --call")
    ns = parser.parse_args()
    server = MCPServer(server_name, tools)
    if ns.list_tools:
        print(json.dumps([t.spec() for t in tools], indent=2, ensure_ascii=False))
        return
    if ns.call:
        args = json.loads(ns.args)
        if ns.call not in server.tools:
            raise SystemExit(f"unknown tool: {ns.call}")
        result = server.tools[ns.call].handler(args)
        print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) if not isinstance(result, str) else result)
        return
    server.serve()

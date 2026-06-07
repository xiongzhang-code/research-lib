#!/usr/bin/env python3
"""MCP tools for mining Codex and shell workflow history."""

from __future__ import annotations

import collections
import json
import re
import time
from pathlib import Path

from common import TMP_ROOT, Tool, json_response, main, schema


HOME = Path("/home/xiongzhang")
SESSION_ROOT = HOME / ".codex" / "sessions"
HISTORY_JSONL = HOME / ".codex" / "history.jsonl"
BASH_HISTORY = HOME / ".bash_history"


CMD_RE = re.compile(r"\b(?:python|bash|sh|git|rg|find|sed|awk|nvidia-smi|gpustat|superrunOpt|adml)\b[^\\n\\r]*")


def recent_session_files(days: int = 30, limit: int = 5000) -> list[Path]:
    cutoff = time.time() - days * 86400
    files = []
    if SESSION_ROOT.exists():
        for path in SESSION_ROOT.rglob("*.jsonl"):
            try:
                if path.stat().st_mtime >= cutoff:
                    files.append(path)
            except OSError:
                continue
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def extract_text_from_jsonl(path: Path, max_lines: int = 20000) -> str:
    parts = []
    try:
        with path.open(errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= max_lines:
                    break
                try:
                    obj = json.loads(line)
                    parts.append(json.dumps(obj, ensure_ascii=False))
                except json.JSONDecodeError:
                    parts.append(line)
    except OSError:
        return ""
    return "\n".join(parts)


def command_frequency(args: dict) -> dict:
    days = int(args.get("days", 30))
    limit = int(args.get("limit", 80))
    counter: collections.Counter[str] = collections.Counter()
    files = recent_session_files(days=days)
    for path in files:
        text = extract_text_from_jsonl(path)
        for match in CMD_RE.finditer(text):
            cmd = match.group(0)
            counter[cmd.split()[0]] += 1
    if BASH_HISTORY.exists():
        for line in BASH_HISTORY.read_text(errors="replace").splitlines():
            if not line.strip():
                continue
            first = line.split()[0]
            counter[first] += 1
    return json_response({"days": days, "session_files": len(files), "top_commands": counter.most_common(limit)})


def search_history(args: dict) -> dict:
    query = args["query"]
    days = int(args.get("days", 30))
    limit = int(args.get("limit", 50))
    rows = []
    for path in recent_session_files(days=days):
        text = extract_text_from_jsonl(path)
        pos = text.lower().find(query.lower())
        if pos >= 0:
            rows.append({"path": str(path), "context": text[max(0, pos - 500): pos + 1000]})
            if len(rows) >= limit:
                break
    return json_response({"query": query, "days": days, "matches": rows})


def write_index(args: dict) -> dict:
    days = int(args.get("days", 30))
    out = Path(args.get("output", str(TMP_ROOT / f"codex_history_index_{days}d.json")))
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(command_frequency({"days": days, "limit": int(args.get("limit", 200))})["content"][0]["text"])
    payload["generated_at"] = time.time()
    payload["source"] = {"sessions": str(SESSION_ROOT), "history_jsonl": str(HISTORY_JSONL), "bash_history": str(BASH_HISTORY)}
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return json_response({"output": str(out), "bytes": out.stat().st_size, "payload": payload})


TOOLS = [
    Tool("command_frequency", "Summarize command frequencies from recent Codex sessions and bash history.", schema({
        "days": {"type": "integer", "default": 30},
        "limit": {"type": "integer", "default": 80},
    }), command_frequency),
    Tool("search_history", "Search recent Codex session history for a keyword and return short contexts.", schema({
        "query": {"type": "string"},
        "days": {"type": "integer", "default": 30},
        "limit": {"type": "integer", "default": 50},
    }, ["query"]), search_history),
    Tool("write_index", "Write a compact history command index under /dat/workspace/xiongzhang/tmp.", schema({
        "days": {"type": "integer", "default": 30},
        "limit": {"type": "integer", "default": 200},
        "output": {"type": "string"},
    }), write_index),
]


if __name__ == "__main__":
    main("history-index-mcp", TOOLS)

#!/usr/bin/env python3
"""MCP tools for production submission conversion and validation."""

from __future__ import annotations

from common import PYTHON, Tool, dry_run_or_exec, json_response, main, python_script, schema


ROOT = "/dat/usercache/xiongzhang"
SUB = f"{ROOT}/projects/versions/SubmissionCheck/v0.0/submission_check/tools"


def run_tool(script_name: str, args: dict, dry_capable: bool = False) -> dict:
    script = f"{SUB}/{script_name}"
    argv = args.get("args") or []
    timeout = int(args.get("timeout", 600))
    if dry_capable:
        dry_run = bool(args.get("dry_run", True))
        return json_response(dry_run_or_exec([PYTHON, script, *argv], dry_run=dry_run, timeout=timeout))
    return json_response(python_script(script, argv, timeout=timeout))


TOOLS = [
    Tool("production_converter", "Convert experiment artifacts to production form. Dry-run by default.", schema({
        "args": {"type": "array", "items": {"type": "string"}},
        "dry_run": {"type": "boolean", "default": True},
        "timeout": {"type": "integer", "default": 600},
    }), lambda args: run_tool("production_converter.py", args, dry_capable=True)),
    Tool("production_validate", "Validate production submission artifacts.", schema({
        "args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), lambda args: run_tool("production_validate.py", args)),
    Tool("generate_checkcfg", "Generate submission check config.", schema({
        "args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), lambda args: run_tool("generate_checkcfg.py", args)),
    Tool("compare_hist_live_nio", "Compare historical and live NIO artifacts.", schema({
        "args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), lambda args: run_tool("compare_hist_live_nio.py", args)),
    Tool("upload_localmodel", "Upload local model artifacts. Dry-run by default.", schema({
        "args": {"type": "array", "items": {"type": "string"}},
        "dry_run": {"type": "boolean", "default": True},
        "timeout": {"type": "integer", "default": 600},
    }), lambda args: run_tool("upload_localmodel.py", args, dry_capable=True)),
]


if __name__ == "__main__":
    main("submission-mcp", TOOLS)

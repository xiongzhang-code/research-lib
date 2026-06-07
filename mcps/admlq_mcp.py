#!/usr/bin/env python3
"""MCP tools for AutoDML ADMLQ queues."""

from __future__ import annotations

from pathlib import Path

from common import PYTHON, Tool, describe_files, dry_run_or_exec, json_response, list_paths, main, python_script, queue_counts, schema


ROOT = "/dat/usercache/xiongzhang"
DML = f"{ROOT}/projects/DML_workspace"
BIG = f"{ROOT}/projects/2026/06/big_scale_model"
ADML = f"{ROOT}/projects/versions/AutoDML/v1.2/adml.py"
SUPER = f"{BIG}/superrunOpt.py"
CANCEL = f"{BIG}/tools/superrunOpt/cancel_admlq_source.py"
KILL = f"{BIG}/kill_superrunOpt.py"


def inspect_queues(args: dict) -> dict:
    queue_root = args.get("queue_root", DML)
    pattern = args.get("pattern", "ADMLQ*")
    limit = int(args.get("limit", 50))
    queues = list_paths(str(Path(queue_root) / pattern), limit=limit)
    return json_response({"queue_root": queue_root, "queues": [queue_counts(q) for q in queues]})


def list_recent(args: dict) -> dict:
    queue_dir = args["queue_dir"]
    subdir = args.get("subdir", "donedir")
    pattern = args.get("pattern", "*.xml")
    limit = int(args.get("limit", 50))
    return json_response(describe_files(list_paths(str(Path(queue_dir) / subdir / pattern), limit=limit), limit=limit))


def submit(args: dict) -> dict:
    cfgpaths = args["cfgpaths"]
    queue = args.get("queue", "semi")
    dry_run = bool(args.get("dry_run", True))
    return json_response(dry_run_or_exec([PYTHON, SUPER, "-q", queue, *cfgpaths], dry_run=dry_run, timeout=int(args.get("timeout", 300))))


def cancel(args: dict) -> dict:
    cfgpath = args["cfgpath"]
    dry_run = bool(args.get("dry_run", True))
    return json_response(dry_run_or_exec([PYTHON, CANCEL, cfgpath], dry_run=dry_run, timeout=int(args.get("timeout", 120))))


def worker_status(args: dict) -> dict:
    cmd = args.get("command", "ps -u \"$USER\" -f | grep -E 'superrunOpt|ADMLQ|runpysim|perfRun' | grep -v grep")
    from common import run_shell

    return json_response(run_shell(cmd, timeout=int(args.get("timeout", 30))))


def adml_help(args: dict) -> dict:
    return json_response(python_script(ADML, ["-h"], timeout=int(args.get("timeout", 30))))


TOOLS = [
    Tool("inspect_queues", "Count cfg/done/retry/fail/log files for ADMLQ directories.", schema({
        "queue_root": {"type": "string", "default": DML},
        "pattern": {"type": "string", "default": "ADMLQ*"},
        "limit": {"type": "integer", "default": 50},
    }), inspect_queues),
    Tool("list_recent", "List recent files in an ADMLQ subdirectory.", schema({
        "queue_dir": {"type": "string"},
        "subdir": {"type": "string", "default": "donedir"},
        "pattern": {"type": "string", "default": "*.xml"},
        "limit": {"type": "integer", "default": 50},
    }, ["queue_dir"]), list_recent),
    Tool("submit_configs", "Submit configs through superrunOpt. Dry-run by default.", schema({
        "cfgpaths": {"type": "array", "items": {"type": "string"}},
        "queue": {"type": "string", "default": "semi"},
        "dry_run": {"type": "boolean", "default": True},
        "timeout": {"type": "integer", "default": 300},
    }, ["cfgpaths"]), submit),
    Tool("cancel_source", "Cancel an ADMLQ source config. Dry-run by default.", schema({
        "cfgpath": {"type": "string"},
        "dry_run": {"type": "boolean", "default": True},
        "timeout": {"type": "integer", "default": 120},
    }, ["cfgpath"]), cancel),
    Tool("worker_status", "Inspect live ADMLQ/superrunOpt/runpysim processes.", schema({
        "command": {"type": "string"},
        "timeout": {"type": "integer", "default": 30},
    }), worker_status),
    Tool("adml_help", "Show adml.py help output for available queue commands.", schema({"timeout": {"type": "integer", "default": 30}}), adml_help),
]


if __name__ == "__main__":
    main("admlq-mcp", TOOLS)

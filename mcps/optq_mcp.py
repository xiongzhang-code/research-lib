#!/usr/bin/env python3
"""MCP tools for OPTQ status and optresult analysis."""

from __future__ import annotations

from pathlib import Path

from common import Tool, describe_files, json_response, list_paths, main, python_script, run_command, schema


ROOT = "/dat/usercache/xiongzhang"
BIG_TOOLS = f"{ROOT}/projects/2026/06/big_scale_model/tools"
OPTQ = f"{ROOT}/opttest/NNOPTQ_zz500"
OPTRESULT = f"{ROOT}/opttest/optresult/ZZ500"


def inspect_optq(args: dict) -> dict:
    optq_dir = args.get("optq_dir", OPTQ)
    limit = int(args.get("limit", 80))
    base = Path(optq_dir)
    data = {"optq_dir": optq_dir, "exists": base.exists()}
    for pattern_name, pattern in {
        "xml": "*.xml",
        "done_xml": "*.done.xml",
        "result": "*.result",
        "err": "*.err",
        "log": "*.log",
    }.items():
        paths = list_paths(str(base / pattern), limit=limit)
        data[pattern_name] = describe_files(paths, limit=limit)
    return json_response(data)


def find_results(args: dict) -> dict:
    root = args.get("result_root", OPTRESULT)
    pattern = args.get("pattern", "*.result")
    limit = int(args.get("limit", 100))
    return json_response(describe_files(list_paths(str(Path(root) / "**" / pattern), limit=limit), limit=limit))


def build_summary(args: dict) -> dict:
    argv = []
    if args.get("result_dir"):
        argv.append(args["result_dir"])
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{BIG_TOOLS}/build_opt_summary.py", argv, timeout=int(args.get("timeout", 600))))


def build_rank(args: dict) -> dict:
    argv = []
    if args.get("result_dir"):
        argv.append(args["result_dir"])
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{BIG_TOOLS}/build_opt_rank.py", argv, timeout=int(args.get("timeout", 600))))


def exposure_summary(args: dict) -> dict:
    argv = []
    if args.get("result_dir"):
        argv.append(args["result_dir"])
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{BIG_TOOLS}/build_factor_exposure_summary.py", argv, timeout=int(args.get("timeout", 600))))


def niupos(args: dict) -> dict:
    argv = ["/dat/pysimrelease/pysim-5.0.0/tools/niupos2025", *args["args"]]
    return json_response(run_command(argv, timeout=int(args.get("timeout", 300))))


TOOLS = [
    Tool("inspect_optq", "List XML/result/log state in an OPTQ directory.", schema({
        "optq_dir": {"type": "string", "default": OPTQ},
        "limit": {"type": "integer", "default": 80},
    }), inspect_optq),
    Tool("find_results", "Find optresult files under a result root.", schema({
        "result_root": {"type": "string", "default": OPTRESULT},
        "pattern": {"type": "string", "default": "*.result"},
        "limit": {"type": "integer", "default": 100},
    }), find_results),
    Tool("build_opt_summary", "Run build_opt_summary.py for a result directory.", schema({
        "result_dir": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), build_summary),
    Tool("build_opt_rank", "Run build_opt_rank.py for a result directory.", schema({
        "result_dir": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), build_rank),
    Tool("build_factor_exposure_summary", "Run factor exposure summary for results.", schema({
        "result_dir": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), exposure_summary),
    Tool("niupos2025", "Run niupos2025 with explicit arguments.", schema({
        "args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 300},
    }, ["args"]), niupos),
]


if __name__ == "__main__":
    main("optq-mcp", TOOLS)

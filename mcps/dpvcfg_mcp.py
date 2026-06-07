#!/usr/bin/env python3
"""MCP tools for dpvcfg/datacfg generation, editing, and validation."""

from __future__ import annotations

from pathlib import Path

from common import Tool, describe_files, json_response, list_paths, main, python_script, schema


ROOT = "/dat/usercache/xiongzhang"
DML = f"{ROOT}/projects/DML_workspace"
BIG_TOOLS = f"{ROOT}/projects/2026/06/big_scale_model/tools"


def find_cfgs(args: dict) -> dict:
    root = args.get("root", f"{DML}/cfgqueue")
    pattern = args.get("pattern", "*.xml")
    limit = int(args.get("limit", 100))
    return json_response(describe_files(list_paths(str(Path(root) / "**" / pattern), limit=limit), limit=limit))


def config_search(args: dict) -> dict:
    argv = []
    if args.get("jsonpath"):
        argv.append(args["jsonpath"])
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{DML}/config_search.py", argv, timeout=int(args.get("timeout", 600)), cwd=DML))


def modify(args: dict) -> dict:
    argv = [args["cfgpath"]]
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{BIG_TOOLS}/modify_dpvcfg.py", argv, timeout=int(args.get("timeout", 300))))


def compare(args: dict) -> dict:
    argv = [args["left"], args["right"]]
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{BIG_TOOLS}/compare_dpvcfg.py", argv, timeout=int(args.get("timeout", 300))))


def check_datacfg(args: dict) -> dict:
    argv = [args["datacfg"]]
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{BIG_TOOLS}/check_datacfg.py", argv, timeout=int(args.get("timeout", 300))))


def build_ensemble(args: dict) -> dict:
    argv = []
    if args.get("seed_cfg"):
        argv.append(args["seed_cfg"])
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(f"{BIG_TOOLS}/build_ensemble_seed_configs.py", argv, timeout=int(args.get("timeout", 600))))


TOOLS = [
    Tool("find_cfgs", "Find dpvcfg XMLs under cfgqueue or another root.", schema({
        "root": {"type": "string", "default": f"{DML}/cfgqueue"},
        "pattern": {"type": "string", "default": "*.xml"},
        "limit": {"type": "integer", "default": 100},
    }), find_cfgs),
    Tool("config_search", "Run config_search.py from a plan JSON or explicit args.", schema({
        "jsonpath": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), config_search),
    Tool("modify_dpvcfg", "Run modify_dpvcfg.py on a config.", schema({
        "cfgpath": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 300},
    }, ["cfgpath"]), modify),
    Tool("compare_dpvcfg", "Compare two dpvcfg XMLs.", schema({
        "left": {"type": "string"},
        "right": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 300},
    }, ["left", "right"]), compare),
    Tool("check_datacfg", "Validate or inspect a datacfg with check_datacfg.py.", schema({
        "datacfg": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 300},
    }, ["datacfg"]), check_datacfg),
    Tool("build_ensemble_seed_configs", "Generate ensemble seed configs from a seed config.", schema({
        "seed_cfg": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }), build_ensemble),
]


if __name__ == "__main__":
    main("dpvcfg-mcp", TOOLS)

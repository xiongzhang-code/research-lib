#!/usr/bin/env python3
"""MCP tools for NIO verification and DynamicPV debug entrypoints."""

from __future__ import annotations

from pathlib import Path

from common import Tool, json_response, main, python_script, run_command, schema


ROOT = "/dat/usercache/xiongzhang"
DML_TOOLS = f"{ROOT}/projects/DML_workspace/tools"
DPV = f"{ROOT}/projects/versions/DynamicPV/v4.3.3"
CHECKNIO = f"{DML_TOOLS}/checknio.py"
COMPARE = f"{DPV}/dynamicpv/dpvdebug/comparenio.py"
TEST_CKP = f"{DPV}/dynamicpv/dpvdebug/test_ckp.py"
TEST_LIVEHIST = f"{DPV}/dynamicpv/dpvdebug/test_livehist.py"


def checknio(args: dict) -> dict:
    argv = []
    if args.get("start"):
        argv += ["-s", str(args["start"])]
    if args.get("delay") is not None:
        argv += ["-d", str(args["delay"])]
    if args.get("dateoffset") is not None:
        argv += ["--dateoffset", str(args["dateoffset"])]
    argv += [args["niopath"]]
    return json_response(python_script(CHECKNIO, argv, timeout=int(args.get("timeout", 300))))


def compare_nio(args: dict) -> dict:
    argv = [args["left"], args["right"]]
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(COMPARE, argv, timeout=int(args.get("timeout", 300))))


def livehist(args: dict) -> dict:
    argv = [args["cfgpath"]]
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(TEST_LIVEHIST, argv, timeout=int(args.get("timeout", 600)), cwd=str(Path(DPV))))


def checkpoint(args: dict) -> dict:
    argv = [args["cfgpath"]]
    if args.get("extra_args"):
        argv += args["extra_args"]
    return json_response(python_script(TEST_CKP, argv, timeout=int(args.get("timeout", 600)), cwd=str(Path(DPV))))


def poscorr(args: dict) -> dict:
    niopaths = args["niopaths"]
    cmd = ["/dat/pysimrelease/pysim-5.0.0/tools/niupos2025", "basenio", "-l", *niopaths]
    if args.get("output_top"):
        cmd += ["-o", str(args["output_top"])]
    return json_response(run_command(cmd, timeout=int(args.get("timeout", 300))))


TOOLS = [
    Tool("checknio", "Run the standard checknio.py completeness check.", schema({
        "niopath": {"type": "string"},
        "start": {"type": "string", "default": "20220101"},
        "delay": {"type": "integer"},
        "dateoffset": {"type": "integer"},
        "timeout": {"type": "integer", "default": 300},
    }, ["niopath"]), checknio),
    Tool("compare_nio", "Compare two NIO files with DynamicPV dpvdebug/comparenio.py.", schema({
        "left": {"type": "string"},
        "right": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 300},
    }, ["left", "right"]), compare_nio),
    Tool("test_livehist", "Run DynamicPV live/hist consistency debug for a cfg.", schema({
        "cfgpath": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }, ["cfgpath"]), livehist),
    Tool("test_checkpoint", "Run DynamicPV checkpoint debug for a cfg.", schema({
        "cfgpath": {"type": "string"},
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 600},
    }, ["cfgpath"]), checkpoint),
    Tool("poscorr", "Compare NIO position correlation using niupos2025 basenio.", schema({
        "niopaths": {"type": "array", "items": {"type": "string"}},
        "output_top": {"type": "integer", "default": 1024},
        "timeout": {"type": "integer", "default": 300},
    }, ["niopaths"]), poscorr),
]


if __name__ == "__main__":
    main("nio-mcp", TOOLS)

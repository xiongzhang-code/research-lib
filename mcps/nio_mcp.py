#!/usr/bin/env python3
"""MCP tools for NIO verification and DynamicPV debug entrypoints."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

from common import TMP_ROOT, Tool, json_response, main, python_script, run_command, schema


ROOT = "/dat/usercache/xiongzhang"
DML_TOOLS = f"{ROOT}/projects/DML_workspace/tools"
DPV = f"{ROOT}/projects/versions/DynamicPV/v4.3.3"
CHECKNIO = f"{DML_TOOLS}/checknio.py"
COMPARE = f"{DPV}/dynamicpv/dpvdebug/comparenio.py"
TEST_CKP = f"{DPV}/dynamicpv/dpvdebug/test_ckp.py"
TEST_LIVEHIST = f"{DPV}/dynamicpv/dpvdebug/test_livehist.py"


def _new_checknio_run_dir() -> Path:
    run_dir = TMP_ROOT / f"nio_mcp_checknio_{os.getpid()}_{time.time_ns()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _checknio_was_interrupted(result: dict) -> bool:
    stderr = result.get("stderr") or ""
    return result.get("returncode") in {-2, 130} or "KeyboardInterrupt" in stderr


def checknio(args: dict) -> dict:
    argv = []
    if args.get("start"):
        argv += ["-s", str(args["start"])]
    if args.get("delay") is not None:
        argv += ["-d", str(args["delay"])]
    if args.get("dateoffset") is not None:
        argv += ["--dateoffset", str(args["dateoffset"])]
    argv += [args["niopath"]]
    run_dir = _new_checknio_run_dir()
    should_cleanup = False
    try:
        result = python_script(CHECKNIO, argv, timeout=int(args.get("timeout", 300)), cwd=str(run_dir))
        result["tmp_run_dir"] = str(run_dir)
        should_cleanup = result.get("returncode") == 0 or _checknio_was_interrupted(result)
        result["tmp_run_dir_cleaned"] = should_cleanup
        return json_response(result)
    except subprocess.TimeoutExpired as exc:
        should_cleanup = True
        return json_response({
            "argv": [CHECKNIO, *argv],
            "cwd": str(run_dir),
            "error": "timeout",
            "timeout": exc.timeout,
            "stdout": (exc.stdout or "").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            "stderr": (exc.stderr or "").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or ""),
            "tmp_run_dir": str(run_dir),
            "tmp_run_dir_cleaned": True,
        })
    except KeyboardInterrupt:
        should_cleanup = True
        raise
    finally:
        if should_cleanup:
            shutil.rmtree(run_dir, ignore_errors=True)


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

#!/usr/bin/env python3
"""MCP tools for GPU and diffsolver runtime monitoring."""

from __future__ import annotations

from pathlib import Path

from common import Tool, json_response, main, python_script, run_shell, schema


ROOT = "/dat/usercache/xiongzhang"
AUTODML = f"{ROOT}/projects/versions/AutoDML/v1.2"
DPV = f"{ROOT}/projects/versions/DynamicPV/v4.3.3"
LEASE_DIR = "/dat/workspace/xiongzhang/tmp/dpv_diffsolver_solver_leases"


def gpustat(args: dict) -> dict:
    script = f"{AUTODML}/GpuStat.py"
    extra = args.get("extra_args") or []
    return json_response(python_script(script, extra, timeout=int(args.get("timeout", 60))))


def nvidia(args: dict) -> dict:
    return json_response(run_shell(args.get("command", "nvidia-smi"), timeout=int(args.get("timeout", 30))))


def monitor_diffsolver(args: dict) -> dict:
    return json_response(python_script(f"{DPV}/tools/monitor/monitor_diffsolver_gpu.py", args.get("extra_args") or [], timeout=int(args.get("timeout", 120))))


def monitor_timeout(args: dict) -> dict:
    return json_response(python_script(f"{DPV}/tools/monitor/monitor_runpysim_timeout.py", args.get("extra_args") or [], timeout=int(args.get("timeout", 120))))


def lease_state(args: dict) -> dict:
    lease_dir = Path(args.get("lease_dir", LEASE_DIR))
    rows = []
    if lease_dir.exists():
        for path in sorted(lease_dir.glob("*"))[: int(args.get("limit", 200))]:
            try:
                stat = path.stat()
                rows.append({"path": str(path), "size": stat.st_size, "mtime": stat.st_mtime, "text": path.read_text(errors="replace")[:500]})
            except OSError as exc:
                rows.append({"path": str(path), "error": str(exc)})
    return json_response({"lease_dir": str(lease_dir), "exists": lease_dir.exists(), "leases": rows})


def diffsolver_log(args: dict) -> dict:
    log = args.get("log", f"{ROOT}/projects/DML_workspace/log/ADMLQ_diffsolver.log")
    lines = int(args.get("lines", 200))
    pattern = args.get("pattern")
    cmd = f"tail -n {lines} {log!r}"
    if pattern:
        cmd += f" | grep -E {pattern!r}"
    return json_response(run_shell(cmd, timeout=int(args.get("timeout", 30))))


TOOLS = [
    Tool("gpustat", "Run AutoDML GpuStat.py.", schema({
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 60},
    }), gpustat),
    Tool("nvidia_smi", "Run nvidia-smi or a caller-provided GPU command.", schema({
        "command": {"type": "string", "default": "nvidia-smi"},
        "timeout": {"type": "integer", "default": 30},
    }), nvidia),
    Tool("monitor_diffsolver_gpu", "Run DynamicPV monitor_diffsolver_gpu.py.", schema({
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 120},
    }), monitor_diffsolver),
    Tool("monitor_runpysim_timeout", "Run monitor_runpysim_timeout.py.", schema({
        "extra_args": {"type": "array", "items": {"type": "string"}},
        "timeout": {"type": "integer", "default": 120},
    }), monitor_timeout),
    Tool("lease_state", "Inspect diffsolver solver lease files.", schema({
        "lease_dir": {"type": "string", "default": LEASE_DIR},
        "limit": {"type": "integer", "default": 200},
    }), lease_state),
    Tool("tail_diffsolver_log", "Tail and optionally grep recent ADMLQ_diffsolver log lines.", schema({
        "log": {"type": "string"},
        "lines": {"type": "integer", "default": 200},
        "pattern": {"type": "string"},
        "timeout": {"type": "integer", "default": 30},
    }), diffsolver_log),
]


if __name__ == "__main__":
    main("gpu-monitor-mcp", TOOLS)

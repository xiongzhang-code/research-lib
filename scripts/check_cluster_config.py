#!/usr/bin/env python3
"""Validate research_lib cluster profile files without third-party deps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = {
    "research_lib",
    "dml_workspace",
    "dynamicpv",
    "autodml",
    "submission_check",
    "opttest",
    "optq",
    "optresult",
    "pysim",
    "tmp",
    "venv_activate",
}
REQUIRED_BINS = {"python", "niupos2025", "nvidia_smi", "gpustat"}
REQUIRED_BEHAVIOR = {"default_dry_run", "allow_submit", "allow_cancel", "allow_upload"}
SERVER_SCRIPTS = {
    "admlq_mcp.py",
    "nio_mcp.py",
    "optq_mcp.py",
    "dpvcfg_mcp.py",
    "gpu_monitor_mcp.py",
    "submission_mcp.py",
    "history_index_mcp.py",
}


def require_dict(obj: dict[str, Any], key: str) -> dict[str, Any]:
    value = obj.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def check_profile(path: Path) -> dict[str, Any]:
    profile = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(profile.get("cluster"), str) or not profile["cluster"]:
        raise ValueError("cluster must be a non-empty string")
    if path.stem != profile["cluster"]:
        raise ValueError(f"profile filename {path.stem!r} does not match cluster {profile['cluster']!r}")

    paths = require_dict(profile, "paths")
    bins = require_dict(profile, "bins")
    behavior = require_dict(profile, "behavior")

    missing_paths = sorted(REQUIRED_PATHS - paths.keys())
    missing_bins = sorted(REQUIRED_BINS - bins.keys())
    missing_behavior = sorted(REQUIRED_BEHAVIOR - behavior.keys())
    if missing_paths or missing_bins or missing_behavior:
        raise ValueError({
            "missing_paths": missing_paths,
            "missing_bins": missing_bins,
            "missing_behavior": missing_behavior,
        })

    non_absolute = [key for key, value in paths.items() if isinstance(value, str) and not Path(value).is_absolute()]
    wrong_behavior = [key for key in REQUIRED_BEHAVIOR if not isinstance(behavior.get(key), bool)]
    if non_absolute or wrong_behavior:
        raise ValueError({"non_absolute_paths": non_absolute, "non_boolean_behavior": wrong_behavior})

    expected_research_lib = str(REPO_ROOT)
    if paths["research_lib"] != expected_research_lib:
        raise ValueError(f"paths.research_lib={paths['research_lib']!r}, expected {expected_research_lib!r}")

    missing_server_scripts = sorted(str(REPO_ROOT / "mcps" / script) for script in SERVER_SCRIPTS if not (REPO_ROOT / "mcps" / script).exists())
    return {
        "cluster": profile["cluster"],
        "profile": str(path),
        "ok": True,
        "missing_server_scripts": missing_server_scripts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", help="Validate one cluster profile by name.")
    args = parser.parse_args()

    cluster_dir = REPO_ROOT / "config" / "clusters"
    profiles = [cluster_dir / f"{args.cluster}.json"] if args.cluster else sorted(cluster_dir.glob("*.json"))
    results = []
    for profile_path in profiles:
        results.append(check_profile(profile_path))
    print(json.dumps({"ok": True, "profiles": results}, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Multi-Cluster Skill/MCP Architecture Plan

- Date: 2026-06-09
- Scope: portable Codex skills and MCP wrappers for MCG's research workflows
- Checkpoint before this document: `93756d9 checkpoint before multi-cluster skill mcp plan`

## Goal

Make `research_lib` the maintainable source of truth for Codex skills and MCP
wrappers while keeping the setup portable across clusters where repository,
workspace, binary, data, and user-home paths differ.

The desired property is:

- skills and MCP code are portable and versioned;
- cluster-specific facts live in configuration;
- global Codex can discover the skills and MCPs by default;
- high-risk queue/submission actions remain dry-run unless explicitly enabled.

## Recommended Structure

Use `research_lib` as the single source repository:

```text
research_lib/
  skills/
    task-monitor/
    dpvcfg-editor/
    opt-analyst/
    nio-verifier/
    diffsolver-operator/
    submission-checker/
    workflow-miner/
  mcps/
    common.py
    admlq_mcp.py
    nio_mcp.py
    optq_mcp.py
    dpvcfg_mcp.py
    gpu_monitor_mcp.py
    submission_mcp.py
    history_index_mcp.py
    validate_mcp_servers.py
  scripts/
    research-mcp
    install_skills.py
    check_cluster_config.py
  config/
    paths.schema.json
    paths.default.json
    clusters/
      gs010.json
      local.json
      <cluster>.json
```

`skills/` contains workflow knowledge. `mcps/` contains executable wrappers.
`scripts/` contains install and launch helpers. `config/` contains cluster
profiles and schema validation.

## Packaging Boundary

Package these into `research_lib`:

- `SKILL.md`, `references/`, `scripts/`, `agents/openai.yaml`, and small
  stable assets for each skill.
- MCP server scripts, shared runtime code, validation/smoke scripts, and MCP
  client config templates.
- Small deterministic glue scripts that are hard to remember and cheap to
  maintain, such as XML rewrite helpers.
- JSON schema and examples documenting required external paths.

Do not package these into `research_lib`:

- large repositories such as `DML_workspace`, `DynamicPV`, `AutoDML`,
  `SubmissionCheck`, `OptTest`, or production submission repos;
- large data/results such as `ADMLQ*`, `OPTQ`, `optresult`, model dirs,
  feature dirs, Barra/risk data, cqcache, and NIO directories;
- cluster binaries such as `niupos2025`, `nvidia-smi`, `gpustat`, PySim
  releases, or scheduler-specific tools;
- user-local state such as Codex sessions, bash history, temp outputs, logs,
  and `__pycache__`.

Those facts should be discovered through cluster configuration.

## Cluster Profile

Add a cluster-aware config file. Proposed schema shape:

```json
{
  "cluster": "gs010",
  "paths": {
    "research_lib": "/dat/usercache/xiongzhang/research_lib",
    "dml_workspace": "/dat/usercache/xiongzhang/projects/DML_workspace",
    "dynamicpv": "/dat/usercache/xiongzhang/projects/versions/DynamicPV/v4.3.3",
    "autodml": "/dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2",
    "submission_check": "/dat/usercache/xiongzhang/projects/versions/SubmissionCheck/v0.0",
    "optq": "/dat/usercache/xiongzhang/opttest/NNOPTQ_zz500",
    "optresult": "/dat/usercache/xiongzhang/opttest/optresult/ZZ500",
    "pysim": "/dat/pysimrelease/pysim-5.0.0",
    "tmp": "/dat/workspace/xiongzhang/tmp",
    "venv_activate": "/home/xiongzhang/venv_lgb/bin/activate"
  },
  "bins": {
    "python": "python3",
    "niupos2025": "/dat/pysimrelease/pysim-5.0.0/tools/niupos2025",
    "nvidia_smi": "nvidia-smi",
    "gpustat": "gpustat"
  },
  "behavior": {
    "default_dry_run": true,
    "allow_submit": false,
    "allow_cancel": false,
    "allow_upload": false
  }
}
```

Path resolution priority:

1. explicit env var: `RESEARCH_CLUSTER_CONFIG`;
2. env var: `RESEARCH_CLUSTER`;
3. hostname-based profile: `config/clusters/$(hostname).json`;
4. default profile: `config/paths.default.json`;
5. error with a clear missing-key message.

MCP code should never silently fall back to a wrong queue, repo, or production
path when a required path is missing.

## Global Codex Discovery

Skills:

- Keep `research_lib/skills` as the source of truth.
- Symlink each skill into the active global Codex skill directory.
- Decision from MCG: install only to `$CODEX_HOME/skills` or
  `~/.codex/skills`.
- Do not mirror skills into `~/.agents/skills` by default. If an old tool only
  scans `~/.agents/skills`, handle that as a one-off compatibility exception.
- Avoid copying unless a cluster is offline or cannot access the source repo.

MCP:

- Register MCP servers globally in Codex config through a stable launcher,
  not by directly pointing to physical MCP script paths.

Example:

```toml
[mcp_servers.admlq]
command = "/home/xiongzhang/bin/research-mcp"
args = ["admlq"]

[mcp_servers.nio]
command = "/home/xiongzhang/bin/research-mcp"
args = ["nio"]
```

`research-mcp` resolves the cluster profile, locates `research_lib`, sets
environment variables for the MCP process, then execs the selected MCP server.

## Existing vs New Scheme

The existing scheme already has:

- a useful skill/MCP taxonomy;
- dependency-free MCP runtime in `mcps/common.py`;
- small skill files under `skills/`;
- MCP wrappers for ADMLQ, NIO, OPTQ, DPVCFG, GPU monitoring, submission, and
  history mining;
- a smoke validator for listing/initializing MCP servers.

The new scheme adds:

- a clear source-of-truth rule for `research_lib`;
- global install strategy via symlinked skills;
- a stable MCP launcher instead of hard-coded MCP script paths;
- cluster profile JSON and schema validation;
- explicit boundary between packaged code and external cluster facts;
- dry-run/permission behavior in config;
- a release and rollback workflow.

Current hard-coded paths in MCPs should be migrated to config lookup, including
`/dat/usercache/xiongzhang`, `/home/xiongzhang/venv_lgb`, PySim paths, OPTQ,
optresult, and Codex history paths.

Known drift in the current state:

- Some existing docs still describe direct `python3 mcps/<server>.py` client
  startup. Keep that only as a debugging entrypoint; global Codex should use
  `research-mcp`.
- Some docs still say `research_lib` is not a git repository. That is stale.
- Existing installed skills may be copied directories rather than symlinks, so
  same-name skills can drift from `research_lib/skills`.
- `mcps/__pycache__/*.pyc` should not be part of a portable release. If already
  tracked, remove it in a separate cleanup commit and add an ignore rule.
- AutoDML-style `cluster_paths.env` can remain as a generated local adapter, but
  it should not become a second source of truth beside `config/clusters/*.json`.

## Safety Model

Split MCP tools by risk level:

- read-only: inspect queues, list configs, parse results, summarize logs;
- dry-run capable: submit/cancel/upload/config conversion wrappers;
- execution tools: PySim runs, queue submission/cancel, uploads, source edits;
- production-risk tools: anything touching submission/upload or production
  directories.
- Decision from MCG: research queues such as `semi`, `semi2`, `predict`, `is`,
  and `diffsolver` are not production-risk queues by themselves. They still need
  normal dry-run and allowlist protection because they mutate queue state, but
  they should not be blocked by production-risk policy.

For execution and production-risk tools:

- default to dry-run. Dry-run means the tool resolves the profile, validates all
  inputs, prints the exact command, target paths, queue names, cfg counts, pids,
  or files it would touch, but does not execute the mutation;
- to execute a mutation, the caller must pass `dry_run=false`;
- require `dry_run=false` plus a profile allow flag such as `allow_submit`,
  `allow_cancel`, or `allow_upload` for actions that mutate queues, files, or
  remote state;
- for high-risk actions, require a `confirm_token` that includes the queue or
  target root, item count, and timestamp;
- validate all tool arguments at handler entry, not only through MCP
  `inputSchema` metadata;
- reject unknown fields, wrong types, unknown queues, non-absolute paths,
  symlink escapes, and paths outside the configured allowlist;
- show audit evidence before mutation, such as target queue, cfg count, pids,
  files to remove, or upload destination.

Do not fold submit/cancel/upload into broad first-phase MCPs until this safety
model is implemented. Keep thin inspect/discover/check tools separate from
mutation-capable operations.

## Recommended Migration Order

1. Freeze `research_lib` as source of truth.
2. Add `config/paths.schema.json`, `config/paths.default.json`, and one real
   cluster profile for the current cluster.
3. Add `scripts/research-mcp` and make it resolve profile plus MCP script.
4. Refactor `mcps/common.py` to load profile config and expose helpers:
   `cfg_path(key)`, `cfg_bin(key)`, `default_dry_run()`, and `require_path(key)`.
5. Refactor MCP servers one by one to remove hard-coded paths.
6. Add `scripts/install_skills.py` to create symlinks and detect conflicting
   installed skill directories.
7. Add `scripts/check_cluster_config.py` to verify required repos, bins, and
   writable temp roots.
8. Update README with install and rollback instructions.
9. Register MCP servers in global Codex config using `research-mcp`.
10. Run smoke tests and then tag the release.

For any local env file already used by a project, generate it from the cluster
profile or treat it as a project-local cache. Do not manually maintain both the
env file and the JSON profile.

## Validation Matrix

Minimum checks after each migration:

```bash
python3 /path/to/research_lib/mcps/validate_mcp_servers.py
python3 /path/to/research_lib/scripts/check_cluster_config.py
```

Tool-level smoke checks:

- `admlq-mcp --list-tools`
- `nio-mcp --list-tools`
- dry-run ADMLQ submit/cancel tools
- `checknio` with a known tiny/safe NIO if available
- `niupos2025` mixed-offset smoke if a safe sample exists
- `dpvcfg` XML rewrite to `/dat/workspace/xiongzhang/tmp`
- opt summary dry run against a known result dir if available

Documentation checks:

- no active skill directory contains an old copied version when a symlink should
  be used;
- active `SKILL.md` descriptions match `research_lib/skills`;
- no MCP server contains a new hard-coded cluster path except as a documented
  fallback in `paths.default.json`.

## Confirmed Decisions

- Install skills only to `$CODEX_HOME/skills` or `~/.codex/skills`.
- Do not treat research queues such as `semi`, `semi2`, `predict`, `is`, or
  `diffsolver` as production-risk queues.
- Keep dry-run as the default mode for mutation-capable MCP tools.

## Open Preferences To Confirm

These choices affect behavior and should be confirmed by MCG before
implementation:

1. Cluster profile selection:
   decide how Codex chooses the cluster profile at startup. The options are:
   explicit `RESEARCH_CLUSTER_CONFIG=/path/to/profile.json`, a short
   `RESEARCH_CLUSTER=<name>` that maps to `config/clusters/<name>.json`,
   hostname auto-detection, or a Codex profile-specific setting. Explicit config
   is safest and easiest to audit; hostname auto-detection is more convenient
   but can choose the wrong profile if hostnames are reused or inconsistent.
2. Offline cluster install mode:
   clarify what counts as an offline cluster and how to install there. In this
   document, an offline cluster means a machine where the canonical
   `research_lib` checkout is not reachable at runtime, for example because the
   shared filesystem is not mounted, network access is restricted, or the
   cluster needs a frozen audited snapshot. Symlink install means global skills
   point directly to the live `research_lib/skills/<skill>` directories, so
   updates and rollbacks follow the repo immediately. Copy pinned snapshot means
   copying skill/MCP files into the target machine and recording the source
   commit or tag; it is more robust when the source repo is unavailable, but it
   can drift and must be updated explicitly.
3. Safety execution gate:
   decide whether queue/file mutations require only `dry_run=false`, or
   `dry_run=false` plus profile allow flags such as `allow_submit` and
   `allow_cancel`. The stricter two-key gate is recommended because it prevents
   a profile that is meant to be read-only from mutating queues even if a caller
   passes `dry_run=false`.
4. Version pinning:
   should each cluster track `master/main`, a named tag, or a pinned commit?
5. Multiple users:
   should config paths be user-specific, or should profiles support template
   variables like `${USER}`, `${HOME}`, and `${CLUSTER}`?
6. MCP scope:
   should all MCP servers be globally enabled, or should high-risk ones such as
   submission/upload be opt-in per cluster?
7. Queue allowlist:
   which queue names should be allowed for real submit/cancel? Confirmed:
   `semi`, `semi2`, `predict`, `is`, and `diffsolver` are not production-risk,
   but they still need to be explicitly listed if allowlist enforcement is used.
8. Confirmation model:
   is `dry_run=false` plus profile allow flag enough for queue operations, or
   should high-risk operations require a `confirm_token`?
9. Existing project env files:
   should project-specific env files such as AutoDML `cluster_paths.env` be
   generated from `research_lib` profiles, or kept as hand-maintained local
   overrides?
10. Execution tools:
   should tools such as `run_pysim_xml` default to disabled/dry-run unless the
   profile explicitly enables execution?
11. Workspace mutation:
   should MCP real execution be limited to `/dat/workspace/xiongzhang/tmp`
   work copies unless the user explicitly allows direct source-tree edits?

## Provisional Recommendation

Use symlinked skills, a single `research-mcp` launcher, and JSON cluster
profiles. Keep all write-heavy tools dry-run by default. Require explicit
profile allow flags for submit/cancel/upload on top of `dry_run=false`.

This gives the best balance:

- easiest daily use: Codex sees skills/MCPs by default;
- portable: moving clusters means adding or selecting one JSON profile;
- maintainable: only `research_lib` is edited and versioned;
- extensible: new MCPs add config keys instead of new hard-coded paths;
- safer: wrong cluster paths fail validation before queue/submission actions.

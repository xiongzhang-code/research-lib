# Research Lib Codex Publish Plan

- Date: 2026-06-10
- Scope: publish `research_lib` skills and MCP servers into the active Codex environment
- Source repo: `/dat/usercache/xiongzhang/research_lib`
- Checkpoint before this document: `5f14aa0 checkpoint before research_lib publish plan`
- Previous architecture reference: `multi_cluster_skill_mcp_architecture_20260609.md`

## Goal

Publish all `research_lib` Codex skills and MCP servers through `~/.codex`
while keeping `research_lib` as the single source of truth.

The desired end state is:

- skills are discovered by Codex from `~/.codex/skills`;
- skill contents remain versioned in `research_lib/skills`;
- MCP servers are registered in `~/.codex/config.toml`;
- MCP runtime starts through a stable launcher, not direct hard-coded script
  paths in Codex config;
- cluster-specific paths and permissions live in profile config;
- mutation-capable MCP operations remain dry-run by default.

## Confirmed Boundaries

1. Implement `research-mcp` plus cluster profile before registering MCPs.
2. Merge the existing `~/.codex/skills/dpvcfg-editor` copy additions back into
   `research_lib/skills/dpvcfg-editor` before replacing it with a symlink.
3. Do not change `/home/xiongzhang/.agents/skills` in this migration.
4. Do not create `/home/xiongzhang/.codex/mcps/research_lib` in the first
   migration. MCP publishing is through launcher plus `~/.codex/config.toml`.
5. Use `research-` prefixed MCP names, such as `research-admlq`, to keep the
   global MCP list grouped and avoid name collisions.

## Skills To Publish

Publish every directory under `research_lib/skills` that contains `SKILL.md`:

- `admlq-debugger`
- `diffsolver-operator`
- `dpvcfg-editor`
- `nio-verifier`
- `opt-analyst`
- `optq-debugger`
- `submission-checker`
- `task-monitor`
- `workflow-miner`

Target layout:

```text
/home/xiongzhang/.codex/skills/<skill-name>
  -> /dat/usercache/xiongzhang/research_lib/skills/<skill-name>
```

Use symlinks by default. Do not copy skill directories unless the target cluster
cannot access the canonical `research_lib` checkout. A copied snapshot must
record the source commit or tag.

## Existing Skill Conflicts

Known current state:

- `/home/xiongzhang/.codex/skills/optq-debugger` is already a symlink to
  `/dat/usercache/xiongzhang/research_lib/skills/optq-debugger`.
- `/home/xiongzhang/.codex/skills/dpvcfg-editor` is a copied directory, not a
  symlink. It has content not currently present in `research_lib`, including
  `agents/` and `references/`.
- `/home/xiongzhang/.agents/skills/opt-analyst` and
  `/home/xiongzhang/.agents/skills/task-monitor` are old installed directories.
  They are outside the first migration scope.

Required handling for `dpvcfg-editor`:

1. Back up the existing copied directory under
   `/dat/workspace/xiongzhang/tmp/research_lib_publish_<timestamp>/`.
2. Diff it against `/dat/usercache/xiongzhang/research_lib/skills/dpvcfg-editor`.
3. Merge useful additions into `research_lib/skills/dpvcfg-editor`.
4. Commit the merge in `research_lib`.
5. Replace `/home/xiongzhang/.codex/skills/dpvcfg-editor` with a symlink.

## MCP Servers To Publish

Source MCP servers stay in:

```text
/dat/usercache/xiongzhang/research_lib/mcps
```

Register these servers in `/home/xiongzhang/.codex/config.toml`:

- `research-admlq` -> `research-mcp admlq`
- `research-nio` -> `research-mcp nio`
- `research-optq` -> `research-mcp optq`
- `research-dpvcfg` -> `research-mcp dpvcfg`
- `research-gpu-monitor` -> `research-mcp gpu-monitor`
- `research-submission` -> `research-mcp submission`
- `research-history-index` -> `research-mcp history-index`

Target config shape:

```toml
[mcp_servers.research-admlq]
command = "/home/xiongzhang/bin/research-mcp"
args = ["admlq"]

[mcp_servers.research-nio]
command = "/home/xiongzhang/bin/research-mcp"
args = ["nio"]
```

Do not register direct commands such as:

```toml
command = "python3"
args = ["/dat/usercache/xiongzhang/research_lib/mcps/admlq_mcp.py"]
```

Direct script paths are acceptable only for temporary debugging, not global
Codex registration.

## Required Launcher And Config

Before MCP registration, add these files to `research_lib`:

```text
research_lib/
  scripts/
    research-mcp
    check_cluster_config.py
  config/
    paths.schema.json
    paths.default.json
    clusters/
      gs010.json
```

The launcher should:

1. Read `/home/xiongzhang/.config/research_lib/env` by default.
2. Use `RESEARCH_CLUSTER` from that env file if present.
3. Fall back to process environment variable `RESEARCH_CLUSTER`.
4. Resolve `config/clusters/<RESEARCH_CLUSTER>.json`.
5. Fail loudly if the cluster name is missing or the profile does not exist.
6. Set the selected profile facts in the MCP process environment.
7. Exec the selected MCP server from `research_lib/mcps`.

Do not guess the cluster from hostname.

Current cluster profile should include at least:

```json
{
  "cluster": "gs010",
  "paths": {
    "research_lib": "/dat/usercache/xiongzhang/research_lib",
    "dml_workspace": "/dat/usercache/xiongzhang/projects/DML_workspace",
    "dynamicpv": "/dat/usercache/xiongzhang/projects/versions/DynamicPV/v4.3.3",
    "autodml": "/dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2",
    "submission_check": "/dat/usercache/xiongzhang/projects/versions/SubmissionCheck/v0.0",
    "opttest": "/dat/usercache/xiongzhang/projects/versions/OptTest/v0.4",
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

## Safety Policy

First migration phase allows:

- skill discovery through symlinks;
- MCP initialization and `tools/list`;
- read-only inspect/list/parse/summarize tools;
- mutation-capable tools only in dry-run mode.

Real mutation requires all of:

- caller passes `dry_run=false`;
- selected cluster profile has the matching allow flag, such as
  `allow_submit`, `allow_cancel`, or `allow_upload`;
- high-risk operations include an explicit confirmation token that identifies
  the target queue/root, item count, and timestamp.

Path-sensitive MCP handlers should reject:

- unknown fields;
- wrong types;
- unknown queue names;
- non-absolute paths;
- symlink escapes;
- paths outside configured allowlists.

## What Not To Publish

Do not copy or publish:

- `mcps/__pycache__/*.pyc`;
- large repos such as `DML_workspace`, `DynamicPV`, `AutoDML`, `OptTest`, or
  `SubmissionCheck`;
- large data/results such as `ADMLQ*`, `OPTQ`, `optresult`, model dirs,
  feature dirs, Barra/risk data, cqcache, and NIO directories;
- cluster binaries such as `niupos2025`, `nvidia-smi`, `gpustat`, PySim
  releases, or scheduler tools;
- user-local state such as Codex sessions, bash history, temporary outputs,
  logs, and `__pycache__`.

## Execution Plan

1. Inspect and record current state:
   - `git -C /dat/usercache/xiongzhang/research_lib status --short`
   - `git -C /dat/usercache/xiongzhang/research_lib rev-parse --short HEAD`
   - list existing `/home/xiongzhang/.codex/skills`
   - inspect `/home/xiongzhang/.codex/config.toml`
2. Create a git checkpoint in `research_lib`.
3. Back up mutable Codex state under
   `/dat/workspace/xiongzhang/tmp/research_lib_publish_<timestamp>/`:
   - `/home/xiongzhang/.codex/config.toml`
   - conflicting skill directories, especially `dpvcfg-editor`
4. Merge `dpvcfg-editor` copied-directory additions into
   `research_lib/skills/dpvcfg-editor`.
5. Add launcher/profile/check scripts in `research_lib`.
6. Commit `research_lib` source changes.
7. Create or update skill symlinks in `/home/xiongzhang/.codex/skills`.
8. Install launcher symlink or wrapper at `/home/xiongzhang/bin/research-mcp`.
9. Create `/home/xiongzhang/.config/research_lib/env` with:

   ```text
   RESEARCH_CLUSTER=gs010
   ```

10. Register `research-*` MCP servers in `/home/xiongzhang/.codex/config.toml`.
11. Run validation and smoke tests.
12. Commit any final `research_lib` documentation/source updates.

## Validation Plan

Required checks after publication:

```bash
find /home/xiongzhang/.codex/skills -maxdepth 1 -type l -ls
python3 /dat/usercache/xiongzhang/research_lib/mcps/validate_mcp_servers.py
/home/xiongzhang/bin/research-mcp admlq --list-tools
/home/xiongzhang/bin/research-mcp nio --list-tools
/home/xiongzhang/bin/research-mcp optq --list-tools
/home/xiongzhang/bin/research-mcp dpvcfg --list-tools
/home/xiongzhang/bin/research-mcp gpu-monitor --list-tools
/home/xiongzhang/bin/research-mcp submission --list-tools
/home/xiongzhang/bin/research-mcp history-index --list-tools
python3 -c 'import tomllib; tomllib.load(open("/home/xiongzhang/.codex/config.toml", "rb"))'
```

At least one MCP stdio initialize smoke should also be run through the launcher.

## Rollback Plan

To roll back Codex publication:

1. Restore `/home/xiongzhang/.codex/config.toml` from the timestamped backup.
2. Remove newly created skill symlinks from `/home/xiongzhang/.codex/skills`.
3. Restore backed-up copied skill directories if needed.
4. Remove `/home/xiongzhang/bin/research-mcp` if it was added for this
   migration.
5. Remove `/home/xiongzhang/.config/research_lib/env` if it was added only for
   this migration.
6. Use the git checkpoint commit to revert `research_lib` source changes if the
   launcher/profile/source update itself must be undone.

## Deferred Decisions

- Whether to add `/home/xiongzhang/.codex/mcps/research_lib` as a convenience
  symlink remains deferred. It is not required for runtime, and the first
  migration should avoid it to keep the execution path unambiguous.
- Whether to migrate or clean `/home/xiongzhang/.agents/skills` remains
  deferred. First migration should leave it untouched unless a specific old
  agent workflow requires compatibility.

# research_lib

`research_lib` 是 MCG research workflows 的 Codex skills 和 MCP servers
单一事实源。它把实验配置编辑、ADMLQ 队列监控、NIO 验证、OPTQ 分析、
DiffSolver 运维、production submission 检查和历史 workflow mining 整理成
可发现、可验证、可跨集群迁移的工具体系。

最终采用的是 `2026-06-10 research_lib_publish_plan` 版本的结构：
`research_lib` 保存源码，skills 通过 `~/.codex/skills` symlink 暴露，
MCP servers 通过 `research-*` 名称注册到 `~/.codex/config.toml`，并统一
由 `research-mcp` launcher 启动。`2026-06-09` 文档保留为架构原则来源，
`2026-06-07` 两篇文档保留为早期分类和实现索引。

## Current Structure

```text
research_lib/
  skills/                 # Codex workflow knowledge; source of truth
  mcps/                   # MCP server implementations and shared runtime
  scripts/
    research-mcp          # cluster-aware MCP launcher
    check_cluster_config.py
  config/
    paths.schema.json
    paths.default.json
    clusters/
      gs010.json
  docs/                   # historical plans, architecture notes, QA docs
```

正式使用时：

```text
/home/xiongzhang/.codex/skills/<skill>
  -> /dat/usercache/xiongzhang/research_lib/skills/<skill>

/home/xiongzhang/bin/research-mcp
  -> /dat/usercache/xiongzhang/research_lib/scripts/research-mcp

/home/xiongzhang/.codex/config.toml
  [mcp_servers.research-*]
  command = "/home/xiongzhang/bin/research-mcp"
```

## Core Workflow

```text
dpvcfg/datacfg generation
  -> ADMLQ training and queue monitoring
  -> NIO verification
  -> OPTQ optimization
  -> result, exposure, and risk analysis
  -> production submission checks
  -> iterate
```

DiffSolver 是这个闭环里的 GPU optimization branch；AutoDML monitoring 和
run-decider 逻辑提供队列可靠性判断。

## Skills

| Skill | Purpose | Main MCPs |
|---|---|---|
| `task-monitor` | Monitor ADMLQ jobs, queue health, retries, failures, and OPTQ handoff. | `research-admlq`, `research-gpu-monitor`, `research-nio`, `research-optq` |
| `dpvcfg-editor` | Rewrite, validate, compare, and batch-generate DynamicPV dpvcfg/datacfg configs. | `research-dpvcfg` |
| `opt-analyst` | Analyze optresult outputs, rank candidates, compare baselines, inspect risk/exposure. | `research-optq`, `research-nio` |
| `nio-verifier` | Check NIO completeness, position correlation, hist/live consistency, and acceptance details. | `research-nio` |
| `diffsolver-operator` | Run and monitor DiffSolver experiments, GPU health, solver budgets, and variants. | `research-gpu-monitor`, `research-admlq`, `research-optq` |
| `submission-checker` | Convert and validate experiment artifacts for production submission. | `research-submission`, `research-nio` |
| `workflow-miner` | Mine Codex sessions and shell history for recurring workflows and skill/MCP updates. | `research-history-index` |
| `admlq-debugger` | Debug failing or stuck ADMLQ and ADMLQ_diffsolver queues. | `research-admlq`, `research-nio`, `research-optq` |
| `optq-debugger` | Debug stuck or incomplete OPTQ/OptTest queue runs and result generation. | `research-optq` |

## MCP Servers

| Codex MCP name | Launcher arg | Server file | Purpose |
|---|---|---|---|
| `research-admlq` | `admlq` | `mcps/admlq_mcp.py` | Inspect ADMLQ queues, tasks, workers, skips, retries, and handoff state. |
| `research-nio` | `nio` | `mcps/nio_mcp.py` | Check NIO completeness, compare NIOs, inspect hist/live outputs. |
| `research-optq` | `optq` | `mcps/optq_mcp.py` | Inspect OPTQ queues, parse optresults, summarize returns and exposures. |
| `research-dpvcfg` | `dpvcfg` | `mcps/dpvcfg_mcp.py` | Generate, edit, compare, and validate dpvcfg/datacfg files. |
| `research-gpu-monitor` | `gpu-monitor` | `mcps/gpu_monitor_mcp.py` | Inspect GPU and DiffSolver runtime health. |
| `research-submission` | `submission` | `mcps/submission_mcp.py` | Validate production conversion, checkcfgs, hist/live NIOs, and upload flow. |
| `research-history-index` | `history-index` | `mcps/history_index_mcp.py` | Index and summarize Codex/bash workflow history. |

MCP runtime helpers live in `mcps/common.py`. Global Codex registration should
use `research-mcp`; direct `python3 mcps/<server>.py` startup is only a
debugging entrypoint.

## Cluster Configuration

Cluster-specific facts live under `config/clusters/*.json`.

Resolution order:

1. `scripts/research-mcp` reads `/home/xiongzhang/.config/research_lib/env`
   unless `RESEARCH_LIB_ENV` points elsewhere.
2. That env file may set `RESEARCH_CLUSTER=<cluster>`.
3. If the env file does not set it, use process env `RESEARCH_CLUSTER`.
4. Load `config/clusters/<RESEARCH_CLUSTER>.json`.
5. If the cluster name or profile is missing, fail loudly. Do not guess from
   hostname.

Each profile records path roots, binary locations, and behavior flags such as
`default_dry_run`, `allow_submit`, `allow_cancel`, and `allow_upload`.

## Safety Model

MCP tools are split by risk:

- read-only tools inspect queues, configs, logs, NIOs, optresults, and history;
- dry-run capable tools resolve paths and commands but do not mutate state;
- execution tools can submit, cancel, upload, edit, or run simulations;
- production-risk tools touch production submission or upload paths.

Mutation-capable operations must default to dry-run. Real mutation requires:

1. caller passes `dry_run=false`;
2. selected cluster profile enables the matching allow flag;
3. high-risk actions include a confirmation token that identifies the target
   queue/root, item count, and timestamp;
4. handlers validate unknown fields, types, queue names, absolute paths,
   symlink escapes, and configured allowlists.

## Packaging Boundary

Keep in this repo:

- `skills/**/SKILL.md`, skill references, scripts, and small stable assets;
- MCP server scripts, shared runtime code, validators, and launch helpers;
- cluster profile schema and example profiles;
- deterministic glue scripts that are cheap to maintain.

Do not package:

- large external repos such as `DML_workspace`, `DynamicPV`, `AutoDML`,
  `OptTest`, or `SubmissionCheck`;
- large data/results such as `ADMLQ*`, `OPTQ`, `optresult`, models, features,
  Barra/risk data, cqcache, or NIO directories;
- cluster binaries such as PySim releases, `niupos2025`, `nvidia-smi`,
  `gpustat`, or scheduler tools;
- user-local state such as Codex sessions, bash history, temp outputs, logs,
  and `__pycache__`.

Temporary files should go under `/dat/workspace/xiongzhang/tmp`.

## Validation

Useful checks after changes:

```bash
python3 scripts/check_cluster_config.py --cluster gs010
python3 mcps/validate_mcp_servers.py
/home/xiongzhang/bin/research-mcp admlq --list-tools
/home/xiongzhang/bin/research-mcp nio --list-tools
/home/xiongzhang/bin/research-mcp optq --list-tools
/home/xiongzhang/bin/research-mcp dpvcfg --list-tools
/home/xiongzhang/bin/research-mcp gpu-monitor --list-tools
/home/xiongzhang/bin/research-mcp submission --list-tools
/home/xiongzhang/bin/research-mcp history-index --list-tools
python3 -c 'import tomllib; tomllib.load(open("/home/xiongzhang/.codex/config.toml", "rb"))'
```

For global discovery, also check:

```bash
find /home/xiongzhang/.codex/skills -maxdepth 1 -type l -ls
rg -n 'mcp_servers.research-|research-mcp' /home/xiongzhang/.codex/config.toml
```

## Documentation Consolidation

The top-level docs overlap heavily. Use them this way:

| Document | Status | Use |
|---|---|---|
| `docs/research_lib_publish_plan_20260610.md` | Final implementation version | Source for current structure, `research-*` MCP names, symlink skills, `research-mcp`, validation, and rollback. |
| `docs/multi_cluster_skill_mcp_architecture_20260609.md` | Architecture reference | Source for long-term principles: source of truth, cluster profiles, packaging boundary, and safety model. |
| `docs/archive/mcp_skill_workflow_summary_20260607.md` | Archived early workflow taxonomy | Historical source for MCP/skill categories and the core research loop. Current inventory lives in this README. |
| `docs/archive/README_mcp_skills_20260607.md` | Archived early implementation index | Historical only. Some details are stale, including the old non-git note, direct `python3` startup wording, and 7-skill list. |

Consolidated duplicate themes:

- skill/MCP lists now live in this README as the current 9-skill and 7-MCP
  inventory;
- launcher, cluster profile, dry-run safety, and symlink publishing are each
  documented once here;
- historical checkpoints, one-time migration details, and old direct script
  registration examples stay under `docs/` or `docs/archive/` rather than the
  main entrypoint.

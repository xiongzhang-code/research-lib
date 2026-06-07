---
name: submission-checker
description: Use when converting experiment artifacts to production submission form, generating checkcfgs, validating production configs/models, comparing hist/live NIO outputs, or uploading local model artifacts. Uses submission-mcp and nio-mcp.
---

# Submission Checker

Announce: `I'm using submission-checker to move from experiment artifacts to production validation with conversion, checkcfg, and hist/live evidence.`

## Defaults

- SubmissionCheck repo: `/dat/usercache/xiongzhang/projects/versions/SubmissionCheck/v0.0`
- MCP entrypoints:
  - `/dat/usercache/xiongzhang/research_lib/mcps/submission_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/nio_mcp.py`

## Workflow

1. Resolve source experiment cfg/model/NIO and intended production output path.
2. Inspect source cfg identity, linked script, model paths, dumpName, SNAPTIME, and required production naming.
3. Run `submission-mcp.production_converter` in dry-run first; only execute with `dry_run=false` after intent is clear.
4. Generate check cfg with `generate_checkcfg`.
5. Validate with `production_validate`.
6. Compare hist/live NIOs with `compare_hist_live_nio` and, when needed, `nio-mcp.checknio`.
7. Upload local model only after conversion and validation pass; `upload_localmodel` is dry-run by default.

## Acceptance Criteria

- Converted files exist in the intended production location.
- Validation command returns success or clearly scoped warnings.
- Hist/live NIO comparison has no unexplained alignment break.
- NIO completeness is checked when the submission depends on a newly generated NIO.

## Guardrails

- Never upload or overwrite production artifacts from an implicit request.
- Preserve source experiment artifacts.
- Put temporary reports under `/dat/workspace/xiongzhang/tmp`.

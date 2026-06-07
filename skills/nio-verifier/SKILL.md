---
name: nio-verifier
description: Use when accepting or debugging a NIO: completeness/tratio checks, date/snaptime/delay alignment, hist/live comparison, checkpoint behavior, poscorr comparisons, or extracting NIO paths from dpvcfg XMLs. Uses nio-mcp and dpvcfg-mcp.
---

# NIO Verifier

Announce: `I'm using nio-verifier to check NIO completeness, date alignment, and hist/live consistency before accepting the artifact.`

## Defaults

- Standard check: `checknio.py -s 20220101`
- DPV debug tools: `/dat/usercache/xiongzhang/projects/versions/DynamicPV/v4.3.3/dynamicpv/dpvdebug`
- MCP entrypoints:
  - `/dat/usercache/xiongzhang/research_lib/mcps/nio_mcp.py`
  - `/dat/usercache/xiongzhang/research_lib/mcps/dpvcfg_mcp.py`

## Workflow

1. Resolve the NIO path from the user input or from `OpNio2.dumpPath + "/" + dumpName + ".N,6656f"` in the dpvcfg.
2. Read cfg fields that affect alignment: `SNAPTIME`, `delay`, `dateoffset`, `pred_delay`, `train_delay`, `di_delay`, and any live/hist mode flags.
3. Run `nio-mcp.checknio` with `start=20220101` and cfg-derived delay/dateoffset when available.
4. Accept completeness only when the full-period summary row has `tratio=1`.
5. If incomplete, inspect missing date ranges, snaptime mismatch, wrong dumpName, stale output directory, and source queue status.
6. For live/hist issues, run `nio-mcp.test_livehist` or `compare_nio` on the smallest relevant cfg/NIO pair.
7. For checkpoint/debug questions, use `nio-mcp.test_checkpoint`.

## Report Shape

- NIO path and source cfg
- completeness/tratio verdict
- key date/snaptime/delay assumptions
- hist/live or checkpoint evidence if checked
- next action: accept, rerun, fix cfg path/name, debug script contract, or wait for queue

## Guardrails

- Never accept a NIO based only on file existence.
- Keep hist/live and OPT result judgments separate.
- Use explicit NIO file paths for correlation comparisons.

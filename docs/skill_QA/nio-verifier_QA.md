# nio-verifier QA

- Skill: `/dat/usercache/xiongzhang/research_lib/skills/nio-verifier/SKILL.md`
- Q_agent: mined recent Codex/bash history and proposed daily task questions.
- A_agent: answered from the current skill workflow and marked unsupported boundaries.

## QA

### Q1. NIO 全不全/能接受吗/跑完了吗？

Q_agent 认为 MCG 常问：`这个 NIO 全不全/能接受吗/跑完了吗？`。关键词包括 `tools/checknio.py`、`.N,6656f`、`--verbose`、`tratio`、`/dat/usercache/xiongzhang/NIODir`。

A_agent 回答：解析 NIO 路径；读取 cfg 中 `SNAPTIME/delay/dateoffset/pred_delay/train_delay/di_delay`；跑 `nio-mcp.checknio`，默认 `start=20220101`；只在 full-period summary row 的 `tratio=1` 时接受。不能只看文件存在；不完整时看 missing date range、snaptime、dumpName、旧目录、queue 状态。

### Q2. config 输出 NIO 在哪/为什么找不到？

Q_agent 认为 MCG 常问：`这个 config 输出的 NIO 在哪？为什么找不到？`。

A_agent 回答：从 dpvcfg 里按 `OpNio2.dumpPath + "/" + dumpName + ".N,6656f"` 解析输出路径。找不到时检查 dumpName 错、输出目录旧、cfg 路径/name 不一致、queue 是否还没产出。

### Q3. checknio 不全是否日期/时间点/delay 对不上？

Q_agent 认为 MCG 常问：`checknio 为什么不全，是不是日期/时间点/delay 对不上？`。

A_agent 回答：读取 cfg 的 `SNAPTIME/delay/dateoffset/pred_delay/train_delay/di_delay`，用 cfg-derived delay/dateoffset 跑 `checknio`，再看缺失区间。重点判断 missing date ranges、snaptime mismatch、delay/dateoffset 不一致。

### Q4. hist 和 live NIO 是否一致？

Q_agent 认为 MCG 常问：`hist 和 live 的 NIO 是否一致？`。关键词包括 `dynamicpv/dpvdebug/test_livehist.py`、`Alpha_*_live.N,6656f`、`predict.N,6656f`、`CompareNio`。

A_agent 回答：针对最小相关 cfg/NIO pair 跑 `nio-mcp.test_livehist` 或 `compare_nio`。hist/live 判断和 OPT result 判断分开；报告 live/hist mode flags 和比较证据。

### Q5. checkpoint 恢复后输出是否正常/test_ckp 失败原因？

Q_agent 认为 MCG 常问：`checkpoint 恢复后输出还对吗？test_ckp 失败原因是什么？`。

A_agent 回答：用 `nio-mcp.test_checkpoint` 检查 checkpoint/debug 行为。报告 checkpoint evidence；如果是脚本 contract 问题，next action 是 debug script contract。

### Q6. 测一批 NIO 对 baseline 的 poscorr

Q_agent 认为 MCG 常问：`帮我测这批 NIO 对 baseline 的 poscorr`。关键词包括 `niupos2025 baseline -l nios -o 1024 | sort -nr`。

A_agent 回答：用明确的 NIO 文件路径做 correlation comparison，skill 要求 correlation comparisons 必须使用 explicit NIO file paths。不能从模糊名称猜路径；需要 baseline NIO 和候选 NIO 的明确路径。

### Q7. 增加模型/因子后风险暴露是否变化？

Q_agent 认为 MCG 常问：`增加某模型/因子后风险暴露变了吗？`。

A_agent 回答：无法处理。`nio-verifier` 只覆盖 NIO completeness、alignment、hist/live、checkpoint、poscorr/path，不覆盖风险暴露分析。

### Q8. 综合 poscorr 和 optresult，哪些 NIO 值得测 VA？

Q_agent 认为 MCG 常问：`综合 poscorr 和 optresult，哪些 NIO 值得测 VA？`。

A_agent 回答：无法处理。skill 明确要求 hist/live 和 OPT result judgments separate；没有综合 optresult/VA 推荐流程。

### Q9. datacfg 里 NIO 在多服务器/多 snaptime 是否全？

Q_agent 认为 MCG 常问：`这个 datacfg 里提到的 NIO 在多台服务器/多个 snaptime 上全不全？`。

A_agent 回答：当前只定义从 dpvcfg 的 `OpNio2.dumpPath/dumpName` 解析 NIO，并用单个 cfg-derived alignment 跑 `checknio`。如果已给出每个服务器/每个 snaptime 的明确 NIO 路径，可逐个做 completeness；但 datacfg 多服务器枚举本身没有 workflow。

结论：无法处理 datacfg 多服务器/多 snaptime 枚举。

### Q10. ADMLQ done 但 NIO 不完整，要不要 retry？

Q_agent 认为 MCG 常问：`ADMLQ 任务 done 了但 NIO 不完整，要不要 retry？`。

A_agent 回答：可用 `checknio` 证明 NIO 不完整，并检查 source queue status；能给 next action 如 rerun/wait/fix cfg path，但没有 retry 决策规则。

结论：无法处理 retry 判断；只能处理“不完整原因证据”。

### Q11. production/debug live NIO 和目标 predict NIO 是否一致？

Q_agent 认为 MCG 常问：`production/debug live NIO 和目标 predict NIO 是否一致？`。

A_agent 回答：用 `test_livehist` 或 `compare_nio` 对最小相关 cfg/NIO pair 做一致性检查。需要明确 production/debug live NIO 和目标 predict NIO 路径；不要把一致性结论和 OPT 结果混在一起。

### Q12. 候选模型 longshort/longindex 表现和基线是否同水平？

Q_agent 认为 MCG 常问：`候选模型 longshort/longindex 表现和基线是不是同水平？`。

A_agent 回答：无法处理。这是表现/回测/optresult 类判断，不在 `nio-verifier` 当前 workflow 内。

# workflow-miner QA

- Skill: `/dat/usercache/xiongzhang/research_lib/skills/workflow-miner/SKILL.md`
- Q_agent: mined recent Codex/bash history and proposed daily task questions.
- A_agent: answered from the current skill workflow and marked unsupported boundaries.

## QA

### Q1. 总结最近 30 天当前目录最常跑命令和流程

Q_agent 认为 MCG 常问：`帮我总结最近 30 天我在当前目录最常跑的命令和流程`。

A_agent 回答：用 `history-index-mcp.command_frequency` 统计最近 30 天命令族，再按当前目录相关记录归类成常跑命令、脚本、队列/结果流程。bash history 无时间戳，只能作补充证据；不能把全历史当最近 30 天。

### Q2. 从历史挖 ADMLQ 日常操作并整理 SOP

Q_agent 认为 MCG 常问：`从历史里挖一下 ADMLQ 相关的日常操作，整理成 SOP`。

A_agent 回答：用 `search_history` 搜 `ADMLQ`，再归类为常用脚本、队列操作、结果检查、失败处理，整理 SOP。只能基于历史命令和会话摘要；没有命中的步骤不能补写。

### Q3. 总结 diffsolver 常见卡点/失败模式

Q_agent 认为 MCG 常问：`我最近 diffsolver 卡在哪里比较多？总结失败模式`。

A_agent 回答：用 `search_history` 搜 `diffsolver`，归纳 recurring blockers / failure modes。只能总结历史中实际出现的卡点；不能推断未记录的失败模式。

### Q4. 统计 superrunOpt 用法并模板化

Q_agent 认为 MCG 常问：`统计一下 superrunOpt 最近怎么用，哪些命令可以模板化`。

A_agent 回答：用 `search_history` 搜 `superrunOpt`，抽取重复命令模板、参数组合和前后置流程。模板只能来自历史证据；不保证覆盖所有合法用法。

### Q5. 挖 cfgqueue 常见配置生成流程

Q_agent 认为 MCG 常问：`帮我挖一下 cfgqueue 的常见配置生成流程`。

A_agent 回答：用 `search_history` 搜 `cfgqueue`，整理配置生成命令、输入输出目录、阶段流程。如果历史只出现零散命令，只能总结零散流程，不能强行补完整 SOP。

### Q6. 整理 checknio 运行方式和检查清单

Q_agent 认为 MCG 常问：`最近 checknio 都是怎么跑的？整理成检查清单`。

A_agent 回答：用 `search_history` 搜 `checknio`，整理常用调用方式、检查对象、通过/失败后的处理。检查清单只能来自历史和命令上下文；不能替代真实 `checknio` 文档。

### Q7. 总结 optresult 常看指标

Q_agent 认为 MCG 常问：`从历史里总结 optresult 分析我通常看哪些指标`。

A_agent 回答：用 `search_history` 搜 `optresult`，归类常看的指标、比较方式、结果文件路径和常见判断。只能总结历史里反复查看的指标；不能凭金融/优化常识扩展。

### Q8. 提炼 niupos 相关性查询固定流程

Q_agent 认为 MCG 常问：`我平时 niupos 怎么查相关性？能不能提炼成一个固定流程？`

A_agent 回答：用 `search_history` 搜 `niupos`，整理输入 NIO、dateoffset、过滤条件、相关性判断流程。只能基于历史查询方式；具体相关性语义若历史不足，需要交给 `niupos` skill 或原工具说明。

### Q9. 总结 SubmissionCheck 历史命令

Q_agent 认为 MCG 常问：`SubmissionCheck 相关历史命令帮我总结一下`。

A_agent 回答：用 `search_history` 搜 `SubmissionCheck`，整理历史命令、参数、检查对象和使用场景。如果没有命中，只能输出“无历史证据”，不能猜命令格式。

### Q10. 总结 runpysim 调用场景

Q_agent 认为 MCG 常问：`最近 runpysim 都在哪些场景被调用？`

A_agent 回答：用 `search_history` 搜 `runpysim`，按调用目的、参数、前后置文件和结果检查分组。只能总结出现过的调用场景；不能推断所有 PySim 使用方式。

### Q11. 根据历史建议新增或更新 skill/MCP

Q_agent 认为 MCG 常问：`根据最近历史，建议新增或更新哪些 skill/MCP？`

A_agent 回答：可以根据挖到的重复流程、卡点和命令模板，提出具体、范围受限的 skill/MCP 更新建议。

无法处理：`workflow-miner` 当前 workflow 只写“推荐 skill/MCP 更新”，没有包含实际新增或修改 skill/MCP 文件的步骤。

### Q12. 整理最近工作习惯成 SOP 和边界清单

Q_agent 认为 MCG 常问：`帮我把最近工作习惯整理成可复用 SOP 和边界清单`。

A_agent 回答：综合 `command_frequency` 和多个 `search_history` 结果，归类为 common scripts、command templates、queue/result workflows、blockers、skill/MCP updates。最近 30 天以 Codex sessions/history 为主；bash history 只能辅助；不能引用大段私有会话，只能短摘要和必要本地路径。

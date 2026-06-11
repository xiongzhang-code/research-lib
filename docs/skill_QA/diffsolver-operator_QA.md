# diffsolver-operator QA

- Skill: `/dat/usercache/xiongzhang/research_lib/skills/diffsolver-operator/SKILL.md`
- Q_agent: mined recent Codex/bash history and proposed daily task questions.
- A_agent: answered from the current skill workflow and marked unsupported boundaries.

## QA

### Q1. 监控 ADMLQ_diffsolver 队列健康

Q_agent 认为 MCG 常问：`帮我看看 diffsolver 队列是不是正常跑着？为什么没产出？`。

A_agent 回答：解析队列日志、infodict、配置服务器、worker target、`diffsolver_global_max_solvers`；优先看近期 log tail；检查 worker 启停、queue produce、skip reason、solver budget、firewall、GPU unhealthy、`Simulation done`；统计相关进程；检查 lease；必要时看 GPU；最后归类健康状态。只做诊断，不 kill worker、不清 lease、不改 solver limit。

### Q2. 检查 diffsolver worker 数和配置是否匹配

Q_agent 认为 MCG 常问：`diffsolver worker 是不是少了？现在应该几个 worker？`。

A_agent 回答：从 infodict 解析配置服务器和 worker target，统计 live `ADMLQ_diffsolver` 等相关进程，对比实际 worker 数和配置目标。如果外部服务器访问失败，只能归类为 access failure；不自动启动或停止 worker。

### Q3. 检查 solver budget / lease 是否卡住

Q_agent 认为 MCG 常问：`是不是 solver budget 用完了？lease 有没有脏的？`。

A_agent 回答：检查 log 中 solver budget、skip、exhaustion 信息；读取 lease dir，按 PID 是否存活和时间戳区分 active/stale；结合 `diffsolver_global_max_solvers` 判断是否 budget exhaustion 或 stale lease pressure。不清理 lease、不调整 limit，除非用户明确要求。

### Q4. 排查 GPU / firewall / new_solver_failed

Q_agent 认为 MCG 常问：`diffsolver 是不是 GPU 或 firewall 挂了？日志里 new_solver_failed 怎么看？`。

A_agent 回答：看近期 log 中 firewall、unhealthy GPU、`new_solver_failed`、retry/fail routing 标记；必要时查 `nvidia-smi`/GpuStat；归类为 GPU firewall/unhealthy 或 external/server/access failure。如果同时出现 firewall/new_solver_failed 和 `Simulation done`，只能标为 false-success candidate，需要继续看结果质量，不能直接判成功可信。

### Q5. 看 infodict_diffsolver.json 配置

Q_agent 认为 MCG 常问：`diffsolver 的 server/worker/solver limit 配置现在是什么？`。

A_agent 回答：读取默认 infodict `/dat/usercache/xiongzhang/projects/versions/AutoDML/v1.2/configure/infodict_diffsolver.json`，提取配置服务器、worker targets、`diffsolver_global_max_solvers`。skill 只定义查看和解析，不定义修改配置。

### Q6. 用 superrunOpt 提交 diffsolver/semi 配置

Q_agent 认为 MCG 常问：`帮我把这个 cfg 用 superrunOpt -q diffsol 提上去；或者 semi/semi2/diffsol 该用哪个？`

A_agent 回答：无法处理。该 skill 只写了 runtime health 和 experiment comparison，没有提交 workflow。

### Q7. 检查 NIO 是否生成完整

Q_agent 认为 MCG 常问：`这个 diffsolver 任务 NIO 出全了吗？帮我 checknio。`

A_agent 回答：无法处理。该 skill 没有 NIO 完整性检查 workflow。

### Q8. 分析 diffsolver optresult 质量

Q_agent 认为 MCG 常问：`这个 diffsolver 结果怎么样？risk/TVR/收益有没有问题？`

A_agent 回答：可部分处理。在 “Experiment Comparison” 中要求把 runtime failure 和 optimizer quality 分开，并按 cfg family、date window、universe、risk/TVR mode、loss/slack knobs、OPT result period 对齐后比较。

边界：skill 没有给具体 optresult 指标、阈值或读取命令；只能做对齐原则和质量证据框架，具体质量分析流程无法由该 skill 单独完成。

### Q9. 比较 diffsolver 不同实验变体

Q_agent 认为 MCG 常问：`帮我比较这几个 longshort/tvr/slack/loss 版本哪个更好。`

A_agent 回答：按 cfg family、日期窗口、universe、risk/TVR mode、loss/slack knobs、OPT result period 对齐；区分 runtime failure 和 optimizer quality，再比较 longshort/tvr/slack/loss 等变体。不把运行失败误当成优化器质量差；配置不可比时不能强行比较。

### Q10. 生成或修改 cfgqueue XML 给 diffsolver 跑

Q_agent 认为 MCG 常问：`基于这个 XML 生成一批 diffsolver cfgqueue；改成 loss/slack/tvr 这组参数。`

A_agent 回答：无法处理。该 skill 没有 XML 生成或修改 workflow。

### Q11. debug livehist / checkpoint

Q_agent 认为 MCG 常问：`这个 diffsolver 为什么从 checkpoint/livehist 恢复失败？`

A_agent 回答：无法处理。该 skill 没有 livehist 或 checkpoint debug workflow。

### Q12. SubmissionCheck converter / validation

Q_agent 认为 MCG 常问：`帮我跑一下 SubmissionCheck，看这个 diffsolver 输出能不能提交。`

A_agent 回答：无法处理。该 skill 没有 SubmissionCheck converter 或 validation workflow。

### Q13. 判断 Simulation done 但结果是否可信

Q_agent 认为 MCG 常问：`日志说 Simulation done，是不是就算成功了？`

A_agent 回答：检查是否存在 firewall/new_solver_failed 标记；如果存在且同时有 `Simulation done`，标记为 false-success candidate；继续分离 runtime health evidence 和 OPT performance evidence，检查结果质量后再接受。不能仅凭 `Simulation done` 判定可信。

### Q14. 外部服务器访问或 MCP 健康问题

Q_agent 认为 MCG 常问：`gpu-monitor/admlq/optq MCP 查不到，是不是服务器访问挂了？`

A_agent 回答：可部分处理。Runtime Health Workflow 的最终分类包含 external server/access failure；skill 也列出了 gpu-monitor-mcp、admlq-mcp、optq-mcp entrypoints。

边界：skill 没有 MCP 自检、重启或修复 workflow；MCP 健康问题本身无法处理，只能在访问失败时归类为 external server/access failure。

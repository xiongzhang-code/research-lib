# task-monitor QA

- Skill: `/dat/usercache/xiongzhang/research_lib/skills/task-monitor/SKILL.md`
- Q_agent: mined recent Codex/bash history and proposed daily task questions.
- A_agent: answered from the current skill workflow and marked unsupported boundaries.

## QA

### Q1. ADMLQ 任务状态怎么判定？

Q_agent 认为 MCG 常问：`帮我看下这个 cfg 跑到哪了 / ADMLQ_semi2 里这些任务是不是都跑完了`。关键词包括 `ADMLQ*_mulworkdir`、`*_retry`、`*_done`、`*_fail`、`log/ADMLQ*.log`、`cfgqueue/**/*.xml`。期望产出是逐个 cfg 标成 `queued/running/retrying/failed/done...` 并给关键证据路径。

A_agent 回答：先解析 `cfgpath`、`nioname`、`queue_dir` 或 ADMLQ family 范围；用 `admlq-mcp.inspect_queues` 或直接查文件系统。证据包括原始 queued XML、已消费源文件 `*.done.xml`、实际运行输出 `donedir`、重试 `retrydir`、失败 `faildir` 和日志 `logdir`。不能只看到 `*.done.xml` 就认为成功，必须检查运行输出目录。报告状态使用 skill 指定 label：`queued`、`running`、`retrying`、`failed`、`done but NIO-incomplete`、`done and waiting for OPTQ`、`already in OPTQ`、`blocked by runtime health`。

### Q2. 一批 cfg 对应的 NIO 是否完备？

Q_agent 认为 MCG 常问：`帮我检查这些 xml 的 nio 是否完备`。关键词包括 `tools/checknio.py -s 20220101`、`NIODir/*.N,6656f`、`OpNio2.dumpPath/dumpName`、`delay/dateoffset`、`tratio=1`。

A_agent 回答：从 cfg 提取 `OpNio2.dumpPath`、`OpNio2.dumpName`、`delay`、`dateoffset`、`SNAPTIME`，然后用 `nio-mcp.checknio`。默认 checker 是 `/dat/usercache/xiongzhang/projects/DML_workspace/tools/checknio.py -s 20220101`。只有 full-period summary row 的 `tratio=1` 才认为 complete。部分日期完备、局部 `tratio` 达标、缺 full-period summary row，都不能报 complete。

### Q3. 跑完后是否已经进入 OPTQ？

Q_agent 认为 MCG 常问：`这个任务跑完了吗，进 NNOPTQ_zz500 了吗`。关键词包括 `/dat/usercache/xiongzhang/opttest/NNOPTQ_zz500`、`*.xml`、`*.done.xml`、`*_predict*`、`nioname_YYMMDD-HHmmSS.xml`。

A_agent 回答：先确认 run finished，再检查 NIO complete；complete 后用 `optq-mcp.inspect_optq` 和文件名搜索判断。默认 OPTQ 是 `/dat/usercache/xiongzhang/opttest/NNOPTQ_zz500`。NIO 不完备时不能判断为进入 OPTQ，应报 `done but NIO-incomplete`。

### Q4. NIO 完备后生成或确认 optcfg？

Q_agent 认为 MCG 常问：`如果完备就产生 optcfg 丢到 optq 测试`。关键词包括 `NNOPTQ_zz500`、`Alpha.dataname`、`Alpha.niodir`、`Macros.SNAPTIME`、`superrunOpt-style`。

A_agent 回答：当前 workflow 支持“确认”：NIO complete 后用 `optq-mcp.inspect_optq` 和 filename search；默认 superrunOpt 风格命名是 `nioname_YYMMDD-HHmmSS.xml`。`Alpha.niodir` 应该是 NIO 文件所在目录，不是完整 NIO 文件路径；same-name-as-dpvcfg 模式只在用户明确要求时使用。

无法处理：生成 optcfg 的具体 workflow 未写入 `task-monitor`。当前 skill 只提到 submit/cancel 工具默认 dry-run，且不能在没有明确意图时提交 OPTQ。

### Q5. 失败任务是否应该 retry？

Q_agent 认为 MCG 常问：`这个 done/fail 要不要重试，为什么进 retry 了`。关键词包括 `autodml/runtime/run_decider.py`、`should_retry_after_run(cfgpath)`、`donedir`、`retrydir`、`faildir`、`.err/.log`。

A_agent 回答：如果 run finished，检查生成 cfg，并在可用时调用 `autodml/runtime/run_decider.py`。以 `should_retry_after_run(cfgpath)` 作为 retry truth source。不能只凭 `faildir`、日志关键词或经验判断 retry；如果 `run_decider.py` 不可用，当前 skill 没给替代判据。

### Q6. 追踪 superrunOpt_ADMLQ 提交任务？

Q_agent 认为 MCG 常问：`帮我追踪这些 xml，跑完就进 optq；展示运行命令`。关键词包括 `tools/superrunOpt/superrunOpt_ADMLQ_semi2.py`、`-c <cfg>`、`-q semi2/diffsol`、`retryonly`。

A_agent 回答：无法处理。当前 `task-monitor` 只写了 OPTQ 的 superrunOpt-style config 命名规则，没有写 `superrunOpt_ADMLQ` 提交流程或追踪 workflow。

### Q7. ADMLQ_diffsolver 卡住或 worker 数不对？

Q_agent 认为 MCG 常问：`diffsolver 怎么不跑了 / worker 少了 / 队列卡住了`。关键词包括 `ADMLQ_diffsolver_mulworkdir`、`ADMLQ_diffsolver.log`、`infodict_diffsolver.json`、`ps aux`、`worker/workernum`。

A_agent 回答：对 diffsolver 队列额外检查 worker process count、近期 `ADMLQ_diffsolver.log`、GPU health 和 solver leases。如果是 runtime 健康问题，状态归类为 `blocked by runtime health`。只检查，不 kill process、不 cancel config，除非用户明确要求。

### Q8. diffsolver GPU/firewall/solver budget 健康检查？

Q_agent 认为 MCG 常问：`diffsolver 是不是 GPU 坏了 / firewall / solver budget 爆了`。关键词包括 `nvidia-smi`、`gpustat`、`GPU status line is unhealthy`、`[DPV_DIFFSOLVER_FIREWALL]`、`global solver budget exhausted`、`solver_leases`。

A_agent 回答：当前 skill 明确写了 GPU health 和 solver leases；MCP 入口包括 `gpu_monitor_mcp.py`。firewall、solver budget 的具体检查字段或命令没有展开。

无法处理：firewall/solver budget 的细节判据。当前只能按 skill 检查 GPU health、solver leases 和日志，不能猜具体判据。

### Q9. 队列 consumer/scheduler 是否还活着？

Q_agent 认为 MCG 常问：`semi/semi2 consumer 都被关闭了，是什么原因`。关键词包括 `adml.py -c infodict_*.json`、`log/ADMLQ_*.log`、`consumer`、`ps aux`、`mulworkdir_retry`。

A_agent 回答：无法处理。当前 `task-monitor` 只明确写 diffsolver 的 worker process count，没有 consumer/scheduler 存活检查 workflow。

### Q10. freq=30 cfg 转 onetrain 后快速补跑/检查？

Q_agent 认为 MCG 常问：`把这个 fq30 dpvcfg 转成 onetrain 再跑/检查`。关键词包括 `modify_dpvcfg_onetrain.py`、`fq30`、`onetrain`、`freq=99999`、`di_delay=3163`、`modelDecayNum=1`。

A_agent 回答：无法处理。当前 `task-monitor` 没有 freq=30 转 onetrain 的 workflow、脚本路径或判定规则。

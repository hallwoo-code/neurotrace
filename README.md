# NeuroTrace ClaimGate

> 面向 ERP/EEG 科研写作的本地论断证据审计工作台：把“看起来合理的结论”还原为可定位、带条件、可人工放行的证据链。

## 项目定位

NeuroTrace ClaimGate 是一个部署于本地算力环境（目标为 NVIDIA DGX Spark）的科研论断审计原型，服务于 ERP/EEG 方向的研究生和导师。

研究者可在论文的 Introduction 或 Discussion 中输入一条候选论断。系统不把它当作一个需要“回答”的问题，而是将它拆解为可核验的研究条件，并且**只依据经批准的本地文献证据**检查：这条论断是否遗漏了任务、人群、语境、时间窗或指标定义；是否忽视反例；是否把非直接证据写成了普遍性结论。最终输出带来源、页码、原文摘录、核验状态与风险说明的 Evidence Pack，供研究者人工决定是否放行。

NeuroTrace 不是通用聊天机器人、联网文献综述工具或自动论文写作器。它的价值在于：让研究结论在进入论文前，先经过一条**本地、可追溯、有边界、可审计**的证据门禁。

## 要解决的问题

ERP/EEG 结果通常高度依赖实验任务、被试群体、材料、语境、时间窗和电极/ROI。将一篇论文的观察结果直接概括为普遍结论，容易造成条件遗漏和过度外推；传统文献检索也难以让研究者快速回到原文页码与具体证据句。

```text
候选论断 → 槽位解析 → 受控本地证据检索 → 条件比对与反证检索
         → 原文页码/摘录锚点核验 → 人工审阅与放行 → Evidence Pack
```

## 核心能力

- 将候选论断拆解为被试、任务、ERP 成分、时间窗和效应方向等核验槽位。
- 基于带来源、页码和哈希字段的 EvidenceCard 进行检索与关系判定。
- 明确区分条件支持、边界、反证与证据不足；不把候选证据自动视为可引用结论。
- 在 Streamlit 工作台中展示调查过程、证据卡、人工审阅与 Evidence Pack 导出。

## 系统设计

| 组件 | 职责 | 输出约束 |
| --- | --- | --- |
| Claim Compiler | 将候选论断编译为被试、任务、ERP 成分、时间窗和效应方向等结构化槽位。 | 关键条件缺失时请求澄清，不臆测。 |
| Boundary Auditor | 仅根据受控证据片段比较条件、识别边界与反例，并生成保守 verdict 和改写建议。 | 不把关联性、综述或不同范式的证据伪装为直接支持。 |
| Evidence Gate | 使用确定性规则、来源锚点与人工审阅状态执行放行控制。 | 无页码、无来源哈希、未确认或被拒绝的证据不得进入正式依据。 |

目标运行主链：

```text
create_case → clarify_case → retrieve_evidence → compare_conditions
→ seek_counterevidence → verify_evidence_anchor → synthesize_finding
→ review_critical_evidence → recompute_verdict → build_hypothesis_casefile
```

## 当前交付状态

- 冻结语料版本为 `neurotrace-corpus-2026-09-28-v2.3`：38 条文献记录、48 张 EvidenceCard 与 12 条 GoldCase。
- EvidenceCard 已完成来源、页码和摘录审核冻结；默认受控集合包含 47 张人工确认卡，另保留 1 张人工拒绝卡用于审计追踪。
- 原型提供演示模式、本地 Ollama 模式、调查流程、证据审阅与 Evidence Pack 导出。
- 仓库提供运行时数据契约、检索本体、GoldCase 合同、处理/验证脚本及自动化回归测试。

### 诚实的能力边界

- GoldCase 当前是数据结构、证据链与流程验收合同，**不是**模型领域性能或科学结论评测结果。
- 冻结语料当前没有 `direct_support` EvidenceCard；不得将这一缺口表述为无条件支持。
- 默认演示数据仅用于验证交互和工作流；研究结论仍须回到原文进行人工确认。
- 模型召回、综合 verdict、澄清质量和安全拒绝的完整真实评测，仍以 PRD 的运行时实施与评测记录为准。

## 仓库结构

```text
app.py / neurotrace/       Streamlit 原型与审计引擎
tests/                     自动化回归测试
01_项目文档/              PRD、运行时契约、审核记录与产品规范
02_数据与证据/            冻结证据卡、文献元数据、关系与 GoldCase 合同
assets/                   已冻结的设计系统、Trace 姿态与演示资产
scripts/                  语料准备、审核、验证与发布辅助脚本
```

原始论文 PDF、个人 Zotero 数据、密钥与环境变量、日志、缓存、运行时生成文件和压缩交接副本均不会提交到公开仓库。部署时请通过 `NEUROTRACE_CORPUS_ROOT` 指向经授权的只读语料目录。

## 快速开始

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

访问 `http://127.0.0.1:8501`。默认演示模式不需要模型；如启用本地模型，使用 `OLLAMA_BASE_URL`、`OLLAMA_MODEL` 和 `NEUROTRACE_PASSWORD` 等环境变量配置，切勿将其写入仓库。

运行基础回归测试：

```powershell
python -m unittest discover -s tests -v
```

运行数据契约检查：

```powershell
python scripts\validate_retrieval_gold_contract.py --data-root "02_数据与证据"
```

## 团队与分工

NeuroTrace 由两位成员并行推进，并以可复核的交付物划分责任：

| 成员 | 主要职责 | 关键交付物 |
| --- | --- | --- |
| **吴昊** | 产品与前端：明确 PRD、用户流程、界面交互和视觉规范；将证据审计流程转化为可操作的工作台体验。 | PRD、交互/视觉规范、Streamlit 前端、演示流程与产品叙事。 |
| **梁文豪** | 工程与部署：实现数据契约、证据处理/检索审计链路、模型与本地环境接入、部署和可复跑验证。 | 审计引擎、运行时数据契约、处理/验证脚本、部署配置与回归测试。 |
| **吴昊、梁文豪** | 联合验收：共同审阅演示案例的结论措辞、条件边界、反证覆盖、页码锚点和端到端可复跑性。 | EvidenceCard/GoldCase 验收、Demo 彩排与最终交付确认。 |

## 证据边界

- 当前冻结语料中不存在 `direct_support` EvidenceCard；不可将这项缺口重标或表述为无条件支持。
- GoldCase 目前是数据结构与流程验收合同，不等同于模型科学结论或领域性能评测。
- 只有具备可回查来源、页码与人工确认状态的证据，才能进入正式判断与导出依据。

详见 [项目记忆](01_项目文档/PROJECT_MEMORY.md)、[运行时数据契约](01_项目文档/NeuroTrace_运行时数据契约与版本化规范_v1.md) 和 [检索/GoldCase 验收规范](01_项目文档/NeuroTrace_检索本体与GoldCase验收规范_v1.md)。


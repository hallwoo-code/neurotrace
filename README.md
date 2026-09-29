# NeuroTrace

NeuroTrace 是一个面向 ERP/EEG 科研论断的本地证据审计原型。它将研究者的候选论断与受控文献证据卡对照，呈现支持条件、边界、反证与来源锚点，并生成更审慎的假设表述。

> 当前仓库交付的是可演示、可审计的原型与冻结语料契约，不是已经完成领域准确率评测的生产系统。任何科研结论仍须由研究者人工复核。

## 核心能力

- 将候选论断拆解为被试、任务、ERP 成分、时间窗和效应方向等核验槽位。
- 基于带来源、页码和哈希字段的 EvidenceCard 进行检索与关系判定。
- 明确区分条件支持、边界、反证与证据不足；不把候选证据自动视为可引用结论。
- 在 Streamlit 工作台中展示调查过程、证据卡、人工审阅与 Evidence Pack 导出。

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

NeuroTrace 由两人并行协作完成，分工以可复核的交付物为边界：

| 角色 | 主要职责 | 关键交付物 |
| --- | --- | --- |
| 产品与领域证据负责人 | 定义产品边界、研究问题与 UI 规格；整理文献、人工核验原文页码与摘录；审核证据角色和 GoldCase。 | PRD、EvidenceCard 审核记录、语料清单、GoldCase、交互/视觉规范。 |
| 工程与部署负责人 | 实现数据契约、检索/审计链路和 Streamlit 工作台；接入本地模型与部署环境；维护测试、导出和可复跑证明。 | 原型代码、运行时契约、验证脚本、部署说明与回归测试。 |

两位成员共同负责演示案例的端到端验收：结论措辞、条件边界、反证覆盖、页码锚点与可复跑性。仓库不以角色替代署名；若需公开个人姓名或组织信息，请由团队成员在此处补充确认后的资料。

## 证据边界

- 当前冻结语料中不存在 `direct_support` EvidenceCard；不可将这项缺口重标或表述为无条件支持。
- GoldCase 目前是数据结构与流程验收合同，不等同于模型科学结论或领域性能评测。
- 只有具备可回查来源、页码与人工确认状态的证据，才能进入正式判断与导出依据。

详见 [项目记忆](01_项目文档/PROJECT_MEMORY.md)、[运行时数据契约](01_项目文档/NeuroTrace_运行时数据契约与版本化规范_v1.md) 和 [检索/GoldCase 验收规范](01_项目文档/NeuroTrace_检索本体与GoldCase验收规范_v1.md)。


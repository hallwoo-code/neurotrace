# NeuroTrace 资产目录

此目录是 NeuroTrace 后续视觉资产的唯一存放位置。

- `trace-postures/`：Trace 的四种状态姿态；文件名与状态对应。
- `ui-mockups/`：供审核的主入口页与调查工作台界面稿；`*-review-v2.png` 是低像素、便于组件化复现的参考基线。`neurotrace-entry-listening-review-v3.png`、`neurotrace-critical-verification-review-v3.png`、`neurotrace-narrow-workbench-review-v3.png` 与 `neurotrace-export-casefile-dialog-review-v3.png` 分别替代对应 v2 稿；不作为可直接实现的前端代码。
- `design-system/`：可直接接入前端的 Token、Logo、图标、组件样式和实现契约。
- `component-showcase/`：零依赖静态组件展厅；直接打开 `index.html` 即可审核交互与开发映射。
- 新增 Logo、图标、纹理、插图、界面视觉资源及导出用视觉资源均保存于本目录或其语义明确的子目录。
- 禁止将可复用资产散落到项目文档、交接包或临时工作目录。

UI 和交互约束见 `../01_项目文档/NeuroTrace_UI_设计与前端交互技术确认规范.md`。


# NeuroTrace 视觉资产清单

**保存日期：** 2026-09-28  
**用途：** 固定当前审核稿与角色资产，后续从获批设计稿中提取可复用的 Logo、组件、状态色和像素图形。

## 角色资产

- `trace-postures/trace-listening.png`
- `trace-postures/trace-thinking.png`
- `trace-postures/trace-scanning.png`
- `trace-postures/trace-presenting.png`

## 当前优先 UI 审核稿

- `ui-mockups/neurotrace-entry-listening-review-v3.png`（替代 v2：去除柔光，Trace 缩为状态锚点）
- `ui-mockups/neurotrace-entry-clarification-review-v2.png`
- `ui-mockups/neurotrace-workbench-default-review-v2.png`
- `ui-mockups/neurotrace-workbench-reading-review-v2.png`
- `ui-mockups/neurotrace-workbench-presenting-review-v2.png`
- `ui-mockups/neurotrace-critical-verification-review-v3.png`（替代 v2：补齐核心结论与边界条件字段）
- `ui-mockups/neurotrace-reject-recalculate-dialog-review-v2.png`
- `ui-mockups/neurotrace-case-dossier-review-v2.png`
- `ui-mockups/neurotrace-export-casefile-dialog-review-v3.png`
- `ui-mockups/neurotrace-state-responsive-components-review-v2.png`
- `ui-mockups/neurotrace-narrow-workbench-review-v3.png`（替代 v2：已裁除两侧黑边与导出残留）
- `ui-mockups/neurotrace-operation-feedback-components-review-v2.png`

## 可直接开发的资产包（v1）

- `design-system/tokens.css`：运行时 Design Tokens。
- `design-system/tokens.json`：设计工具/构建工具可读取的 Token 源值。
- `design-system/neurotrace-logo.svg`：固定 Logo 入口；引用 `neurotrace-logo-source.png`，后者从获批入口稿的首图 Logo 锁定提取。
- `design-system/fonts/z-labs-pixel-12px-cn.woff2`：随包交付的中文像素 Webfont；其 OFL 授权文本见同目录。
- `design-system/neurotrace-icons.svg`：3px 网格、`crispEdges` 的方块式 SVG Symbol 图标集。
- `design-system/components.css`：按钮、Tag、字段、证据卡、进度、Toast、Dialog 等基础组件。
- `design-system/DESIGN_CONTRACT.md`：视觉与语义不可变约束。
- `component-showcase/index.html`：可直接打开的交互组件展厅。

## 固定视觉规则

- 左上角 Logo：珊瑚色脑电/白色放大镜图形加白色像素字标 `NEUROTRACE`。
- Trace：保留现有帽饰、深色风衣、脑电徽章和浮动扫描器。
- 界面：低分辨率像素风、实色面板、2px 像素边框、短标签、少量重复图标；避免纹理、渐变、景深、模糊和不可复现的装饰。
- 状态色：青绿为确认，琥珀为待核验，暗红为风险/反证。
- 代码资产以 `design-system/` 为唯一实现源；界面审核稿用于布局核对，不作为前端运行时图片背景。


from __future__ import annotations

import base64
import hmac
import html
import os
from pathlib import Path

import streamlit as st

from neurotrace.engine import ROOT, ROLES, VERDICTS, exports, investigate, load_samples, parse_pdf, pdf_bytes, review

ASSETS = ROOT / "assets"
SYSTEM = ASSETS / "design-system"
POSTURES = ASSETS / "trace-postures"
POSES = {"LISTENING": "trace-listening.png", "THINKING": "trace-thinking.png", "SCANNING": "trace-scanning.png", "PRESENTING": "trace-presenting.png"}
TONES = {"direct_support": "support", "conditional_support": "support", "boundary": "qualify", "counterevidence": "counter", "insufficient": "neutral"}
DECISIONS = {"confirmed": "已确认", "rejected": "已驳回", "pending": "待核验"}
STATUS_TONES = {"confirmed": "status-confirmed", "rejected": "status-rejected", "pending": "status-pending"}


def uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def icon(symbol: str) -> str:
    return f'<span class="nt-icon" aria-hidden="true"><svg><use href="#{symbol}"/></svg></span>'


def visual_system() -> None:
    font = uri(SYSTEM / "fonts" / "z-labs-pixel-12px-cn.woff2", "font/woff2")
    tokens = (SYSTEM / "tokens.css").read_text(encoding="utf-8").replace('url("./fonts/z-labs-pixel-12px-cn.woff2")', f'url("{font}")')
    components = (SYSTEM / "components.css").read_text(encoding="utf-8").replace('@import url("./tokens.css");', "")
    st.markdown(f"""<style>
/* Hallmark · macrostructure: Workbench · tone: technical evidence archive · anchor hue: frozen NeuroTrace midnight navy
 * audience: ERP/EEG researchers · use: inspect, review, and export traceable evidence
 * pre-emit critique: P5 H5 E5 S5 R5 V4
 */
{tokens}
{components}
/* Streamlit adapter: only maps frozen primitives onto real Streamlit DOM. */
html, body, .stApp, [data-testid="stAppViewContainer"] {{ background: var(--nt-canvas); color: var(--nt-text); font-family: var(--nt-font-body); overflow-x: clip; }}
[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
.block-container {{ max-width: 1520px; padding: var(--nt-space-md) clamp(var(--nt-space-md), 3vw, var(--nt-space-2xl)) var(--nt-space-2xl); }}
[data-testid="stVerticalBlock"] {{ gap: var(--nt-space-md); min-width: 0; }}
[data-testid="stMarkdownContainer"], [data-testid="stText"], [data-testid="stCaptionContainer"], [data-testid="stWidgetLabel"], [data-testid="stStatusWidget"], [data-testid="stAlert"] {{ color: var(--nt-text) !important; font-family: var(--nt-font-body) !important; }}
[data-testid="stMarkdownContainer"] p, [data-testid="stText"] p {{ color: inherit !important; line-height: 1.6; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, [data-testid="stWidgetLabel"] p {{ color: var(--nt-text-muted) !important; font-size: var(--nt-text-xs) !important; }}
h1, h2, h3, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {{ color: var(--nt-text) !important; font-family: var(--nt-font-pixel) !important; font-style: normal; min-width: 0; overflow-wrap: anywhere; }}
h1 {{ font-size: clamp(var(--nt-text-lg), 3vw, var(--nt-text-xl)) !important; }}
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{ background: var(--nt-surface-deep) !important; color: var(--nt-text) !important; border: var(--nt-border) solid var(--nt-rule-strong) !important; border-radius: var(--nt-radius) !important; font-family: var(--nt-font-body) !important; }}
[data-testid="stTextArea"] textarea::placeholder, [data-testid="stTextInput"] input::placeholder {{ color: var(--nt-text-muted) !important; }}
@media (hover: hover) and (pointer: fine) {{ [data-testid="stTextArea"] textarea:hover, [data-testid="stTextInput"] input:hover, [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {{ background: var(--nt-surface-raised) !important; }} }}
[data-testid="stTextArea"] textarea:focus-visible, [data-testid="stTextInput"] input:focus-visible, [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {{ outline: var(--nt-border) solid var(--nt-focus) !important; outline-offset: var(--nt-space-2xs) !important; box-shadow: none !important; }}
[data-testid="stTextArea"] textarea[aria-invalid="true"], [data-testid="stTextInput"] input[aria-invalid="true"] {{ border-color: var(--nt-red) !important; }}
[data-testid="stTextArea"] textarea:disabled, [data-testid="stTextInput"] input:disabled {{ background: var(--nt-surface-deep) !important; border-color: var(--nt-rule) !important; color: var(--nt-text-muted) !important; cursor: not-allowed; opacity: .65; }}
[data-testid="stTextInput"] [data-baseweb="base-input"]:has(input:disabled) {{ background: var(--nt-surface-deep) !important; opacity: 1 !important; }}
[data-testid="stTextInput"] input:disabled {{ color: var(--nt-text-muted) !important; -webkit-text-fill-color: var(--nt-text-muted) !important; opacity: 1 !important; }}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label, [data-testid="stFileUploader"] label {{ color: var(--nt-text) !important; font-family: var(--nt-font-body) !important; }}
[data-testid="stRadio"] input, [data-testid="stCheckbox"] input {{ accent-color: var(--nt-teal); }}
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{ min-height: 2.75rem; border: var(--nt-border) solid var(--nt-rule-strong) !important; border-radius: var(--nt-radius) !important; background: var(--nt-surface-raised) !important; color: var(--nt-text) !important; font: 700 var(--nt-text-xs)/1 var(--nt-font-pixel) !important; white-space: nowrap; }}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{ background: var(--nt-teal) !important; border-color: var(--nt-teal) !important; color: var(--nt-ink) !important; }}
@media (hover: hover) and (pointer: fine) {{ .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{ background: var(--nt-paper) !important; border-color: var(--nt-ink) !important; color: var(--nt-ink) !important; }} }}
.stButton > button:active, .stDownloadButton > button:active, .stFormSubmitButton > button:active {{ transform: translate(var(--nt-space-3xs), var(--nt-space-3xs)); }}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible, .stFormSubmitButton > button:focus-visible, a:focus-visible {{ outline: var(--nt-border) solid var(--nt-focus) !important; outline-offset: var(--nt-space-2xs) !important; }}
.stButton > button:disabled, .stDownloadButton > button:disabled, .stFormSubmitButton > button:disabled {{ background: var(--nt-surface-deep) !important; border-color: var(--nt-rule) !important; color: var(--nt-text-muted) !important; opacity: .65; }}
[class*="st-key-confirm-"] button {{ background: var(--nt-teal) !important; border-color: var(--nt-teal) !important; color: var(--nt-ink) !important; }}
[class*="st-key-pending-"] button {{ background: var(--nt-amber) !important; border-color: var(--nt-amber) !important; color: var(--nt-ink) !important; }}
[class*="st-key-reject-"] button {{ background: var(--nt-red) !important; border-color: var(--nt-red) !important; color: var(--nt-text) !important; }}
[data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {{ background: var(--nt-surface) !important; color: var(--nt-text) !important; border: var(--nt-border) solid var(--nt-rule-strong) !important; border-radius: var(--nt-radius) !important; box-shadow: var(--nt-shadow-pixel); }}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary span {{ color: var(--nt-text) !important; font-family: var(--nt-font-pixel) !important; }}
[data-testid="stMetric"] {{ background: var(--nt-surface) !important; border: var(--nt-border) solid var(--nt-rule) !important; border-radius: var(--nt-radius) !important; padding: var(--nt-space-sm) !important; }}
[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {{ color: var(--nt-text) !important; font-family: var(--nt-font-pixel) !important; }}
[data-testid="stAlert"] {{ border: var(--nt-border-thin) solid var(--nt-rule-strong); border-radius: var(--nt-radius); }}
[data-testid="stAlert"] * {{ color: inherit !important; }}
[data-testid="stStatusWidget"] {{ background: var(--nt-surface-deep); border: var(--nt-border) solid var(--nt-rule-strong); border-radius: var(--nt-radius); }}
.nt-header {{ display: flex; justify-content: space-between; align-items: center; gap: var(--nt-space-md); padding-block: var(--nt-space-sm) var(--nt-space-md); border-bottom: var(--nt-border) solid var(--nt-rule); margin-bottom: var(--nt-space-lg); }}
.nt-logo img {{ display: block; width: min(17rem, 48vw); height: auto; }}
.nt-nav {{ display: flex; gap: var(--nt-space-xs); flex-wrap: wrap; }}
.nt-nav a {{ display: inline-flex; align-items: center; gap: var(--nt-space-xs); min-height: 2.5rem; padding: var(--nt-space-xs) var(--nt-space-sm); color: var(--nt-text-muted); border: var(--nt-border-thin) solid var(--nt-rule); background: var(--nt-surface); font: 700 var(--nt-text-xs)/1 var(--nt-font-pixel); text-decoration: none; white-space: nowrap; }}
.nt-nav svg {{ width: var(--nt-text-base); height: var(--nt-text-base); }}
.nt-nav a[aria-current="page"] {{ color: var(--nt-text); border-color: var(--nt-teal); background: var(--nt-surface-raised); }}
.nt-trace-panel {{ display: grid; place-items: center; min-width: 0; padding: var(--nt-space-lg); background: var(--nt-surface-deep); color: var(--nt-text); border: var(--nt-border) solid var(--nt-rule-strong); }}
.nt-trace-panel img {{ width: 100%; max-height: 34rem; object-fit: contain; image-rendering: pixelated; }}
.nt-evidence {{ margin-block: var(--nt-space-sm); }}
.nt-evidence.selected .nt-evidence-card {{ outline: var(--nt-border) solid var(--nt-teal); outline-offset: var(--nt-space-2xs); }}
.nt-evidence-card h3 {{ color: var(--nt-ink) !important; }}
.nt-evidence-card__meta {{ flex-wrap: wrap; }}
.nt-tag--status-confirmed {{ color: var(--nt-teal); }} .nt-tag--status-pending {{ color: var(--nt-amber); }} .nt-tag--status-rejected {{ color: var(--nt-red); }}
.nt-evidence-card .nt-tag {{ color: inherit; }} .nt-evidence-card .nt-tag--support, .nt-evidence-card .nt-tag--status-confirmed {{ color: var(--nt-teal); }} .nt-evidence-card .nt-tag--qualify, .nt-evidence-card .nt-tag--status-pending {{ color: var(--nt-amber); }} .nt-evidence-card .nt-tag--counter, .nt-evidence-card .nt-tag--status-rejected {{ color: var(--nt-red); }} .nt-evidence-card .nt-tag--neutral {{ color: var(--nt-ink-muted); }}
.nt-event {{ display: grid; gap: var(--nt-space-2xs); padding-block: var(--nt-space-sm); border-bottom: var(--nt-border-thin) solid var(--nt-rule); color: var(--nt-text); }} .nt-event small {{ color: var(--nt-text-muted); font-family: var(--nt-font-pixel); }}
.nt-note, .nt-risk {{ padding: var(--nt-space-sm); background: var(--nt-surface-deep); color: var(--nt-text-muted); font-size: var(--nt-text-xs); line-height: 1.6; }} .nt-note {{ border-left: var(--nt-border) solid var(--nt-teal); }} .nt-risk {{ border-left: var(--nt-border) solid var(--nt-amber); }}
.nt-reader {{ display: grid; gap: var(--nt-space-md); padding: var(--nt-space-lg); background: var(--nt-paper); color: var(--nt-ink); border: var(--nt-border) solid var(--nt-ink); box-shadow: var(--nt-shadow-pixel); }} .nt-reader h2, .nt-reader p {{ color: var(--nt-ink) !important; }} .nt-reader .nt-caption {{ color: var(--nt-ink-muted) !important; }} .nt-reader blockquote {{ margin: 0; padding: var(--nt-space-md); border-left: var(--nt-border) solid var(--nt-amber); background: var(--nt-paper-muted); color: var(--nt-ink); white-space: pre-wrap; line-height: 1.6; }}
@media (max-width: 63.99rem) {{ .nt-header {{ align-items: flex-start; flex-direction: column; }} .block-container {{ padding-inline: var(--nt-space-md); }} .nt-nav {{ width: 100%; }} .nt-nav a {{ flex: 1 1 auto; justify-content: center; }} .st-key-workbench-main [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; }} .st-key-workbench-main [data-testid="stColumn"] {{ width: 100% !important; flex: 1 1 100% !important; }} .st-key-reader-index {{ display: none; }} .st-key-reader-paper, [data-testid="stElementContainer"]:has(.nt-reader) {{ position: fixed !important; inset: 0 !important; z-index: var(--nt-z-modal) !important; display: block !important; width: 100vw !important; max-width: none !important; height: 100vh !important; overflow-y: auto !important; padding: var(--nt-space-md) !important; background: var(--nt-canvas) !important; }} [class*="st-key-reader-close"] {{ position: fixed !important; top: var(--nt-space-md) !important; left: var(--nt-space-md) !important; z-index: var(--nt-z-toast) !important; }} .st-key-reader-paper .nt-reader, [data-testid="stElementContainer"]:has(.nt-reader) .nt-reader {{ min-height: calc(100vh - 2 * var(--nt-space-md)); }} }}
@media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ transition-duration: 150ms !important; animation-duration: 150ms !important; animation-iteration-count: 1 !important; }} }}
</style>""", unsafe_allow_html=True)


def initialise() -> None:
    for key, value in {"uploaded_cards": [], "case": None, "clarification": None, "reader_card": None, "reject_card": None}.items():
        if key not in st.session_state:
            st.session_state[key] = value


def page() -> str:
    value = st.query_params.get("view", "neural-trace")
    return value if value in {"neural-trace", "workbench"} else "neural-trace"


def header(active: str) -> None:
    source = (SYSTEM / "neurotrace-logo.svg").read_text(encoding="utf-8").replace("neurotrace-logo-source.png", uri(SYSTEM / "neurotrace-logo-source.png", "image/png"))
    icons = (SYSTEM / "neurotrace-icons.svg").read_text(encoding="utf-8")
    logo = f"data:image/svg+xml;base64,{base64.b64encode(source.encode()).decode()}"
    current = {"neural-trace": "", "workbench": ""}
    current[active] = ' aria-current="page"'
    st.markdown(f'<div aria-hidden="true" style="display:none">{icons}</div><header class="nt-header"><a class="nt-logo" href="?view=neural-trace" aria-label="NeuroTrace 新建调查"><img src="{logo}" alt="NEUROTRACE"/></a><nav class="nt-nav" aria-label="主导航"><a href="?view=neural-trace"{current["neural-trace"]}><svg aria-hidden="true"><use href="#nt-scan"/></svg>新建调查</a><a href="?view=workbench"{current["workbench"]}><svg aria-hidden="true"><use href="#nt-evidence"/></svg>调查工作台</a></nav></header>', unsafe_allow_html=True)


def pose(name: str) -> None:
    image = uri(POSTURES / POSES[name], "image/png")
    st.markdown(f'<figure class="nt-trace-panel"><img src="{image}" alt="Trace {name.lower()}"/></figure>', unsafe_allow_html=True)


def config() -> tuple[str, str, str, list[dict]]:
    with st.expander("调查配置", expanded=False):
        run_mode = st.radio("运行方式", ["演示模式 · 无需模型", "本地模型 · Ollama"], horizontal=True)
        mode = "demo" if run_mode.startswith("演示") else "ollama"
        base_url = st.text_input("模型服务地址", os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"), disabled=mode == "demo")
        model = st.text_input("模型名称", os.environ.get("OLLAMA_MODEL", "qwen3:8b"), disabled=mode == "demo")
        source = st.radio("资料来源", ["交接包样例", "我上传的 PDF"], horizontal=True)
        if source == "我上传的 PDF":
            files = st.file_uploader("导入论文 PDF", type=["pdf"], accept_multiple_files=True)
            if st.button("解析并加入本次资料库", disabled=not files):
                with st.spinner("正在逐页解析 PDF…"):
                    for file in files or []:
                        try:
                            cards = parse_pdf(file.getvalue(), file.name)
                            known = {item["card_id"] for item in st.session_state.uploaded_cards}
                            st.session_state.uploaded_cards.extend(item for item in cards if item["card_id"] not in known)
                            st.success(f"{file.name}：已加入 {len(cards)} 条可定位片段")
                        except Exception as exc:
                            st.error(f"{file.name}：{exc}")
            st.caption("单份最多 25 MB；扫描件暂不支持 OCR。")
        corpus = load_samples() if source == "交接包样例" else st.session_state.uploaded_cards
        st.caption(f"当前可检索片段：{len(corpus)}")
    return mode, base_url, model, corpus


def investigate_case(question: str, corpus: list[dict], mode: str, base_url: str, model: str) -> None:
    st.session_state.case = None
    try:
        with st.status("正在执行调查", expanded=True) as status:
            pose("SCANNING")
            case = investigate(question, corpus, mode, base_url, model, lambda event: st.write(event["message"]))
            st.session_state.case = case
            status.update("调查完成" if not case["error"] else "模型调用未完成", state="complete" if not case["error"] else "error", expanded=False)
    except Exception as exc:
        st.error(str(exc))


def entry_content() -> bool:
    mode, base_url, model, corpus = config()
    show_workbench = False
    pending = st.session_state.clarification
    left, right = st.columns([.8, 1.2])
    with left:
        pose("THINKING" if pending else "LISTENING")
    with right:
        if pending:
            st.title("补齐一个关键条件")
            st.write("当前问题还不足以定位证据。请选择最影响解释的一项信息；不需要填写冗长问卷。")
            with st.form("clarification_form"):
                focus = st.selectbox("本次最需要确认的维度", ["研究任务或语境", "被试群体", "ERP 成分与指标方向"])
                detail = st.text_input("补充内容", placeholder="例如：词汇判断任务中的晚期正波振幅")
                submit = st.form_submit_button("带着条件开始调查", type="primary", disabled=not corpus)
            if submit:
                st.session_state.clarification = None
                investigate_case(f"{pending}\n补充条件（{focus}）：{detail.strip() or '用户未补充'}", corpus, mode, base_url, model)
                st.query_params["view"] = "workbench"
                show_workbench = True
        else:
            st.title("从一条论断开始核验")
            st.write("输入你的研究问题。NeuroTrace 只依据当前批准的本地证据，呈现支持、限定和反证，并保留可回查的调查记录。")
            if mode == "demo":
                st.info("当前为流程演示：检索、审阅和导出真实执行，但样例关系不是科研结论。")
            with st.form("question_form"):
                question = st.text_area("研究问题", value="情绪唤醒度是否会影响 LPC 振幅？", height=128, max_chars=2000, key="investigation-question")
                submit = st.form_submit_button("开始调查", type="primary", disabled=not corpus)
            if submit:
                if len(question.strip()) < 12:
                    st.session_state.clarification = question
                    st.rerun()
                investigate_case(question, corpus, mode, base_url, model)
                st.query_params["view"] = "workbench"
                show_workbench = True
    return show_workbench


def entry() -> None:
    screen = st.empty()
    with screen.container():
        show_workbench = entry_content()
    if show_workbench:
        screen.empty()
        workbench()


def evidence_html(card: dict, relation: dict, decision: str, selected: bool = False) -> str:
    relation_tone = TONES.get(relation.get("role"), "neutral")
    status_tone = STATUS_TONES.get(decision, "status-pending")
    source = "交接包样例（无原始 PDF）" if card["source_type"] == "sample" else "本次上传 PDF"
    relation_label = ROLES.get(relation.get("role"), "未分析")
    return f'<article class="nt-evidence{" selected" if selected else ""}"><div class="nt-evidence-card"><div class="nt-evidence-card__meta"><span>{html.escape(card["card_id"])} · PDF 第 {card["page"]} 页</span><span class="nt-tag nt-tag--{relation_tone}">关系：{html.escape(relation_label)}</span><span class="nt-tag nt-tag--{status_tone}">核验：{html.escape(DECISIONS[decision])}</span></div><h3>{html.escape(card["title"])}</h3><p>{html.escape(relation.get("reason") or "尚未完成关系分析。")}</p><div class="nt-evidence-card__condition">关键条件：{html.escape(relation.get("conditions") or card.get("conditions") or "尚待核对研究条件")}</div><div class="nt-evidence-card__meta"><span>{source}</span><span>页码可回查</span></div></div></article>'


def review_actions(case: dict, card: dict) -> None:
    cid = card["card_id"]
    first, second, third, fourth = st.columns(4)
    first.markdown(icon("nt-evidence"), unsafe_allow_html=True)
    second.markdown(icon("nt-check"), unsafe_allow_html=True)
    third.markdown(icon("nt-pause"), unsafe_allow_html=True)
    fourth.markdown(icon("nt-reject"), unsafe_allow_html=True)
    if first.button("查看原文", key=f"view-{cid}"):
        st.session_state.reader_card = cid
        st.rerun()
    if second.button("确认采用", key=f"confirm-{cid}"):
        review(case, cid, "confirmed")
        st.rerun()
    if third.button("暂缓核验", key=f"pending-{cid}"):
        review(case, cid, "pending")
        st.rerun()
    if fourth.button("驳回证据", key=f"reject-{cid}"):
        st.session_state.reject_card = cid
        st.rerun()


def reject_panel(case: dict) -> None:
    cid = st.session_state.reject_card
    if not cid:
        return
    st.warning("驳回会立即重新计算相关判断。请留下可审计的原因。")
    with st.form(f"reject-form-{cid}"):
        reason = st.text_area("驳回原因", placeholder="例如：页码无法定位、条件不匹配，或摘录并非该研究结果。", max_chars=1000, key=f"reject-reason-{cid}")
        save, cancel = st.columns(2)
        commit = save.form_submit_button("提交驳回并重算", type="primary")
        abandon = cancel.form_submit_button("取消")
    if abandon:
        st.session_state.reject_card = None
        st.rerun()
    if commit:
        if not reason.strip():
            st.error("请填写驳回原因后再重算。")
        else:
            review(case, cid, "rejected")
            case["reviews"][cid]["reason"] = reason.strip()
            st.session_state.reject_card = None
            st.rerun()


def export_dossier(case: dict) -> None:
    with st.container(border=True):
        st.subheader("数字档案袋")
        st.markdown('<div class="nt-note">论文事实：导出包含来源、页码、摘录、关系与核验状态。</div>', unsafe_allow_html=True)
        st.markdown('<div class="nt-risk">研究建议：当前判断与待检验问题是基于证据链的建议，不等同于论文事实。</div>', unsafe_allow_html=True)
        st.caption(f"案件状态：{case['finding']['status']} · 创建时间：{case['created_at']}")
        data = exports(case)
        for column, extension, mime in zip(st.columns(3), ["md", "json", "csv"], ["text/markdown", "application/json", "text/csv"]):
            column.markdown(icon("nt-download"), unsafe_allow_html=True)
            column.download_button(f"导出 {extension.upper()}", data[extension].encode("utf-8"), file_name=f"neurotrace-{case['case_id']}.{extension}", mime=mime, key=f"export-{extension}")


def progress_html(events: list[dict]) -> str:
    completed = len(events)
    scale = 1 if completed else 0
    return f'<div class="nt-progress" role="progressbar" aria-label="真实执行进度" aria-valuemin="0" aria-valuemax="{max(completed, 1)}" aria-valuenow="{completed}" style="--nt-progress-scale:{scale}"><span>执行记录</span><span class="nt-progress__rail"><span class="nt-progress__value"></span></span><span>{completed} 项</span></div>'

def verification_sort_key(case: dict, card: dict, relations: dict[str, dict]) -> tuple[int, int, str]:
    relation = relations.get(card["card_id"], {})
    impact = {"counterevidence": 0, "boundary": 1, "conditional_support": 2, "direct_support": 3, "insufficient": 4}
    decision = case["reviews"].get(card["card_id"], {}).get("decision", "pending")
    return impact.get(relation.get("role"), 5), 0 if decision == "pending" else 1, card["card_id"]


def workbench() -> None:
    case = st.session_state.case
    if not case:
        st.info("尚未建立调查。请从“新建调查”输入一个研究问题。")
        return
    if case["error"]:
        st.error(case["error"] + " 未以演示结果替代模型输出。")
    finding = case["finding"]
    if finding["is_demo"]:
        st.warning("本案为流程演示；确认样例卡不会转变为正式引用。")
    a, b, c = st.columns(3)
    a.metric("召回证据", len(case["cards"]))
    b.metric("保留证据", len(finding["active_card_ids"]))
    c.metric("本次耗时", f"{case['elapsed_seconds']:.2f} 秒")
    relations = {item["card_id"]: item for item in case["relations"]}
    cards = {item["card_id"]: item for item in case["cards"]}
    ordered_cards = sorted(case["cards"], key=lambda card: verification_sort_key(case, card, relations))
    selected = st.session_state.reader_card
    if selected in cards:
        left, right = st.columns([.85, 2.15])
        with left:
            with st.container(border=True, key="reader-index"):
                st.subheader("本案证物")
                for item in ordered_cards:
                    relation = relations.get(item["card_id"], {})
                    decision = case["reviews"].get(item["card_id"], {}).get("decision", "pending")
                    st.markdown(evidence_html(item, relation, decision, item["card_id"] == selected), unsafe_allow_html=True)
                    if item["card_id"] != selected and st.button("定位证物", key=f"locate-{item['card_id']}"):
                        st.session_state.reader_card = item["card_id"]
                        st.rerun()
        with right:
            card = cards[selected]
            with st.container(key="reader-paper"):
                if st.button("退出阅读", key="reader-close"):
                    st.session_state.reader_card = None
                    st.rerun()
                st.markdown(f'<article class="nt-reader"><h2>{html.escape(card["title"])}</h2><p class="nt-caption">自动定位：PDF 第 {card["page"]} 页 · 证物 {html.escape(card["card_id"])}</p><blockquote>{html.escape(card["quote"])}</blockquote><p>关键条件：{html.escape(relations.get(selected, {}).get("conditions") or card.get("conditions", "尚待核对"))}</p></article>', unsafe_allow_html=True)
                if card["source_type"] == "pdf":
                    try:
                        st.download_button("下载原始 PDF 核对页码", pdf_bytes(card), file_name=card["title"], mime="application/pdf", key=f"pdf-{selected}")
                    except (OSError, ValueError) as exc:
                        st.error(str(exc))
                else:
                    st.caption("此为交接包样例，未包含原始 PDF；页码字段保留为演示锚点。")
        return
    main = st.container(key="workbench-main")
    left, center, right = main.columns([.9, 2.1, 1])
    with left:
        with st.container(border=True):
            st.subheader("本案基线")
            st.write(case["question"])
            st.caption(f"案件编号：{case['case_id']}")
            st.caption(f"运行方式：{case['mode']} · 模型：{case['model']}")
            st.markdown('<div class="nt-note">原始问题、来源模式和审阅决定都保留在本案记录中。</div>', unsafe_allow_html=True)
    with center:
        with st.container(border=True):
            st.subheader("当前判断")
            st.markdown(f"**{VERDICTS[finding['verdict']]}**")
            st.write(finding["summary"])
            st.markdown('<div class="nt-note">这是受当前语料、核验状态和证据条件约束的判断，不代替研究者的科学结论。</div>', unsafe_allow_html=True)
            st.subheader("待检验问题")
            st.write(finding["hypothesis"])
            st.subheader("关键核验")
            st.caption("先显示最可能改变最终判断、且仍待核验的证据。")
            if not case["cards"]:
                st.info("没有检索到相关片段。请修改问题或导入相关 PDF。")
            for card in ordered_cards:
                relation = relations.get(card["card_id"], {})
                decision = case["reviews"].get(card["card_id"], {}).get("decision", "pending")
                st.markdown(evidence_html(card, relation, decision), unsafe_allow_html=True)
                review_actions(case, card)
            reject_panel(case)
            export_dossier(case)
    with right:
        with st.container(border=True):
            st.subheader("真实执行流")
            pose("PRESENTING")
            st.markdown(progress_html(case["events"]), unsafe_allow_html=True)
            for event in case["events"]:
                stage = html.escape(str(event.get("stage", "event")))
                message = html.escape(str(event.get("message", "")))
                timing = event.get("elapsed_seconds")
                st.markdown(f'<div class="nt-event"><small>{stage} · {timing if timing is not None else "状态变更"} 秒</small><span>{message}</span></div>', unsafe_allow_html=True)


def run() -> None:
    st.set_page_config(page_title="NeuroTrace · 研究证据工作台", page_icon="🔎", layout="wide")
    visual_system()
    initialise()
    password = os.environ.get("NEUROTRACE_PASSWORD", "")
    if password and not st.session_state.get("authenticated"):
        header("neural-trace")
        st.title("进入受控工作台")
        entered = st.text_input("工作台访问密码", type="password")
        if st.button("进入工作台", type="primary"):
            if hmac.compare_digest(entered.encode(), password.encode()):
                st.session_state.authenticated = True
                st.rerun()
            st.error("密码不正确，请重新输入。")
        st.stop()
    active = page()
    header(active)
    if active == "workbench":
        workbench()
    else:
        entry()


run()

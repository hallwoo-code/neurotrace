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


def uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def visual_system() -> None:
    font = uri(SYSTEM / "fonts" / "z-labs-pixel-12px-cn.woff2", "font/woff2")
    tokens = (SYSTEM / "tokens.css").read_text(encoding="utf-8").replace('url("./fonts/z-labs-pixel-12px-cn.woff2")', f'url("{font}")')
    components = (SYSTEM / "components.css").read_text(encoding="utf-8").replace('@import url("./tokens.css");', "")
    st.markdown(f"""<style>
/* Hallmark · macrostructure: Workbench · tone: technical evidence archive · anchor hue: frozen NeuroTrace midnight navy
 * audience: ERP/EEG researchers · use: inspect, review, and export traceable evidence
 * pre-emit critique: P5 H5 E4 S5 R5 V4
 */
{tokens}
{components}
html,body,[data-testid="stAppViewContainer"]{{background:var(--nt-canvas);color:var(--nt-text);overflow-x:clip}}[data-testid="stHeader"],[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{{display:none}}.block-container{{max-width:1520px;padding:1rem clamp(1rem,3vw,3rem) 3rem}}[data-testid="stVerticalBlock"]{{gap:1rem}}h1,h2,h3{{color:var(--nt-text)!important;font-family:var(--nt-font-pixel)!important;font-style:normal;overflow-wrap:anywhere}}h1{{font-size:clamp(1.75rem,3vw,2.45rem)!important}}[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input{{background:var(--nt-surface-deep)!important;color:var(--nt-text)!important;border:var(--nt-border) solid var(--nt-rule-strong)!important;border-radius:0!important}}[data-testid="stTextArea"] textarea:focus,[data-testid="stTextInput"] input:focus{{outline:var(--nt-border) solid var(--nt-focus)!important;outline-offset:.25rem!important;box-shadow:none!important}}[data-testid="stSelectbox"] div[data-baseweb="select"]>div{{background:var(--nt-surface-deep);color:var(--nt-text);border:var(--nt-border) solid var(--nt-rule-strong);border-radius:0}}button[kind="primary"],button[kind="secondary"]{{min-height:2.75rem;border-radius:0!important;border:var(--nt-border) solid var(--nt-rule-strong)!important;font-family:var(--nt-font-pixel)!important;white-space:nowrap}}button[kind="primary"]{{background:var(--nt-teal)!important;color:var(--nt-ink)!important;border-color:var(--nt-teal)!important}}button[kind="secondary"]{{background:var(--nt-surface-raised)!important;color:var(--nt-text)!important}}button[kind="secondary"]:hover{{background:var(--nt-paper)!important;color:var(--nt-ink)!important}}button:focus-visible,a:focus-visible{{outline:var(--nt-border) solid var(--nt-focus)!important;outline-offset:.25rem!important}}button:active{{transform:translate(.125rem,.125rem)}}[data-testid="stExpander"]{{background:var(--nt-surface)!important;border:var(--nt-border) solid var(--nt-rule-strong)!important;border-radius:0!important;box-shadow:var(--nt-shadow-pixel)}}[data-testid="stMetric"]{{background:var(--nt-surface)!important;border:var(--nt-border) solid var(--nt-rule)!important;border-radius:0!important;padding:.75rem!important}}[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{{color:var(--nt-text)!important;font-family:var(--nt-font-pixel)}}
.nt-header{{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:.75rem 0 1rem;border-bottom:var(--nt-border) solid var(--nt-rule);margin-bottom:1.5rem}}.nt-logo img{{display:block;width:min(17rem,48vw);height:auto}}.nt-nav{{display:flex;gap:.5rem;flex-wrap:wrap}}.nt-nav a{{display:inline-flex;align-items:center;min-height:2.5rem;padding:.5rem .75rem;color:var(--nt-text-muted);border:var(--nt-border-thin) solid var(--nt-rule);font:700 var(--nt-text-xs)/1 var(--nt-font-pixel);text-decoration:none;white-space:nowrap}}.nt-nav a[aria-current="page"]{{color:var(--nt-text);border-color:var(--nt-teal);background:var(--nt-surface-raised)}}.nt-trace{{background:var(--nt-surface-deep);border:var(--nt-border) solid var(--nt-rule-strong);padding:1.5rem}}.nt-trace img{{width:100%;max-height:34rem;object-fit:contain;image-rendering:pixelated}}.nt-copy{{min-width:0}}.nt-copy p{{color:var(--nt-text-muted);line-height:1.65;max-width:56ch}}.nt-shell{{background:var(--nt-surface);border:var(--nt-border) solid var(--nt-rule);padding:1rem;min-width:0}}.nt-shell h2{{margin-top:0}}.nt-evidence{{margin:.85rem 0}}.nt-evidence .nt-evidence-card{{box-shadow:var(--nt-shadow-pixel)}}.nt-evidence.selected .nt-evidence-card{{outline:var(--nt-border) solid var(--nt-teal);outline-offset:.25rem}}.nt-event{{display:grid;gap:.25rem;padding:.75rem 0;border-bottom:var(--nt-border-thin) solid var(--nt-rule)}}.nt-event small{{color:var(--nt-text-muted);font-family:var(--nt-font-pixel)}}.nt-note,.nt-risk{{padding:.75rem;background:var(--nt-surface-deep);color:var(--nt-text-muted);font-size:var(--nt-text-xs);line-height:1.6}}.nt-note{{border-left:var(--nt-border) solid var(--nt-teal)}}.nt-risk{{border-left:var(--nt-border) solid var(--nt-amber)}}.nt-reader{{background:var(--nt-paper);color:var(--nt-ink);border:var(--nt-border) solid var(--nt-ink);box-shadow:var(--nt-shadow-pixel);padding:1.5rem;min-width:0}}.nt-reader h2{{color:var(--nt-ink)!important}}.nt-reader blockquote{{margin:1rem 0;padding:1rem;border-left:var(--nt-border) solid var(--nt-amber);background:var(--nt-paper-muted);white-space:pre-wrap;line-height:1.6}}
@media(max-width:47.99rem){{.nt-header{{align-items:flex-start;flex-direction:column}}.block-container{{padding-inline:1rem}}}}@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{transition-duration:150ms!important;animation-duration:150ms!important;animation-iteration-count:1!important}}}}
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
    logo = f"data:image/svg+xml;base64,{base64.b64encode(source.encode()).decode()}"
    current = {"neural-trace": "", "workbench": ""}
    current[active] = ' aria-current="page"'
    st.markdown(f'<header class="nt-header"><a class="nt-logo" href="?view=neural-trace" aria-label="NeuroTrace 新建调查"><img src="{logo}" alt="NEUROTRACE"/></a><nav class="nt-nav" aria-label="主导航"><a href="?view=neural-trace"{current["neural-trace"]}>新建调查</a><a href="?view=workbench"{current["workbench"]}>调查工作台</a></nav></header>', unsafe_allow_html=True)


def pose(name: str) -> None:
    st.markdown('<div class="nt-trace">', unsafe_allow_html=True)
    st.image(str(POSTURES / POSES[name]), width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)


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
            st.image(str(POSTURES / POSES["SCANNING"]), width=112)
            case = investigate(question, corpus, mode, base_url, model, lambda event: st.write(event["message"]))
            st.session_state.case = case
            status.update("调查完成" if not case["error"] else "模型调用未完成", state="complete" if not case["error"] else "error", expanded=False)
    except Exception as exc:
        st.error(str(exc))


def entry() -> None:
    mode, base_url, model, corpus = config()
    pending = st.session_state.clarification
    left, right = st.columns([.8, 1.2])
    with left:
        pose("THINKING" if pending else "LISTENING")
    with right:
        st.markdown('<section class="nt-copy">', unsafe_allow_html=True)
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
                st.rerun()
        else:
            st.title("从一条论断开始核验")
            st.write("输入你的研究问题。NeuroTrace 只依据当前批准的本地证据，呈现支持、限定和反证，并保留可回查的调查记录。")
            if mode == "demo":
                st.info("当前为流程演示：检索、审阅和导出真实执行，但样例关系不是科研结论。")
            with st.form("question_form"):
                question = st.text_area("研究问题", value="情绪唤醒度是否会影响 LPC 振幅？", height=128, max_chars=2000)
                submit = st.form_submit_button("开始调查", type="primary", disabled=not corpus)
            if submit:
                if len(question.strip()) < 12:
                    st.session_state.clarification = question
                    st.rerun()
                investigate_case(question, corpus, mode, base_url, model)
                st.query_params["view"] = "workbench"
                st.rerun()
        st.markdown("</section>", unsafe_allow_html=True)


def evidence_html(card: dict, relation: dict, decision: str, selected: bool = False) -> str:
    tone = TONES.get(relation.get("role"), "neutral")
    source = "交接包样例（无原始 PDF）" if card["source_type"] == "sample" else "本次上传 PDF"
    return f'<article class="nt-evidence{" selected" if selected else ""}"><div class="nt-evidence-card"><div class="nt-evidence-card__meta"><span>{html.escape(card["card_id"])} · PDF 第 {card["page"]} 页</span><span class="nt-tag nt-tag--{tone}">{html.escape(DECISIONS[decision])}</span></div><h3>{html.escape(ROLES.get(relation.get("role"), "未分析"))} · {html.escape(card["title"])}</h3><p>{html.escape(relation.get("reason") or "尚未完成关系分析。")}</p><div class="nt-evidence-card__condition">关键条件：{html.escape(relation.get("conditions") or card.get("conditions") or "尚待核对研究条件")}</div><div class="nt-evidence-card__meta"><span>{source}</span><span>页码可回查</span></div></div></article>'


def review_actions(case: dict, card: dict) -> None:
    cid = card["card_id"]
    first, second, third, fourth = st.columns(4)
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
        reason = st.text_area("驳回原因", placeholder="例如：页码无法定位、条件不匹配，或摘录并非该研究结果。", max_chars=1000)
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
    with st.expander("案件卷宗与导出", expanded=False):
        st.markdown('<div class="nt-note">论文事实：导出包含来源、页码、摘录、关系与核验状态。</div>', unsafe_allow_html=True)
        st.markdown('<div class="nt-risk">研究建议：当前判断与待检验问题是基于证据链的建议，不等同于论文事实。</div>', unsafe_allow_html=True)
        st.caption(f"案件状态：{case['finding']['status']} · 创建时间：{case['created_at']}")
        data = exports(case)
        for column, extension, mime in zip(st.columns(3), ["md", "json", "csv"], ["text/markdown", "application/json", "text/csv"]):
            column.download_button(f"导出 {extension.upper()}", data[extension].encode("utf-8"), file_name=f"neurotrace-{case['case_id']}.{extension}", mime=mime)


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
    selected = st.session_state.reader_card
    if selected in cards:
        left, right = st.columns([.85, 2.15])
        with left:
            st.markdown('<section class="nt-shell">', unsafe_allow_html=True)
            st.subheader("本案证物")
            for card in case["cards"]:
                relation = relations.get(card["card_id"], {})
                decision = case["reviews"].get(card["card_id"], {}).get("decision", "pending")
                st.markdown(evidence_html(card, relation, decision, card["card_id"] == selected), unsafe_allow_html=True)
                if card["card_id"] != selected and st.button("定位此证物", key=f"locate-{card['card_id']}"):
                    st.session_state.reader_card = card["card_id"]
                    st.rerun()
            if st.button("关闭阅读态"):
                st.session_state.reader_card = None
                st.rerun()
            st.markdown("</section>", unsafe_allow_html=True)
        with right:
            card = cards[selected]
            st.markdown('<section class="nt-reader">', unsafe_allow_html=True)
            st.subheader(card["title"])
            st.caption(f"自动定位：PDF 第 {card['page']} 页 · 证物 {card['card_id']}")
            st.markdown(f"<blockquote>{html.escape(card['quote'])}</blockquote>", unsafe_allow_html=True)
            st.write(f"关键条件：{relations.get(selected, {}).get('conditions') or card.get('conditions', '尚待核对')}")
            if card["source_type"] == "pdf":
                try:
                    st.download_button("下载原始 PDF 核对页码", pdf_bytes(card), file_name=card["title"], mime="application/pdf", key=f"pdf-{selected}")
                except (OSError, ValueError) as exc:
                    st.error(str(exc))
            else:
                st.caption("此为交接包样例，未包含原始 PDF；页码字段保留为演示锚点。")
            st.markdown("</section>", unsafe_allow_html=True)
        return
    left, center, right = st.columns([.9, 2.1, 1])
    with left:
        st.markdown('<section class="nt-shell">', unsafe_allow_html=True)
        st.subheader("本案基线")
        st.write(case["question"])
        st.caption(f"案件编号：{case['case_id']}")
        st.caption(f"运行方式：{case['mode']} · 模型：{case['model']}")
        st.markdown('<div class="nt-note">原始问题、来源模式和审阅决定都保留在本案记录中。</div>', unsafe_allow_html=True)
        st.markdown("</section>", unsafe_allow_html=True)
    with center:
        st.markdown('<section class="nt-shell">', unsafe_allow_html=True)
        st.subheader("当前判断")
        st.markdown(f"**{VERDICTS[finding['verdict']]}**")
        st.write(finding["summary"])
        st.markdown('<div class="nt-note">这是受当前语料、核验状态和证据条件约束的判断，不代替研究者的科学结论。</div>', unsafe_allow_html=True)
        st.subheader("待检验问题")
        st.write(finding["hypothesis"])
        st.subheader("证据与审阅")
        if not case["cards"]:
            st.info("没有检索到相关片段。请修改问题或导入相关 PDF。")
        for card in case["cards"]:
            relation = relations.get(card["card_id"], {})
            decision = case["reviews"].get(card["card_id"], {}).get("decision", "pending")
            st.markdown(evidence_html(card, relation, decision), unsafe_allow_html=True)
            review_actions(case, card)
        reject_panel(case)
        export_dossier(case)
        st.markdown("</section>", unsafe_allow_html=True)
    with right:
        st.markdown('<section class="nt-shell">', unsafe_allow_html=True)
        st.subheader("真实执行流")
        st.image(str(POSTURES / POSES["PRESENTING"]), width=112)
        for event in case["events"]:
            stage = html.escape(str(event.get("stage", "event")))
            message = html.escape(str(event.get("message", "")))
            timing = event.get("elapsed_seconds")
            st.markdown(f'<div class="nt-event"><small>{stage} · {timing if timing is not None else "状态变更"} 秒</small><span>{message}</span></div>', unsafe_allow_html=True)
        st.markdown("</section>", unsafe_allow_html=True)


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

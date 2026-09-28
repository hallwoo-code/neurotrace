from __future__ import annotations

import hmac
import os

import streamlit as st

from neurotrace.engine import ROOT, ROLES, VERDICTS, exports, investigate, load_samples, parse_pdf, pdf_bytes, review

st.set_page_config(page_title="NeuroTrace · 研究证据工作台", page_icon="🔎", layout="wide")
password = os.environ.get("NEUROTRACE_PASSWORD", "")
if password:
    if not st.session_state.get("authenticated"):
        st.title("NeuroTrace")
        entered = st.text_input("工作台访问密码", type="password")
        if st.button("进入工作台"):
            if hmac.compare_digest(entered.encode(), password.encode()):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密码不正确")
        st.stop()

st.markdown("""<style>
.stApp {background:#f4f6f8;}
.block-container {padding-top:2rem; max-width:1450px;}
h1,h2,h3 {color:#182c43;}
div[data-testid="stMetric"] {background:white; padding:14px; border-radius:10px; border:1px solid #e2e8ef;}
div[data-testid="stExpander"] {background:white; border-radius:10px;}
</style>""", unsafe_allow_html=True)

if "uploaded_cards" not in st.session_state:
    st.session_state.uploaded_cards = []
if "case" not in st.session_state:
    st.session_state.case = None

with st.sidebar:
    st.title("🔎 NeuroTrace")
    st.caption("研究证据工作台 · 原型 0.1")
    mode_label = st.radio("运行方式", ["演示模式 · 无需模型", "本地模型 · Ollama"])
    mode = "demo" if mode_label.startswith("演示") else "ollama"
    base_url = st.text_input("模型服务地址", os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"), disabled=mode == "demo")
    model = st.text_input("模型名称", os.environ.get("OLLAMA_MODEL", "qwen3:8b"), disabled=mode == "demo")
    st.caption("模型名是可修改的示例；以节点上实际已安装的模型为准。")
    st.divider()
    source = st.radio("资料来源", ["交接包样例", "我上传的 PDF"])
    if source == "我上传的 PDF":
        files = st.file_uploader("导入论文 PDF", type=["pdf"], accept_multiple_files=True)
        st.caption("每份最多 25 MB。PDF 保存到本机 data/pdfs；页面刷新后可重新导入。暂不支持扫描件 OCR。")
        if st.button("解析并加入本次资料库", disabled=not files):
            with st.spinner("正在逐页解析 PDF…"):
                for file in files or []:
                    try:
                        cards = parse_pdf(file.getvalue(), file.name)
                        existing = {c["card_id"] for c in st.session_state.uploaded_cards}
                        st.session_state.uploaded_cards.extend(c for c in cards if c["card_id"] not in existing)
                        st.success(f"{file.name}：解析得到 {len(cards)} 条片段")
                    except Exception as exc:
                        st.error(f"{file.name}：{exc}")
        if st.button("清空本次资料库"):
            st.session_state.uploaded_cards = []
            st.rerun()
        st.caption("清空仅移除本次索引，不删除已保存的 PDF。")
    corpus = load_samples() if source == "交接包样例" else st.session_state.uploaded_cards
    st.metric("可检索片段", len(corpus))
    st.caption("切换设置仅影响下一次调查；已有结果保留创建时的来源和模式。")

st.title("你想弄清楚什么？")
st.caption("从一个研究问题出发，查看依据、审阅证据、留下可追溯的调查档案。")
if mode == "demo":
    st.info("当前为流程演示：真实执行检索、审阅和导出，但不调用模型。展示的关系是样例，不是科研结论。")
elif source == "交接包样例":
    st.warning("当前将调用模型分析交接包样例。样例没有原始 PDF，输出仍标为演示档案。")

with st.form("question_form"):
    question = st.text_area("研究问题", value="情绪唤醒度是否会影响 LPC 振幅？", height=90, max_chars=2000)
    run = st.form_submit_button("开始调查", type="primary", disabled=not corpus)
if run:
    st.session_state.case = None
    try:
        with st.status("调查进行中", expanded=True) as status:
            case = investigate(question, corpus, mode, base_url, model, lambda e: st.write(e["message"]))
            st.session_state.case = case
            status.update(label="调查完成" if not case["error"] else "模型调用未完成", state="complete" if not case["error"] else "error", expanded=False)
    except Exception as exc:
        st.error(str(exc))

case = st.session_state.case
if case:
    if case["error"]:
        st.error(case["error"] + " 没有用演示结果替代模型输出。")
    finding = case["finding"]
    if finding["is_demo"]:
        st.warning("本次结果仅用于流程演示；确认样例卡也不会变成正式引用。")
    a, b, c = st.columns(3)
    a.metric("召回证据", len(case["cards"]))
    b.metric("保留证据", len(finding["active_card_ids"]))
    c.metric("本次耗时", f"{case['elapsed_seconds']:.2f} 秒")
    left, center, right = st.columns([1, 2.7, 1.2])
    with left:
        st.subheader("本次调查")
        st.write(case["question"])
        st.caption(f"编号：{case['case_id']}")
        st.caption(f"模式：{case['mode']}")
        st.caption(f"模型：{case['model']}")
        st.caption("审阅操作即时重算；重新调查会创建新档案。")
    with center:
        st.subheader("目前能得到的判断")
        st.markdown(f"**{VERDICTS[finding['verdict']]}**")
        st.write(finding["summary"])
        st.caption("这是原型中的保守聚合规则，尚未经过领域评测。")
        st.subheader("下一步可检验的问题")
        st.write(finding["hypothesis"])
        st.subheader("证据与审阅")
        if not case["cards"]:
            st.info("没有检索到相关片段。请修改问题或导入相关 PDF。")
        relations = {r["card_id"]: r for r in case["relations"]}
        for card in case["cards"]:
            cid = card["card_id"]
            relation = relations.get(cid, {})
            decision = case["reviews"].get(cid, {}).get("decision", "pending")
            tag = {"confirmed": "已确认", "rejected": "已驳回", "pending": "待审阅"}[decision]
            title = f"{ROLES.get(relation.get('role'), '未分析')} · {tag} · {card['title']}"
            with st.expander(title, expanded=False):
                st.caption(f"{cid} · PDF 第 {card['page']} 页 · {'交接包样例，无原始文件' if card['source_type'] == 'sample' else '上传的 PDF'}")
                st.text(card["quote"])
                st.write(relation.get("reason", "尚未完成模型分析。"))
                st.caption(relation.get("conditions", ""))
                if card["source_type"] == "pdf":
                    try:
                        st.download_button("下载原始 PDF 核对页码", pdf_bytes(card), file_name=card["title"], mime="application/pdf", key=f"pdf-{case['case_id']}-{cid}")
                    except (OSError, ValueError) as exc:
                        st.error(str(exc))
                x, y, z = st.columns(3)
                for column, label, value in [(x, "确认原文", "confirmed"), (y, "驳回证据", "rejected"), (z, "恢复待审", "pending")]:
                    if column.button(label, key=f"{case['case_id']}-{cid}-{value}"):
                        review(case, cid, value)
                        st.rerun()
        st.subheader("导出本次档案")
        data = exports(case)
        st.caption(f"档案状态：{case['finding']['status']}。待核验及演示结果会保留相应标记。")
        for column, extension, mime in zip(st.columns(3), ["md", "json", "csv"], ["text/markdown", "application/json", "text/csv"]):
            column.download_button(f"下载 {extension.upper()}", data[extension].encode("utf-8"), file_name=f"neurotrace-{case['case_id']}.{extension}", mime=mime)
    with right:
        st.subheader("调查记录")
        for event in case["events"]:
            st.caption(event["message"])
else:
    st.markdown("**先体验一条完整流程**")
    st.write("使用上方默认问题开始调查，再展开证据卡、确认或驳回，最后下载档案。无需先准备论文或模型。")

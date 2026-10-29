"""Streamlit web app:  streamlit run app.py"""
import html
from pathlib import Path

import streamlit as st

from contract_search.cli import DATA, UNANS, build_searcher
from contract_search.config import Config

st.set_page_config(page_title="Contract Clause Search", layout="wide")


@st.cache_resource(show_spinner="Building index…")
def get_searcher(config_path: str):
    cfg = Config.load(config_path)
    searcher, cfg, docs = build_searcher(cfg, DATA, UNANS)
    return searcher, cfg, sorted(docs)


configs = sorted(Path("configs").glob("*.yaml"), key=lambda p: (p.stem != "final", p.stem))
configs = [p.as_posix() for p in configs]  # forward slashes on Windows too
default = 0  # final.yaml first when it exists

with st.sidebar:
    st.header("Settings")
    config_path = st.selectbox("Pipeline config", configs, index=default)
    k = st.slider("Passages to return", 1, 20, 5)
    context = st.slider("Context characters around a hit", 0, 600, 200, step=50)

searcher, cfg, doc_ids = get_searcher(config_path)

st.title("Contract clause search")
st.caption(f"{len(doc_ids)} contracts indexed · config `{cfg.name}` · retriever `{cfg.retriever}` · "
           f"chunker `{cfg.chunker}`/{cfg.chunk_size} · abstention thresholds "
           f"doc={cfg.doc_threshold:.2f}, clause={cfg.clause_threshold:.2f}")

examples = ["Consider the <contract name>; Does this agreement allow sublicensing to a third party?"]
question = st.text_area("Question", placeholder=examples[0], height=80)
st.caption("Tip: start with “Consider the <contract description>;” to search a specific contract.")

if st.button("Search", type="primary") and question.strip():
    res = searcher.search(question.strip(), k)
    c1, c2 = st.columns(2)
    c1.metric("Contract match confidence", f"{res.doc_conf:.2f}" if res.named_contract else "n/a")
    c2.metric("Clause match confidence", f"{res.clause_conf:.2f}")
    if res.abstained:
        st.warning(f"**No answer returned.** {res.reason}")
        with st.expander("Show the closest passages anyway (below the relevance threshold)"):
            for p in res.passages[:3]:
                st.markdown(f"`{p.doc_id}` [{p.start}:{p.end}]")
                st.text(p.text[:800])
    else:
        for i, p in enumerate(res.passages, 1):
            doc = searcher.index.docs[p.doc_id]
            before = doc[max(0, p.start - context):p.start]
            after = doc[p.end:p.end + context]
            with st.container(border=True):
                st.markdown(f"**#{i}** · `{p.doc_id}` · chars **{p.start}–{p.end}** · score {p.score:.3f}")
                # st.html renders raw HTML without Markdown, so indented contract lines
                # are not turned into code blocks (which broke the highlighting)
                st.html(
                    f"<div style='white-space:pre-wrap;font-size:0.9em;font-family:sans-serif'>"
                    f"<span style='opacity:0.45'>…{html.escape(before)}</span>"
                    f"<mark>{html.escape(p.text)}</mark>"
                    f"<span style='opacity:0.45'>{html.escape(after)}…</span></div>")

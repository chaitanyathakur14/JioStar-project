"""Query-time search: routing, scoring, fusion, reranking, abstention."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .config import Config
from .index import Index
from .text import QUERY_BOILERPLATE, split_query, tokenize


@dataclass
class Passage:
    doc_id: str
    start: int
    end: int
    score: float
    text: str = ""


@dataclass
class SearchResult:
    query: str
    passages: list                      # ranked list[Passage] (always filled, even if abstaining)
    doc_conf: float = 1.0               # how well the named contract matches the corpus
    clause_conf: float = 1.0            # how well the top passage covers the question
    named_contract: bool = False
    abstained: bool = False
    reason: str = ""
    routed_docs: list = field(default_factory=list)


def idf_coverage(query_toks: list[str], target_toks: set, idf_fn) -> float:
    """Share of the query's IDF mass that appears in the target text (0..1).
    Rare words (party names, specific legal terms) dominate the score."""
    q = set(query_toks)
    if not q:
        return 0.0
    total = sum(idf_fn(t) for t in q)
    hit = sum(idf_fn(t) for t in q if t in target_toks)
    return hit / total if total else 0.0


def _rrf(rankings: list[np.ndarray], n: int, k: int) -> np.ndarray:
    fused = np.zeros(n, dtype=np.float32)
    for order in rankings:
        ranks = np.empty(n, dtype=np.float32)
        ranks[order] = np.arange(len(order))
        fused += 1.0 / (k + ranks + 1)
    return fused


class Searcher:
    def __init__(self, index: Index, cfg: Config | None = None):
        # cfg may differ from index.cfg in query-time fields (routing, thresholds, rerank)
        self.index = index
        self.cfg: Config = cfg or index.cfg
        self._reranker = None

    # ---- scoring ------------------------------------------------------------
    def _chunk_scores(self, text: str, toks: list[str]) -> np.ndarray:
        ix, cfg = self.index, self.cfg
        if cfg.retriever == "bm25":
            return ix.bm25.score(toks)
        if cfg.retriever == "tfidf":
            qv = ix.tfidf.transform([toks])
            return np.asarray((ix.tfidf_matrix @ qv.T).todense()).ravel()
        qe = ix.encoder.encode([text])[0]
        dense = ix.chunk_emb @ qe
        if cfg.retriever == "dense":
            return dense
        bm = ix.bm25.score(toks)
        return _rrf([np.argsort(-bm), np.argsort(-dense)], len(bm), cfg.rrf_k)

    def _rerank(self, question: str, cand: list[int], scores: np.ndarray) -> list[int]:
        if self._reranker is None:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(self.cfg.rerank_model)
        pairs = [(question, self.index.chunk_text(i)) for i in cand]
        rs = self._reranker.predict(pairs)
        order = np.argsort(-np.asarray(rs))
        for j, i in enumerate(order):
            scores[cand[i]] = float(rs[i])
        return [cand[i] for i in order]

    # ---- main entry -----------------------------------------------------------
    def search(self, query: str, k: int = 8) -> SearchResult:
        ix, cfg = self.index, self.cfg
        descriptor, question = split_query(query)
        res = SearchResult(query, [], named_contract=bool(descriptor))

        mask = np.ones(len(ix.chunks), dtype=bool)
        if descriptor:
            dtoks = tokenize(descriptor, cfg.stem, drop=QUERY_BOILERPLATE)
            dscores = ix.doc_bm25.score(dtoks)
            best = int(np.argmax(dscores)) if len(dscores) else 0
            res.doc_conf = idf_coverage(dtoks, ix.doc_tokens[best], ix.doc_bm25.term_idf)
            if cfg.doc_routing:
                top = np.argsort(-dscores)[: cfg.doc_top_n]
                res.routed_docs = [ix.doc_ids[i] for i in top]
                mask = np.isin(ix.chunk_doc, top)

        text = question if (cfg.query_mode == "question_only" and descriptor) else query
        toks = tokenize(text, cfg.stem, drop=QUERY_BOILERPLATE)
        scores = self._chunk_scores(text, toks).astype(np.float32)
        scores[~mask] = -np.inf

        n_cand = max(k, cfg.rerank_top if cfg.rerank else k)
        order = [int(i) for i in np.argsort(-scores)[:n_cand] if np.isfinite(scores[i])]
        if cfg.rerank and order:
            order = self._rerank(question, order, scores)
        order = order[:k]

        # abstention signal from the question terms only (descriptor already checked)
        qtoks = tokenize(question, cfg.stem, drop=QUERY_BOILERPLATE)
        # best coverage among the top 5 (top-1 is often a preamble matching party names)
        res.clause_conf = max((idf_coverage(qtoks, set(ix.chunk_tokens[i]), ix.bm25.term_idf)
                               for i in order[:5]), default=0.0)

        res.passages = [self._passage(i, float(scores[i])) for i in order]
        if cfg.retriever in ("bm25", "tfidf") and order and scores[order[0]] <= 0:
            res.clause_conf = 0.0  # not a single query term matched anywhere
        self.apply_abstention(res, cfg.doc_threshold, cfg.clause_threshold)
        return res

    def _passage(self, i: int, score: float) -> Passage:
        ix, n = self.index, self.cfg.neighbor_expand
        c = ix.chunks[i]
        start, end = c.start, c.end
        if n:
            lo, hi = max(0, i - n), min(len(ix.chunks) - 1, i + n)
            same = [j for j in range(lo, hi + 1) if ix.chunks[j].doc_id == c.doc_id]
            start = min(ix.chunks[j].start for j in same)
            end = max(ix.chunks[j].end for j in same)
        return Passage(c.doc_id, start, end, score, ix.docs[c.doc_id][start:end])

    @staticmethod
    def apply_abstention(res: SearchResult, doc_t: float, clause_t: float) -> SearchResult:
        res.abstained, res.reason = False, ""
        if res.named_contract and res.doc_conf < doc_t:
            res.abstained, res.reason = True, "The named contract does not appear to be in the corpus."
        elif res.clause_conf <= 0 or res.clause_conf < clause_t or not res.passages:
            res.abstained, res.reason = True, "No passage is relevant enough to answer this question."
        return res

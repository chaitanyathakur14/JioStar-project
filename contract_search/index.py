"""Indexes over chunks and over whole contracts.

BM25 is implemented directly (sparse matrix of precomputed term weights) so
every part of the scoring is visible and explainable."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from .chunking import Chunk, chunk_document
from .config import Config
from .text import title_from_path, tokenize

CACHE_DIR = Path("cache")


def _identity(x):
    return x


class BM25:
    def __init__(self, token_lists: list[list[str]], k1: float = 1.2, b: float = 0.75):
        self.vec = CountVectorizer(analyzer=_identity)
        tf = self.vec.fit_transform(token_lists).tocsr().astype(np.float32)
        self.vocab = self.vec.vocabulary_
        n = tf.shape[0]
        df = np.asarray((tf > 0).sum(axis=0)).ravel()
        self.idf = np.log(1 + (n - df + 0.5) / (df + 0.5)).astype(np.float32)
        self.max_idf = float(math.log(1 + (n + 0.5) / 0.5))  # idf of an unseen term
        dl = np.asarray(tf.sum(axis=1)).ravel()
        avgdl = dl.mean() if n else 1.0
        tf = tf.tocoo()
        denom = tf.data + k1 * (1 - b + b * dl[tf.row] / avgdl)
        w = self.idf[tf.col] * tf.data * (k1 + 1) / denom
        self.W = sparse.csc_matrix((w, (tf.row, tf.col)), shape=tf.shape)
        self.n = n

    def term_idf(self, tok: str) -> float:
        j = self.vocab.get(tok)
        return float(self.idf[j]) if j is not None else self.max_idf

    def score(self, tokens: list[str]) -> np.ndarray:
        cols = [self.vocab[t] for t in tokens if t in self.vocab]
        if not cols:
            return np.zeros(self.n, dtype=np.float32)
        return np.asarray(self.W[:, cols].sum(axis=1)).ravel()


class DenseEncoder:
    """Optional sentence-transformers encoder with on-disk embedding cache."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # optional dependency
        self.model = SentenceTransformer(model_name)
        self.name = model_name

    def encode(self, texts: list[str], cache_key: str | None = None) -> np.ndarray:
        path = None
        if cache_key:
            CACHE_DIR.mkdir(exist_ok=True)
            h = hashlib.sha1((self.name + cache_key).encode()).hexdigest()[:16]
            path = CACHE_DIR / f"emb_{h}.npy"
            if path.exists():
                return np.load(path)
        emb = self.model.encode(texts, batch_size=64, normalize_embeddings=True,
                                show_progress_bar=len(texts) > 500)
        emb = np.asarray(emb, dtype=np.float32)
        if path:
            np.save(path, emb)
        return emb


def dense_available() -> bool:
    try:
        import sentence_transformers  # noqa: F401
        return True
    except Exception:
        return False


class Index:
    def __init__(self, cfg: Config, docs: dict[str, str]):
        self.cfg = cfg
        self.docs = docs
        self.doc_ids = sorted(docs)
        self.titles = {d: title_from_path(d) for d in self.doc_ids}

        # ---- chunks ----
        self.chunks: list[Chunk] = []
        for d in self.doc_ids:
            self.chunks.extend(chunk_document(d, docs[d], cfg.chunker, cfg.chunk_size, cfg.chunk_overlap))
        pos = {d: i for i, d in enumerate(self.doc_ids)}
        self.chunk_doc = np.array([pos[c.doc_id] for c in self.chunks], dtype=np.int64)
        texts = [self.index_text(c) for c in self.chunks]
        self.chunk_tokens = [tokenize(t, cfg.stem) for t in texts]
        self.bm25 = BM25(self.chunk_tokens, cfg.bm25_k1, cfg.bm25_b)

        # ---- whole-contract index for routing: file-name title + opening text ----
        doc_texts = [self.titles[d] + "\n" + docs[d][:3000] for d in self.doc_ids]
        self.doc_tokens = [set(tokenize(t, cfg.stem)) for t in doc_texts]
        self.doc_bm25 = BM25([tokenize(t, cfg.stem) for t in doc_texts], cfg.bm25_k1, cfg.bm25_b)

        self.tfidf = self.tfidf_matrix = None
        if cfg.retriever == "tfidf":
            self.tfidf = TfidfVectorizer(analyzer=_identity, sublinear_tf=True)
            self.tfidf_matrix = self.tfidf.fit_transform(self.chunk_tokens)

        self.encoder = self.chunk_emb = None
        if cfg.retriever in ("dense", "hybrid"):
            self.encoder = DenseEncoder(cfg.dense_model)
            key = cfg.index_key() + str(len(self.chunks)) + str(sum(c.end for c in self.chunks))
            self.chunk_emb = self.encoder.encode(texts, cache_key=key)

    def index_text(self, c: Chunk) -> str:
        body = self.docs[c.doc_id][c.start:c.end]
        return f"{self.titles[c.doc_id]}\n{body}" if self.cfg.title_prefix else body

    def chunk_text(self, i: int) -> str:
        c = self.chunks[i]
        return self.docs[c.doc_id][c.start:c.end]

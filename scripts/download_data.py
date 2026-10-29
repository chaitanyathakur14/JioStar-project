"""Download only what we need from the LegalBench-RAG mirror on Hugging Face:
benchmarks/cuad.json and corpus/cuad/."""
import sys

from huggingface_hub import snapshot_download

target = sys.argv[1] if len(sys.argv) > 1 else "data/legalbench-rag"
snapshot_download(repo_id="awinml/legalbench-rag", repo_type="dataset", local_dir=target,
                  allow_patterns=["benchmarks/cuad.json", "corpus/cuad/*"])
print("downloaded to", target)

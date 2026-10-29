"""A tiny synthetic dataset in the exact LegalBench-RAG layout, so the whole
pipeline (load -> index -> search -> evaluate -> loop) can be tested offline."""
import json

import pytest

PARTIES = [("Acme Media Inc", "Blue River Studios LLC", "License Agreement"),
           ("Northstar Broadcasting Corp", "Lotus Films Ltd", "Distribution Agreement"),
           ("Helix Software Inc", "Orbit Retail Group", "Reseller Agreement"),
           ("Pioneer Foods Co", "Granite Logistics LLC", "Supply Agreement"),
           ("Vega Pharma Ltd", "Cedar Research Labs", "Collaboration Agreement"),
           ("Summit Energy Inc", "Delta Grid Services", "Services Agreement")]

CLAUSES = {
    "sublicense": "Licensee may not sublicense any of the rights granted hereunder to any third party without the prior written consent of Licensor.",
    "exclusivity": "During the Exclusivity Period, which shall end on the third anniversary of the Effective Date, Licensor shall not grant similar rights to any other person in the Territory.",
    "ip": "All intellectual property rights in any derivative works created by Licensee shall be owned exclusively by Licensor.",
    "law": "This Agreement shall be governed by and construed in accordance with the laws of the State of New York.",
    "termination": "Either party may terminate this Agreement for convenience upon ninety (90) days prior written notice to the other party.",
    "liability": "In no event shall either party's aggregate liability exceed the total fees paid in the twelve months preceding the claim.",
}
FILLER = ("The parties acknowledge the recitals above and agree that the provisions of this section are "
          "administrative in nature and relate to notices, counterparts and headings. ")

QUESTIONS = {
    "sublicense": "Does this agreement allow the licensee to sublicense rights to a third party?",
    "exclusivity": "When does the exclusivity period end?",
    "ip": "Who owns intellectual property in derivative works?",
    "law": "Which state law governs this agreement?",
    "termination": "Can a party terminate for convenience and with what notice?",
    "liability": "Is there a cap on aggregate liability?",
}


def make_contract(i, a, b, kind):
    parts = [f"{kind.upper()}\n\nThis {kind} is entered into by {a} and {b}.\n\n"]
    for n, (key, clause) in enumerate(sorted(CLAUSES.items(), key=lambda kv: (len(kv[0]) * 3 + i) % 7), 1):
        parts.append(f"{n}. {key.title()}\n\n{FILLER * (1 + (n + i) % 3)}{clause} {FILLER}\n\n")
    return "".join(parts)


@pytest.fixture(scope="session")
def dataset(tmp_path_factory):
    root = tmp_path_factory.mktemp("lbr")
    (root / "corpus" / "cuad").mkdir(parents=True)
    (root / "benchmarks").mkdir()
    tests = []
    for i, (a, b, kind) in enumerate(PARTIES):
        fname = f"cuad/{a.replace(' ', '')}_{kind.replace(' ', '')}.txt"
        text = make_contract(i, a, b, kind)
        (root / "corpus" / fname).write_text(text, encoding="utf-8")
        for key, q in QUESTIONS.items():
            s = text.index(CLAUSES[key])
            tests.append({"query": f"Consider the {kind} between {a} and {b}; {q}",
                          "snippets": [{"file_path": fname, "span": [s, s + len(CLAUSES[key])],
                                        "answer": CLAUSES[key]}]})
    (root / "benchmarks" / "cuad.json").write_text(json.dumps({"tests": tests}), encoding="utf-8")
    unans = [{"type": "contract_not_in_corpus",
              "query": f"Consider the Format License between Zyxquor Pictures {n} and Plimbeth Media {n}; "
                       f"What is the license fee?"} for n in range(12)]
    unans += [{"type": "topic_absent", "query": q} for q in [
        "What frame rate must the delivery masters use?", "Which subtitle languages must be delivered?",
        "What audio loudness in LUFS is required?", "How many ad breaks per hour are allowed?",
        "Which censor certificate is required before release?", "Who approves casting of lead roles?",
        "What blackout rules apply to live cricket?", "How long is the catch-up window after telecast?",
        "What dubbing languages are licensed?", "Who pays music cue sheet royalties?",
        "What is the SVOD holdback window?", "Can clips be cut into vertical videos?"]]
    up = root / "unanswerable.json"
    up.write_text(json.dumps(unans), encoding="utf-8")
    return root, up

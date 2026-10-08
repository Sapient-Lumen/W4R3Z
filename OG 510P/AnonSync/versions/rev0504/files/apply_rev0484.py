from pathlib import Path

root = Path(__file__).resolve().parent
docs = root / "docs"

# This helper rewrites the rev0484 tranche if needed.
updates = {
    "2044-resilio-remedy-hardening-attestation-successor-execution-completion-partial-commit-and-terminal-disposition-fragmentation-evaluation.md": "# Resilio remedy-hardening attestation successor execution completion, partial commit, and terminal disposition fragmentation evaluation

This file is managed by apply_rev0484.py in the packaged archive.
",
}

for name, content in updates.items():
    (docs / name).write_text(content)

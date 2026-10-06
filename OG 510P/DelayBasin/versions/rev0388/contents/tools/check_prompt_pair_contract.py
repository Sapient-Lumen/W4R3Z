import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
text = (ROOT / "docs/50-promptcraft/prompt-pairs.md").read_text(encoding="utf-8")
required = [
    "research online",
    "do not keep PDFs or other large non-crucial artifacts long-term",
    "Run `make lint`",
]
missing = [item for item in required if item not in text]
if missing:
    print("prompt-pair contract missing required phrases:")
    for item in missing:
        print(f"  - {item}")
    sys.exit(1)
print("check_prompt_pair_contract: OK")

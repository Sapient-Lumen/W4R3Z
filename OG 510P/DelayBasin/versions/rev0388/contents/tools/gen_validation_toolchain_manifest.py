import hashlib
import json
import pathlib
import re

from validation_toolchain_lib import build_validation_toolchain

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "VALIDATION-TOOLCHAIN-MANIFEST.json"
OUT_MD = ROOT / "docs/00-meta/validation-toolchain.md"
CHANGELOG = ROOT / "CHANGELOG.md"


def current_revision() -> str:
    text = CHANGELOG.read_text(encoding="utf-8")
    m = re.search(r"(rev\d{4})", text)
    if not m:
        raise SystemExit("CHANGELOG.md missing current revision header")
    return m.group(1)


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(rel: str, *, order: int | None = None, role: str | None = None) -> dict:
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"missing validation-toolchain file: {rel}")
    row = {
        "path": rel,
        "size": path.stat().st_size,
        "sha256": sha256_path(path),
    }
    if order is not None:
        row = {"order": order, **row}
    if role is not None:
        row["role"] = role
    return row


def tool_role(name: str) -> str:
    if name.startswith("gen_"):
        return "generator"
    if name.startswith("check_"):
        return "checker"
    return "validation-tool"


def support_modules() -> list[str]:
    names = {path.name for path in (ROOT / "tools").glob("*_lib.py")}
    names.update({"packet_contract_common.py", "shadow_contract_common.py"})
    return sorted(name for name in names if (ROOT / "tools" / name).exists())


def build_payload() -> dict:
    tools = build_validation_toolchain(ROOT)
    ordered = []
    for index, name in enumerate(tools, start=1):
        row = file_record(f"tools/{name}", order=index, role=tool_role(name))
        ordered.append(row)
    support = [file_record(f"tools/{name}", role="support-module") for name in support_modules()]
    entrypoints = [
        file_record("tools/run_lint_suite.py", role="admission-entrypoint"),
        file_record("tools/package_release.py", role="release-entrypoint"),
        file_record("Makefile", role="command-surface"),
        file_record("VALIDATION-INDEX.json", role="coverage-index"),
    ]
    return {
        "project": "DelayBasin",
        "revision": current_revision(),
        "surface": "VALIDATION-TOOLCHAIN-MANIFEST.json",
        "guide_surface": "docs/00-meta/validation-toolchain.md",
        "state": "generated-toolchain-fingerprint",
        "non_claim": "This is not a lint-sovereign, validation-score-sovereign, hash-governance-court, toolchain-certification-tribunal, or manifest-notary-authority; it records toolchain identity and hashes for audit only.",
        "generated_from": [
            "tools/validation_toolchain_lib.py",
            "tools/run_lint_suite.py",
            "Makefile",
            "VALIDATION-INDEX.json",
        ],
        "ordering_rule": "ordered_lint_tools is exactly validation_toolchain_lib.build_validation_toolchain(ROOT) at generation time",
        "hash_algorithm": "sha256",
        "ordered_lint_tools": ordered,
        "support_modules": support,
        "entrypoints": entrypoints,
        "counts": {
            "ordered_lint_tools": len(ordered),
            "support_modules": len(support),
            "entrypoints": len(entrypoints),
        },
        "repair": "ordinary-continuation",
    }


def render_md(payload: dict) -> str:
    lines = []
    lines.append("# Validation toolchain manifest")
    lines.append("")
    lines.append("This generated guide makes the `make lint` admission wrapper inspectable without turning it into a certification authority.")
    lines.append("It pairs with `VALIDATION-TOOLCHAIN-MANIFEST.json`, which records ordered tool scripts, support modules, entrypoints, sizes, and SHA-256 hashes.")
    lines.append("")
    lines.append("## Non-claim")
    lines.append(payload["non_claim"])
    lines.append("")
    lines.append("## Counts")
    counts = payload["counts"]
    lines.append(f"- Ordered lint tools: {counts['ordered_lint_tools']}")
    lines.append(f"- Support modules: {counts['support_modules']}")
    lines.append(f"- Entrypoints: {counts['entrypoints']}")
    lines.append("")
    lines.append("## Entrypoints")
    for row in payload["entrypoints"]:
        lines.append(f"- `{row['path']}` — {row['role']} — `{row['sha256'][:16]}…`")
    lines.append("")
    lines.append("## First and last ordered lint tools")
    if payload["ordered_lint_tools"]:
        first = payload["ordered_lint_tools"][0]
        last = payload["ordered_lint_tools"][-1]
        lines.append(f"- First: `{first['path']}`")
        lines.append(f"- Last: `{last['path']}`")
    lines.append("")
    lines.append("## Use")
    lines.append("Use this manifest to detect admission-wrapper drift, support-module edits, and generator/checker identity changes. Do not use it as a review court or proof that the archive is semantically correct.")
    return "\n".join(lines).rstrip() + "\n"


payload = build_payload()
OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
OUT_MD.write_text(render_md(payload), encoding="utf-8")
print(f"wrote {OUT_JSON}")
print(f"wrote {OUT_MD}")

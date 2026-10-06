import hashlib
import json
import pathlib

from validation_toolchain_lib import build_validation_toolchain

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "VALIDATION-TOOLCHAIN-MANIFEST.json"
GUIDE = ROOT / "docs/00-meta/validation-toolchain.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def support_modules() -> list[str]:
    names = {path.name for path in (ROOT / "tools").glob("*_lib.py")}
    names.update({"packet_contract_common.py", "shadow_contract_common.py"})
    return sorted(name for name in names if (ROOT / "tools" / name).exists())


def assert_record(row: dict, rel: str) -> None:
    path = ROOT / rel
    if row.get("path") != rel:
        raise SystemExit(f"toolchain manifest path mismatch: {row.get('path')} != {rel}")
    if not path.exists():
        raise SystemExit(f"toolchain manifest referenced missing path: {rel}")
    if row.get("size") != path.stat().st_size:
        raise SystemExit(f"toolchain manifest size drift: {rel}")
    if row.get("sha256") != sha256_path(path):
        raise SystemExit(f"toolchain manifest sha256 drift: {rel}")


receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
guide = GUIDE.read_text(encoding="utf-8")
if manifest.get("project") != "DelayBasin" or manifest.get("revision") != receipt.get("revision"):
    raise SystemExit("VALIDATION-TOOLCHAIN-MANIFEST project/revision drifted")
if manifest.get("surface") != "VALIDATION-TOOLCHAIN-MANIFEST.json" or manifest.get("guide_surface") != "docs/00-meta/validation-toolchain.md":
    raise SystemExit("VALIDATION-TOOLCHAIN-MANIFEST self/guide surface drifted")
if manifest.get("state") != "generated-toolchain-fingerprint":
    raise SystemExit("VALIDATION-TOOLCHAIN-MANIFEST state drifted")
non_claim = manifest.get("non_claim", "")
for bad in ["lint-sovereign", "validation-score-sovereign", "hash-governance-court", "toolchain-certification-tribunal", "manifest-notary-authority"]:
    if bad not in non_claim or bad not in guide:
        raise SystemExit(f"validation toolchain manifest missing non-claim {bad}")

tools = build_validation_toolchain(ROOT)
rows = manifest.get("ordered_lint_tools")
if not isinstance(rows, list) or len(rows) != len(tools):
    raise SystemExit("VALIDATION-TOOLCHAIN-MANIFEST ordered_lint_tools count drifted")
for index, (row, name) in enumerate(zip(rows, tools), start=1):
    if row.get("order") != index:
        raise SystemExit(f"toolchain order drift for {name}")
    assert_record(row, f"tools/{name}")
    expected_role = "generator" if name.startswith("gen_") else "checker" if name.startswith("check_") else "validation-tool"
    if row.get("role") != expected_role:
        raise SystemExit(f"toolchain role drift for {name}")

support = manifest.get("support_modules")
expected_support = support_modules()
if not isinstance(support, list) or [row.get("path") for row in support] != [f"tools/{name}" for name in expected_support]:
    raise SystemExit("VALIDATION-TOOLCHAIN-MANIFEST support module list drifted")
for row in support:
    assert_record(row, row["path"])

entrypoints = manifest.get("entrypoints")
expected_entrypoints = ["tools/run_lint_suite.py", "tools/package_release.py", "Makefile", "VALIDATION-INDEX.json"]
if not isinstance(entrypoints, list) or [row.get("path") for row in entrypoints] != expected_entrypoints:
    raise SystemExit("VALIDATION-TOOLCHAIN-MANIFEST entrypoint list drifted")
for row in entrypoints:
    assert_record(row, row["path"])

counts = manifest.get("counts", {})
expected_counts = {"ordered_lint_tools": len(tools), "support_modules": len(expected_support), "entrypoints": len(expected_entrypoints)}
if counts != expected_counts:
    raise SystemExit(f"VALIDATION-TOOLCHAIN-MANIFEST counts drifted: {counts} != {expected_counts}")
for needle in ["Ordered lint tools", "Support modules", "Entrypoints", "Do not use it as a review court"]:
    if needle not in guide:
        raise SystemExit(f"validation toolchain guide missing {needle}")
print("check_validation_toolchain_manifest_contract: OK")

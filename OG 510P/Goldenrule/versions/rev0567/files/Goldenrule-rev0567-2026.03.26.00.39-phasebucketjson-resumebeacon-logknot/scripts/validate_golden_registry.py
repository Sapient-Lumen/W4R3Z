#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "goldens" / "registry.yaml"


def fail(msg: str) -> None:
    print(f"goldens: {msg}", file=sys.stderr)
    raise SystemExit(1)


def is_text(path: Path) -> bool:
    data = path.read_bytes()
    return b"\x00" not in data


def main() -> int:
    if not REGISTRY_PATH.exists():
        fail(f"missing registry: {REGISTRY_PATH}")

    try:
        entries = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"registry parse error: {exc}")

    if not isinstance(entries, list) or not entries:
        fail("registry must be a non-empty JSON list (YAML-compatible)")

    seen = set()
    required = {"id", "path", "owner", "regen_command", "meaning", "provenance"}

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"entry {idx} must be an object")

        missing = required - set(entry)
        if missing:
            fail(f"entry {idx} missing keys: {sorted(missing)}")

        gid = str(entry["id"])
        if gid in seen:
            fail(f"duplicate id: {gid}")
        seen.add(gid)

        rel = str(entry["path"])
        if rel.startswith("artifacts/"):
            fail(f"golden path cannot live under artifacts/: {rel}")

        fpath = ROOT / rel
        if not fpath.exists():
            fail(f"missing golden file for {gid}: {rel}")

        textual = bool(entry.get("textual", True))
        if textual and not is_text(fpath):
            fail(f"golden marked textual but appears binary: {rel}")

        if not textual and not entry.get("binary_justification"):
            fail(f"binary golden requires binary_justification: {gid}")

        prov = entry["provenance"]
        if not isinstance(prov, dict):
            fail(f"provenance must be object for {gid}")
        for key in ["generated_by", "generated_at", "code_version", "assumptions"]:
            if key not in prov:
                fail(f"provenance missing {key} for {gid}")

    print(f"goldens: ok ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

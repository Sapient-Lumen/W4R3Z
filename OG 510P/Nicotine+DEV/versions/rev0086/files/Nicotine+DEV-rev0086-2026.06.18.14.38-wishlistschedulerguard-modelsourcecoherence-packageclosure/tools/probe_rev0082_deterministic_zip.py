#!/usr/bin/env python3
"""Mutation-test the current deterministic ZIP builder and auditor."""
from __future__ import annotations

import argparse
import sys
import tempfile
import warnings
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_current_zip import audit_zip  # noqa: E402
from build_current_package import build_package  # noqa: E402
from cube_runtime import canonical_json, derive_revision, sha256_path, write_csv, write_json  # noqa: E402

REVISION = derive_revision(ROOT)


def malformed_zip(path: Path, names: list[str]) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(path, "w") as archive:
            for name in names:
                archive.writestr(name, b"x")


def run() -> dict:
    rows: list[dict[str, str]] = []

    def add(check_id: str, passed: bool, detail: str = "") -> None:
        rows.append({"check_id": check_id, "status": "pass" if passed else "fail", "detail": detail})

    with tempfile.TemporaryDirectory(prefix="rev0082-zip-contract-", dir="/mnt/data") as temp_name:
        temp = Path(temp_name)
        fixture = temp / "fixture"
        (fixture / "nested").mkdir(parents=True)
        (fixture / "data").mkdir()
        (fixture / "data/current_zip_contract.json").write_bytes((ROOT / "data/current_zip_contract.json").read_bytes())
        (fixture / "alpha.txt").write_text("alpha\n", encoding="utf-8")
        executable = fixture / "nested/run.py"
        executable.write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
        executable.chmod(0o755)
        (fixture / "nested/é.txt").write_text("NFC\n", encoding="utf-8")
        (fixture / "prefix").mkdir()
        (fixture / "prefix/member.txt").write_text("member\n", encoding="utf-8")
        (fixture / "prefix.side.txt").write_text("side\n", encoding="utf-8")

        first = temp / "fixture.zip"
        first_result = build_package(fixture, first)
        first_hash = sha256_path(first)
        saved = temp / "first.zip"
        saved.write_bytes(first.read_bytes())
        second_result = build_package(fixture, first)
        second_hash = sha256_path(first)
        add("two builds byte-identical", first_hash == second_hash, f"{first_hash} {second_hash}")
        add("second build equals saved first", saved.read_bytes() == first.read_bytes())
        good = audit_zip(first, root=fixture, contract_root=fixture)
        add("valid fixture accepted", good["status"] == "pass", str(good.get("errors", [])))
        serialized_good = canonical_json(good)
        add("auditor result JSON serializable", bool(serialized_good), str(type(serialized_good).__name__))
        with zipfile.ZipFile(first) as archive:
            root_name = fixture.name + "/"
            relative_names = [info.filename[len(root_name):] for info in archive.infolist()[1:]]
        add("prefix-sensitive POSIX member order", relative_names == sorted(relative_names), str(relative_names))
        add("builder reports same member count", first_result["members"] == second_result["members"] == 7)

        malformed = {
            "duplicate": ["duplicate/", "duplicate/a", "duplicate/a"],
            "casefold": ["casefold/", "casefold/A.txt", "casefold/a.txt"],
            "traversal": ["traversal/", "traversal/../escape"],
            "extra-directory": ["extra-directory/", "extra-directory/sub/", "extra-directory/sub/a"],
        }
        for name, members in malformed.items():
            path = temp / f"{name}.zip"
            malformed_zip(path, members)
            audit = audit_zip(path, contract_root=ROOT)
            add(f"mutation rejected: {name}", audit["status"] == "fail", "; ".join(audit.get("errors", [])[:3]))

    result = {
        "revision": REVISION,
        "status": "pass" if all(row["status"] == "pass" for row in rows) else "fail",
        "checks_passed": sum(row["status"] == "pass" for row in rows),
        "checks_total": len(rows),
        "deterministic_sha256": first_hash,
        "mutations_rejected": sum(row["check_id"].startswith("mutation rejected") and row["status"] == "pass" for row in rows),
        "rows": rows,
    }
    write_json(ROOT / f"data/{REVISION}_zip_contract_selftest.json", result)
    write_csv(ROOT / f"data/{REVISION}_zip_contract_checks.csv", rows,
              fields=("check_id", "status", "detail"))
    return result


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = run()
    except Exception as exc:
        result = {"revision": REVISION, "status": "fail", "errors": [f"{type(exc).__name__}: {exc}"]}
    print(canonical_json(result), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

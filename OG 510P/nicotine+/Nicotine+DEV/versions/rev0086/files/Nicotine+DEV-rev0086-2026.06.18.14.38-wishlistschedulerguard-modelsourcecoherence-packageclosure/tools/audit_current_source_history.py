#!/usr/bin/env python3
"""Validate data-driven source-history claims against the external Git bundle."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, derive_revision, run_bounded, safe_relative, sha256_bytes, write_csv, write_json  # noqa: E402
from source_bundle_locator import (  # noqa: E402
    GIT_ROOT_SUFFIX,
    LANE_HEADS,
    SOURCE_CONTRACT_PATH,
    inspect_bundle,
    locate_source_bundle,
)

CONTRACT = ROOT / "data/current_source_history_contract.json"
HEX40 = re.compile(r"[0-9a-f]{40}")


def _extract_git_root(source_zip: Path, destination: Path, suffix: str) -> int:
    with zipfile.ZipFile(source_zip) as archive:
        head_matches = [name for name in archive.namelist() if name.endswith(f"{suffix}.git/HEAD")]
        if len(head_matches) != 1:
            raise RuntimeError(f"expected one {suffix}.git/HEAD, found {len(head_matches)}")
        prefix = head_matches[0][:-len(".git/HEAD")]
        count = 0
        for info in archive.infolist():
            if not info.filename.startswith(prefix):
                continue
            relative_text = info.filename[len(prefix):]
            if not relative_text:
                continue
            relative = PurePosixPath(relative_text)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"unsafe Git entry: {info.filename}")
            target = destination.joinpath(*relative.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            count += 1
        return count


def _git(repo: Path, args: list[str], command_rows: list[dict[str, object]]) -> tuple[int, str]:
    command = ["git", "-c", "core.fileMode=false", *args]
    result = run_bounded(command, cwd=repo, timeout=60)
    output = result.stdout.rstrip("\n")
    command_rows.append({
        "index": len(command_rows),
        "command": " ".join(command),
        "returncode": result.returncode,
        "output_bytes": len(output.encode("utf-8")),
        "output_sha256": sha256_bytes(output.encode("utf-8")),
    })
    return result.returncode, output


def audit(root: Path, source_zip: Path) -> dict[str, Any]:
    revision = derive_revision(root)
    contract = json.loads((root / CONTRACT.relative_to(ROOT)).read_text(encoding="utf-8"))
    runtime = root / f"evidence/{revision}-source-history-runtime"
    if runtime.exists():
        shutil.rmtree(runtime)
    runtime.mkdir(parents=True)

    rows: list[dict[str, str]] = []
    command_rows: list[dict[str, object]] = []
    errors: list[str] = []

    def add(check_id: str, kind: str, passed: bool, detail: object = "") -> None:
        rows.append({
            "check": check_id,
            "kind": kind,
            "status": "pass" if passed else "fail",
            "detail": str(detail),
        })
        if not passed:
            errors.append(f"{check_id}: {detail}")

    inspection = inspect_bundle(source_zip)
    add("contract version", "contract", contract.get("version") == 3, contract.get("version"))
    source_contract_ref = contract.get("source_contract")
    add(
        "source contract reference",
        "contract",
        source_contract_ref == SOURCE_CONTRACT_PATH.as_posix(),
        source_contract_ref,
    )
    add(
        "source bundle digest",
        "bundle",
        inspection.status == "pass",
        inspection.sha256,
    )
    suffix = GIT_ROOT_SUFFIX
    add("Git root suffix", "source-contract", suffix == "git-full/", suffix)
    for stale_key in ("source_bundle_contract", "source_bundle_sha256", "executable_head", "git_root_suffix"):
        add(f"contract omits duplicate {stale_key}", "contract", stale_key not in contract, stale_key)
    checks = contract.get("checks")
    add("checks nonempty", "contract", isinstance(checks, list) and bool(checks), type(checks).__name__)

    with tempfile.TemporaryDirectory(prefix=f"{revision}-git-history-") as temp_name:
        repo = Path(temp_name) / "repo"
        extracted = _extract_git_root(source_zip, repo, str(suffix))
        add("Git files extracted", "bundle", extracted > 500, extracted)
        rc, head = _git(repo, ["rev-parse", "HEAD"], command_rows)
        add("executable Git head", "git", rc == 0 and head == LANE_HEADS["github-branch-master"], head)

        seen_ids: set[str] = set()
        for raw in checks if isinstance(checks, list) else []:
            if not isinstance(raw, dict):
                add("non-object check", "contract", False, type(raw).__name__)
                continue
            check_id = raw.get("id")
            kind = raw.get("kind")
            valid_id = isinstance(check_id, str) and bool(check_id) and check_id not in seen_ids
            add(f"contract row id: {check_id}", "contract-row", valid_id, check_id)
            if not valid_id:
                continue
            seen_ids.add(check_id)

            passed = False
            detail = ""
            if kind == "ancestor":
                ancestor = raw.get("ancestor")
                descendant = raw.get("descendant")
                valid = all(isinstance(value, str) and HEX40.fullmatch(value) for value in (ancestor, descendant))
                if valid:
                    rc, detail = _git(repo, ["merge-base", "--is-ancestor", ancestor, descendant], command_rows)
                    passed = rc == 0
                else:
                    detail = {"ancestor": ancestor, "descendant": descendant}

            elif kind in {"file_contains", "file_not_contains"}:
                commit = raw.get("commit")
                path = raw.get("path")
                needle = raw.get("text")
                valid = (
                    isinstance(commit, str)
                    and HEX40.fullmatch(commit.rstrip("^")) is not None
                    and commit.count("^") <= 1
                    and isinstance(path, str)
                    and safe_relative(path)
                    and isinstance(needle, str)
                    and bool(needle)
                )
                if valid:
                    rc, content = _git(repo, ["show", f"{commit}:{path}"], command_rows)
                    present = needle in content
                    passed = rc == 0 and (present if kind == "file_contains" else not present)
                    detail = f"present={present}; bytes={len(content.encode('utf-8'))}"
                else:
                    detail = {"commit": commit, "path": path, "text": needle}

            elif kind == "subject_equals":
                commit = raw.get("commit")
                expected = raw.get("text")
                valid = isinstance(commit, str) and HEX40.fullmatch(commit) is not None and isinstance(expected, str)
                if valid:
                    rc, subject = _git(repo, ["show", "-s", "--format=%s", commit], command_rows)
                    passed = rc == 0 and subject == expected
                    detail = subject
                else:
                    detail = {"commit": commit, "text": expected}

            else:
                detail = f"unsupported kind: {kind}"

            add(check_id, str(kind), passed, detail)

    write_csv(
        runtime / "commands.csv",
        command_rows,
        fields=("index", "command", "returncode", "output_bytes", "output_sha256"),
    )

    return {
        "revision": revision,
        "status": "pass" if not errors else "fail",
        "source_zip": source_zip.name,
        "source_sha256": inspection.sha256,
        "checks_passed": sum(row["status"] == "pass" for row in rows),
        "checks_total": len(rows),
        "history_claims": len(checks) if isinstance(checks, list) else 0,
        "rows": rows,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_source_history_summary.json", {key: value for key, value in result.items() if key != "rows"})
    write_csv(
        root / f"data/{revision}_source_history_checks.csv",
        result["rows"],
        fields=("check", "kind", "status", "detail"),
    )
    lines = [
        f"# {revision} source-history provenance audit",
        "",
        f"Status: **{result['status']}**",
        "",
        "```text",
        f"history claims: {result['history_claims']}",
        f"checks: {result['checks_passed']}/{result['checks_total']}",
        f"source SHA-256: {result['source_sha256']}",
        "```",
        "",
    ]
    if result["errors"]:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in result["errors"]])
    (root / f"evidence/{revision}-source-history-provenance.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-zip", default="auto")
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    selected, _inspections = locate_source_bundle(args.source_zip)
    result = audit(root, selected)
    if args.write_data:
        write_outputs(root, result)
    print(canonical_json({key: value for key, value in result.items() if key != "rows"}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

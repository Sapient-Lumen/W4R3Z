#!/usr/bin/env python3
"""Fast structural audit for an MTGSim datacube checkout.

This is intentionally lightweight and stdlib-only. It catches packaging and
refactor hazards that are easy to miss under cloud time limits: accidental
redistribution of official rules documents, broken revision metadata, duplicate
C++ test names, Python syntax regressions, unexpected cache/build payload, and
large files that should be reviewed before zipping.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "audit"
FORBIDDEN_RULE_SUFFIXES = {".pdf", ".docx", ".txt", ".rtf"}
CACHE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
LARGE_FILE_REVIEW_BYTES = 2_000_000


@dataclass
class AuditIssue:
    severity: str
    code: str
    detail: str


def rel(path: pathlib.Path, root: pathlib.Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def append_jsonl(path: pathlib.Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def compact_history_record(report: dict[str, Any], report_path: pathlib.Path, root: pathlib.Path) -> dict[str, Any]:
    """Keep audit history trend-readable without duplicating heavy inventories."""
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    cpp_tests = summary.get("cpp_tests", {}) if isinstance(summary.get("cpp_tests"), dict) else {}
    scenarios = summary.get("scenarios", {}) if isinstance(summary.get("scenarios"), dict) else {}
    revision_identity = summary.get("revision_identity", {}) if isinstance(summary.get("revision_identity"), dict) else {}

    return {
        "schema": "mtgsim.datacube_audit_history.compact.v2",
        "source_schema": report.get("schema"),
        "created_at_local": report.get("created_at_local"),
        "status": report.get("status"),
        "duration_sec": report.get("duration_sec"),
        "root": pathlib.Path(str(report.get("root", ""))).name if report.get("root") else None,
        "report": rel(report_path, root),
        "summary": {
            "errors": summary.get("errors"),
            "warnings": summary.get("warnings"),
            "issues": summary.get("issues"),
            "cpp_tests": {
                "available": cpp_tests.get("available"),
                "cases": cpp_tests.get("cases"),
                "duplicates": cpp_tests.get("duplicates"),
                "missing_rules": cpp_tests.get("missing_rules"),
                "missing_tags": cpp_tests.get("missing_tags"),
                "rule_refs": len(cpp_tests.get("rule_refs", [])) if isinstance(cpp_tests.get("rule_refs"), list) else cpp_tests.get("rule_refs"),
            },
            "scenarios": {
                "available": scenarios.get("available"),
                "files": scenarios.get("files"),
                "duplicate_names": scenarios.get("duplicate_names"),
                "missing_create": len(scenarios.get("missing_create", [])) if isinstance(scenarios.get("missing_create"), list) else scenarios.get("missing_create"),
                "missing_validate": len(scenarios.get("missing_validate", [])) if isinstance(scenarios.get("missing_validate"), list) else scenarios.get("missing_validate"),
            },
            "revision_identity": {
                "expected": revision_identity.get("expected"),
                "official_manifest_matches": revision_identity.get("official_manifest", {}).get("matches") if isinstance(revision_identity.get("official_manifest"), dict) else None,
                "rules_ledger_matches": revision_identity.get("rules_ledger", {}).get("matches") if isinstance(revision_identity.get("rules_ledger"), dict) else None,
                "readme_matches": revision_identity.get("README.md", {}).get("matches") if isinstance(revision_identity.get("README.md"), dict) else None,
                "changelog_matches": revision_identity.get("CHANGELOG.md", {}).get("matches") if isinstance(revision_identity.get("CHANGELOG.md"), dict) else None,
                "artifact_report_matches": revision_identity.get("ARTIFACT_REPORT.md", {}).get("matches") if isinstance(revision_identity.get("ARTIFACT_REPORT.md"), dict) else None,
            },
        },
    }


def add(issues: list[AuditIssue], severity: str, code: str, detail: str) -> None:
    issues.append(AuditIssue(severity, code, detail))


def audit_revision(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    path = root / "REVISION.json"
    if not path.exists():
        add(issues, "error", "revision.missing", "REVISION.json is missing")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add(issues, "error", "revision.invalid_json", str(exc))
        return {}
    revision = str(data.get("revision", ""))
    revision_match = re.fullmatch(r"rev(\d{4})", revision)
    if revision_match is None:
        add(issues, "error", "revision.id", "revision field should look exactly like rev####")
    else:
        revision_number = int(revision_match.group(1))
        if data.get("revision_number") != revision_number:
            add(
                issues,
                "error",
                "revision.number_mismatch",
                f"revision_number={data.get('revision_number')!r}; expected {revision_number}",
            )
        if data.get("revision_string") != revision:
            add(
                issues,
                "error",
                "revision.string_mismatch",
                f"revision_string={data.get('revision_string')!r}; expected {revision!r}",
            )
        project = str(data.get("project", "MTGSim"))
        expected_tag = f"{project}-{revision}"
        if data.get("revision_tag") != expected_tag:
            add(
                issues,
                "error",
                "revision.tag_mismatch",
                f"revision_tag={data.get('revision_tag')!r}; expected {expected_tag!r}",
            )
        if revision_number > 0:
            expected_previous = f"rev{revision_number - 1:04d}"
            if data.get("previous_revision") != expected_previous:
                add(
                    issues,
                    "error",
                    "revision.previous_mismatch",
                    f"previous_revision={data.get('previous_revision')!r}; expected {expected_previous!r}",
                )
        rules_progress_revision = str(data.get("rules_progress", {}).get("ledger_revision", ""))
        if rules_progress_revision != revision:
            add(
                issues,
                "error",
                "revision.rules_progress_mismatch",
                f"rules_progress.ledger_revision={rules_progress_revision!r}; expected {revision!r}",
            )

        slug = str(data.get("filename_slug", ""))
        created_at_local = str(data.get("created_at_local", ""))
        datacube_name = str(data.get("datacube_name", ""))
        if not re.fullmatch(r"[a-z0-9]+", slug):
            add(issues, "error", "revision.filename_slug", "filename_slug must be non-empty lowercase alphanumeric text")
        created_match = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", created_at_local)
        if created_match and slug:
            date_part = ".".join(created_match.groups())
            expected_datacube_name = f"{project}-{revision}-{date_part}-{slug}"
            expected_zip_filename = f"{expected_datacube_name}.zip"
            if datacube_name != expected_datacube_name:
                add(
                    issues,
                    "error",
                    "revision.datacube_name_mismatch",
                    f"datacube_name={datacube_name!r}; expected {expected_datacube_name!r}",
                )
            for field in ("datacube_filename", "zip_filename", "package_filename"):
                observed_filename = data.get(field)
                if observed_filename != expected_zip_filename:
                    add(
                        issues,
                        "error",
                        "revision.filename_mismatch",
                        f"{field}={observed_filename!r}; expected {expected_zip_filename!r}",
                    )
            for section_name in ("artifact", "package"):
                section = data.get(section_name)
                if not isinstance(section, dict):
                    add(issues, "error", "revision.artifact_section_missing", section_name)
                    continue
                expected_section_values = {
                    "name": expected_datacube_name,
                    "filename": expected_zip_filename,
                    "path": expected_zip_filename,
                    "filename_slug": slug,
                }
                for field, expected_value in expected_section_values.items():
                    observed_value = section.get(field)
                    if observed_value != expected_value:
                        add(
                            issues,
                            "error",
                            "revision.artifact_field_mismatch",
                            f"{section_name}.{field}={observed_value!r}; expected {expected_value!r}",
                        )
            revision_metadata_sections = {
                "artifact": data.get("artifact"),
                "package": data.get("package"),
                "release": data.get("release"),
                "release_checks": data.get("release_checks"),
                "validation": data.get("validation"),
                "rule_coverage": data.get("rule_coverage"),
                "rules_progress": data.get("rules_progress"),
                "datacube_audit": data.get("datacube_audit"),
                "zip_integrity": data.get("zip_integrity"),
            }
            for section_name, section in revision_metadata_sections.items():
                refs = sorted(set(re.findall(r"rev\d{4}", json.dumps(section, sort_keys=True, default=str))))
                stale_refs = [value for value in refs if value != revision]
                if stale_refs:
                    add(
                        issues,
                        "error",
                        "revision.metadata_stale_reference",
                        f"{section_name} contains stale revision reference(s): {', '.join(stale_refs)}",
                    )
    if not data.get("codename"):
        add(issues, "warning", "revision.codename", "codename is empty")
    if not data.get("created_at_local"):
        add(issues, "warning", "revision.created_at_local", "created_at_local is empty")
    root_name = root.name
    expected_revision = revision
    if expected_revision and expected_revision not in root_name:
        add(issues, "warning", "revision.root_name", f"root directory {root_name!r} does not contain revision {expected_revision!r}")
    return data


def audit_revision_identity(root: pathlib.Path, issues: list[AuditIssue], revision: dict[str, Any]) -> dict[str, Any]:
    """Keep externally visible revision metadata from drifting independently."""
    expected = str(revision.get("revision", ""))
    checks: dict[str, Any] = {"expected": expected}
    if not expected:
        return checks

    json_paths = {
        "official_manifest": root / "data" / "rules" / "official" / "manifest.json",
        "rules_ledger": root / "data" / "rules" / "coverage" / "rules_ledger.json",
    }
    for name, path in json_paths.items():
        if not path.exists():
            add(issues, "error", "revision.identity_file_missing", rel(path, root))
            checks[name] = {"available": False}
            continue
        try:
            observed = str(json.loads(path.read_text(encoding="utf-8")).get("revision", ""))
        except json.JSONDecodeError as exc:
            add(issues, "error", "revision.identity_invalid_json", f"{rel(path, root)}: {exc}")
            checks[name] = {"available": True, "valid_json": False}
            continue
        checks[name] = {"available": True, "observed": observed, "matches": observed == expected}
        if observed != expected:
            add(issues, "error", "revision.identity_mismatch", f"{rel(path, root)}={observed!r}; expected {expected!r}")

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        tool_section = re.search(r"(?ms)^\[tool\.mtgsim\]\s*(.*?)(?=^\[|\Z)", text)
        revision_match = re.search(r'(?m)^revision\s*=\s*["\']([^"\']+)["\']', tool_section.group(1) if tool_section else "")
        observed = revision_match.group(1) if revision_match else ""
        checks["pyproject"] = {"available": True, "observed": observed, "matches": observed == expected}
        if observed != expected:
            add(issues, "error", "revision.pyproject_mismatch", f"pyproject.toml tool.mtgsim revision={observed!r}; expected {expected!r}")
    else:
        add(issues, "error", "revision.identity_file_missing", "pyproject.toml")
        checks["pyproject"] = {"available": False}

    text_surfaces = {
        "README.md": root / "README.md",
        "ARTIFACT_REPORT.md": root / "ARTIFACT_REPORT.md",
        "CHANGELOG.md": root / "CHANGELOG.md",
    }
    for name, path in text_surfaces.items():
        if not path.exists():
            add(issues, "error", "revision.identity_file_missing", name)
            checks[name] = {"available": False}
            continue
        head = path.read_text(encoding="utf-8", errors="replace")[:1000]
        matches = expected in head
        checks[name] = {"available": True, "matches": matches}
        if not matches:
            add(issues, "error", "revision.identity_heading_mismatch", f"{name} does not identify {expected} near its beginning")

    cli = root / "apps" / "mtgsim_cli.cpp"
    if cli.exists():
        hardcoded = sorted(set(re.findall(r"rev\d{4}", cli.read_text(encoding="utf-8", errors="replace"))))
        stale = [value for value in hardcoded if value != expected]
        checks["cli_hardcoded_revisions"] = hardcoded
        for value in stale:
            add(issues, "error", "revision.cli_stale_banner", f"apps/mtgsim_cli.cpp contains stale hard-coded {value}")
    return checks


def audit_build_budget_guard(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check the hard build deadline and sanitizer hotspot guard end to end."""
    probes = {
        "tools/build.py": [
            "remaining_budget",
            "timeout_sec=timeout_sec",
            "start_new_session",
            "os.killpg",
            "sanitize_validation_opt_level",
            "sanitize_validation_debug_level",
            "--sanitize-validation-opt-level",
            "hard wall-clock deadline",
        ],
        "tools/audit_datacube.py": [
            "PYTHONDONTWRITEBYTECODE",
            'compile(source, str(path), "exec")',
        ],
        "tests/python/test_build_tool.py": [
            "check_sanitizer_validation_hotspot",
            "check_hard_subprocess_timeout",
            "build.BudgetExceeded",
        ],
        "docs/architecture/mission_truth_and_cloud_budget_rev0067.md": [
            "forensic evidence",
            "not yet replay",
            "hard subprocess deadline",
            "sanitizer",
        ],
    }
    results: dict[str, Any] = {"probes": {}}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "build_budget.probe_file_missing", relpath)
            results["probes"][relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        results["probes"][relpath] = {}
        for needle in needles:
            present = needle in text
            results["probes"][relpath][needle] = present
            if not present:
                add(issues, "error", "build_budget.wiring_missing", f"{relpath} missing {needle!r}")

    test_script = root / "tests" / "python" / "test_build_tool.py"
    if test_script.exists():
        try:
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            proc = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10.0,
                env=env,
            )
        except subprocess.TimeoutExpired:
            add(issues, "error", "build_budget.self_test_timeout", "tests/python/test_build_tool.py exceeded 10 seconds")
            results["self_test"] = {"status": "timeout"}
        else:
            results["self_test"] = {
                "status": "passed" if proc.returncode == 0 else "failed",
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-1000:],
                "stderr_tail": proc.stderr[-1000:],
            }
            if proc.returncode != 0:
                add(issues, "error", "build_budget.self_test_failed", (proc.stderr or proc.stdout)[-2000:])
    return results


def audit_official_rules_policy(root: pathlib.Path, issues: list[AuditIssue]) -> None:
    official = root / "data" / "rules" / "official"
    if not official.exists():
        add(issues, "error", "rules.official_dir_missing", rel(official, root))
        return
    for path in official.rglob("*"):
        if path.is_file() and path.suffix.lower() in FORBIDDEN_RULE_SUFFIXES:
            add(issues, "error", "rules.official_text_bundled", f"{rel(path, root)} should remain local/private, not in shared datacube")


def audit_filesystem_payload(root: pathlib.Path, issues: list[AuditIssue]) -> None:
    for path in root.rglob("*"):
        if any(part in CACHE_DIR_NAMES for part in path.parts):
            add(issues, "warning", "payload.cache_dir", rel(path, root))
            continue
        if path.is_file() and path.stat().st_size > LARGE_FILE_REVIEW_BYTES:
            add(issues, "warning", "payload.large_file", f"{rel(path, root)} size={path.stat().st_size}")
    if (root / "build").exists():
        add(issues, "warning", "payload.build_dir_present", "build/ exists in working tree; packaging should exclude it")


def audit_python_syntax(root: pathlib.Path, issues: list[AuditIssue]) -> None:
    # Compile in memory so an audit never dirties the tree it is inspecting.
    for path in sorted((root / "tools").glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
        except (OSError, UnicodeError, SyntaxError) as exc:
            add(issues, "error", "python.syntax", f"{rel(path, root)}: {exc}")


def audit_cpp_test_binary(root: pathlib.Path, issues: list[AuditIssue], exe: pathlib.Path | None) -> dict[str, Any]:
    explicit_exe = exe is not None
    if exe is None:
        exe = root / "build" / "gcc-release" / "mtgsim_tests"
    if not exe.exists():
        # Clean linked datacubes intentionally exclude build outputs. Treat the
        # default missing build binary as neutral source-package state, while
        # still warning when a caller explicitly asked to audit a test executable.
        if explicit_exe:
            add(issues, "warning", "cpp_tests.executable_missing", rel(exe, root))
        return {"available": False, "expected_path": rel(exe, root), "default_build_output_excluded": not explicit_exe}
    proc = subprocess.run([str(exe), "--list-json"], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        add(issues, "error", "cpp_tests.discovery_failed", (proc.stderr or proc.stdout)[-2000:])
        return {"available": True, "discovery_returncode": proc.returncode}
    try:
        cases = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        add(issues, "error", "cpp_tests.discovery_json", str(exc))
        return {"available": True, "discovery_returncode": proc.returncode}
    seen: set[str] = set()
    duplicates: list[str] = []
    missing_rules: list[str] = []
    missing_tags: list[str] = []
    for case in cases:
        name = str(case.get("name", ""))
        if name in seen:
            duplicates.append(name)
        seen.add(name)
        if not case.get("rules"):
            missing_rules.append(name)
        if not case.get("tags"):
            missing_tags.append(name)
    for name in duplicates:
        add(issues, "error", "cpp_tests.duplicate_name", name)
    for name in missing_rules:
        add(issues, "warning", "cpp_tests.missing_rules", name)
    for name in missing_tags:
        add(issues, "warning", "cpp_tests.missing_tags", name)
    rule_refs = sorted({str(rule) for case in cases for rule in case.get("rules", [])})
    case_names = sorted(str(case.get("name", "")) for case in cases)
    return {
        "available": True,
        "cases": len(cases),
        "duplicates": len(duplicates),
        "missing_rules": len(missing_rules),
        "missing_tags": len(missing_tags),
        "rule_refs": rule_refs,
        "case_names": case_names,
    }


def audit_rule_ledger_alignment(root: pathlib.Path, issues: list[AuditIssue], revision: dict[str, Any], cpp_tests: dict[str, Any]) -> dict[str, Any]:
    ledger_path = root / "data" / "rules" / "coverage" / "rules_ledger.json"
    if not ledger_path.exists():
        add(issues, "error", "rules.ledger_missing", rel(ledger_path, root))
        return {"available": False}
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add(issues, "error", "rules.ledger_invalid_json", str(exc))
        return {"available": True, "valid_json": False}

    revision_id = str(revision.get("revision", ""))
    ledger_revision = str(ledger.get("revision", ""))
    if revision_id and ledger_revision and revision_id != ledger_revision:
        add(issues, "error", "rules.ledger_revision_mismatch", f"REVISION.json={revision_id} ledger={ledger_revision}")

    rules = ledger.get("rules", [])
    ledger_rule_ids = {str(row.get("rule_id", "")) for row in rules}
    cpp_rule_refs = set(cpp_tests.get("rule_refs", [])) if cpp_tests.get("available") else set()
    missing_rule_rows = sorted(rule for rule in cpp_rule_refs if rule and rule not in ledger_rule_ids)
    for rule in missing_rule_rows:
        add(issues, "error", "rules.cpp_ref_missing_ledger_row", rule)

    ledger_test_case_names = set()
    duplicate_test_refs: list[str] = []
    seen_test_refs: set[str] = set()
    for row in rules:
        for ref in row.get("tests", []):
            ref = str(ref)
            if ref in seen_test_refs:
                duplicate_test_refs.append(ref)
            seen_test_refs.add(ref)
            if "::" in ref:
                ledger_test_case_names.add(ref.rsplit("::", 1)[-1])
    # Duplicate test refs are usually acceptable when a case covers multiple rows,
    # so this is informational in the report rather than an issue.
    cpp_case_names = set(cpp_tests.get("case_names", [])) if cpp_tests.get("available") else set()
    cases_missing_from_ledger = sorted(cpp_case_names - ledger_test_case_names)
    for name in cases_missing_from_ledger:
        add(issues, "warning", "rules.cpp_case_unlinked_from_ledger", name)

    return {
        "available": True,
        "valid_json": True,
        "ledger_revision": ledger_revision,
        "rules": len(rules),
        "cpp_rule_refs": sorted(cpp_rule_refs),
        "cpp_rule_refs_missing_ledger_rows": missing_rule_rows,
        "cpp_cases_missing_from_ledger": cases_missing_from_ledger,
        "unique_ledger_test_cases": len(ledger_test_case_names),
        "duplicate_ledger_test_refs": len(duplicate_test_refs),
    }



def audit_scenario_files(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    scenario_dir = root / "tests" / "scenarios"
    if not scenario_dir.exists():
        add(issues, "warning", "scenarios.dir_missing", rel(scenario_dir, root))
        return {"available": False, "files": 0}
    files = sorted(scenario_dir.glob("*.mtgscn"))
    if not files:
        add(issues, "warning", "scenarios.none", "no scenario files found")
    seen: set[str] = set()
    duplicates: list[str] = []
    missing_create: list[str] = []
    missing_validate: list[str] = []
    for path in files:
        if path.stem in seen:
            duplicates.append(path.stem)
        seen.add(path.stem)
        text = path.read_text(encoding="utf-8", errors="replace")
        commands = []
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if line:
                commands.append(line.split()[0])
        if "create" not in commands:
            missing_create.append(rel(path, root))
        if "validate" not in commands:
            missing_validate.append(rel(path, root))
    for name in duplicates:
        add(issues, "error", "scenarios.duplicate_name", name)
    for path in missing_create:
        add(issues, "warning", "scenarios.missing_create", path)
    for path in missing_validate:
        add(issues, "warning", "scenarios.missing_validate", path)
    return {
        "available": True,
        "files": len(files),
        "duplicate_names": len(duplicates),
        "missing_create": missing_create,
        "missing_validate": missing_validate,
        "names": [path.stem for path in files],
    }


def audit_fuzz_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the randomized invariant runner is wired through the cube.

    This intentionally audits wiring, not semantic coverage. Semantic coverage is
    validated by run_fuzz.py and the C++ invariant checks.
    """
    required_files = [
        root / "apps" / "mtgsim_fuzz.cpp",
        root / "tools" / "run_fuzz.py",
        root / "tests" / "python" / "test_fuzz_runner.py",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "fuzz.missing_file", path)

    probes = {
        "tools/build.py": ["mtgsim_fuzz", "\"fuzz\"", "MTGSIM_BUILD_AUTO_JOBS"],
        "tools/harness.py": ["fuzz_parallel_step", "run_fuzz.py", "python.fuzz_runner"],
        "tools/run_cpp_tests.py": ["MTGSIM_AUTO_JOBS", "auto_parallelism_cap"],
        "tools/run_scenarios.py": ["MTGSIM_AUTO_JOBS", "auto_parallelism_cap"],
        "tools/run_fuzz.py": ["MTGSIM_AUTO_JOBS", "auto_parallelism_cap", "--profile", "--require-risk-seams", "risk_seams", "minimal_failing_steps", "shrink_failed_results", "--no-shrink-failures", "failed_repro_commands"],
        "tools/metrics_db.py": ["record_fuzz_report"],
        "docs/architecture/harness_design.md": ["rev0036 auto-parallelism cap", "MTGSIM_AUTO_JOBS"],
        "apps/mtgsim_fuzz.cpp": ["FuzzProfile", "risk-seams", "Fuzz Warden", "Fuzz Walker", "trigger_stack_actions", "loyalty_actions"],
        "tests/python/test_fuzz_runner.py": ["check_failure_step_shrinker_binary_searches", "minimal_failing_steps", "minimal_repro_command", "command_text"],
        "CMakeLists.txt": ["mtgsim_fuzz", "mtgsim_fuzz_smoke"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "fuzz.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "fuzz.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }



def audit_trigger_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the triggered-ability scaffold is wired through core, scenarios, CMake, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "trigger_etb_gain_life.mtgscn",
        root / "tests" / "scenarios" / "trigger_death_gain_life.mtgscn",
        root / "tests" / "scenarios" / "trigger_self_dies_lki.mtgscn",
        root / "tests" / "scenarios" / "trigger_targeted_damage_player.mtgscn",
        root / "tests" / "scenarios" / "trigger_self_dies_color_snapshot_protection.mtgscn",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "triggers.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["TriggerDefinition", "PendingTrigger", "TriggerEventKind", "PutPendingTriggersOnStack", "source_zone_change_index", "trigger_order"],
        "include/mtgsim/engine.hpp": ["pending_trigger_count", "put_pending_triggers_on_stack"],
        "src/engine.cpp": ["queue_matching_triggers_for_event", "queue_matching_triggers_from_snapshots", "create_triggered_ability_stack_object", "choose_default_trigger_targets", "apply_effect_payload", "valid_pending_trigger_order", "append_pending_trigger_order_actions", "move_object_with_precomputed_ltb_snapshots", "pre_creature_sba_ltb_snapshots"],
        "src/validation.cpp": ["trigger.invalid_controller", "ability.invalid_zone"],
        "apps/mtgsim_scenario.cpp": ["trigger=", "expect_pending_triggers", "put_triggers"],
        "tests/cpp/test_engine.cpp": ["test_creature_etb_trigger_queues_and_resolves_gain_life", "test_creature_dies_trigger_from_sba_queues_and_resolves", "test_self_dies_trigger_uses_last_known_source_snapshot", "test_targeted_trigger_chooses_legal_target_when_put_on_stack", "test_self_dies_targeted_trigger_uses_source_color_snapshot_for_protection", "test_pending_trigger_order_choice_preserves_player_selected_sequence", "test_pending_trigger_order_rejects_cross_apnap_reordering", "test_simultaneous_sba_dies_triggers_share_pre_batch_lki_snapshot"],
        "CMakeLists.txt": ["mtgsim_scenario_trigger"],
        "data/rules/coverage/rules_ledger.json": ["\"603\"", "603.10", "704.3", "test_creature_etb_trigger_queues_and_resolves_gain_life", "test_pending_trigger_order_choice_preserves_player_selected_sequence", "test_simultaneous_sba_dies_triggers_share_pre_batch_lki_snapshot", "101.4"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "triggers.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "triggers.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }



def audit_prevention_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the damage-prevention/replacement scaffold is wired through core, tests, scenarios, CMake, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "prevention_targeted_damage.mtgscn",
        root / "tests" / "scenarios" / "prevention_combat_damage.mtgscn",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "prevention.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["DamagePreventionShield", "damage_prevention_shields", "unpreventable", "ShieldAppliedToUnpreventableDamage"],
        "include/mtgsim/engine.hpp": ["add_damage_prevention_shield", "damage_prevention_shield_total", "deal_unpreventable_damage_to_target"],
        "src/engine.cpp": ["apply_damage_prevention", "apply_unpreventable_damage_prevention", "damage_prevented", "damage_prevention_applied_unpreventable", "clear_prevention_links_for_object"],
        "src/validation.cpp": ["prevention.empty_shield", "prevention.object_not_battlefield", "damage_prevention_record.unpreventable_delta_mismatch"],
        "apps/mtgsim_scenario.cpp": ["prevent_damage", "expect_prevention"],
        "tests/cpp/test_engine.cpp": ["test_damage_prevention_shield_prevents_targeted_player_damage", "test_combat_damage_uses_prevention_pipeline_for_objects", "test_unpreventable_damage_applies_prevention_without_reducing_shields"],
        "CMakeLists.txt": ["mtgsim_scenario_prevention"],
        "src/rules.cpp": ["core.prevention", "614,615"],
        "data/rules/coverage/rules_ledger.json": ["\"614\"", "\"615\"", "615.12", "test_damage_prevention_shield_prevents_targeted_player_damage", "test_unpreventable_damage_applies_prevention_without_reducing_shields"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "prevention.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "prevention.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }



def audit_zone_change_replacement_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the zone-change replacement scaffold is wired through core, tests, scenarios, CMake, docs, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "zone_replacement_dies_exile_no_trigger.mtgscn",
        root / "tests" / "scenarios" / "zone_replacement_source_scope.mtgscn",
        root / "tests" / "scenarios" / "zone_replacement_recheck_choice.mtgscn",
        root / "docs" / "architecture" / "zone_change_replacement.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "zone_replacement.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["ZoneChangeReplacementDefinition", "zone_change_replacements", "choice_rank", "ReplacementPriorityTier", "priority_tier"],
        "src/engine.cpp": ["apply_zone_change_replacement", "zone_change_replaced", "zone_change_replacement_applies_to_object", "collect_zone_change_replacement_candidates", "zone_change_replacement_choice", "candidate_min_priority_tier", "eligible_candidate_count"],
        "src/validation.cpp": ["zone_replacement.invalid_scope", "zone_replacement.inactive", "zone_replacement.invalid_priority_tier"],
        "apps/mtgsim_scenario.cpp": ["apply_zone_change_replacement_option", "replacement=NAME:SCOPE:FROM_ZONE:TO_ZONE:REPLACEMENT_ZONE", "choice="],
        "tests/cpp/test_engine.cpp": ["test_zone_change_replacement_exiles_creature_instead_of_dying", "test_zone_change_replacement_source_scope_only_replaces_itself", "test_zone_change_replacement_rechecks_modified_event_and_choice_rank", "test_zone_change_replacement_priority_tier_forces_eligible_choice", "test_validation_catches_invalid_zone_change_replacement_definition"],
        "CMakeLists.txt": ["mtgsim_scenario_zone_replacement", "zone_replacement_dies_exile_no_trigger.mtgscn", "zone_replacement_recheck_choice.mtgscn"],
        "docs/architecture/prevention_and_replacement.md": ["zone-change replacement", "ZoneChangeReplacementDefinition", "zone_change_replacement_choice", "ReplacementPriorityTier"],
        "docs/architecture/zone_change_replacement.md": ["ZoneChangeReplacementDefinition", "zone_change_replaced", "dies triggers", "rechecked", "rev0184 priority-tier seal"],
        "data/rules/coverage/rules_ledger.json": ["test_zone_change_replacement_exiles_creature_instead_of_dying", "test_zone_change_replacement_rechecks_modified_event_and_choice_rank", "test_zone_change_replacement_priority_tier_forces_eligible_choice", "zone-change replacement", "priority tier"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "zone_replacement.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "zone_replacement.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }




def audit_zone_change_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that structured zone-change records stay wired to movement, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["ZoneChangeRecord", "zone_change_records", "requested_zone", "from_zone_change_index"],
        "include/mtgsim/engine.hpp": ["zone_change_record_count", "latest_zone_change_record"],
        "src/engine.cpp": ["ZoneChangeRecord", "replacement_applied", "creature_died", "move_object"],
        "src/validation.cpp": ["zone_change_record.nonadvancing_zone_change_index", "zone_change_record.invalid_zone", "zone_change_record.future_sequence"],
        "tests/cpp/test_engine.cpp": ["test_zone_change_record_preserves_requested_and_final_destination", "latest_zone_change_record", "requested_zone", "nonadvancing_zone_change_index"],
        "docs/architecture/zone_change_replacement.md": ["ZoneChangeRecord", "requested_zone", "finalized replacement destination"],
        "data/rules/coverage/rules_ledger.json": ["test_zone_change_record_preserves_requested_and_final_destination", "ZoneChangeRecord"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "zone_change_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "zone_change_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_zone_replacement_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that applied zone-change replacement records stay wired through event emission, movement, validation, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["ZoneChangeReplacementRecord", "zone_change_replacement_records", "event_to_zone", "first_replacement_record_index", "candidate_min_priority_tier", "eligible_candidate_count"],
        "include/mtgsim/engine.hpp": ["zone_change_replacement_record_count", "latest_zone_change_replacement_record"],
        "src/types.cpp": ["EventRecordKind::ZoneReplacement", "zone_replacement"],
        "src/engine.cpp": ["ZoneChangeReplacementRecord", "EventRecordKind::ZoneReplacement", "zone_change_replacement_records", "zone_replacement_record_index", "eligible_candidate_count", "candidate_min_priority_tier"],
        "src/validation.cpp": ["zone_replacement_record.invalid_zone_change_link", "zone_replacement_record.zone_change_range_ownership_mismatch", "zone_change_record.replacement_chain_mismatch", "zone_change_record.replacement_pass_mismatch", "zone_change_record.duplicate_replacement_effect", "event_record.invalid_zone_replacement_link", "zone_replacement_record.priority_tier_skip", "zone_replacement_record.zero_eligible_candidates"],
        "tests/cpp/test_engine.cpp": ["test_zone_replacement_record_links_choice_passes_and_final_movement", "test_zone_change_replacement_priority_tier_forces_eligible_choice", "zone_change_record.replacement_chain_mismatch", "zone_replacement_record.zone_change_range_ownership_mismatch", "latest_zone_change_replacement_record", "EventRecordKind::ZoneReplacement"],
        "docs/architecture/zone_change_replacement.md": ["ZoneChangeReplacementRecord", "event_to_zone", "candidate_count", "rev0183 replacement-chain validation seal", "rev0184 priority-tier seal", "eligible_candidate_count"],
        "docs/architecture/audit_refactor_notes.md": ["rev0051", "rev0183", "rev0184", "ZoneChangeReplacementRecord", "zone_change_replacement_records", "candidate_min_priority_tier"],
        "data/rules/coverage/rules_ledger.json": ["test_zone_replacement_record_links_choice_passes_and_final_movement", "test_zone_change_replacement_priority_tier_forces_eligible_choice", "ZoneChangeReplacementRecord", "616", "eligible_candidate_count"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "zone_replacement_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "zone_replacement_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_damage_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that structured damage records stay wired to the damage/prevention path, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["DamageRecord", "damage_records", "prevented_by_protection", "source_zone_change_index", "not_dealt", "damage_disallowed_by_target_type", "first_damage_counter_change_record_index", "damage_counter_change_record_count", "first_damage_life_change_record_index", "damage_life_change_record_count"],
        "include/mtgsim/engine.hpp": ["damage_record_count", "latest_damage_record"],
        "src/engine.cpp": ["DamageRecord", "append_damage_record", "apply_damage_prevention", "damage_prevented_by_protection", "damage_disallowed_target_type", "counter_change_records_before_damage_results", "life_change_records_before_damage_results", "link_life_change_record_range_to_damage"],
        "src/validation.cpp": ["damage_record.amount_mismatch", "damage_record.protection_amount_mismatch", "damage_record.target_zone_change_index_mismatch", "damage_record.undamageable_object_dealt", "damage_record.missing_counter_change_range", "damage_record.counter_change_source_mismatch", "damage_record.missing_player_life_change_range", "damage_record.life_change_backlink_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_damage_record_captures_prevention_protection_and_source_keywords", "test_damage_to_non_damageable_object_is_disallowed_and_typed", "test_damage_record_links_player_and_lifelink_life_change_rows", "latest_damage_record", "damage_record.protection_amount_mismatch", "first_damage_counter_change_record_index", "damage_record.missing_counter_change_range", "first_damage_life_change_record_index", "damage_record.missing_player_life_change_range"],
        "docs/architecture/prevention_and_replacement.md": ["DamageRecord", "typed damage", "prevented/dealt", "not_dealt", "damage counter-change", "damage life-change"],
        "docs/architecture/audit_refactor_notes.md": ["rev0047", "rev0176", "rev0177", "rev0178", "DamageRecord", "damage_records", "not_dealt", "damage counter-change", "damage_life_change_record_count"],
        "data/rules/coverage/rules_ledger.json": ["test_damage_record_captures_prevention_protection_and_source_keywords", "test_damage_to_non_damageable_object_is_disallowed_and_typed", "test_damage_record_links_player_and_lifelink_life_change_rows", "DamageRecord", "damage-counter", "damage-life"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "damage_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "damage_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_damage_prevention_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that finite prevention shields emit typed add/consume/expiry records linked through damage and zone-change records."""
    probes = {
        "include/mtgsim/types.hpp": ["DamagePreventionRecord", "DamagePreventionRecordKind", "damage_prevention_record_index", "damage_prevention_records", "first_damage_prevention_record_index", "damage_prevention_record_count"],
        "include/mtgsim/engine.hpp": ["damage_prevention_record_count", "latest_damage_prevention_record"],
        "src/types.cpp": ["EventRecordKind::DamagePrevention", "shield_consumed", "shield_expired"],
        "src/engine.cpp": ["record_damage_prevention_change", "link_damage_prevention_record_range_to_damage", "DamagePreventionRecordKind::ShieldAdded", "DamagePreventionRecordKind::ShieldConsumed", "DamagePreventionRecordKind::ShieldExpired"],
        "src/validation.cpp": ["event_record.invalid_damage_prevention_link", "damage_record.invalid_prevention_record_range", "zone_change_record.invalid_damage_prevention_range", "damage_prevention_record.invalid_damage_link", "damage_prevention_record.event_record_link_count"],
        "tests/cpp/test_engine.cpp": ["test_damage_prevention_record_tracks_add_consume_and_damage_range", "test_damage_prevention_record_tracks_zone_expiry_and_zone_range", "latest_damage_prevention_record", "EventRecordKind::DamagePrevention"],
        "docs/architecture/prevention_and_replacement.md": ["DamagePreventionRecord", "damage_prevention_records", "shield consumption", "zone-change expiry"],
        "docs/architecture/audit_refactor_notes.md": ["rev0065", "DamagePreventionRecord", "damage_prevention_records"],
        "data/rules/coverage/rules_ledger.json": ["test_damage_prevention_record_tracks_add_consume_and_damage_range", "test_damage_prevention_record_tracks_zone_expiry_and_zone_range", "DamagePreventionRecord", "614", "615"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "damage_prevention_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "damage_prevention_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_life_change_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that life-total mutations stay wired to typed records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["LifeChangeRecord", "LifeChangeKind", "life_change_record_index", "life_change_records", "damage_record_index", "damage_result", "lifelink_result"],
        "include/mtgsim/engine.hpp": ["life_change_record_count", "latest_life_change_record"],
        "src/types.cpp": ["LifeChangeKind", "loss", "gain"],
        "src/engine.cpp": ["record_life_change", "EventRecordKind::LifeChange", "life_change_records", "link_life_change_record_range_to_damage"],
        "src/validation.cpp": ["event_record.invalid_life_change_link", "life_change_record.gain_delta_mismatch", "life_change_record.event_record_link_count", "life_change_record.invalid_damage_link", "life_change_record.lifelink_controller_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_life_change_record_links_gain_loss_and_validation", "test_damage_record_links_player_and_lifelink_life_change_rows", "latest_life_change_record", "EventRecordKind::LifeChange", "lifelink_result"],
        "docs/architecture/engine_design.md": ["LifeChangeRecord", "life_change_records", "life-total", "damage-result backlinks"],
        "docs/architecture/audit_refactor_notes.md": ["rev0061", "rev0178", "LifeChangeRecord", "life_change_records", "damage-result backlinks"],
        "data/rules/coverage/rules_ledger.json": ["test_life_change_record_links_gain_loss_and_validation", "test_damage_record_links_player_and_lifelink_life_change_rows", "LifeChangeRecord", "119", "damage-life"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "life_change_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "life_change_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_mana_change_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that mana-pool mutations stay wired to typed records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["ManaChangeRecord", "ManaChangeKind", "mana_change_record_index", "mana_change_records"],
        "include/mtgsim/engine.hpp": ["mana_change_record_count", "latest_mana_change_record"],
        "src/types.cpp": ["ManaChangeKind", "produced", "paid", "emptied"],
        "src/engine.cpp": ["record_mana_change", "add_mana_pool_recorded", "pay_mana_cost_recorded", "EventRecordKind::ManaChange"],
        "src/validation.cpp": ["event_record.invalid_mana_change_link", "mana_change_record.paid_delta_mismatch", "mana_change_record.event_record_link_count"],
        "tests/cpp/test_engine.cpp": ["test_mana_change_record_links_production_payment_and_clearing", "latest_mana_change_record", "EventRecordKind::ManaChange"],
        "docs/architecture/engine_design.md": ["ManaChangeRecord", "mana_change_records", "mana-pool"],
        "docs/architecture/audit_refactor_notes.md": ["rev0062", "ManaChangeRecord", "mana_change_records"],
        "data/rules/coverage/rules_ledger.json": ["test_mana_change_record_links_production_payment_and_clearing", "ManaChangeRecord", "106"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_change_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_change_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_counter_change_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that object/player counter mutations stay wired to typed records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["CounterChangeRecord", "CounterChangeKind", "counter_change_record_index", "counter_change_records", "cost_payment", "zone_change_cleanup", "zone_change_record_index", "first_counter_change_record_index", "counter_change_record_count"],
        "include/mtgsim/engine.hpp": ["counter_change_record_count", "latest_counter_change_record"],
        "src/types.cpp": ["CounterChangeKind", "object_added", "object_removed", "player_added"],
        "src/engine.cpp": ["record_counter_change", "record_object_counter_change", "record_player_counter_change", "EventRecordKind::CounterChange", "loyalty_cost_paid", "clear_counters_for_zone_change", "zone_change_cleanup"],
        "src/validation.cpp": ["event_record.invalid_counter_change_link", "counter_change_record.object_add_delta_mismatch", "counter_change_record.event_record_link_count", "counter_change_record.cost_source_mismatch", "zone_change_record.invalid_counter_change_range", "zone_change_record.counter_change_backlink_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_counter_change_record_links_object_player_and_damage_counters", "test_counter_change_record_links_loyalty_costs_and_zone_cleanup", "latest_counter_change_record", "EventRecordKind::CounterChange"],
        "docs/architecture/engine_design.md": ["CounterChangeRecord", "counter_change_records", "counter mutation", "rev0064 counter costs"],
        "docs/architecture/audit_refactor_notes.md": ["rev0064", "CounterChangeRecord", "zone_change_cleanup", "cost_payment"],
        "data/rules/coverage/rules_ledger.json": ["test_counter_change_record_links_object_player_and_damage_counters", "test_counter_change_record_links_loyalty_costs_and_zone_cleanup", "CounterChangeRecord", "122", "606.4"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "counter_change_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "counter_change_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_action_receipt_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that apply_action has a durable transition receipt instead of UI-label-only replay hints."""
    probes = {
        "include/mtgsim/types.hpp": ["ActionReceiptRecord", "action_receipt_records", "kActionReceiptRecordSchemaVersion", "state_hash_before", "journal_entries_after", "journal_hash_after_action", "journal_entries_after_action", "has_post_action_journal_seal", "choice_page_location_found", "choice_page_schema_version", "choice_page_state_hash", "choice_page_choice_request_hash", "choice_page_total_actions_lower_bound", "choice_page_remaining_actions_lower_bound", "choice_page_hash", "choice_queue_location_schema_version", "kChoiceRequestQueueSchemaVersion", "choice_queue_schema_version", "kLegalActionSchemaVersion", "action_schema_version", "kStateCoreSchemaVersion", "state_schema_version", "kChoiceRequestSchemaVersion", "choice_request_schema_version", "trigger_order"],
        "include/mtgsim/engine.hpp": ["legal_action_hash", "action_receipt_hash", "canonical_action_string", "action_receipt_record_count", "latest_action_receipt_record"],
        "src/engine.cpp": ["append_action_receipt", "legal_action_hash", "action_receipt_hash", "MTGSim.ActionReceiptRecord.v1", "canonical_action_string", "action_receipt_records", "record.journal_entries_after", "record.journal_hash_after_action = record.journal_hash_after", "record.journal_entries_after_action = record.journal_entries_after", "receipt.has_post_action_journal_seal()", "record.trigger_order = action.trigger_order"],
        "src/validation.cpp": ["action_receipt.action_hash_mismatch", "action_receipt.non_contiguous_index", "action_from_receipt(receipt)", "action_receipt.legal_without_page_location", "action_receipt.page_location_zero_hash", "action_receipt.page_location_state_hash", "action_receipt.page_location_choice_request_hash", "action_receipt.page_count_lower_bound_mismatch", "action_receipt.page_count_exact_flag_mismatch", "action_receipt.page_count_remaining_lower_bound_mismatch", "action_receipt.choice_queue_location_schema_version", "action_receipt.choice_queue_schema_version", "action_receipt.action_schema_version", "action_receipt.state_schema_version", "action_receipt.choice_request_schema_version", "action_receipt.choice_queue_schema_version", "action_receipt.state_schema_version", "action_receipt.zero_journal_hash", "action_receipt.post_action_journal_hash_alias_mismatch", "action_receipt.post_action_journal_count_alias_mismatch", "action_receipt.post_action_journal_seal_missing", "action_receipt.trigger_order_stack_mismatch", "action_receipt.trigger_order_invalid_record"],
        "tests/cpp/test_engine.cpp": ["test_canonical_action_hash_ignores_display_label", "test_apply_action_records_transition_receipt_hashes", "action_receipt_hash(*receipt)", "test_action_receipt_post_action_journal_alias_is_validated", "test_trimmed_branch_records_new_action_receipt_only", "action_schema_version", "state_schema_version", "choice_request_schema_version", "choice_queue_schema_version", "post_action_journal_hash_alias_mismatch", "test_pending_trigger_order_choice_preserves_player_selected_sequence", "trigger_order="],
        "docs/architecture/action_receipts_replay_seed_rev0069.md": ["ActionReceiptRecord", "canonical action hash", "replay-seed"],
        "docs/architecture/transition_receipt_journal_alias_rev0122.md": ["ActionReceiptRecord", "journal_hash_after_action", "journal_entries_after_action", "has_post_action_journal_seal", "post-action/pre-receipt"],
        "docs/architecture/transition_causal_receipt_hash_rev0123.md": ["ActionReceiptRecord", "action_receipt_hash", "causal_receipt_hash", "kActionReceiptRecordSchemaVersion", "committed_with_hashed_causal_receipt"],
        "docs/architecture/audit_refactor_notes.md": ["rev0069", "rev0122", "rev0123", "ActionReceiptRecord", "canonical action hash", "action_receipt_hash", "causal_receipt_hash", "has_post_action_journal_seal"],
        "data/rules/coverage/rules_ledger.json": ["ActionReceiptRecord", "action_receipt_hash", "causal_receipt_hash", "test_apply_action_records_transition_receipt_hashes", "test_action_receipt_post_action_journal_alias_is_validated", "test_trimmed_branch_records_new_action_receipt_only", "post_action_journal_hash_alias_mismatch", "test_pending_trigger_order_choice_preserves_player_selected_sequence", "trigger_order"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "action_receipt.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "action_receipt.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_transition_result_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the first-class transition result exposes the same choice-proof spine as receipts."""
    probes = {
        "include/mtgsim/types.hpp": [
            "TransitionResult",
            "LegalAction action",
            "ChoiceQueueLocation queue_location",
            "choice_page_location_checked",
            "choice_queue_location_checked",
            "choice_queue_location_found",
            "staged_commit_attempted",
            "staged_commit_applied",
            "staged_receipt_checked",
            "staged_receipt_consistent",
            "staged_adoption_guard_passed",
            "staged_commit_adopted",
            "has_checked_page_location",
            "has_checked_queue_location",
            "has_selected_action",
            "committed_with_staged_adoption",
            "committed_with_atomic_adoption_guard",
            "committed_with_action_journal_seal",
            "committed_with_hashed_causal_receipt",
            "committed_with_checkpoint_seals",
            "committed_with_choice_proofs",
            "action_receipt_schema_version",
            "causal_receipt_hash",
            "journal_hash_after_action",
            "journal_entries_after_action",
            "has_post_action_journal_seal",
            "StateCheckpointSeal checkpoint_before",
            "StateCheckpointSeal checkpoint_after",
            "has_transition_checkpoint_seals",
            "committed_with_checkpoint_seals",
            "rejected_with_checkpoint_stability",
            "kTransitionBoundarySealSchemaVersion",
            "transition_boundary_schema_version",
            "transition_boundary_hash",
            "has_transition_boundary_seal",
            "committed_with_transition_boundary_seal",
            "TransitionBoundaryFailureKind",
            "TransitionBoundaryVerifyResult",
            "expected_transition_boundary_hash",
            "observed_causal_receipt_hash",
            "kTransitionPreflightSealSchemaVersion",
            "transition_preflight_schema_version",
            "transition_preflight_hash",
            "has_transition_preflight_seal",
            "committed_with_preflight_choice_seal",
            "expected_transition_preflight_hash",
            "observed_transition_preflight_hash",
            "PreflightSealMissing",
            "PreflightSealMismatch",
            "kTransitionTraceHandoffSealSchemaVersion",
            "transition_trace_handoff_schema_version",
            "transition_trace_handoff_hash",
            "has_transition_trace_handoff_seal",
            "committed_with_trace_handoff_seal",
            "expected_transition_trace_handoff_hash",
            "observed_transition_trace_handoff_hash",
            "TraceHandoffSealMissing",
            "TraceHandoffSealMismatch",
            "kActionTraceEntrySchemaVersion",
            "action_trace_entry_schema_version",
            "action_trace_entry_hash",
            "has_action_trace_entry_seal",
            "expected_action_trace_entry_hash",
            "observed_action_trace_entry_hash",
            "expected_action_trace_entry_schema_version",
            "observed_action_trace_entry_schema_version",
            "TraceEntrySealMissing",
            "TraceEntrySealMismatch",
        ],
        "include/mtgsim/engine.hpp": [
            "pending_transition_for_player",
            "commit_action_transition",
            "transition_result_matches_receipt",
            "verify_transition_result_boundary",
            "check_transition_result_boundary",
            "transition_result_boundary_hash",
            "transition_result_preflight_hash",
            "action_trace_entry_from_transition_result",
            "action_trace_entry_hash",
            "transition_result_matches_action_trace_entry",
            "transition_result_trace_entry_hash",
            "transition_result_trace_handoff_hash",
        ],
        "src/engine.cpp": [
            "canonicalize_legal_action",
            "preflight_action_transition",
            "ActionTransitionPreflight",
            "result.action = transition_action",
            "receipt.action_hash == legal_action_hash(result.action)",
            "transition_result_matches_receipt",
            "verify_transition_result_boundary",
            "verify_state_checkpoint_seal(before, result.checkpoint_before)",
            "verify_state_checkpoint_seal(after, result.checkpoint_after)",
            "out.expected_causal_receipt_hash != result.causal_receipt_hash",
            "result.queue_location = make_choice_queue_location",
            "result.choice_page_location_checked = true",
            "result.choice_queue_location_checked = true",
            "result.choice_queue_location_found = result.queue_location.found",
            "GameState staged_game = game",
            "transition_receipt_matches_result",
            "result.staged_receipt_checked = true",
            "result.causal_receipt_hash = action_receipt_hash(*receipt)",
            "result.staged_adoption_guard_passed",
            "result.journal_hash_after_action = journal_hash(staged_game)",
            "result.checkpoint_before = make_state_checkpoint_seal(game)",
            "result.checkpoint_after = make_state_checkpoint_seal(game)",
            "result.has_transition_checkpoint_seals()",
            "receipt.journal_hash_after == result.journal_hash_after_action",
            "receipt.journal_entries_after == result.journal_entries_after_action",
            "staged_receipt_guard_failed",
            "game = std::move(staged_game)",
            "append_action_receipt",
            "MTGSim.TransitionBoundarySeal.v1",
            "MTGSim.TransitionPreflightSeal.v1",
            "seal_transition_result_preflight",
            "transition_result_preflight_hash",
            "result.transition_preflight_hash = transition_result_preflight_hash(result)",
            "TransitionBoundaryFailureKind::PreflightSealMismatch",
            "seal_transition_result_boundary",
            "result.transition_boundary_hash = transition_result_boundary_hash(result)",
            "out.expected_transition_boundary_hash != result.transition_boundary_hash",
            "TransitionBoundaryVerifyResult check_transition_result_boundary",
            "TransitionBoundaryFailureKind::ReceiptHashMismatch",
            "TransitionBoundaryFailureKind::AfterCheckpointMismatch",
            "verify_transition_result_boundary(const TransitionResult& result",
            "action_trace_entry_from_receipt_record",
            "action_trace_entry_from_transition_result",
            "action_trace_entry_hash",
            "transition_result_matches_action_trace_entry",
            "transition_result_trace_entry_hash",
            "transition_result_trace_handoff_hash",
            "MTGSim.ActionTraceEntry.v1",
            "MTGSim.TransitionTraceHandoffSeal.v1",
            "result.transition_trace_handoff_hash = transition_result_trace_handoff_hash(result)",
            "TransitionBoundaryFailureKind::TraceHandoffSealMissing",
            "TransitionBoundaryFailureKind::TraceHandoffSealMismatch",
            "result.action_trace_entry_hash = transition_result_trace_entry_hash(result)",
            "result.action_trace_entry_schema_version = kActionTraceEntrySchemaVersion",
            "TransitionBoundaryFailureKind::TraceEntrySealMissing",
            "TransitionBoundaryFailureKind::TraceEntrySealMismatch",
            "out.expected_action_trace_entry_hash",
            "out.observed_action_trace_entry_hash",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_transition_result_exposes_need_choice_surface",
            "test_commit_action_transition_rejects_without_journal_mutation",
            "test_commit_action_transition_commits_with_single_causal_receipt",
            "test_commit_action_transition_carries_choice_proof_hashes",
            "test_commit_action_transition_adopts_the_staged_legacy_equivalent",
            "test_commit_action_transition_checks_staged_receipt_before_adoption",
            "test_commit_action_transition_carries_hashed_causal_receipt",
            "test_commit_action_transition_carries_canonical_selected_action",
            "test_commit_action_transition_carries_state_checkpoint_seals",
            "test_commit_action_transition_carries_post_action_journal_seal",
            "test_commit_action_transition_projects_exact_action_trace_entry",
            "test_transition_trace_handoff_uses_canonical_trace_entry_hash",
            "test_verify_transition_result_boundary_binds_committed_state_and_receipt",
            "test_verify_transition_result_boundary_accepts_pending_and_rejected_without_mutation",
            "test_transition_result_boundary_seal_hashes_committed_pending_and_rejected",
            "test_transition_boundary_diagnostics_localize_failure_kind",
            "test_transition_result_preflight_seal_hashes_choice_surface",
            "test_action_receipt_post_action_journal_alias_is_validated",
            "test_commit_action_transition_projects_exact_action_trace_entry",
            "committed_with_staged_adoption",
            "committed_with_atomic_adoption_guard",
            "committed_with_action_journal_seal",
            "committed_with_hashed_causal_receipt",
            "committed_with_choice_proofs",
            "transition_result_matches_receipt",
            "verify_transition_result_boundary",
            "has_selected_action",
            "transition_result_matches_receipt(result, *receipt)",
            "has_checked_queue_location",
            "has_post_action_journal_seal",
            "transition_result_boundary_hash",
            "has_transition_boundary_seal",
            "committed_with_transition_boundary_seal",
            "check_transition_result_boundary",
            "transition_result_preflight_hash",
            "has_transition_preflight_seal",
            "committed_with_preflight_choice_seal",
            "TransitionBoundaryFailureKind::PreflightSealMismatch",
            "TransitionBoundaryFailureKind::BoundarySealMismatch",
            "TransitionBoundaryFailureKind::ReceiptHashMismatch",
            "TraceHandoffSealMissing",
            "TraceHandoffSealMismatch",
            "transition_result_trace_handoff_hash",
            "action_trace_entry_from_transition_result",
            "action_trace_entry_hash",
            "transition_result_matches_action_trace_entry",
            "test_transition_result_carries_first_class_trace_entry_seal",
            "has_action_trace_entry_seal",
            "TraceEntrySealMismatch",
        ],
        "docs/architecture/transition_choice_proof_spine_rev0118.md": [
            "TransitionResult",
            "ChoiceQueueLocation",
            "choice_queue_location_checked",
            "committed_with_choice_proofs",
            "nonmutating rejection",
        ],
        "docs/architecture/transition_staged_commit_rev0119.md": [
            "staged GameState",
            "preflight_action_transition",
            "commit_failed_without_adoption",
            "committed_with_staged_adoption",
            "atomic adoption",
        ],
        "docs/architecture/transition_atomic_adoption_guard_rev0120.md": [
            "transition_receipt_matches_result",
            "staged_receipt_checked",
            "staged_receipt_consistent",
            "staged_adoption_guard_passed",
            "committed_with_atomic_adoption_guard",
            "staged_receipt_guard_failed",
        ],
        "docs/architecture/transition_action_journal_seal_rev0121.md": [
            "journal_hash_after_action",
            "journal_entries_after_action",
            "transition_receipt_matches_result",
            "committed_with_action_journal_seal",
            "post-action/pre-receipt",
        ],
        "docs/architecture/transition_receipt_journal_alias_rev0122.md": [
            "ActionReceiptRecord",
            "journal_hash_after_action",
            "journal_entries_after_action",
            "has_post_action_journal_seal",
            "post-action/pre-receipt",
        ],
        "docs/architecture/transition_causal_receipt_hash_rev0123.md": [
            "TransitionResult",
            "ActionReceiptRecord",
            "action_receipt_hash",
            "causal_receipt_hash",
            "kActionReceiptRecordSchemaVersion",
            "committed_with_hashed_causal_receipt",
        ],
        "docs/architecture/transition_selected_action_seal_rev0124.md": [
            "TransitionResult",
            "LegalAction action",
            "canonicalizes",
            "transition_result_matches_receipt",
            "ActionReceiptRecord",
            "selected action",
        ],
        "docs/architecture/transition_checkpoint_seal_rev0125.md": [
            "TransitionResult",
            "StateCheckpointSeal checkpoint_before",
            "StateCheckpointSeal checkpoint_after",
            "has_transition_checkpoint_seals",
            "committed_with_checkpoint_seals",
            "rejected_with_checkpoint_stability",
        ],
        "docs/architecture/transition_boundary_verifier_rev0126.md": [
            "verify_transition_result_boundary",
            "StateCheckpointSeal checkpoint_before",
            "StateCheckpointSeal checkpoint_after",
            "proposal `GameState`",
            "adopted or unchanged after `GameState`",
            "causal `ActionReceiptRecord`",
            "NeedChoice",
            "Rejected",
            "Committed",
        ],
        "docs/architecture/transition_boundary_seal_rev0127.md": [
            "kTransitionBoundarySealSchemaVersion",
            "transition_boundary_hash",
            "transition_result_boundary_hash",
            "has_transition_boundary_seal",
            "committed_with_transition_boundary_seal",
            "seal_transition_result_boundary",
        ],
        "docs/architecture/transition_boundary_diagnostics_rev0128.md": [
            "TransitionBoundaryFailureKind",
            "TransitionBoundaryVerifyResult",
            "check_transition_result_boundary",
            "BoundarySealMismatch",
            "AfterCheckpointMismatch",
            "ReceiptHashMismatch",
            "NeedChoiceMissingActions",
            "StatusInvalid",
        ],
        "docs/architecture/transition_preflight_choice_seal_rev0129.md": [
            "kTransitionPreflightSealSchemaVersion",
            "transition_preflight_hash",
            "transition_result_preflight_hash",
            "has_transition_preflight_seal",
            "committed_with_preflight_choice_seal",
            "PreflightSealMissing",
            "PreflightSealMismatch",
        ],
        "docs/architecture/transition_trace_handoff_seal_rev0130.md": [
            "kTransitionTraceHandoffSealSchemaVersion",
            "transition_trace_handoff_hash",
            "transition_result_trace_handoff_hash",
            "action_trace_entry_from_transition_result",
            "action_trace_entry_hash",
            "transition_result_matches_action_trace_entry",
            "TraceHandoffSealMissing",
            "TraceHandoffSealMismatch",
            "expected_transition_trace_handoff_hash",
            "observed_transition_trace_handoff_hash",
            "ActionTraceEntry",
            "action_trace_entry_from_receipt_record",
        ],
        "docs/architecture/transition_trace_entry_hash_rev0131.md": [
            "transition_result_trace_entry_hash",
            "action_trace_entry_from_transition_result",
            "action_trace_entry_hash",
            "transition_result_trace_handoff_hash",
            "canonical trace-entry hash",
            "test_transition_trace_handoff_uses_canonical_trace_entry_hash",
            "receipt/result seam",
        ],
        "docs/architecture/transition_trace_entry_seal_rev0132.md": [
            "kActionTraceEntrySchemaVersion",
            "action_trace_entry_schema_version",
            "action_trace_entry_hash",
            "has_action_trace_entry_seal",
            "TraceEntrySealMissing",
            "TraceEntrySealMismatch",
            "expected_action_trace_entry_hash",
            "observed_action_trace_entry_hash",
            "transition_result_trace_entry_hash",
            "ActionTraceEntry",
            "test_transition_result_carries_first_class_trace_entry_seal",
        ],
        "docs/architecture/audit_refactor_notes.md": [
            "rev0118",
            "rev0119",
            "rev0120",
            "rev0121",
            "rev0122",
            "rev0123",
            "rev0124",
            "rev0125",
            "rev0126",
            "rev0127",
            "rev0128",
            "rev0129",
            "rev0130",
            "rev0131",
            "rev0132",
            "TransitionResult",
            "choice-proof spine",
            "staged commit",
            "atomic adoption guard",
            "journal_hash_after_action",
            "post-action journal",
            "has_post_action_journal_seal",
            "action_receipt_hash",
            "causal_receipt_hash",
            "committed_with_hashed_causal_receipt",
            "transition_result_matches_receipt",
            "selected-action",
            "checkpoint_before",
            "committed_with_checkpoint_seals",
            "ChoiceQueueLocation",
            "verify_transition_result_boundary",
            "transition_boundary_hash",
            "transition_result_boundary_hash",
            "has_transition_boundary_seal",
            "committed_with_transition_boundary_seal",
            "proposal state",
            "adopted state",
            "TransitionBoundaryFailureKind",
            "TransitionBoundaryVerifyResult",
            "check_transition_result_boundary",
            "transition_preflight_hash",
            "transition_result_preflight_hash",
            "has_transition_preflight_seal",
            "committed_with_preflight_choice_seal",
            "PreflightSealMissing",
            "PreflightSealMismatch",
            "transition_trace_handoff_hash",
            "transition_result_trace_handoff_hash",
            "committed_with_trace_handoff_seal",
            "TraceHandoffSealMissing",
            "TraceHandoffSealMismatch",
            "action_trace_entry_from_transition_result",
            "transition_result_matches_action_trace_entry",
            "transition_result_trace_entry_hash",
            "canonical trace-entry hash",
            "has_action_trace_entry_seal",
            "action_trace_entry_hash",
            "TraceEntrySealMissing",
            "TraceEntrySealMismatch",
        ],
        "data/rules/coverage/rules_ledger.json": [
            "test_commit_action_transition_carries_choice_proof_hashes",
            "test_commit_action_transition_adopts_the_staged_legacy_equivalent",
            "test_commit_action_transition_checks_staged_receipt_before_adoption",
            "test_commit_action_transition_carries_hashed_causal_receipt",
            "test_commit_action_transition_carries_canonical_selected_action",
            "test_commit_action_transition_carries_state_checkpoint_seals",
            "test_commit_action_transition_carries_post_action_journal_seal",
            "test_commit_action_transition_projects_exact_action_trace_entry",
            "test_transition_trace_handoff_uses_canonical_trace_entry_hash",
            "test_verify_transition_result_boundary_binds_committed_state_and_receipt",
            "test_verify_transition_result_boundary_accepts_pending_and_rejected_without_mutation",
            "test_transition_result_boundary_seal_hashes_committed_pending_and_rejected",
            "test_transition_boundary_diagnostics_localize_failure_kind",
            "test_action_receipt_post_action_journal_alias_is_validated",
            "committed_with_staged_adoption",
            "committed_with_atomic_adoption_guard",
            "committed_with_action_journal_seal",
            "committed_with_hashed_causal_receipt",
            "committed_with_choice_proofs",
            "transition_result_matches_receipt",
            "verify_transition_result_boundary",
            "has_selected_action",
            "has_transition_checkpoint_seals",
            "causal_receipt_hash",
            "action_receipt_hash",
            "journal_hash_after_action",
            "choice_queue_location_checked",
            "transition_boundary_hash",
            "transition_result_boundary_hash",
            "committed_with_transition_boundary_seal",
            "TransitionBoundaryFailureKind",
            "TransitionBoundaryVerifyResult",
            "check_transition_result_boundary",
            "ReceiptHashMismatch",
            "transition_preflight_hash",
            "transition_result_preflight_hash",
            "has_transition_preflight_seal",
            "committed_with_preflight_choice_seal",
            "PreflightSealMissing",
            "PreflightSealMismatch",
            "transition_trace_handoff_hash",
            "transition_result_trace_handoff_hash",
            "committed_with_trace_handoff_seal",
            "TraceHandoffSealMissing",
            "TraceHandoffSealMismatch",
            "action_trace_entry_from_transition_result",
            "action_trace_entry_hash",
            "transition_result_matches_action_trace_entry",
            "transition_result_trace_entry_hash",
            "test_transition_result_carries_first_class_trace_entry_seal",
            "has_action_trace_entry_seal",
            "action_trace_entry_hash",
            "TraceEntrySealMissing",
            "TraceEntrySealMismatch",
        ],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "transition_result.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "transition_result.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_action_trace_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that action receipts can be exported, serialized, parsed, and replay-verified from a checkpoint."""
    probes = {
        "include/mtgsim/types.hpp": ["ActionTraceEntry", "ActionReplayResult", "ActionTraceParseResult", "expected_state_hash_after", "LegalActionValidationSource", "expected_choice_page_location_present", "expected_choice_page_schema_version", "expected_choice_page_context_present", "expected_choice_page_state_hash", "expected_choice_page_choice_request_hash", "expected_choice_page_total_actions_lower_bound", "expected_choice_page_remaining_actions_lower_bound", "expected_choice_page_hash", "expected_choice_queue_location_schema_version", "expected_choice_queue_schema_version", "expected_action_schema_version", "expected_state_schema_version", "expected_choice_request_schema_version", "ChoicePageLocationMismatch", "ActionHashMismatch", "StateHashSchemaMismatch"],
        "include/mtgsim/engine.hpp": ["action_from_receipt", "export_action_trace", "serialize_action_trace", "parse_action_trace", "replay_action_trace"],
        "src/engine.cpp": ["serialize_action_trace", "parse_action_trace", "MTGSim.ActionTrace.v17", "trigger_order", "MTGSim.ActionTrace.v16", "MTGSim.ActionTrace.v15", "MTGSim.ActionTrace.v14", "MTGSim.ActionTrace.v13", "MTGSim.ActionTrace.v12", "MTGSim.ActionTrace.v7", "MTGSim.ActionTrace.v6", "MTGSim.ActionTrace.v5", "MTGSim.ActionTrace.v4", "MTGSim.ActionTrace.v3", "MTGSim.ActionTrace.v2", "MTGSim.ActionTrace.v1", "choice_source", "choice_page_found", "choice_page_schema", "choice_page_total_lower", "choice_page_remaining_lower", "choice_page_state", "choice_page_request_hash", "choice_page_hash", "choice_queue_schema", "choice_queue_location_schema", "choice_schema", "action_schema", "state_schema", "ChoiceValidationSourceMismatch", "ChoicePageLocationMismatch", "non-contiguous trace step", "StateHashAfterMismatch"],
        "src/validation.cpp": ["action_from_receipt(receipt)", "action_receipt.action_hash_mismatch", "action_receipt.action_schema_version", "action_receipt.choice_request_schema_version", "action_receipt.choice_queue_schema_version", "action_receipt.state_schema_version"],
        "tests/cpp/test_engine.cpp": ["test_pending_trigger_order_choice_preserves_player_selected_sequence", "test_action_trace_export_replays_state_hash_sequence", "test_action_trace_text_roundtrip_replays_from_checkpoint", "test_action_trace_text_codec_preserves_vector_targets_and_rejects_bad_steps", "test_action_trace_default_excludes_illegal_receipts", "test_action_trace_replay_detects_choice_validation_source_drift_without_mutation", "test_action_trace_replay_detects_choice_page_location_drift_without_mutation", "test_action_trace_replay_detects_choice_page_hash_drift_without_mutation", "test_action_trace_replay_detects_choice_page_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_page_count_drift_without_mutation", "test_action_trace_replay_detects_choice_page_context_drift_without_mutation", "test_action_trace_replay_detects_choice_queue_schema_drift_without_mutation", "test_action_trace_replay_detects_action_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_request_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_request_queue_schema_drift_without_mutation", "test_action_trace_replay_detects_state_hash_schema_drift_without_mutation"],
        "docs/architecture/action_trace_replay_check_rev0070.md": ["ActionTraceEntry", "replay_action_trace", "first divergent transition"],
        "docs/architecture/action_trace_text_codec_rev0071.md": ["MTGSim.ActionTrace.v17", "trigger_order", "MTGSim.ActionTrace.v1", "MTGSim.ActionTrace.v2", "MTGSim.ActionTrace.v3", "MTGSim.ActionTrace.v4", "MTGSim.ActionTrace.v5", "MTGSim.ActionTrace.v6", "MTGSim.ActionTrace.v7", "MTGSim.ActionTrace.v14", "MTGSim.ActionTrace.v16", "MTGSim.ActionTrace.v15", "MTGSim.ActionTrace.v14", "MTGSim.ActionTrace.v13", "MTGSim.ActionTrace.v12", "parse_action_trace", "LegalAction::label", "checkpoint serialization", "choice_page_found", "choice_page_schema", "choice_page_total_lower", "choice_page_remaining_lower", "choice_page_state", "choice_page_request_hash", "choice_page_hash", "choice_queue_schema", "choice_queue_location_schema", "choice_schema", "action_schema", "state_schema"],
        "docs/architecture/legal_action_schema_seal_rev0110.md": ["kLegalActionSchemaVersion", "action_schema", "ActionTrace.v13", "ActionHashMismatch", "schema drift"],
        "docs/architecture/choice_request_schema_seal_rev0111.md": ["kChoiceRequestSchemaVersion", "choice_schema", "ActionTrace.v14", "ChoiceRequestHashMismatch", "schema drift"],
        "docs/architecture/choice_request_queue_schema_seal_rev0112.md": ["kChoiceRequestQueueSchemaVersion", "choice_queue_schema", "ActionTrace.v15", "ChoiceQueueHashMismatch", "schema drift"],
        "docs/architecture/state_hash_schema_seal_rev0113.md": ["kStateCoreSchemaVersion", "state_schema", "ActionTrace.v16", "StateHashSchemaMismatch", "schema drift"],
        "docs/architecture/audit_refactor_notes.md": ["rev0071", "rev0110", "rev0111", "rev0112", "rev0113", "plain-text trace codec", "checkpoint serialization", "choice_queue_schema", "choice_schema", "action_schema", "state_schema", "state_schema"],
        "data/rules/coverage/rules_ledger.json": ["test_pending_trigger_order_choice_preserves_player_selected_sequence", "ActionTrace.v17", "trigger_order", "test_action_trace_text_roundtrip_replays_from_checkpoint", "ActionTraceParseResult", "rev0071", "test_action_trace_replay_detects_choice_validation_source_drift_without_mutation", "test_action_trace_replay_detects_choice_page_location_drift_without_mutation", "test_action_trace_replay_detects_choice_page_hash_drift_without_mutation", "test_action_trace_replay_detects_choice_page_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_page_count_drift_without_mutation", "test_action_trace_replay_detects_choice_page_context_drift_without_mutation", "test_action_trace_replay_detects_choice_queue_schema_drift_without_mutation", "test_action_trace_replay_detects_action_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_request_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_request_queue_schema_drift_without_mutation", "test_action_trace_replay_detects_state_hash_schema_drift_without_mutation", "choice_schema", "action_schema", "state_schema", "state_schema"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "action_trace.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "action_trace.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_state_checkpoint_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that persisted traces can be bound to a starting StateCore/Journals checkpoint seal."""
    probes = {
        "include/mtgsim/types.hpp": ["StateCheckpointSeal", "StateCheckpointParseResult", "CheckpointHashMismatch", "CheckpointSchemaMismatch", "kStateCheckpointSealSchemaVersion", "schema_version", "journal_entries"],
        "include/mtgsim/engine.hpp": ["make_state_checkpoint_seal", "verify_state_checkpoint_seal", "serialize_state_checkpoint_seal", "parse_state_checkpoint_seal", "replay_action_trace_from_checkpoint"],
        "src/engine.cpp": ["MTGSim.StateCheckpointSeal.v2", "MTGSim.StateCheckpointSeal.v1", "checkpoint_schema", "verify_state_checkpoint_seal", "checkpoint seal should contain exactly one data line", "CheckpointHashMismatch", "CheckpointSchemaMismatch"],
        "tests/cpp/test_engine.cpp": ["test_state_checkpoint_seal_roundtrip_and_guarded_replay", "test_state_checkpoint_seal_rejects_wrong_checkpoint_without_mutation", "test_state_checkpoint_seal_parser_rejects_duplicate_and_unknown_fields", "test_state_checkpoint_seal_schema_drift_rejected_without_mutation", "checkpoint_schema"],
        "docs/architecture/state_checkpoint_seal_rev0072.md": ["StateCheckpointSeal", "MTGSim.StateCheckpointSeal.v1", "not full state deserialization", "wrong starting state"],
        "docs/architecture/state_checkpoint_schema_seal_rev0115.md": ["StateCheckpointSeal.v2", "checkpoint_schema", "CheckpointSchemaMismatch", "duplicate read"],
        "docs/architecture/audit_refactor_notes.md": ["rev0072", "rev0115", "checkpoint seal", "checkpoint_schema", "wrong starting state"],
        "data/rules/coverage/rules_ledger.json": ["StateCheckpointSeal", "StateCheckpointSeal.v2", "test_state_checkpoint_seal_roundtrip_and_guarded_replay", "test_state_checkpoint_seal_schema_drift_rejected_without_mutation", "rev0072", "rev0115"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "state_checkpoint.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "state_checkpoint.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_state_core_snapshot_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that StateCore snapshots can reconstruct replay roots without pretending journal rows were serialized."""
    probes = {
        "include/mtgsim/types.hpp": ["StateCoreSnapshotParseResult", "source_checkpoint", "journal_trimmed"],
        "include/mtgsim/engine.hpp": ["serialize_state_core_snapshot", "parse_state_core_snapshot"],
        "src/engine.cpp": ["MTGSim.StateCoreSnapshot.v1", "write_game_core_snapshot", "read_game_core_snapshot", "snapshot.state_hash", "StateCore snapshot hash mismatch"],
        "tests/cpp/test_engine.cpp": ["test_state_core_snapshot_roundtrip_replays_trace_from_text", "test_state_core_snapshot_preserves_pending_prevention_and_continuous_effect_core", "test_state_core_snapshot_parser_rejects_hash_tampering"],
        "docs/architecture/state_core_snapshot_rev0073.md": ["StateCoreSnapshotParseResult", "MTGSim.StateCoreSnapshot.v1", "trimmed/empty journal", "replay root"],
        "docs/architecture/audit_refactor_notes.md": ["rev0073", "StateCore snapshot", "trimmed/empty journal"],
        "data/rules/coverage/rules_ledger.json": ["StateCoreSnapshotParseResult", "test_state_core_snapshot_roundtrip_replays_trace_from_text", "rev0073"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "state_core_snapshot.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "state_core_snapshot.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_cli_replay_artifact_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that snapshot+trace replay is exposed as an executable disk artifact path."""
    probes = {
        "apps/mtgsim_cli.cpp": ["--write-demo-replay", "--verify-replay", "--artifact-roundtrip", "parse_state_core_snapshot", "parse_action_trace", "replay_action_trace"],
        "CMakeLists.txt": ["mtgsim_cli_replay_artifact_roundtrip", "--artifact-roundtrip", "cli;replay;artifacts"],
        "README.md": ["--write-demo-replay", "--verify-replay", "StateCoreSnapshot.v1", "ActionTrace.v1"],
        "ARTIFACT_REPORT.md": ["CLI replay artifact", "mtgsim_cli_replay_artifact_roundtrip"],
        "docs/architecture/cli_replay_artifact_path_rev0075.md": ["--write-demo-replay", "--verify-replay", "StateCoreSnapshot.v1", "ActionTrace.v1"],
        "docs/architecture/audit_refactor_notes.md": ["rev0075", "CLI replay artifact", "disk-bound replay"],
        "data/rules/coverage/rules_ledger.json": ["rev0075", "CLI replay artifact", "mtgsim_cli_replay_artifact_roundtrip"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "cli_replay.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "cli_replay.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_replay_bundle_manifest_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that replay bundles have a manifest binding snapshot, trace, checkpoint, and final state."""
    probes = {
        "include/mtgsim/types.hpp": ["ReplayArtifactManifest", "kReplayArtifactManifestSchemaVersion", "ReplayArtifactVerifyResult", "ManifestSchemaMismatch", "PaidActionJournalMissing", "paid_action_journal_attached", "bundle_hash"],
        "include/mtgsim/engine.hpp": ["make_replay_artifact_manifest", "make_replay_artifact_manifest_with_paid_action_journal", "parse_replay_artifact_manifest", "verify_replay_artifact_bundle", "verify_replay_artifact_bundle_with_paid_action_journal", "replay_artifact_text_hash"],
        "src/engine.cpp": ["MTGSim.ReplayArtifactManifest.v3", "MTGSim.ReplayArtifactManifest.v2", "manifest_schema", "paid_action_journal_text_hash", "PaidActionJournalTextHashMismatch", "manifest schema mismatch", "snapshot text hash mismatch", "manifest action_count does not match parsed trace", "final StateCore hash mismatch"],
        "apps/mtgsim_cli.cpp": ["--write-demo-replay-bundle", "--verify-replay-bundle", "--artifact-bundle-roundtrip", "--paid-replay-bundle-roundtrip", "manifest_schema", "verify_replay_artifact_bundle", "verify_replay_artifact_bundle_with_paid_action_journal"],
        "CMakeLists.txt": ["mtgsim_cli_replay_bundle_roundtrip", "mtgsim_cli_paid_replay_bundle_roundtrip", "--artifact-bundle-roundtrip", "--paid-replay-bundle-roundtrip", "cli;replay;artifacts;manifest"],
        "tests/cpp/test_engine.cpp": ["test_replay_artifact_manifest_roundtrip_verifies_snapshot_trace_bundle", "test_replay_artifact_manifest_binds_paid_action_transaction_journal", "test_replay_artifact_manifest_rejects_snapshot_tampering_before_replay", "test_replay_artifact_manifest_parser_rejects_manifest_tampering", "test_replay_artifact_manifest_schema_seal_rejects_schema_drift_before_replay"],
        "README.md": ["ReplayArtifactManifest.v3", "paid-action journal attachment", "ReplayArtifactManifest.v2", "manifest_schema", "--artifact-bundle-roundtrip", "manifest-bound"],
        "ARTIFACT_REPORT.md": ["ReplayArtifactManifest.v3", "paid-action journal attachment", "ReplayArtifactManifest.v2", "manifest schema", "mtgsim_cli_replay_bundle_roundtrip", "mtgsim_cli_paid_replay_bundle_roundtrip"],
        "docs/architecture/replay_artifact_manifest_rev0076.md": ["ReplayArtifactManifest.v1", "bundle_hash", "snapshot text hash", "final StateCore hash"],
        "docs/architecture/replay_artifact_manifest_schema_seal_rev0114.md": ["ReplayArtifactManifest.v2", "manifest_schema", "ManifestSchemaMismatch", "bundle_hash"],
        "docs/architecture/audit_refactor_notes.md": ["rev0114", "rev0170", "ReplayArtifactManifest", "paid-action journal attachment", "artifact trust"],
        "data/rules/coverage/rules_ledger.json": ["rev0114", "rev0170", "ReplayArtifactManifest.v2", "ReplayArtifactManifest.v3", "test_replay_artifact_manifest_schema_seal_rejects_schema_drift_before_replay", "test_replay_artifact_manifest_binds_paid_action_transaction_journal", "mtgsim_cli_replay_bundle_roundtrip", "mtgsim_cli_paid_replay_bundle_roundtrip"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "replay_bundle_manifest.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "replay_bundle_manifest.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_replay_bundle_diagnostics_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that manifest-bound replay failures surface typed diagnostics and an inspectable CLI path."""
    probes = {
        "include/mtgsim/types.hpp": ["ReplayArtifactFailureKind", "expected_checkpoint_state_hash", "actual_action_count", "FinalStateHashMismatch"],
        "src/engine.cpp": ["ReplayArtifactFailureKind::CheckpointSealMismatch", "ReplayArtifactFailureKind::ActionCountMismatch", "ReplayArtifactFailureKind::FinalStateHashMismatch"],
        "apps/mtgsim_cli.cpp": ["--inspect-replay-bundle", "--artifact-bundle-inspect-roundtrip", "replay_artifact_failure_name", "verification_ok="],
        "CMakeLists.txt": ["mtgsim_cli_replay_bundle_inspect_roundtrip", "--artifact-bundle-inspect-roundtrip", "diagnostics"],
        "tests/cpp/test_engine.cpp": ["test_replay_artifact_manifest_diagnostics_identify_checkpoint_and_action_mismatches", "test_replay_artifact_manifest_diagnostics_identify_final_hash_mismatch", "ReplayArtifactFailureKind"],
        "README.md": ["--inspect-replay-bundle", "diagnostic", "ReplayArtifactFailureKind"],
        "ARTIFACT_REPORT.md": ["ReplayArtifactFailureKind", "mtgsim_cli_replay_bundle_inspect_roundtrip", "diagnostics"],
        "docs/architecture/replay_bundle_diagnostics_rev0077.md": ["ReplayArtifactFailureKind", "--inspect-replay-bundle", "action-count mismatch", "final StateCore"],
        "docs/architecture/audit_refactor_notes.md": ["rev0077", "replay bundle diagnostics", "inspect"],
        "data/rules/coverage/rules_ledger.json": ["117-replay-bundle-diagnostics", "rev0077", "mtgsim_cli_replay_bundle_inspect_roundtrip"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "replay_bundle_diagnostics.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "replay_bundle_diagnostics.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_replay_bundle_prefix_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that replay-bundle failures can emit a manifest-bound longest-known-good prefix."""
    probes = {
        "include/mtgsim/types.hpp": ["ReplayArtifactPrefixResult", "prefix_action_count", "next_bad_step", "prefix_manifest_text"],
        "include/mtgsim/engine.hpp": ["make_replay_artifact_prefix_bundle", "ReplayArtifactPrefixResult"],
        "src/engine.cpp": ["make_replay_artifact_prefix_bundle", "longest known-good", "TraceReplayFailed", "FinalStateHashMismatch"],
        "apps/mtgsim_cli.cpp": ["--write-replay-prefix", "--artifact-bundle-prefix-roundtrip", "prefix_actions=", "next_bad_step="],
        "CMakeLists.txt": ["mtgsim_cli_replay_bundle_prefix_roundtrip", "--artifact-bundle-prefix-roundtrip", "prefix"],
        "tests/cpp/test_engine.cpp": ["test_replay_artifact_prefix_bundle_localizes_first_bad_action", "test_replay_artifact_prefix_bundle_normalizes_final_hash_mismatch", "ReplayArtifactPrefixResult"],
        "README.md": ["--write-replay-prefix", "longest known-good prefix", "mtgsim_cli_replay_bundle_prefix_roundtrip"],
        "ARTIFACT_REPORT.md": ["ReplayArtifactPrefixResult", "mtgsim_cli_replay_bundle_prefix_roundtrip", "longest known-good prefix"],
        "docs/architecture/replay_bundle_prefix_localizer_rev0078.md": ["ReplayArtifactPrefixResult", "--write-replay-prefix", "longest known-good prefix", "next_bad_step"],
        "docs/architecture/audit_refactor_notes.md": ["rev0078", "replay prefix", "longest known-good prefix"],
        "data/rules/coverage/rules_ledger.json": ["117-replay-prefix-localizer", "rev0078", "mtgsim_cli_replay_bundle_prefix_roundtrip"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "replay_bundle_prefix.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "replay_bundle_prefix.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_replay_bundle_resume_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that replay-bundle failures can emit a fresh snapshot plus suffix resume probe."""
    probes = {
        "include/mtgsim/types.hpp": ["ReplayArtifactResumeResult", "resume_snapshot_text", "suffix_manifest_text", "suffix_verify"],
        "include/mtgsim/engine.hpp": ["make_replay_artifact_resume_probe", "ReplayArtifactResumeResult"],
        "src/engine.cpp": ["make_replay_artifact_resume_probe", "resume probe", "suffix_trace_text", "make_branch_state"],
        "apps/mtgsim_cli.cpp": ["--write-replay-resume-probe", "--artifact-bundle-resume-roundtrip", "resume_state_hash=", "suffix_replay_mismatch_index="],
        "CMakeLists.txt": ["mtgsim_cli_replay_bundle_resume_roundtrip", "--artifact-bundle-resume-roundtrip", "resume"],
        "tests/cpp/test_engine.cpp": ["test_replay_artifact_resume_probe_rebases_first_bad_action_to_suffix_step_one", "test_replay_artifact_resume_probe_verified_bundle_writes_empty_suffix", "ReplayArtifactResumeResult"],
        "README.md": ["--write-replay-resume-probe", "resume probe", "mtgsim_cli_replay_bundle_resume_roundtrip"],
        "ARTIFACT_REPORT.md": ["ReplayArtifactResumeResult", "mtgsim_cli_replay_bundle_resume_roundtrip", "resume snapshot"],
        "docs/architecture/replay_resume_probe_rev0079.md": ["ReplayArtifactResumeResult", "--write-replay-resume-probe", "suffix step one", "StateCoreSnapshot.v1"],
        "docs/architecture/audit_refactor_notes.md": ["rev0079", "ReplayArtifactResumeResult", "resume artifact"],
        "data/rules/coverage/rules_ledger.json": ["117-replay-resume-probe", "rev0079", "mtgsim_cli_replay_bundle_resume_roundtrip"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "replay_bundle_resume.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "replay_bundle_resume.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_discard_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that discard choices stay wired to typed records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["DiscardRecord", "DiscardRecordKind", "discard_record_index", "discard_records", "cleanup_hand_size", "used_zone_change_pipeline"],
        "include/mtgsim/engine.hpp": ["discard_card", "discard_record_count", "latest_discard_record", "discard_down_to_max_hand_size"],
        "src/types.cpp": ["DiscardRecordKind", "explicit_choice", "cleanup_hand_size", "discard"],
        "src/engine.cpp": ["record_discard_record", "discard_card_for_reason", "EventRecordKind::Discard", "discard_records", "discard_cleanup"],
        "src/validation.cpp": ["event_record.invalid_discard_link", "discard_record.invalid_zone_change_link", "discard_record.event_record_link_count", "discard_record.zone_pipeline_not_used"],
        "tests/cpp/test_engine.cpp": ["test_discard_record_links_explicit_choice_and_validation", "latest_discard_record", "EventRecordKind::Discard", "DiscardRecordKind::CleanupHandSize"],
        "docs/architecture/engine_design.md": ["DiscardRecord", "discard_records", "discard choices"],
        "docs/architecture/audit_refactor_notes.md": ["rev0066", "DiscardRecord", "cleanup discard"],
        "data/rules/coverage/rules_ledger.json": ["test_discard_record_links_explicit_choice_and_validation", "DiscardRecord", "701.9", "514"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "discard_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "discard_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_trigger_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that structured trigger records stay wired through queueing, stack placement, validation, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["TriggerRecord", "trigger_records", "put_on_stack_sequence", "trigger_record_index", "trigger_order", "chosen_targets", "choice_target_set_hash", "target_choice_recorded", "no_legal_choices", "stack_resolution_record_index", "resolved_sequence", "resolution_outcome"],
        "include/mtgsim/engine.hpp": ["trigger_record_count", "latest_trigger_record", "target_choice_set_hash"],
        "src/engine.cpp": ["TriggerRecord", "trigger_record_index", "put_on_stack_sequence", "stack_order", "valid_pending_trigger_order", "trigger_order_label", "move_object_with_precomputed_ltb_snapshots", "pre_creature_sba_ltb_snapshots", "seal_trigger_target_choice", "enumerate_legal_trigger_target_sets", "trigger_record_index_for_stack_object", "resolved_effect_payload_applied"],
        "src/validation.cpp": ["trigger_record.invalid_put_on_stack_sequence", "trigger_record.missing_source_zone_change_index", "trigger.missing_record", "action_receipt.trigger_order_stack_mismatch", "trigger_record.choice_target_set_hash_mismatch", "trigger_record.stacked_without_choice_record", "trigger_record.chosen_target_count_mismatch", "trigger_record.resolution_backlink_mismatch", "stack_resolution_record.missing_trigger_record_link", "event_record.stack_resolution_trigger_link_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_trigger_record_links_queue_lki_and_stack_object", "latest_trigger_record", "trigger_record.invalid_put_on_stack_sequence", "test_pending_trigger_order_choice_preserves_player_selected_sequence", "test_simultaneous_sba_dies_triggers_share_pre_batch_lki_snapshot", "test_trigger_record_choice_seal_validation_rejects_tampered_payload", "test_trigger_resolution_backlink_seals_stack_resolution_record", "trigger_order="],
        "docs/architecture/triggers_and_events.md": ["TriggerRecord", "typed trigger", "put_on_stack_sequence", "rev0172 pending trigger order choice", "rev0175 simultaneous SBA look-back batch", "rev0187 trigger target-choice seal", "rev0188 trigger resolution backlink seal", "trigger_order"],
        "docs/architecture/audit_refactor_notes.md": ["rev0048", "rev0172", "rev0175", "rev0187", "rev0188", "TriggerRecord", "trigger_records", "trigger_order", "pre_creature_sba_ltb_snapshots", "choice_target_set_hash", "stack_resolution_record_index"],
        "data/rules/coverage/rules_ledger.json": ["test_trigger_record_links_queue_lki_and_stack_object", "TriggerRecord", "test_pending_trigger_order_choice_preserves_player_selected_sequence", "test_simultaneous_sba_dies_triggers_share_pre_batch_lki_snapshot", "test_trigger_record_choice_seal_validation_rejects_tampered_payload", "test_trigger_resolution_backlink_seals_stack_resolution_record", "603.3d", "608.2b", "608.2n", "603.10", "704.3", "101.4"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "trigger_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "trigger_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_event_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the unified typed EventRecord spine stays wired to emission, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["EventRecordKind", "EventRecord", "event_records", "zone_change_record_index", "damage_record_index", "damage_prevention_record_index", "life_change_record_index", "mana_change_record_index", "counter_change_record_index", "discard_record_index", "trigger_record_index", "stack_placement_record_index", "stack_resolution_record_index", "priority_transition_record_index", "draw_record_index", "mulligan_record_index", "mulligan_keep_record_index"],
        "include/mtgsim/engine.hpp": ["event_record_count", "latest_event_record"],
        "src/engine.cpp": ["EventRecordLinks", "record_event_with_links", "EventRecordKind::ZoneChange", "EventRecordKind::Damage", "EventRecordKind::DamagePrevention", "EventRecordKind::LifeChange", "EventRecordKind::ManaChange", "EventRecordKind::CounterChange", "EventRecordKind::Discard", "EventRecordKind::TriggerQueued", "EventRecordKind::TriggerPutOnStack", "EventRecordKind::StackPlacement", "EventRecordKind::StackResolution", "EventRecordKind::PriorityTransition", "EventRecordKind::CombatDeclaration", "EventRecordKind::CombatDamageAssignment", "EventRecordKind::Draw", "EventRecordKind::Mulligan", "EventRecordKind::MulliganKeep"],
        "src/validation.cpp": ["event_record.count_mismatch", "event_record.invalid_zone_change_link", "event_record.invalid_damage_link", "event_record.invalid_damage_prevention_link", "event_record.invalid_life_change_link", "event_record.invalid_mana_change_link", "event_record.invalid_counter_change_link", "event_record.invalid_discard_link", "event_record.invalid_trigger_link", "event_record.invalid_stack_placement_link", "event_record.invalid_stack_resolution_link", "event_record.invalid_priority_transition_link", "event_record.invalid_combat_declaration_link", "event_record.invalid_combat_damage_assignment_link", "event_record.invalid_draw_link", "event_record.invalid_mulligan_link", "event_record.invalid_mulligan_keep_link", "zone_change_record.event_record_link_count", "damage_record.event_record_link_count", "damage_prevention_record.event_record_link_count", "life_change_record.event_record_link_count", "mana_change_record.event_record_link_count", "counter_change_record.event_record_link_count", "discard_record.event_record_link_count", "draw_record.event_record_link_count", "mulligan_record.event_record_link_count", "mulligan_keep_record.event_record_link_count"],
        "tests/cpp/test_engine.cpp": ["test_event_record_spine_links_zone_damage_and_trigger_records", "latest_event_record", "EventRecordKind::Damage", "EventRecordKind::DamagePrevention", "EventRecordKind::LifeChange", "EventRecordKind::ManaChange", "EventRecordKind::CounterChange", "EventRecordKind::Discard", "event_record.invalid_trigger_link"],
        "docs/architecture/triggers_and_events.md": ["EventRecord", "typed event spine", "TriggerRecord"],
        "docs/architecture/audit_refactor_notes.md": ["rev0049", "EventRecord", "event_records"],
        "data/rules/coverage/rules_ledger.json": ["test_event_record_spine_links_zone_damage_and_trigger_records", "EventRecord", "StackResolutionRecord"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "event_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "event_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_draw_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed draw records stay wired through draw_card, move_object, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["DrawRecord", "DrawRecordOutcome", "draw_record_index", "draw_records", "Draw"],
        "include/mtgsim/engine.hpp": ["draw_record_count", "latest_draw_record"],
        "src/types.cpp": ["DrawRecordOutcome", "drew_card", "empty_library"],
        "src/engine.cpp": ["DrawRecord", "record_draw_record", "EventRecordKind::Draw", "move_object(game, top, player_id, Zone::Hand)"],
        "src/validation.cpp": ["draw_record.invalid_zone_change_link", "event_record.invalid_draw_link", "draw_record.empty_attempt_count_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_draw_record_uses_zone_change_pipeline_and_empty_library_record", "latest_draw_record", "EventRecordKind::Draw"],
        "docs/architecture/engine_design.md": ["DrawRecord", "draw_records", "library->hand"],
        "docs/architecture/audit_refactor_notes.md": ["rev0057", "DrawRecord", "draw_records"],
        "data/rules/coverage/rules_ledger.json": ["test_draw_record_uses_zone_change_pipeline_and_empty_library_record", "DrawRecord", "121"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "draw_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "draw_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_mulligan_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed mulligan records stay wired through hand return, shuffle, draw, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["MulliganRecord", "mulligan_record_index", "mulligan_records", "mulligans_taken", "Mulligan"],
        "include/mtgsim/engine.hpp": ["take_mulligan", "mulligan_record_count", "latest_mulligan_record"],
        "src/types.cpp": ["EventRecordKind::Mulligan", "mulligan"],
        "src/engine.cpp": ["MulliganRecord", "record_mulligan_record", "take_mulligan", "move_object(game, *it, player_id, Zone::Library)", "draw_card(game, player_id)", "EventRecordKind::Mulligan"],
        "src/validation.cpp": ["mulligan_record.hand_not_cleared", "event_record.invalid_mulligan_link", "mulligan_record.invalid_return_zone_change_range", "mulligan_record.draw_attempt_count_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_mulligan_record_returns_hand_shuffles_and_redraws_through_pipelines", "latest_mulligan_record", "EventRecordKind::Mulligan"],
        "docs/architecture/engine_design.md": ["MulliganRecord", "mulligan_records", "hand-to-library"],
        "docs/architecture/audit_refactor_notes.md": ["rev0058", "MulliganRecord", "mulligan_records"],
        "data/rules/coverage/rules_ledger.json": ["test_mulligan_record_returns_hand_shuffles_and_redraws_through_pipelines", "MulliganRecord", "103"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mulligan_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mulligan_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_mulligan_keep_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that London mulligan keep/bottom records stay wired through choices, zone movement, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["MulliganKeepRecord", "mulligan_keep_record_index", "mulligan_keep_records", "MulliganKeep", "bottomed_cards"],
        "include/mtgsim/engine.hpp": ["keep_mulligan_hand", "mulligan_keep_record_count", "latest_mulligan_keep_record"],
        "src/types.cpp": ["EventRecordKind::MulliganKeep", "mulligan_keep"],
        "src/engine.cpp": ["MulliganKeepRecord", "record_mulligan_keep_record", "keep_mulligan_hand", "place_library_object_on_bottom", "EventRecordKind::MulliganKeep"],
        "src/validation.cpp": ["mulligan_keep_record.invalid_bottom_zone_change_range", "event_record.invalid_mulligan_keep_link", "mulligan_keep_record.not_placed_on_bottom"],
        "tests/cpp/test_engine.cpp": ["test_mulligan_keep_record_bottoms_choices_through_zone_pipeline", "latest_mulligan_keep_record", "EventRecordKind::MulliganKeep"],
        "docs/architecture/engine_design.md": ["MulliganKeepRecord", "mulligan_keep_records", "bottoming"],
        "docs/architecture/audit_refactor_notes.md": ["rev0059", "MulliganKeepRecord", "mulligan_keep_records"],
        "docs/roadmap.md": ["rev0059", "MulliganKeepRecord", "bottoming cards after keeping"],
        "data/rules/coverage/rules_ledger.json": ["test_mulligan_keep_record_bottoms_choices_through_zone_pipeline", "MulliganKeepRecord", "103.5"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mulligan_keep_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mulligan_keep_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_stack_placement_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed stack-placement records stay wired through casting/activation, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["StackPlacementRecord", "StackPlacementKind", "stack_placement_record_index", "stack_placement_records", "StackPlacement"],
        "include/mtgsim/engine.hpp": ["stack_placement_record_count", "latest_stack_placement_record"],
        "src/types.cpp": ["StackPlacementKind", "stack_placement", "activated_ability"],
        "src/engine.cpp": ["StackPlacementRecord", "record_stack_placement", "EventRecordKind::StackPlacement", "move_spell_card_to_stack_for_cast", "priority_player = caster"],
        "src/validation.cpp": ["stack_placement_record.priority_after_not_controller", "event_record.invalid_stack_placement_link", "stack_placement_record.invalid_stack_enter_zone_change"],
        "tests/cpp/test_engine.cpp": ["test_stack_placement_record_retains_priority_and_links_spell_and_ability", "latest_stack_placement_record", "EventRecordKind::StackPlacement"],
        "docs/architecture/activated_abilities.md": ["StackPlacementRecord", "priority_after", "tap_cost_paid"],
        "docs/architecture/audit_refactor_notes.md": ["rev0055", "StackPlacementRecord", "stack_placement_records"],
        "data/rules/coverage/rules_ledger.json": ["test_stack_placement_record_retains_priority_and_links_spell_and_ability", "StackPlacementRecord", "117.3c"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "stack_placement_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "stack_placement_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_stack_resolution_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed stack-resolution records stay wired through resolution, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["StackResolutionRecord", "StackResolutionOutcome", "TargetResolutionCheckRecord", "TargetLegalityFailureKind", "target_resolution_checks", "trigger_record_index", "stack_resolution_record_index", "stack_resolution_records"],
        "include/mtgsim/engine.hpp": ["stack_resolution_record_count", "latest_stack_resolution_record"],
        "src/types.cpp": ["StackResolutionOutcome", "TargetLegalityFailureKind", "object_zone_change_mismatch", "no_legal_targets", "aura_attach_failed"],
        "src/engine.cpp": ["StackResolutionRecord", "make_target_resolution_checks", "legal_targets_on_resolution", "trigger_record_index_for_stack_object", "TargetLegalityFailureKind::ObjectZoneChangeMismatch", "stack_resolution_recorded", "EventRecordKind::StackResolution", "resolve_aura_no_legal_enchant"],
        "src/validation.cpp": ["stack_resolution_record.invalid_leave_zone_change", "event_record.invalid_stack_resolution_link", "stack_resolution_record.required_target_failed_mismatch", "stack_resolution_record.target_check_count_mismatch", "stack_resolution_record.legal_target_check_count_mismatch", "stack_resolution_record.missing_trigger_record_link", "stack_resolution_record.trigger_record_backlink_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_stack_resolution_record_blocks_aura_target_failure_without_battlefield_transit", "test_trigger_resolution_backlink_seals_stack_resolution_record", "TargetLegalityFailureKind::ObjectZoneChangeMismatch", "legal_target_check_count_mismatch", "StackResolutionOutcome::NoLegalTargets", "event_record.invalid_stack_resolution_link"],
        "docs/architecture/effects_and_targets.md": ["StackResolutionRecord", "TargetResolutionCheckRecord", "CR 608.2b", "resolve_aura_no_legal_enchant"],
        "docs/architecture/audit_refactor_notes.md": ["rev0173", "rev0188", "TargetResolutionCheckRecord", "StackResolutionRecord", "stack_resolution_records", "stack_resolution_record_index"],
        "data/rules/coverage/rules_ledger.json": ["test_stack_resolution_record_blocks_aura_target_failure_without_battlefield_transit", "test_trigger_resolution_backlink_seals_stack_resolution_record", "TargetResolutionCheckRecord", "StackResolutionRecord", "608.2b", "608.2n"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "stack_resolution_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "stack_resolution_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_priority_transition_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed priority-transition records stay wired through pass-priority, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["PriorityTransitionRecord", "PriorityTransitionOutcome", "priority_transition_record_index", "priority_transition_records"],
        "include/mtgsim/engine.hpp": ["priority_transition_record_count", "latest_priority_transition_record"],
        "src/types.cpp": ["PriorityTransitionOutcome", "priority_advanced", "stack_resolved", "step_advanced"],
        "src/engine.cpp": ["PriorityTransitionRecord", "record_priority_transition", "EventRecordKind::PriorityTransition", "pass_priority", "PriorityTransitionOutcome::StackResolved"],
        "src/validation.cpp": ["priority_transition_record.after_pass_count_mismatch", "event_record.invalid_priority_transition_link", "priority_transition_record.invalid_stack_resolution_link"],
        "tests/cpp/test_engine.cpp": ["test_priority_transition_record_links_pass_resolution_and_step_advance", "latest_priority_transition_record", "PriorityTransitionOutcome::StackResolved"],
        "docs/architecture/timing_land_play_and_flash.md": ["PriorityTransitionRecord", "priority_transition_records", "StackResolved"],
        "docs/architecture/audit_refactor_notes.md": ["rev0056", "PriorityTransitionRecord", "priority_transition_records"],
        "data/rules/coverage/rules_ledger.json": ["test_priority_transition_record_links_pass_resolution_and_step_advance", "PriorityTransitionRecord", "117.3c"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "priority_transition_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "priority_transition_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_state_based_action_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed state-based action records stay wired through SBA execution, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["StateBasedActionRecord", "StateBasedActionKind", "state_based_action_record_index", "state_based_action_records", "check_index", "pass_candidate_count"],
        "include/mtgsim/engine.hpp": ["state_based_action_record_count", "latest_state_based_action_record"],
        "src/types.cpp": ["StateBasedActionKind", "creature_damage_destroy", "token_cease"],
        "src/engine.cpp": ["StateBasedActionRecord", "record_state_based_action", "EventRecordKind::StateBasedAction", "link_state_based_action_to_zone_change", "pass_candidate_count", "clear_attachment_links_for_zone_change"],
        "src/validation.cpp": ["state_based_action_record.damage_destroy_no_result", "event_record.invalid_state_based_action_link", "state_based_action_record.regeneration_not_consumed", "state_based_action_record.zero_check_index", "state_based_action_record.pass_index_regressed"],
        "tests/cpp/test_engine.cpp": ["test_state_based_action_record_links_damage_destroy_and_regeneration", "test_sba_pass_barrier_delays_aura_cleanup_from_creature_death", "latest_state_based_action_record", "EventRecordKind::StateBasedAction", "check_index"],
        "docs/architecture/destroy_and_regeneration.md": ["StateBasedActionRecord", "regeneration_applied", "CreatureDamageDestroy"],
        "docs/architecture/sba_pass_barrier_rev0185.md": ["check_index", "pass_index", "pass_candidate_count", "clear_attachment_links_for_zone_change"],
        "docs/architecture/audit_refactor_notes.md": ["rev0052", "rev0185", "StateBasedActionRecord", "state_based_action_records", "check_index"],
        "data/rules/coverage/rules_ledger.json": ["test_state_based_action_record_links_damage_destroy_and_regeneration", "test_sba_pass_barrier_delays_aura_cleanup_from_creature_death", "StateBasedActionRecord", "704.3", "704.5g"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "state_based_action_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "state_based_action_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_combat_declaration_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed combat declaration records stay wired through declarations, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["CombatDeclarationRecord", "CombatDeclarationKind", "combat_declaration_record_index", "combat_declaration_records", "CombatDeclaration"],
        "include/mtgsim/engine.hpp": ["combat_declaration_record_count", "latest_combat_declaration_record"],
        "src/types.cpp": ["CombatDeclaration", "combat_declaration", "CombatDeclarationKind"],
        "src/engine.cpp": ["CombatDeclarationRecord", "record_combat_declaration", "EventRecordKind::CombatDeclaration", "blocker_count_for_attacker"],
        "src/validation.cpp": ["combat_declaration_record.menace_not_satisfied", "event_record.invalid_combat_declaration_link", "combat_declaration_record.vigilance_tap_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_combat_declaration_record_links_vigilance_and_menace_batch_context", "latest_combat_declaration_record", "EventRecordKind::CombatDeclaration"],
        "docs/architecture/combat_scaffold.md": ["CombatDeclarationRecord", "menace_satisfied", "vigilance"],
        "docs/architecture/audit_refactor_notes.md": ["rev0054", "CombatDeclarationRecord", "combat_declaration_records"],
        "data/rules/coverage/rules_ledger.json": ["test_combat_declaration_record_links_vigilance_and_menace_batch_context", "CombatDeclarationRecord", "509"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "combat_declaration_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "combat_declaration_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_combat_damage_assignment_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that typed combat-damage assignment records stay wired through combat, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": ["CombatDamageAssignmentRecord", "combat_damage_assignment_record_index", "combat_damage_assignment_records", "CombatDamageAssignment"],
        "include/mtgsim/engine.hpp": ["combat_damage_assignment_record_count", "latest_combat_damage_assignment_record"],
        "src/types.cpp": ["CombatDamageAssignment", "combat_damage_assignment"],
        "src/engine.cpp": ["CombatDamageAssignmentRecord", "record_combat_damage_assignment", "EventRecordKind::CombatDamageAssignment", "excess_trample"],
        "src/validation.cpp": ["combat_damage_assignment_record.invalid_damage_link", "event_record.invalid_combat_damage_assignment_link", "combat_damage_assignment_record.excess_without_trample"],
        "tests/cpp/test_engine.cpp": ["test_combat_damage_assignment_record_links_trample_batches_to_damage_records", "latest_combat_damage_assignment_record", "EventRecordKind::CombatDamageAssignment"],
        "docs/architecture/combat_scaffold.md": ["CombatDamageAssignmentRecord", "excess_trample", "DamageRecord"],
        "docs/architecture/audit_refactor_notes.md": ["rev0053", "CombatDamageAssignmentRecord", "combat_damage_assignment_records"],
        "data/rules/coverage/rules_ledger.json": ["test_combat_damage_assignment_record_links_trample_batches_to_damage_records", "CombatDamageAssignmentRecord", "510"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "combat_damage_assignment_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "combat_damage_assignment_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_destroy_regeneration_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the destroy/regeneration scaffold is wired through core, tests, scenarios, CMake, registry, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "destroy_spell_permanent.mtgscn",
        root / "tests" / "scenarios" / "regeneration_replaces_destroy.mtgscn",
        root / "tests" / "scenarios" / "regeneration_sba_limits.mtgscn",
        root / "docs" / "architecture" / "destroy_and_regeneration.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "destroy_regen.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["DestroyPermanent", "RegeneratePermanent", "regeneration_shields"],
        "include/mtgsim/engine.hpp": ["add_regeneration_shield", "regeneration_shield_count", "destroy_permanent"],
        "src/engine.cpp": ["EffectKind::DestroyPermanent", "EffectKind::RegeneratePermanent", "regenerated", "regeneration_shields_expired", "sba_creature_graveyard"],
        "src/validation.cpp": ["object.regeneration_outside_battlefield"],
        "apps/mtgsim_scenario.cpp": ["effect=", "regenerate", "destroy", "expect_regeneration"],
        "apps/mtgsim_fuzz.cpp": ["DestroyPermanent", "RegeneratePermanent", "Fuzz Doom", "Fuzz Mend"],
        "tests/cpp/test_engine.cpp": ["test_destroy_spell_moves_target_permanent_to_owner_graveyard", "test_regeneration_spell_creates_shield_that_replaces_destroy", "test_regeneration_saves_lethal_damage_sba_but_not_zero_toughness", "test_indestructible_ignores_destroy_permanent"],
        "CMakeLists.txt": ["mtgsim_scenario_destroy_regen"],
        "src/rules.cpp": ["core.destroy", "701.8", "701.19"],
        "data/cards/sample_cards.json": ["Sample Ruin Spell", "Sample Renewal Spell", "destroy", "regenerate"],
        "tools/card_db.py": ["effect_kind", "effect_amount", "target_mask"],
        "data/rules/coverage/rules_ledger.json": ["\"701.8\"", "\"701.19\"", "\"704.5f\"", "\"704.5g\"", "\"704.5h\"", "test_regeneration_spell_creates_shield_that_replaces_destroy"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "destroy_regen.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "destroy_regen.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }



def audit_counter_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the counter scaffold is wired through core, scenarios, CMake, tests, registry, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "counter_spell_growth.mtgscn",
        root / "tests" / "scenarios" / "counter_sba_cancel.mtgscn",
        root / "docs" / "architecture" / "counters_and_power_toughness.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "counters.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["CounterKind", "CounterSet", "AddCounters", "effect_counter_kind"],
        "include/mtgsim/engine.hpp": ["add_counter_to_object", "effective_power", "effective_toughness"],
        "src/engine.cpp": ["cancel_opposing_power_toughness_counters", "clear_counters_for_zone_change", "EffectKind::AddCounters"],
        "src/validation.cpp": ["object.counters_outside_battlefield"],
        "apps/mtgsim_scenario.cpp": ["add_counter", "expect_counter", "expect_effective_pt", "counter effect option"],
        "tests/cpp/test_engine.cpp": ["test_counter_spell_adds_counters_to_target_on_resolution", "test_opposing_power_toughness_counters_cancel_as_sba"],
        "CMakeLists.txt": ["mtgsim_scenario_counter"],
        "src/rules.cpp": ["core.counters", "122"],
        "data/rules/coverage/rules_ledger.json": ["\"122\"", "test_counter_spell_adds_counters_to_target_on_resolution"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "counters.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "counters.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }




def audit_keyword_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the keyword/static-ability scaffold is wired through core, scenarios, CMake, cards, registry, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "keyword_flying_reach.mtgscn",
        root / "tests" / "scenarios" / "keyword_lifelink_vigilance.mtgscn",
        root / "tests" / "scenarios" / "keyword_deathtouch_sba.mtgscn",
        root / "tests" / "scenarios" / "keyword_first_double_strike.mtgscn",
        root / "tests" / "scenarios" / "keyword_double_strike_unblocked.mtgscn",
        root / "tests" / "scenarios" / "keyword_trample_excess.mtgscn",
        root / "tests" / "scenarios" / "keyword_indestructible_damage.mtgscn",
        root / "tests" / "scenarios" / "keyword_haste_summoning_sickness.mtgscn",
        root / "tests" / "scenarios" / "keyword_defender_no_attack.mtgscn",
        root / "tests" / "scenarios" / "keyword_hexproof_shroud_targeting.mtgscn",
        root / "tests" / "scenarios" / "keyword_protection_from_red.mtgscn",
        root / "tests" / "scenarios" / "keyword_menace_batch_block.mtgscn",
        root / "docs" / "architecture" / "keyword_static_abilities.md",
        root / "docs" / "architecture" / "protection_menace_and_colors.md",
        root / "docs" / "architecture" / "combat_requirements_solver_rev0085.md",
        root / "docs" / "architecture" / "combat_requirement_maximizer_rev0086.md",
        root / "docs" / "architecture" / "combat_alone_restrictions_rev0087.md",
        root / "docs" / "architecture" / "combat_must_be_blocked_rev0088.md",
        root / "docs" / "architecture" / "combat_all_able_blockers_rev0089.md",
        root / "docs" / "architecture" / "combat_mana_costs_rev0090.md",
        root / "docs" / "architecture" / "combat_declaration_priority_gates_rev0091.md",
        root / "docs" / "architecture" / "combat_damage_order_choice_rev0092.md",
        root / "docs" / "architecture" / "combat_can_block_only_flying_rev0094.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "keywords.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["KeywordAbilityMask", "AbilityFlying", "AbilityReach", "AbilityDeathtouch", "AbilityLifelink", "AbilityVigilance", "AbilityFirstStrike", "AbilityDoubleStrike", "AbilityTrample", "AbilityIndestructible", "AbilityHaste", "AbilityDefender", "AbilityHexproof", "AbilityShroud", "AbilityMenace", "CardColorMask", "color_mask", "protection_color_mask", "ability_mask", "AttackAssignment", "attackers_declared_this_step", "blocker_declaration_complete_players", "attacks_each_combat_if_able", "blocks_each_combat_if_able", "must_be_blocked_if_able", "all_able_blockers_block_this_if_able", "cant_attack_alone", "cant_block_alone", "max_attackers_each_combat", "max_blockers_each_combat", "max_blockers_to_block_this", "can_block_only_flying", "attack_cost", "block_cost", "combat_damage_ordered_blockers", "OrderCombatDamage", "deathtouch_damage_marked", "blocked", "controlled_since_turn_start_index", "turn_start_index"],
        "include/mtgsim/engine.hpp": ["object_has_ability", "can_block_attacker_by_evasion", "object_has_summoning_sickness", "target_ref_is_legal_for_source", "target_ref_is_legal_for_source_object", "enumerate_legal_targets_for_source", "object_color_mask", "object_has_protection_from_color", "can_declare_attackers", "make_declare_attackers_action", "attack_assignments_from_action", "can_declare_blockers", "make_declare_blockers_action", "block_assignments_from_action", "can_order_combat_damage", "order_combat_damage", "make_order_combat_damage_action", "combat_damage_order_from_action"],
        "src/engine.cpp": ["source_has_keyword", "can_block_attacker_by_evasion", "lifelink_gain", "deathtouch_damage", "AbilityVigilance", "AbilityFirstStrike", "AbilityDoubleStrike", "AbilityTrample", "AbilityIndestructible", "AbilityHaste", "AbilityDefender", "AbilityHexproof", "AbilityShroud", "AbilityMenace", "object_has_summoning_sickness", "target_ref_is_legal_for_source_object", "target_has_protection_from_source", "object_color_mask", "declare_attackers", "make_declare_attackers_action", "attack_assignments_from_action", "maximum_satisfied_attack_requirements", "attack_requirements_satisfied_maximally", "attack_declaration_restrictions_satisfied", "attack_declaration_basic_constraints_satisfied", "object_cant_attack_alone", "object_attack_cost", "attack_declaration_cost", "combat_attack_cost_payable", "pay_combat_declaration_mana_cost", "attacker_has_any_legal_defending_target", "attack_declaration_choice_pending", "append_attack_declaration_actions", "attackers_declared_this_step", "declare_blockers", "make_declare_blockers_action", "block_assignments_from_action", "block_assignment_basic_legal", "block_declaration_basic_constraints_satisfied", "object_cant_block_alone", "object_can_block_only_flying", "object_max_blockers_to_block_this", "object_block_cost", "block_declaration_cost", "combat_block_cost_payable", "object_must_be_blocked_if_able", "object_requires_all_able_blockers", "satisfied_block_requirement_count", "maximum_satisfied_block_requirements", "block_requirements_satisfied_maximally", "blocker_declaration_choice_pending_for_player", "any_blocker_declaration_choice_pending", "append_block_declaration_actions", "blocker_declaration_complete_players", "can_order_combat_damage", "order_combat_damage", "make_order_combat_damage_action", "combat_damage_order_from_action", "damage_order_choice_pending", "append_combat_damage_order_actions", "current_blockers_for_attacker", "ordered_blockers_for_combat_damage", "combat_damage_ordered_blockers", "targets.reserve(assignments.size() * 2U)", "controlled_since_turn_start_index", "split_combat_damage", "combat_damage_trample_defender", "blocked"],
        "src/validation.cpp": ["combat.illegal_flying_block", "object.deathtouch_damage_without_damage", "combat.blocked_without_attacking", "combat.blocker_without_attacker_blocked", "combat.summoning_sick_attacker", "combat.defender_attacking", "combat.menace_underblocked", "combat.illegal_protection_block", "combat.attackers_declared_flag_wrong_step", "combat.blockers_declared_invalid_player", "combat.attack_limit_exceeded", "combat.block_limit_exceeded", "combat.cant_attack_alone_violation", "combat.cant_block_alone_violation", "combat.attacker_blocker_limit_exceeded", "combat.can_block_only_flying_violation", "object.control_timestamp_outside_battlefield"],
        "apps/mtgsim_scenario.cpp": ["abilities=", "expect_ability", "expect_blocked", "expect_summoning_sick", "deal_damage", "ready", "first_strike", "double_strike", "trample", "indestructible", "haste", "defender", "hexproof", "shroud", "menace", "color=", "protection=", "expect_color", "expect_protection", "block_batch", "make_declare_blockers_action"],
        "tests/cpp/test_engine.cpp": ["test_flying_attacker_requires_flying_or_reach_blocker", "test_lifelink_combat_damage_gains_life", "test_deathtouch_damage_is_lethal_sba", "test_first_strike_kills_blocker_before_regular_damage", "test_first_strike_nonlethal_damage_allows_regular_blocker_damage", "test_double_strike_unblocked_deals_two_combat_damage_batches", "test_trample_assigns_excess_damage_to_defending_player", "test_indestructible_survives_lethal_and_deathtouch_damage", "test_summoning_sickness_blocks_attack_until_ready", "test_haste_ignores_summoning_sickness_for_attack", "test_defender_cannot_attack_even_when_ready", "test_hexproof_filters_opposing_targeting_but_allows_controller", "test_shroud_filters_all_spell_targeting", "test_protection_from_red_filters_source_aware_targeting", "test_menace_requires_two_blockers_and_batch_declaration_supports_it", "test_batch_attack_declaration_replays_and_closes_window", "test_empty_block_declaration_replays_and_closes_window", "test_combat_attack_requirement_filters_empty_and_subset_declarations", "test_combat_attack_requirements_maximize_under_attack_limit", "test_combat_attack_requirements_treat_cant_attack_alone_as_global_restriction", "test_combat_block_requirement_filters_empty_and_subset_declarations", "test_combat_block_requirements_maximize_under_block_limit", "test_combat_block_requirements_treat_cant_block_alone_as_global_restriction", "test_combat_must_be_blocked_filters_empty_declarations", "test_combat_must_be_blocked_maximizes_under_single_blocker_choice", "test_must_be_blocked_menace_requires_complete_pair_or_none_when_unable", "test_all_able_blockers_requirement_forces_complete_lure_block", "test_all_able_blockers_requirement_maximizes_under_blocker_cap", "test_per_attacker_blocker_limit_maximizes_lure_requirements", "test_per_attacker_blocker_limit_can_make_menace_must_be_blocked_unsatisfiable", "test_can_block_only_flying_restriction_feeds_requirement_solver", "test_validation_catches_can_block_only_flying_metadata", "test_combat_attack_mana_cost_gates_and_pays_transactionally", "test_combat_block_mana_cost_gates_and_pays_transactionally", "test_combat_declaration_choices_gate_priority_until_complete", "test_combat_damage_order_is_required_replayable_and_used", "OrderCombatDamage", "priority pass should not be offered before attackers", "active player should not be able to pass while a defender's block declaration is pending", "test_must_block_menace_limit_can_make_requirement_unsatisfiable", "test_must_block_menace_requires_complete_legal_declaration", "test_validation_catches_combat_declaration_limit_violations", "test_validation_catches_cant_attack_or_block_alone_metadata", "public LegalAction enumeration should expose the two-blocker menace batch", "public LegalAction enumeration should expose the two-attacker declaration batch", "explicit no-block declaration", "receipt projection should decode legacy one-target block actions back into assignments"],
        "CMakeLists.txt": ["mtgsim_scenario_keywords", "mtgsim_scenario_keyword_trample", "mtgsim_scenario_keyword_indestructible", "mtgsim_scenario_keyword_summoning", "mtgsim_scenario_keyword_targeting", "mtgsim_scenario_keyword_protection", "mtgsim_scenario_keyword_menace"],
        "src/rules.cpp": ["core.keywords", "core.summoning_sickness", "core.costs", "302.6", "508.1h", "509.1d", "702.10", "702.3", "702.11", "702.18", "702.16", "702.111"],
        "tools/card_db.py": ["ABILITY_MASKS", "COLOR_MASKS", "colors_json", "color_mask", "protection_colors_json", "protection_color_mask", "trample", "indestructible", "double_strike", "haste", "defender", "hexproof", "shroud", "menace"],
        "data/cards/schema/card_catalog_schema.sql": ["keywords_json", "ability_mask", "colors_json", "color_mask", "protection_colors_json", "protection_color_mask"],
        "data/rules/coverage/rules_ledger.json": ["\"302.6\"", "\"702.10\"", "\"702.3\"", "\"702.11\"", "\"702.18\"", "\"702.16\"", "\"702.111\"", "test_summoning_sickness_blocks_attack_until_ready", "test_hexproof_filters_opposing_targeting_but_allows_controller", "test_protection_from_red_filters_source_aware_targeting", "test_menace_requires_two_blockers_and_batch_declaration_supports_it", "test_combat_attack_requirement_filters_empty_and_subset_declarations", "test_combat_attack_requirements_maximize_under_attack_limit", "test_combat_attack_requirements_treat_cant_attack_alone_as_global_restriction", "test_combat_block_requirement_filters_empty_and_subset_declarations", "test_combat_block_requirements_maximize_under_block_limit", "test_combat_block_requirements_treat_cant_block_alone_as_global_restriction", "test_combat_must_be_blocked_filters_empty_declarations", "test_combat_must_be_blocked_maximizes_under_single_blocker_choice", "test_must_be_blocked_menace_requires_complete_pair_or_none_when_unable", "test_all_able_blockers_requirement_forces_complete_lure_block", "test_all_able_blockers_requirement_maximizes_under_blocker_cap", "test_per_attacker_blocker_limit_maximizes_lure_requirements", "test_per_attacker_blocker_limit_can_make_menace_must_be_blocked_unsatisfiable", "test_can_block_only_flying_restriction_feeds_requirement_solver", "test_validation_catches_can_block_only_flying_metadata", "test_combat_attack_mana_cost_gates_and_pays_transactionally", "test_combat_block_mana_cost_gates_and_pays_transactionally", "test_combat_declaration_choices_gate_priority_until_complete", "test_combat_damage_order_is_required_replayable_and_used", "test_must_block_menace_limit_can_make_requirement_unsatisfiable", "test_must_block_menace_requires_complete_legal_declaration", "test_validation_catches_combat_declaration_limit_violations", "test_validation_catches_cant_attack_or_block_alone_metadata", "test_validation_catches_can_block_only_flying_metadata"],
        "docs/architecture/combat_requirements_solver_rev0085.md": ["attacks_each_combat_if_able", "blocks_each_combat_if_able", "menace", "not a complete CR 508/509 solver"],
        "docs/architecture/combat_requirement_maximizer_rev0086.md": ["max_attackers_each_combat", "max_blockers_each_combat", "maximum satisfiable", "not full CR 508/509"],
        "docs/architecture/combat_alone_restrictions_rev0087.md": ["cant_attack_alone", "cant_block_alone", "optional partners", "not a complete CR 508/509"],
        "docs/architecture/combat_must_be_blocked_rev0088.md": ["must_be_blocked_if_able", "attacker-side", "maximum legal requirement count", "not a complete CR 509"],
        "docs/architecture/combat_all_able_blockers_rev0089.md": ["all_able_blockers_block_this_if_able", "lure-style", "maximum-satisfaction", "not a complete CR 509"],
        "docs/architecture/combat_mana_costs_rev0090.md": ["attack_cost", "block_cost", "not forced", "not a complete CR 508/509"],
        "docs/architecture/combat_declaration_priority_gates_rev0091.md": ["mandatory turn-based choice gates", "PassPriority", "priority resumes", "not a complete CR 508/509"],
        "docs/architecture/combat_damage_order_choice_rev0092.md": ["OrderCombatDamage", "combat_damage_ordered_blockers", "priority", "not a complete CR 509/510"],
        "docs/architecture/combat_can_block_only_flying_rev0094.md": ["can_block_only_flying", "block only creatures with flying", "combat.can_block_only_flying_violation", "not a complete defender-specific restriction language"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "keywords.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "keywords.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }


def audit_attachment_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that Aura/Equipment attachment scaffolding is wired through core, tests, scenarios, CMake, registry, and card DB."""
    required_files = [
        root / "tests" / "scenarios" / "attachment_aura_grants_flying.mtgscn",
        root / "tests" / "scenarios" / "attachment_equipment_detaches.mtgscn",
        root / "tests" / "scenarios" / "attachment_unattached_aura_sba.mtgscn",
        root / "docs" / "architecture" / "attachments_aura_equipment.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "attachments.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["AttachmentKind", "attachment_kind", "attachment_power_bonus", "attachment_toughness_bonus", "attachment_granted_ability_mask", "attached_to"],
        "include/mtgsim/engine.hpp": ["can_attach_object", "attach_object_to", "detach_object", "object_attachment_target", "attachment_count_for_target"],
        "src/engine.cpp": ["AttachmentKind::Aura", "AttachmentKind::Equipment", "clear_attachment_links_for_zone_change", "resolve_aura_no_legal_enchant", "attachment_granted_ability_mask", "sba_aura_graveyard", "sba_attachment_unattach"],
        "src/validation.cpp": ["attachment.outside_battlefield", "attachment.non_attachment_attached", "attachment.illegal_attachment", "attachment.aura_unattached"],
        "apps/mtgsim_scenario.cpp": ["attachment=", "attach_bonus=", "expect_attached", "expect_attachment_count", "parse_attachment_kind"],
        "tests/cpp/test_engine.cpp": ["test_aura_spell_enters_attached_and_grants_bonus_ability", "test_equipment_can_attach_to_creature_and_grants_bonus", "test_zone_change_graveyards_aura_but_detaches_equipment", "test_sba_handles_unattached_aura_and_illegal_equipment", "test_validation_catches_illegal_attachment_metadata"],
        "CMakeLists.txt": ["mtgsim_scenario_attachments"],
        "src/rules.cpp": ["core.attachments", "301.5", "303.4", "701.3"],
        "tools/card_db.py": ["ATTACHMENT_KINDS", "attachment_kind", "attachment_power_bonus", "attachment_granted_ability_mask", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["attachment_kind", "attachment_power_bonus", "attachment_granted_ability_mask"],
        "data/cards/sample_cards.json": ["Sample Flight Aura", "Sample Training Boots", "attachment_kind", "attach_bonus", "grants"],
        "data/rules/coverage/rules_ledger.json": ["\"301.5\"", "\"303.4\"", "\"303.4a\"", "\"303.4g\"", "\"701.3\"", "test_aura_spell_enters_attached_and_grants_bonus_ability"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "attachments.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "attachments.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }


def audit_static_effect_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the static continuous-effect / tiny layer seam stays wired."""
    required_files = [
        root / "tests" / "scenarios" / "static_anthem_layer.mtgscn",
        root / "tests" / "scenarios" / "static_flying_evasion_layer.mtgscn",
        root / "tests" / "scenarios" / "static_plague_sba_layer.mtgscn",
        root / "tests" / "scenarios" / "static_ability_removal_layer.mtgscn",
        root / "tests" / "scenarios" / "static_base_pt_set_layer.mtgscn",
        root / "tests" / "scenarios" / "static_base_pt_sba_layer.mtgscn",
        root / "docs" / "architecture" / "static_effects_and_layers.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "static_effects.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["StaticEffectDefinition", "StaticEffectScope", "static_effects", "removed_ability_mask", "sets_power_toughness"],
        "include/mtgsim/engine.hpp": ["static_power_modifier", "static_toughness_modifier", "object_has_ability"],
        "src/engine.cpp": ["static_effect_applies_to", "static_power_modifier", "static_toughness_modifier", "source_has_keyword", "static_power_toughness_set", "removed_ability_mask"],
        "src/validation.cpp": ["static_effect.invalid_scope", "static_effect.inactive", "static_effect.invalid_ability_mask"],
        "apps/mtgsim_scenario.cpp": ["static=", "apply_static_effect_option", "parse_static_effect_scope", "set_pt=", "remove_abilities="],
        "tests/cpp/test_engine.cpp": ["test_static_anthem_updates_derived_power_toughness", "test_static_ability_removal_removes_printed_keyword_and_evasion", "test_static_base_power_toughness_set_applies_before_counters_and_modifiers"],
        "CMakeLists.txt": ["mtgsim_scenario_static_effects", "mtgsim_scenario_static_base_pt", "mtgsim_scenario_static_ability_removal"],
        "src/rules.cpp": ["core.static_effects", "613.1f", "613.1g", "613.4b", "613.4c"],
        "tools/card_db.py": ["static_effects_json", "static_effect_count", "normalize_static_effects", "static_removed_ability_mask_union", "static_set_pt_count", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["static_effects_json", "static_effect_count", "static_granted_ability_mask_union", "static_removed_ability_mask_union", "static_set_pt_count"],
        "data/cards/sample_cards.json": ["Sample Anthem Matrix", "Sample Downdraft Matrix", "Sample Base Setter Matrix"],
        "data/rules/coverage/rules_ledger.json": ["\"604\"", "\"611\"", "\"613.1f\"", "\"613.1g\"", "\"613.4b\"", "\"613.4c\"", "test_static_base_power_toughness_set_applies_before_counters_and_modifiers"],
        "docs/architecture/static_effects_and_layers.md": ["StaticEffectDefinition", "layer-6", "layer-7", "base P/T"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "static_effects.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "static_effects.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}


def audit_type_color_layer_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that narrow layer-4/type and layer-5/color derived-characteristic seams stay wired."""
    required_files = [
        root / "tests" / "scenarios" / "static_type_land_animation_layer.mtgscn",
        root / "tests" / "scenarios" / "static_color_painter_layer.mtgscn",
        root / "tests" / "scenarios" / "static_type_removal_combat_layer.mtgscn",
        root / "docs" / "architecture" / "static_effects_and_layers.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "type_color.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["added_type_mask", "removed_type_mask", "sets_color", "PermanentsYouControl", "PermanentsOpponentsControl", "AllPermanents"],
        "include/mtgsim/engine.hpp": ["object_type_mask", "object_has_type", "object_color_mask"],
        "src/engine.cpp": ["object_type_mask", "static_effect_has_type_layer_payload", "static_effect_has_color_layer_payload", "static_effect_applies_to_types", "removed_type_mask", "set_color_mask"],
        "src/validation.cpp": ["static_effect.invalid_type_mask", "static_effect.invalid_color_mask", "object_is_current_type"],
        "apps/mtgsim_scenario.cpp": ["expect_type", "add_types=", "remove_types=", "set_color=", "all_permanents"],
        "apps/mtgsim_fuzz.cpp": ["object_type_mask", "object_has_any_type"],
        "tests/cpp/test_engine.cpp": ["test_static_type_effect_animates_land_for_actions_and_sba", "test_static_type_removal_stops_creature_combat_and_creature_sba", "test_static_color_effect_recolors_source_characteristics", "test_validation_catches_invalid_static_type_and_color_masks"],
        "tests/scenarios/static_type_land_animation_layer.mtgscn": ["add_types=creature", "expect_type", "expect_effective_pt"],
        "tests/scenarios/static_color_painter_layer.mtgscn": ["set_color=blue", "expect_color"],
        "tests/scenarios/static_type_removal_combat_layer.mtgscn": ["remove_types=creature", "expect_type"],
        "CMakeLists.txt": ["mtgsim_scenario_static_type_color"],
        "tools/card_db.py": ["static_added_type_mask_union", "static_removed_type_mask_union", "static_set_color_count", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["static_added_type_mask_union", "static_removed_type_mask_union", "static_set_color_count"],
        "data/cards/sample_cards.json": ["Sample Land Animator Matrix", "Sample Blue Painter Matrix", "Sample Type Eraser Matrix"],
        "src/rules.cpp": ["core.types_colors", "613.1d", "613.1e"],
        "data/rules/coverage/rules_ledger.json": ["\"205\"", "\"613.1d\"", "\"613.1e\"", "test_static_type_effect_animates_land_for_actions_and_sba"],
        "docs/architecture/static_effects_and_layers.md": ["layer-4", "layer-5", "object_type_mask", "object_color_mask"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "type_color.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "type_color.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}

def audit_test_matrix_inventory(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the decomposable test-matrix planner exposes work units and shard bins."""
    probes = {
        "tools/plan_test_matrix.py": ["work_units", "duration_greedy_bins", "fuzz_seed_units", "mtgsim.test_matrix_plan.v2"],
        "tools/harness.py": ["test.matrix_plan", "--target-shards", "--fuzz-seeds"],
        "REVISION.json": ["test_matrix_planner"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "matrix.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "matrix.wiring_missing", f"{relpath} missing {needle!r}")

    latest = root / "reports" / "harness" / "test_matrix_plan_latest.json"
    latest_summary: dict[str, Any] = {"available": latest.exists()}
    if latest.exists():
        try:
            payload = json.loads(latest.read_text(encoding="utf-8"))
            latest_summary.update({
                "schema": payload.get("schema"),
                "work_units": len(payload.get("work_units", [])),
                "duration_greedy_bins": len(payload.get("duration_greedy_bins", [])),
            })
            if payload.get("schema") != "mtgsim.test_matrix_plan.v2":
                add(issues, "warning", "matrix.latest_schema", f"latest matrix schema is {payload.get('schema')!r}")
        except json.JSONDecodeError as exc:
            add(issues, "warning", "matrix.latest_invalid_json", str(exc))
    return {"probes": probe_results, "latest_report": latest_summary}


def audit_token_exile_sacrifice_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that token/exile/sacrifice scaffolding is wired through core, tests, scenarios, registry, and card DB."""
    required_files = [
        root / "tests" / "scenarios" / "token_create_spell.mtgscn",
        root / "tests" / "scenarios" / "token_sacrifice_ceases.mtgscn",
        root / "tests" / "scenarios" / "exile_spell_permanent.mtgscn",
        root / "tests" / "scenarios" / "exiled_token_ceases.mtgscn",
        root / "docs" / "architecture" / "tokens_exile_and_sacrifice.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "tokens.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["ceased_to_exist", "created_token_definition_index", "ExilePermanent", "CreateToken"],
        "include/mtgsim/engine.hpp": ["create_token", "create_tokens", "object_ceased_to_exist", "exile_permanent", "sacrifice_permanent"],
        "src/engine.cpp": ["cease_token_object", "token_ceased_to_exist", "EffectKind::CreateToken", "EffectKind::ExilePermanent", "sacrifice_permanent", "exile_permanent"],
        "src/validation.cpp": ["zone.ceased_object_contained", "object.invalid_ceased_object", "object.ceased_metadata"],
        "apps/mtgsim_scenario.cpp": ["create_token", "expect_token", "expect_ceased", "sacrifice", "exile", "create_token:COUNT:DEF_INDEX"],
        "tests/cpp/test_engine.cpp": ["test_create_token_spell_resolution_uses_definition_payload", "test_token_sacrifice_queues_dies_trigger_then_token_ceases_on_sba", "test_exile_spell_moves_target_to_exile_without_dies_trigger", "test_exiled_token_ceases_and_cannot_move_again"],
        "CMakeLists.txt": ["mtgsim_scenario_tokens"],
        "src/rules.cpp": ["core.tokens", "111", "701.7", "701.13", "701.21", "704.5d"],
        "tools/card_db.py": ["mtgsim.card_catalog.v17", "is_token", "created_token_definition_index", "token_cards", "create_token_effect_cards", "exile_effect_cards"],
        "data/cards/schema/card_catalog_schema.sql": ["is_token", "created_token_definition_index", "idx_card_definitions_is_token"],
        "data/cards/sample_cards.json": ["Sample Saproling Token", "Sample Token Maker", "Sample Exile Spell", "is_token", "create_token", "exile"],
        "data/rules/coverage/rules_ledger.json": ["\"111\"", "\"406\"", "\"701.7\"", "\"701.13\"", "\"701.21\"", "\"704.5d\""],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "tokens.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "tokens.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }

def audit_planeswalker_loyalty_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that planeswalker/loyalty scaffolding is wired through core, scenarios, registry, card DB, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "planeswalker_loyalty_damage.mtgscn",
        root / "tests" / "scenarios" / "planeswalker_combat_attack.mtgscn",
        root / "tests" / "scenarios" / "loyalty_ability_stack.mtgscn",
        root / "docs" / "architecture" / "planeswalkers_and_loyalty.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "planeswalkers.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["printed_loyalty", "LoyaltyAbilityDefinition", "attacked_object", "loyalty_ability_activated_turn", "ActivateLoyaltyAbility"],
        "include/mtgsim/engine.hpp": ["planeswalker_loyalty", "activate_loyalty_ability", "declare_attacker_to_target"],
        "src/engine.cpp": ["add_entering_planeswalker_loyalty", "object_is_battlefield_planeswalker", "sba_planeswalker_graveyard", "create_loyalty_ability_stack_object", "combat_damage_defender"],
        "src/validation.cpp": ["combat.attacked_object_not_combat_target", "object.loyalty_on_non_planeswalker", "planeswalker.zero_loyalty_pending_sba"],
        "apps/mtgsim_scenario.cpp": ["loyalty_ability=", "expect_loyalty", "expect_attacking_target", "action loyalty"],
        "tests/cpp/test_engine.cpp": ["test_planeswalker_enters_with_printed_loyalty_and_zero_loyalty_sba", "test_combat_can_attack_planeswalker_and_remove_loyalty", "test_loyalty_ability_timing_cost_once_per_turn_and_resolution"],
        "CMakeLists.txt": ["mtgsim_scenario_planeswalkers"],
        "src/rules.cpp": ["core.planeswalkers", "306.5", "606.6", "704.5i"],
        "tools/card_db.py": ["loyalty_ability_cards", "loyalty_ability_json", "planeswalkers"],
        "data/cards/schema/card_catalog_schema.sql": ["loyalty INTEGER", "loyalty_ability_json", "idx_card_definitions_loyalty"],
        "data/cards/sample_cards.json": ["Sample Mind Sculptor", "Sample Reckless Pyromancer", "loyalty_ability"],
        "data/rules/coverage/rules_ledger.json": ["\"306\"", "\"306.5\"", "\"306.6\"", "\"306.8\"", "\"606.3\"", "\"704.5i\""],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "planeswalkers.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "planeswalkers.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }




def audit_modal_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that modal spell mode choice is wired through core, scenarios, registry, card DB, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "modal_charm_damage.mtgscn",
        root / "tests" / "scenarios" / "modal_charm_untargeted.mtgscn",
        root / "tests" / "scenarios" / "modal_target_illegal_before_resolution.mtgscn",
        root / "docs" / "architecture" / "modal_spells_and_choices.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "modal.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["SpellModeDefinition", "modes", "chosen_mode_index", "mode_index"],
        "include/mtgsim/engine.hpp": ["cast_from_hand_to_stack_paying_mana_with_mode"],
        "src/engine.cpp": ["valid_spell_mode_index", "spell_mode_definition", "required_target_count_for_mode", "choose_mode", "resolve_spell_invalid_mode", "mode#"],
        "src/validation.cpp": ["modal.missing_choice", "modal.invalid_choice", "object.chosen_mode_outside_stack", "target.count_mismatch"],
        "apps/mtgsim_scenario.cpp": ["mode=", "expect_mode", "action cast_paid PLAYER OBJECT [mode=N]"],
        "tests/cpp/test_engine.cpp": ["test_modal_spell_requires_mode_and_targeted_mode_resolves", "test_modal_untargeted_mode_can_be_chosen_without_target", "test_modal_action_enumeration_emits_mode_variants", "test_validation_catches_modal_stack_metadata_errors"],
        "CMakeLists.txt": ["mtgsim_scenario_modal"],
        "src/rules.cpp": ["core.modal", "700.2", "700.2a", "700.2c", "700.2f", "115.8"],
        "tools/card_db.py": ["normalize_modes", "modal_cards", "mode_count", "modal_target_mask_union", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["modes_json", "mode_count", "modal_target_mask_union"],
        "data/cards/sample_cards.json": ["Sample Prism Charm", "Sample Modal Growth", "modes"],
        "data/rules/coverage/rules_ledger.json": ["\"700.2\"", "\"700.2a\"", "\"700.2c\"", "\"700.2f\"", "\"115.8\"", "test_modal_spell_requires_mode_and_targeted_mode_resolves"],
        "docs/architecture/modal_spells_and_choices.md": ["mode", "chosen_mode_index", "mode_index", "target"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "modal.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "modal.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }

def audit_battle_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that battle/defense/protector scaffolding is wired through core, scenarios, registry, card DB, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "battle_targeted_damage.mtgscn",
        root / "tests" / "scenarios" / "battle_combat_attack.mtgscn",
        root / "tests" / "scenarios" / "battle_protector_blocks.mtgscn",
        root / "docs" / "architecture" / "battles_defense_and_protectors.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "battles.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["printed_defense", "Defense", "battle_protector", "attacked_object"],
        "include/mtgsim/engine.hpp": ["battle_defense", "battle_protector", "set_battle_protector", "declare_attacker_to_target"],
        "src/engine.cpp": ["add_entering_battle_defense_and_protector", "object_is_battlefield_battle", "damage_battle", "sba_battle_graveyard", "battle_protector_set"],
        "src/validation.cpp": ["battle.missing_protector", "battle.protector_outside_battlefield", "combat.battle_protector_attacking", "object.defense_on_non_battle"],
        "apps/mtgsim_scenario.cpp": ["defense=", "protector", "expect_defense", "expect_battle_protector"],
        "tests/cpp/test_engine.cpp": ["test_battle_enters_with_defense_and_default_protector", "test_damage_to_battle_removes_defense_and_zero_defense_sba", "test_combat_can_attack_own_battle_protected_by_opponent", "test_battle_protector_blocks_attackers_to_battle", "test_targeted_spell_can_damage_battle", "test_validation_catches_illegal_battle_metadata"],
        "CMakeLists.txt": ["mtgsim_scenario_battles"],
        "src/rules.cpp": ["core.battles", "310.4", "310.8", "704.5v", "122.1g"],
        "tools/card_db.py": ["printed_defense", "battle_defense_cards", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["printed_defense", "idx_card_definitions_printed_defense"],
        "data/cards/sample_cards.json": ["Sample Siege Battle", "defense", "Sample Battle Bolt"],
        "data/rules/coverage/rules_ledger.json": ["\"310\"", "\"310.4\"", "\"310.8b\"", "\"704.5v\"", "test_battle_enters_with_defense_and_default_protector"],
        "docs/architecture/battles_defense_and_protectors.md": ["defense counters", "protector", "TargetRef"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "battles.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "battles.wiring_missing", f"{relpath} missing {needle!r}")

    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
    }


def audit_card_db_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    required_files = [
        root / "tools" / "card_db.py",
        root / "data" / "cards" / "sample_cards.json",
        root / "data" / "cards" / "schema" / "card_catalog_schema.sql",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "cards.missing_file", path)

    probes = {
        "tools/harness.py": ["cards.catalog", "tools/card_db.py"],
        "REVISION.json": ["card_catalog"],
        "tools/card_db.py": ["COLOR_MASKS", "protection_color_mask", "mtgsim.card_catalog.v17", "menace", "static_effects_json", "static_effect_count", "attachment_kind", "attachment_granted_ability_mask", "is_token", "created_token_definition_index", "loyalty_ability_cards"],
        "data/cards/schema/card_catalog_schema.sql": ["color_mask", "protection_color_mask", "attachment_kind", "attachment_granted_ability_mask", "is_token", "created_token_definition_index", "static_effects_json", "static_effect_count"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "cards.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "warning", "cards.wiring_missing", f"{relpath} missing {needle!r}")

    sample_summary: dict[str, Any] = {}
    sample_path = root / "data" / "cards" / "sample_cards.json"
    if sample_path.exists():
        try:
            payload = json.loads(sample_path.read_text(encoding="utf-8"))
            sample_summary = {"cards": len(payload.get("cards", [])), "notice_present": bool(payload.get("notice"))}
            if not payload.get("notice"):
                add(issues, "warning", "cards.sample_notice_missing", rel(sample_path, root))
        except json.JSONDecodeError as exc:
            add(issues, "error", "cards.sample_invalid_json", str(exc))
    return {
        "available": not missing_files,
        "missing_files": missing_files,
        "probes": probe_results,
        "sample": sample_summary,
    }


def audit_activated_ability_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that generic activated abilities are wired through core, scenarios, fuzz, card DB, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "activated_ping_stack.mtgscn",
        root / "tests" / "scenarios" / "activated_tap_sickness_gate.mtgscn",
        root / "tests" / "scenarios" / "activated_token_sorcery_speed.mtgscn",
        root / "tests" / "scenarios" / "activated_sacrifice_cost_source_lki_stack_order.mtgscn",
        root / "tests" / "scenarios" / "activated_cost_target_locked_before_payment.mtgscn",
        root / "docs" / "architecture" / "activated_abilities.md",
    ]
    missing_files = []
    for path in required_files:
        if not path.exists():
            missing_files.append(rel(path))
            add(issues, "error", "activated.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["ActivatedAbilityDefinition", "activated_abilities", "ActivateActivatedAbility", "ability_index", "sacrifice_cost"],
        "include/mtgsim/engine.hpp": ["can_activate_activated_ability", "activate_activated_ability"],
        "src/engine.cpp": ["create_activated_ability_stack_object", "activated_ability_put_on_stack", "choose_target", "can_activate_activated_ability", "can_pay_activated_ability_costs", "pay_selected_sacrifice_cost", "ActivateActivatedAbility"],
        "src/rules.cpp": ["core.activated", "602.2", "117.1b", "sacrifice_cost"],
        "apps/mtgsim_scenario.cpp": ["activated=", "action activate", "ability=", "parse_tap_cost", ":sac=COUNT,TYPES"],
        "apps/mtgsim_fuzz.cpp": ["ActivatedAbilityDefinition", "activated_actions"],
        "tests/cpp/test_engine.cpp": ["test_activated_ability_with_tap_and_mana_cost_resolves_from_stack", "test_activated_ability_action_enumeration_emits_target_variants", "test_activated_ability_sorcery_speed_and_create_token_payload", "test_activated_sacrifice_cost_can_sacrifice_source_and_queue_trigger_above_ability", "test_activated_ability_locks_target_before_activation_costs_are_paid", "test_activated_sacrifice_cost_without_matching_permanent_blocks_action"],
        "tests/scenarios/activated_sacrifice_cost_source_lki_stack_order.mtgscn": ["activated=Blood_Rite", ":sac=1,creature", "expect_pending_triggers 1", "expect_life 1 23"],
        "tests/scenarios/activated_cost_target_locked_before_payment.mtgscn": ["activated=Last_Spark", "target=object:1", "expect_event_order activated_ability_put_on_stack choose_target", "expect_event_order choose_target pay_sacrifice_cost"],
        "CMakeLists.txt": ["mtgsim_scenario_activated", "mtgsim_scenario_activated_sacrifice_cost", "mtgsim_scenario_activated_cost_target_lock"],
        "tools/card_db.py": ["normalize_activated_abilities", "activated_ability_cards", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["activated_abilities_json", "activated_ability_count", "activated_target_mask_union"],
        "data/cards/sample_cards.json": ["Sample Spark Mage", "activated_abilities", "Sample Token Engine"],
        "data/rules/coverage/rules_ledger.json": ["\"602.2\"", "\"602.2a\"", "\"602.2b\"", "test_activated_ability_with_tap_and_mana_cost_resolves_from_stack", "activated_sacrifice_cost_source_lki_stack_order.mtgscn"],
        "docs/architecture/activated_abilities.md": ["ActivatedAbilityDefinition", "ability_index", "tap cost", "stack", "rev0040 activated sacrifice costs"],
    }
    probe_results: dict[str, Any] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            probe_results[relpath] = {"missing": True}
            add(issues, "error", "activated.probe_file_missing", relpath)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "activated.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}


def audit_mana_ability_payment_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that explicit mana abilities and auto-payment stay wired through engine, scenarios, card DB, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "mana_auto_cast_sources.mtgscn",
        root / "tests" / "scenarios" / "mana_auto_non_greedy_tap_mode.mtgscn",
        root / "tests" / "scenarios" / "mana_generic_ability_no_stack.mtgscn",
        root / "tests" / "scenarios" / "mana_auto_activated_cost.mtgscn",
        root / "docs" / "architecture" / "mana_abilities_and_auto_payment.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "mana_ability.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["ManaAbilityDefinition", "mana_abilities", "ActivateManaAbility", "mana_ability_index"],
        "include/mtgsim/engine.hpp": ["can_activate_mana_ability", "activate_mana_ability", "can_pay_mana_cost_with_available_mana", "pay_mana_cost_with_mana_abilities"],
        "src/engine.cpp": ["select_mana_ability_pay_plan", "max_search_nodes", "mana_auto_plan", "mana_ability_definition_for_index", "pay_mana_cost_with_mana_abilities", "ActivateManaAbility"],
        "src/rules.cpp": ["core.mana_abilities", "601.2g", "605.3b", "pay_mana_cost_with_mana_abilities"],
        "apps/mtgsim_scenario.cpp": ["mana_ability=", "action mana", "expect_mana", "parse_mana_pool_text"],
        "apps/mtgsim_fuzz.cpp": ["ActivateManaAbility", "mana_actions"],
        "tests/cpp/test_engine.cpp": ["test_mana_ability_api_resolves_immediately_without_stack", "test_auto_mana_payment_casts_spell_by_tapping_sources", "test_auto_mana_payment_searches_non_greedy_tap_modes", "test_action_enumerator_lists_generic_mana_abilities"],
        "CMakeLists.txt": ["mtgsim_scenario_mana_auto", "mtgsim_scenario_mana_auto_search"],
        "tools/card_db.py": ["mana_abilities_json", "explicit_mana_ability_count", "mtgsim.card_catalog.v17", "normalize_mana_abilities"],
        "data/cards/schema/card_catalog_schema.sql": ["mana_abilities_json", "mana_ability_count", "explicit_mana_ability_count"],
        "data/cards/sample_cards.json": ["Sample Mana Prism", "mana_abilities", "Sample Chromatic Filter"],
        "data/rules/coverage/rules_ledger.json": ["\"605.1a\"", "\"605.3a\"", "\"605.3b\"", "\"601.2g\"", "test_auto_mana_payment_casts_spell_by_tapping_sources", "test_auto_mana_payment_searches_non_greedy_tap_modes"],
        "docs/architecture/mana_abilities_and_auto_payment.md": ["ManaAbilityDefinition", "601.2g", "605.3b", "auto-payment", "bounded search"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_ability.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_ability.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}

def audit_timing_land_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that spell timing, flash, and land-play special-action scaffolds stay wired."""
    required_files = [
        root / "tests" / "scenarios" / "timing_flash_in_combat.mtgscn",
        root / "tests" / "scenarios" / "land_play_special_action.mtgscn",
        root / "tests" / "scenarios" / "land_play_resets_next_turn.mtgscn",
        root / "docs" / "architecture" / "timing_land_play_and_flash.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "timing_land.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["AbilityFlash", "lands_played_this_turn", "max_land_plays_per_turn", "PlayLand"],
        "include/mtgsim/engine.hpp": ["can_cast_spell_now", "can_play_land", "play_land_from_hand"],
        "src/engine.cpp": ["player_has_sorcery_speed_window", "definition_has_flash", "can_cast_spell_now", "play_land", "lands_played_this_turn"],
        "src/validation.cpp": ["player.land_play_limit_exceeded"],
        "apps/mtgsim_scenario.cpp": ["main_phase", "priority PLAYER STEP", "action play_land", "expect_land_plays", "flash"],
        "tests/cpp/test_engine.cpp": ["test_timing_permissions_allow_instants_and_flash_but_gate_noninstants", "test_land_play_is_special_action_and_lands_cannot_be_cast", "test_land_play_action_enumeration_and_illegal_timing", "test_validation_catches_land_play_limit_overage"],
        "CMakeLists.txt": ["mtgsim_scenario_timing", "mtgsim_scenario_land_play"],
        "src/rules.cpp": ["core.timing", "core.land_play", "117.1a", "305.1", "702.8"],
        "tools/card_db.py": ["flash_cards", "mtgsim.card_catalog.v17", "\"flash\": 1 << 14"],
        "data/cards/sample_cards.json": ["Sample Flash Ambusher", "Sample Timing Ritual", "Sample Training Ground"],
        "data/rules/coverage/rules_ledger.json": ["\"117.1a\"", "\"305.1\"", "\"305.2\"", "\"305.9\"", "\"702.8\"", "test_timing_permissions_allow_instants_and_flash_but_gate_noninstants"],
        "docs/architecture/timing_land_play_and_flash.md": ["can_cast_spell_now", "play_land_from_hand", "flash", "land-play"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "timing_land.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "timing_land.wiring_missing", f"{relpath} missing {needle!r}")

    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}


def audit_control_change_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that control-changing effects are wired through engine, scenarios, registry, card DB, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "control_spell_steals_creature.mtgscn",
        root / "tests" / "scenarios" / "control_change_static_scope.mtgscn",
        root / "tests" / "scenarios" / "control_change_combat_sickness.mtgscn",
        root / "docs" / "architecture" / "control_change_and_controller_zones.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "control.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["GainControlPermanent", "controller", "controlled_since_turn_start_index"],
        "include/mtgsim/engine.hpp": ["gain_control_of_permanent", "object_has_summoning_sickness"],
        "src/engine.cpp": ["gain_control_of_permanent", "gain_control", "clear_combat_links_for_object", "EffectKind::GainControlPermanent"],
        "src/rules.cpp": ["core.control", "108.4", "109.4", "110.2", "613.1b"],
        "apps/mtgsim_scenario.cpp": ["gain_control", "expect_controller", "gain_control_permanent"],
        "apps/mtgsim_fuzz.cpp": ["Fuzz Steal", "GainControlPermanent"],
        "tests/cpp/test_engine.cpp": ["test_gain_control_spell_moves_battlefield_container_and_owner_graveyard", "test_gain_control_helper_updates_sickness_and_clears_combat", "test_control_change_recomputes_static_effect_scopes", "test_validation_catches_controller_container_mismatch"],
        "CMakeLists.txt": ["mtgsim_scenario_control_change"],
        "tools/card_db.py": ["gain_control_effect_cards", "mtgsim.card_catalog.v17"],
        "data/cards/sample_cards.json": ["Sample Control Ray", "gain_control", "Sample Controller Anthem"],
        "data/rules/coverage/rules_ledger.json": ["\"108.4\"", "\"109.4\"", "\"110.2\"", "\"613.1b\"", "test_gain_control_spell_moves_battlefield_container_and_owner_graveyard"],
        "docs/architecture/control_change_and_controller_zones.md": ["gain_control_of_permanent", "controller", "613.1b", "summoning sickness"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "control.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "control.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}

def audit_temporary_continuous_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that temporary continuous effects generated by spells remain wired through core, tests, docs, CMake, and catalog metadata."""
    expected_files = [
        root / "tests" / "scenarios" / "temporary_pump_cleanup.mtgscn",
        root / "tests" / "scenarios" / "temporary_flying_grant_cleanup.mtgscn",
        root / "tests" / "scenarios" / "temporary_land_animation_cleanup.mtgscn",
        root / "docs" / "architecture" / "temporary_continuous_effects.md",
    ]
    missing_files = [rel(path) for path in expected_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "temporary_continuous.missing_file", path)
    probes = {
        "include/mtgsim/types.hpp": ["ContinuousEffectDefinition", "ContinuousEffectDuration", "continuous_effects", "CreateContinuousEffect", "zone_change_index"],
        "include/mtgsim/engine.hpp": ["create_continuous_effect", "continuous_effect_count", "expire_continuous_effects"],
        "src/engine.cpp": ["create_continuous_effect", "expire_continuous_effects", "continuous_effect_applies_to", "next_continuous_effect_timestamp", "locked_targets"],
        "src/validation.cpp": ["continuous_effect.invalid_duration", "continuous_effect.invalid_locked_object", "continuous_effect.missing_payload"],
        "apps/mtgsim_scenario.cpp": ["continuous=", "expect_continuous_effects", "apply_continuous_effect_option", "create_continuous"],
        "tests/cpp/test_engine.cpp": ["test_temporary_pump_effect_expires_at_cleanup", "test_temporary_effect_lock_breaks_on_zone_change", "test_temporary_ability_effects_apply_in_timestamp_order_after_static_layer", "test_validation_catches_malformed_continuous_effect_record"],
        "CMakeLists.txt": ["mtgsim_scenario_temporary_continuous", "temporary_pump_cleanup.mtgscn"],
        "src/rules.cpp": ["core.temporary_continuous", "611.2a", "613.7", "514.2"],
        "tools/card_db.py": ["continuous_effects_json", "continuous_effect_count", "continuous_effect_cards", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["continuous_effects_json", "continuous_effect_count", "continuous_granted_ability_mask_union"],
        "data/cards/sample_cards.json": ["Sample Temporary Growth", "Sample Temporary Wings", "Sample Temporary Animation"],
        "data/rules/coverage/rules_ledger.json": ["\"611.2a\"", "\"613.7\"", "test_temporary_pump_effect_expires_at_cleanup"],
        "docs/architecture/temporary_continuous_effects.md": ["ContinuousEffectDefinition", "until-cleanup", "timestamp", "locked target"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "temporary_continuous.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "temporary_continuous.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}

def audit_layer_timestamp_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that timestamp-ordered layer scaffolding remains wired through core, tests, scenarios, docs, registry, and ledger."""
    expected_files = [
        root / "tests" / "scenarios" / "timestamp_static_newer_type_order.mtgscn",
        root / "tests" / "scenarios" / "timestamp_static_newer_ability_removal.mtgscn",
        root / "tests" / "scenarios" / "timestamp_static_newer_base_pt.mtgscn",
        root / "docs" / "architecture" / "layer_timestamp_order.md",
    ]
    missing_files = [rel(path, root) for path in expected_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "layer_timestamps.missing_file", path)
    probes = {
        "include/mtgsim/types.hpp": ["layer_timestamp", "next_layer_timestamp", "ContinuousEffectDefinition"],
        "src/engine.cpp": ["collect_layer_effects", "source_static_effect_timestamp", "next_layer_timestamp", "layer_timestamp", "static_effect_has_base_pt_set_payload"],
        "src/validation.cpp": ["object.missing_layer_timestamp", "object.layer_timestamp_outside_battlefield", "continuous_effect.missing_timestamp"],
        "tests/cpp/test_engine.cpp": ["test_timestamp_order_newer_static_type_effect_beats_older_temporary_type_effect", "test_timestamp_order_newer_static_ability_removal_beats_older_temporary_grant", "test_timestamp_order_newer_static_base_pt_set_beats_older_temporary_base_pt_set", "test_attachment_receives_new_layer_timestamp_when_attached"],
        "tests/scenarios/timestamp_static_newer_type_order.mtgscn": ["expect_type", "remove_types=creature", "expect_continuous_effects"],
        "tests/scenarios/timestamp_static_newer_ability_removal.mtgscn": ["remove_abilities=flying", "expect_ability"],
        "tests/scenarios/timestamp_static_newer_base_pt.mtgscn": ["set_pt=5/5", "set_pt=1/1", "expect_effective_pt"],
        "CMakeLists.txt": ["mtgsim_scenario_timestamp_order", "timestamp_static_newer_type_order.mtgscn"],
        "src/rules.cpp": ["core.layer_timestamps", "613.7a", "613.7b", "613.7d", "613.7e", "613.9"],
        "data/rules/coverage/rules_ledger.json": ["\"613.7a\"", "\"613.7b\"", "\"613.7d\"", "\"613.7e\"", "test_timestamp_order_newer_static_base_pt_set_beats_older_temporary_base_pt_set"],
        "docs/architecture/layer_timestamp_order.md": ["layer timestamp", "GameObject::layer_timestamp", "613.7", "timestamp-sorted"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "layer_timestamps.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "layer_timestamps.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}


def audit_layer_dependency_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that dependency-ordered layer scaffolding remains wired through projection, tests, scenarios, docs, DB, registry, and ledger."""
    expected_files = [
        root / "tests" / "scenarios" / "dependency_ability_order.mtgscn",
        root / "tests" / "scenarios" / "dependency_type_order.mtgscn",
        root / "tests" / "scenarios" / "dependency_cycle_timestamp_fallback.mtgscn",
        root / "docs" / "architecture" / "layer_dependencies.md",
    ]
    missing_files = [rel(path, root) for path in expected_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "layer_dependencies.missing_file", path)
    probes = {
        "include/mtgsim/types.hpp": ["depends_on_effect_names", "StaticEffectDefinition"],
        "src/engine.cpp": ["dependency_ordered_layer_effects", "effect_names_match_dependency", "Dependency loops fall back", "collect_layer_effects"],
        "src/validation.cpp": ["self_dependency", "validate_static_effect_dependencies"],
        "apps/mtgsim_scenario.cpp": ["depends=", "parse_dependency_names", "depends_on_effect_names"],
        "tests/cpp/test_engine.cpp": ["test_dependency_order_overrides_timestamp_for_ability_layer", "test_dependency_order_overrides_timestamp_for_type_layer", "test_dependency_loop_falls_back_to_timestamp_order", "test_validation_catches_static_effect_self_dependency"],
        "tests/scenarios/dependency_ability_order.mtgscn": ["depends=Dependency_wings", "expect_ability"],
        "tests/scenarios/dependency_type_order.mtgscn": ["depends=Dependency_animate", "expect_type"],
        "tests/scenarios/dependency_cycle_timestamp_fallback.mtgscn": ["depends=Loop_wings", "depends=Loop_grounder"],
        "CMakeLists.txt": ["mtgsim_scenario_layer_dependencies", "dependency_ability_order.mtgscn"],
        "tools/card_db.py": ["depends_on_effect_names", "static_dependency_count", "continuous_dependency_count", "mtgsim.card_catalog.v17"],
        "data/cards/schema/card_catalog_schema.sql": ["static_dependency_count", "continuous_dependency_count"],
        "data/cards/sample_cards.json": ["Sample Dependency Grounder", "depends_on"],
        "src/rules.cpp": ["core.layer_dependencies", "613.8", "613.8a", "613.8b", "613.8c"],
        "data/rules/coverage/rules_ledger.json": ["\"613.8\"", "\"613.8a\"", "\"613.8b\"", "\"613.8c\"", "test_dependency_order_overrides_timestamp_for_ability_layer"],
        "docs/architecture/layer_dependencies.md": ["dependency", "timestamp", "613.8", "cycle"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "layer_dependencies.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "layer_dependencies.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}


def audit_copy_effect_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that copy-effect/copiable-definition scaffolding is wired through core, tests, scenarios, docs, card DB, and ledger."""
    expected_files = [
        root / "tests" / "scenarios" / "copy_effect_dragon_projection.mtgscn",
        root / "tests" / "scenarios" / "copy_effect_snapshot_independence.mtgscn",
        root / "tests" / "scenarios" / "copy_effect_static_source_projection.mtgscn",
        root / "tests" / "scenarios" / "copy_effect_expires_on_zone_change.mtgscn",
        root / "docs" / "architecture" / "copy_effects_and_copiable_values.md",
    ]
    missing_files = [rel(path, root) for path in expected_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "copy_effect.missing_file", path)
    probes = {
        "include/mtgsim/types.hpp": ["BecomeCopyPermanent", "has_copy_effect", "copied_definition_index"],
        "include/mtgsim/engine.hpp": ["become_copy_of_permanent", "clear_copy_effect", "object_copiable_definition_index"],
        "src/engine.cpp": ["current_definition_for_object", "become_copy_of_permanent", "copy_effect_expired", "EffectKind::BecomeCopyPermanent"],
        "src/validation.cpp": ["copy.outside_battlefield", "copy.invalid_definition", "copy.stale_definition"],
        "apps/mtgsim_scenario.cpp": ["copy OBJECT SOURCE_OBJECT", "expect_copy", "expect_copiable_definition", "become_copy"],
        "tests/cpp/test_engine.cpp": ["test_copy_effect_updates_derived_type_color_pt_and_keywords", "test_copy_effect_snapshot_does_not_track_later_source_copy_changes", "test_copy_effect_derived_static_effect_source_recomputes_projection", "test_copy_effect_grants_copied_activated_ability_surface", "test_copy_effect_clears_on_zone_change_and_validation_catches_bad_copy_metadata"],
        "tests/scenarios/copy_effect_dragon_projection.mtgscn": ["copy 1 2", "expect_copy", "expect_copiable_definition"],
        "CMakeLists.txt": ["mtgsim_scenario_copy_effects", "copy_effect_dragon_projection.mtgscn"],
        "src/rules.cpp": ["core.copy", "707", "613.1a", "613.2a"],
        "tools/card_db.py": ["copy_effect_cards", "mtgsim.card_catalog.v17"],
        "data/cards/sample_cards.json": ["Sample Copy Spell", "Sample Copy Dragon", "copy"],
        "data/rules/coverage/rules_ledger.json": ["\"707\"", "\"707.2\"", "\"707.2b\"", "\"613.1a\"", "\"613.2a\""],
        "docs/architecture/copy_effects_and_copiable_values.md": ["copy", "copiable", "Layer 1", "current-definition"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "copy_effect.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "copy_effect.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}



def audit_sacrifice_cost_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that sacrifice-as-cost is wired through core, scenario DSL, tests, docs, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "sacrifice_cost_trigger_stack_order.mtgscn",
        root / "tests" / "scenarios" / "sacrifice_cost_target_locked_before_payment.mtgscn",
        root / "tests" / "scenarios" / "activated_sacrifice_cost_source_lki_stack_order.mtgscn",
        root / "tests" / "scenarios" / "activated_cost_target_locked_before_payment.mtgscn",
        root / "docs" / "architecture" / "mana_abilities_and_auto_payment.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "sacrifice_cost.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["SacrificeCostDefinition", "sacrifice_cost", "required_type_mask"],
        "src/engine.cpp": ["select_sacrifice_cost_objects", "pay_sacrifice_cost", "pay_selected_sacrifice_cost", "finish_paid_cast_after_costs", "can_pay_spell_costs", "can_pay_activated_ability_costs", "pay_sacrifice_cost_failed", "!game.pending_triggers.empty()"],
        "src/validation.cpp": ["sacrifice_cost.invalid_type_mask", "sacrifice_cost.inactive", "activated.sacrifice_cost.invalid_type_mask"],
        "apps/mtgsim_scenario.cpp": ["apply_sacrifice_cost_option", "parse_sacrifice_cost_text", "sacrifice_cost=COUNT:TYPES", "sac_cost=", ":sac=COUNT,TYPES", "expect_event_order"],
        "tests/cpp/test_engine.cpp": ["test_sacrifice_cost_cast_queues_trigger_above_spell", "test_sacrifice_cost_without_matching_permanent_blocks_cast_action", "test_targeted_spell_locks_target_before_sacrifice_costs_are_paid", "test_activated_sacrifice_cost_can_sacrifice_source_and_queue_trigger_above_ability", "test_activated_ability_locks_target_before_activation_costs_are_paid"],
        "tests/scenarios/sacrifice_cost_trigger_stack_order.mtgscn": ["sacrifice_cost=1:creature", "expect_actions 1 put_triggers 1", "expect_life 1 23"],
        "tests/scenarios/sacrifice_cost_target_locked_before_payment.mtgscn": ["sacrifice_cost=1:creature", "target=object:1", "expect_event_order cast_spell choose_target", "expect_event_order choose_target pay_sacrifice_cost"],
        "tests/scenarios/activated_sacrifice_cost_source_lki_stack_order.mtgscn": [":sac=1,creature", "expect_actions 1 put_triggers 1", "expect_life 1 23"],
        "tests/scenarios/activated_cost_target_locked_before_payment.mtgscn": [":sac=1,creature", "target=object:1", "expect_event_order choose_target pay_sacrifice_cost"],
        "CMakeLists.txt": ["mtgsim_scenario_sacrifice_cost", "mtgsim_scenario_sacrifice_cost_target_lock", "sacrifice_cost_target_locked_before_payment.mtgscn", "mtgsim_scenario_activated_sacrifice_cost", "mtgsim_scenario_activated_cost_target_lock"],
        "data/rules/coverage/rules_ledger.json": ["test_sacrifice_cost_cast_queues_trigger_above_spell", "sacrifice_cost_target_locked_before_payment.mtgscn", "test_targeted_spell_locks_target_before_sacrifice_costs_are_paid", "test_activated_ability_locks_target_before_activation_costs_are_paid", "sacrifice-as-cost"],
        "docs/architecture/mana_abilities_and_auto_payment.md": ["rev0039 sacrifice-as-cost spine", "rev0040 activated sacrifice-cost bridge", "rev0041 paid-cast ordering correction", "rev0042 activated-cost ordering correction", "finish_paid_cast_after_costs"],
        "docs/architecture/scenario_tests.md": ["rev0041 event-order expectation", "expect_event_order"],
        "docs/roadmap.md": ["rev0041 roadmap update", "cost component", "rollback"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "sacrifice_cost.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "sacrifice_cost.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}


def audit_multitarget_resolution_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that multi-target choice, action, partial-resolution, scenario, docs, and ledger seams stay wired."""
    required_files = [
        root / "tests" / "scenarios" / "multitarget_partial_resolution.mtgscn",
        root / "docs" / "architecture" / "effects_and_targets.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "multitarget.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["target_count", "std::vector<TargetRef> targets"],
        "include/mtgsim/engine.hpp": ["enumerate_legal_target_sets_for_source_object", "cast_from_hand_to_stack_paying_mana_with_targets", "activate_activated_ability_with_targets"],
        "src/engine.cpp": ["target_set_is_legal_for_source_object", "target_list_label", "resolve_spell_partial_legal_targets", "enumerate_legal_target_sets_for_source_object"],
        "src/validation.cpp": ["target.count_mismatch", "target.duplicate_choice", "target_count_without_mask"],
        "apps/mtgsim_scenario.cpp": ["parse_target_spec", "parse_target_refs", "targets="],
        "tests/cpp/test_engine.cpp": ["test_multi_target_spell_partially_resolves_legal_targets", "test_multi_target_spell_with_all_targets_illegal_has_no_effect", "test_action_enumerator_lists_multi_target_cast_variants"],
        "tests/scenarios/multitarget_partial_resolution.mtgscn": ["effect=damage:3:object*2", "targets=object:3,object:4", "resolve_spell_partial_legal_targets"],
        "CMakeLists.txt": ["mtgsim_scenario_multitarget_partial", "multitarget_partial_resolution.mtgscn"],
        "data/rules/coverage/rules_ledger.json": ["test_multi_target_spell_partially_resolves_legal_targets", "multitarget_partial_resolution.mtgscn", "partial-target resolution"],
        "docs/architecture/effects_and_targets.md": ["multi-target", "partial-target", "608.2b"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "multitarget.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "multitarget.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}



def audit_stack_counterspell_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that stack-object targeting and counterspell resolution stay wired across source, scenarios, docs, cards, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "stack_counterspell_targets_stack_object.mtgscn",
        root / "docs" / "architecture" / "effects_and_targets.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "stack_counterspell.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["TargetStackObject", "CounterSpell"],
        "include/mtgsim/engine.hpp": ["enumerate_legal_targets", "target_ref_is_legal_for_source_object"],
        "src/engine.cpp": ["counter_stack_object", "object_is_stack_object", "counter_spell", "counter_ability", "TargetStackObject"],
        "src/types.cpp": ["CounterSpell", "counter_spell"],
        "src/validation.cpp": ["TargetStackObject", "legal_target_mask"],
        "apps/mtgsim_scenario.cpp": ["counterspell", "stack_object", "target expects player:N, object:N, or stack:N", "expect_event_count"],
        "tests/cpp/test_engine.cpp": ["test_counterspell_targets_stack_object_and_moves_it_to_graveyard", "TargetStackObject", "CounterSpell"],
        "tests/scenarios/stack_counterspell_targets_stack_object.mtgscn": ["effect=counterspell:1:stack", "target=stack:2", "expect_event_count damage_player 0"],
        "CMakeLists.txt": ["mtgsim_scenario_stack_counterspell", "stack_counterspell_targets_stack_object.mtgscn"],
        "data/rules/coverage/rules_ledger.json": ["\"701.6\"", "test_counterspell_targets_stack_object_and_moves_it_to_graveyard", "stack_counterspell_targets_stack_object.mtgscn"],
        "data/cards/sample_cards.json": ["Sample Stack Cancel", "counterspell", "stack"],
        "tools/card_db.py": ["counterspell_effect_cards", '"stack": 1 << 2'],
        "docs/architecture/effects_and_targets.md": ["stack-object target", "CounterSpell", "counter_spell"],
        "docs/architecture/engine_design.md": ["stack-object targeting", "counter_stack_object"],
        "docs/architecture/audit_refactor_notes.md": ["audit_stack_counterspell_wiring", "stack counterspell seam"],
        "src/rules.cpp": ["701.6", "TargetStackObject", "counterspell"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "stack_counterspell.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "stack_counterspell.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}


def audit_target_identity_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that chosen object-target identity snapshots are wired through core, validation, tests, scenarios, docs, and ledger."""
    required_files = [
        root / "tests" / "scenarios" / "target_blink_identity_stale_before_resolution.mtgscn",
        root / "docs" / "architecture" / "effects_and_targets.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "target_identity.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["object_zone_change_index", "wildcard for legacy/transient refs"],
        "src/engine.cpp": ["stamp_target_for_choice", "target.object_zone_change_index", "target_ref_is_legal"],
        "src/validation.cpp": ["target.missing_object_lki", "@zc"],
        "tests/cpp/test_engine.cpp": ["test_object_target_zone_change_identity_makes_stack_target_illegal", "object_zone_change_index"],
        "tests/scenarios/target_blink_identity_stale_before_resolution.mtgscn": ["move 4 2 exile", "move 4 2 battlefield", "expect_damage 4 0"],
        "CMakeLists.txt": ["mtgsim_scenario_target_lki", "target_blink_identity_stale_before_resolution.mtgscn"],
        "data/rules/coverage/rules_ledger.json": ["test_object_target_zone_change_identity_makes_stack_target_illegal", "target_blink_identity_stale_before_resolution.mtgscn", "object target zone-change snapshots"],
        "docs/architecture/effects_and_targets.md": ["object target identity", "zone-change snapshot", "leaves and re-enters"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "target_identity.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "target_identity.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}



def audit_choice_request_queue_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that APNAP choice-request queues stay wired through receipts, trace replay, validation, tests, docs, and ledger."""
    required_files = [
        root / "docs" / "architecture" / "choice_request_queue_apnap_guard_rev0081.md",
        root / "docs" / "architecture" / "choice_queue_location_schema_rev0109.md",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "choice_request_queue.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": ["ChoiceRequestQueue", "choice_queue_hash", "ChoiceQueueHashMismatch", "kChoiceRequestQueueSchemaVersion", "choice_queue_schema_version", "expected_choice_queue_schema_version", "kChoiceQueueLocationSchemaVersion", "ChoiceQueueLocation", "choice_queue_location_schema_version", "expected_choice_queue_location_schema_version"],
        "include/mtgsim/engine.hpp": ["apnap_ordered_players", "choice_request_queue", "choice_request_queue_hash"],
        "src/engine.cpp": ["MTGSim.ChoiceRequestQueue.v1", "find_choice_request_for_player", "ChoiceQueueHashMismatch", "choice_queue_index", "choice_queue_schema", "MTGSim.ActionTrace.v12", "MTGSim.ActionTrace.v13", "MTGSim.ActionTrace.v14", "MTGSim.ActionTrace.v15", "MTGSim.ActionTrace.v16", "MTGSim.ActionTrace.v17"],
        "src/validation.cpp": ["action_receipt.zero_choice_queue_hash", "choice_queue_index_out_of_range", "action_receipt.choice_queue_schema_version", "action_receipt.choice_queue_location_schema_version"],
        "apps/mtgsim_cli.cpp": ["choice_queue_hash_mismatch"],
        "tests/cpp/test_engine.cpp": ["test_apnap_ordered_players_skips_lost_and_starts_with_active", "test_choice_request_queue_metadata_roundtrips_and_guards_replay", "test_action_trace_replay_detects_choice_queue_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_request_queue_schema_drift_without_mutation", "test_action_trace_replay_detects_state_hash_schema_drift_without_mutation"],
        "data/rules/coverage/rules_ledger.json": ["ChoiceRequestQueue", "test_choice_request_queue_metadata_roundtrips_and_guards_replay", "test_action_trace_replay_detects_choice_queue_schema_drift_without_mutation", "test_action_trace_replay_detects_choice_request_queue_schema_drift_without_mutation", "APNAP", "choice_queue_schema"],
        "docs/architecture/choice_request_queue_apnap_guard_rev0081.md": ["ChoiceRequestQueue", "APNAP", "choice_queue_hash"],
        "docs/architecture/choice_queue_location_schema_rev0109.md": ["choice_queue_schema", "choice_queue_location_schema", "ActionTrace.v12", "kChoiceQueueLocationSchemaVersion", "schema drift"],
        "docs/architecture/choice_request_queue_schema_seal_rev0112.md": ["choice_queue_schema", "ActionTrace.v15", "kChoiceRequestQueueSchemaVersion", "schema drift"],
        "docs/architecture/audit_refactor_notes.md": ["rev0081", "rev0109", "rev0112", "choice queue", "choice_queue_schema"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "choice_request_queue.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "choice_request_queue.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}

def audit_legal_action_frontier_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that bounded legal-action frontier truth stays executable, receipted, benchmarked, and documented."""
    required_files = [
        root / "docs" / "architecture" / "mission_legal_surface_budget_audit_rev0095.md",
        root / "benchmarks" / "bench_legal_action_frontier.cpp",
        root / "reports" / "bench" / "legal_action_frontier_latest.json",
    ]
    missing_files = [rel(path, root) for path in required_files if not path.exists()]
    for path in missing_files:
        add(issues, "error", "legal_action_frontier.missing_file", path)

    probes = {
        "include/mtgsim/types.hpp": [
            "struct LegalActionFrontier",
            "LegalActionValidationSource",
            "LegalActionValidation",
            "struct LegalActionPage",
            "struct LegalActionPageLocation",
            "kLegalActionPageSchemaVersion",
            "schema_version",
            "total_actions_lower_bound",
            "remaining_actions_lower_bound",
            "expected_choice_page_count_present",
            "expected_choice_page_context_present",
            "state_hash",
            "choice_request_hash",
            "kChoiceRequestSchemaVersion",
            "choice_request_schema_version",
            "kChoiceRequestQueueSchemaVersion",
            "choice_queue_schema_version",
            "choice_validation_source",
            "choice_page_location_found",
            "choice_page_schema_version",
            "choice_page_state_hash",
            "choice_page_choice_request_hash",
            "choice_page_total_actions_lower_bound",
            "choice_page_remaining_actions_lower_bound",
            "choice_page_hash",
            "page_hash",
            "effective_limit",
            "action_frontier_complete",
            "action_generation_limit",
            "choice_action_frontier_complete",
            "choice_action_generation_limit",
        ],
        "include/mtgsim/engine.hpp": ["enumerate_legal_action_frontier", "validate_legal_action", "enumerate_legal_action_page", "locate_legal_action_page", "legal_action_page_hash"],
        "src/engine.cpp": [
            "MTGSim.ChoiceRequest.v2",
            "choice_schema",
            "can_declare_attackers_with_requirement_max",
            "can_declare_blockers_with_requirement_max",
            "directly_validate_unlisted_frontier_action",
            "validate_action_for_choice_request",
            "validate_legal_action",
            "enumerate_legal_action_page",
            "locate_legal_action_page",
            "frontier.complete = false",
            "choice_action_frontier_complete",
            "choice_page_location_found",
            "choice_page_location_checked",
            "choice_page_checked",
            "page_schema_version",
            "legal_action_page_hash",
            "choice_page_schema",
            "choice_page_state",
            "choice_page_request_hash",
            "choice_page_total_lower",
            "choice_page_remaining_lower",
            "choice_page_hash",
        ],
        "src/validation.cpp": [
            "action_receipt.incomplete_frontier_without_limit",
            "action_receipt.incomplete_frontier_count_mismatch",
            "action_receipt.incomplete_frontier_wrong_kind",
            "action_receipt.frontier_exceeds_limit",
            "action_receipt.direct_validation_complete_frontier",
            "action_receipt.direct_validation_wrong_kind",
            "action_receipt.legal_without_page_location_check",
            "action_receipt.legal_without_page_location",
            "action_receipt.illegal_with_page_location_check",
            "action_receipt.page_location_found_without_check",
            "action_receipt.page_location_schema_version",
            "action_receipt.page_location_state_hash",
            "action_receipt.page_location_choice_request_hash",
            "action_receipt.page_location_zero_hash",
            "action_receipt.page_count_lower_bound_mismatch",
            "action_receipt.page_count_exact_flag_mismatch",
            "action_receipt.page_count_remaining_lower_bound_mismatch",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_attack_action_frontier_reports_exact_completion_boundary",
            "test_truncated_attack_frontier_accepts_direct_legal_declaration_and_replays",
            "test_truncated_block_frontier_accepts_direct_legal_declaration_and_replays",
            "test_truncated_damage_order_frontier_accepts_direct_legal_order_and_replays",
            "test_attack_action_page_reaches_actions_omitted_by_frontier_prefix",
            "test_legal_action_page_location_finds_tail_combat_actions",
            "test_legal_action_page_location_reports_missing_without_mutation",
            "test_legal_action_page_zero_limit_still_advances_and_hashes_page",
            "test_action_trace_replay_detects_choice_page_location_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_hash_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_schema_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_count_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_context_drift_without_mutation",
            "test_action_trace_replay_rejects_applied_choice_page_proof_elision_without_mutation",
            "validate_legal_action",
            "DirectDomainValidation",
        ],
        "tools/build.py": ["bench-branch", "bench-frontier", "bench_legal_action_frontier"],
        "tests/python/test_build_tool.py": ["check_all_benchmark_sources_are_build_targets"],
        "CMakeLists.txt": ["bench_legal_action_frontier"],
        "data/rules/coverage/rules_ledger.json": [
            "test_attack_action_frontier_reports_exact_completion_boundary",
            "test_truncated_attack_frontier_accepts_direct_legal_declaration_and_replays",
            "test_truncated_block_frontier_accepts_direct_legal_declaration_and_replays",
            "test_truncated_damage_order_frontier_accepts_direct_legal_order_and_replays",
            "test_attack_action_page_reaches_actions_omitted_by_frontier_prefix",
            "test_legal_action_page_location_finds_tail_combat_actions",
            "test_legal_action_page_location_reports_missing_without_mutation",
            "test_legal_action_page_zero_limit_still_advances_and_hashes_page",
            "test_action_trace_replay_detects_choice_page_location_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_hash_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_schema_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_count_drift_without_mutation",
            "test_action_trace_replay_detects_choice_page_context_drift_without_mutation",
            "test_action_trace_replay_rejects_applied_choice_page_proof_elision_without_mutation",
            "validate_legal_action",
            "DirectDomainValidation",
        ],
        "docs/architecture/mission_legal_surface_budget_audit_rev0095.md": [
            "trusted transitions",
            "LegalActionFrontier",
            "bounded prefix",
            "coverage-guided fuzzing",
            "structured, queryable action protocol",
        ],
        "reports/bench/legal_action_frontier_latest.json": [
            "mtgsim.legal_action_frontier_benchmark_report.v1",
            "post_fix_measurement",
            "pre_fix_observation",
            "page_location_regressions",
        ],
        "docs/architecture/legal_action_page_location_rev0098.md": [
            "locate_legal_action_page",
            "LegalActionPageLocation",
            "page cursor",
            "not a replacement for validation",
        ],
        "docs/architecture/action_trace_page_location_rev0099.md": [
            "ActionTrace.v4",
            "choice_page_found",
            "choice_page_hash",
            "ChoicePageLocationMismatch",
            "before StateCore mutation",
        ],
        "docs/architecture/legal_action_page_hash_rev0100.md": [
            "legal_action_page_hash",
            "effective_limit",
            "zero-limit",
            "choice_page_hash",
        ],
        "docs/architecture/legal_action_page_protocol_rev0102.md": [
            "kLegalActionPageSchemaVersion",
            "ActionTrace.v5",
            "choice_page_schema",
            "append_bounded_frontier_actions",
            "single enumerator",
        ],
        "docs/architecture/legal_action_page_count_contract_rev0103.md": [
            "total_actions_lower_bound",
            "total_actions_exact",
            "remaining_actions_lower_bound",
            "ActionTrace.v6",
            "choice_page_total_lower",
            "ChoicePageLocationMismatch",
        ],
        "docs/architecture/legal_action_page_context_seal_rev0104.md": [
            "state_hash",
            "choice_request_hash",
            "ActionTrace.v7",
            "choice_page_state",
            "choice_page_request_hash",
            "ChoicePageLocationMismatch",
        ],
        "docs/architecture/action_trace_page_proof_sentinel_rev0106.md": [
            "choice_page_location_checked",
            "choice_page_checked",
            "ActionTrace.v8",
            "test_action_trace_replay_rejects_applied_choice_page_proof_elision_without_mutation",
            "ChoicePageLocationMismatch",
        ],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "legal_action_frontier.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "legal_action_frontier.wiring_missing", f"{relpath} missing {needle!r}")
    return {"available": not missing_files, "missing_files": missing_files, "probes": probe_results}



def audit_paid_action_transaction_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the rev0134 paid-action transaction seam remains wired."""
    probes = {
        "src/engine.cpp": [
            "commit_paid_action_body_transaction",
            "select_mana_ability_pay_plan_excluding_tap_sources",
            "activation_locked_tap_sources",
            "pay_mana_cost_with_mana_abilities_excluding_tap_sources",
            "activate_activated_ability_with_targets",
            "cast_from_hand_to_stack_paying_mana_with_mode_and_targets",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_activated_ability_tap_cost_locks_source_before_auto_mana_payment",
            "failed double-tap activation should not leak a synthetic stack object",
            "activation should pay mana from the external source",
        ],
        "docs/architecture/paid_action_transaction_spine_rev0134.md": [
            "commit_paid_action_body_transaction",
            "activation tap-cost",
            "double-tap",
            "rollback",
            "one causal receipt",
        ],
        "docs/audit_refactor_notes.md": ["rev0134", "paid action transaction spine", "double-tap"],
        "docs/architecture/audit_refactor_notes.md": ["rev0134", "paid action transaction spine", "double-tap"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0134",
            "test_activated_ability_tap_cost_locks_source_before_auto_mana_payment",
            "activation tap-cost source",
        ],
        "README.md": ["rev0134", "Paid Transaction Spine", "double-tap"],
        "CHANGELOG.md": ["rev0134", "Paid Transaction Spine", "double-tap"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "paid_transaction.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "paid_transaction.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_attack_tap_cost_lock_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the rev0136 attack declaration tap-source lock remains wired."""
    probes = {
        "src/engine.cpp": [
            "attack_declaration_locked_tap_sources",
            "pay_combat_declaration_mana_cost_excluding_tap_sources",
            "can_pay_mana_cost_with_available_mana_excluding_tap_sources",
            "pay_mana_cost_with_mana_abilities_excluding_tap_sources",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_attack_cost_locks_nonvigilance_attackers_out_of_auto_mana_payment",
            "declaration tap lock",
            "self-funded nonvigilance attack-cost",
        ],
        "docs/architecture/attack_tap_cost_lock_rev0136.md": [
            "attack_declaration_locked_tap_sources",
            "nonvigilance",
            "self-fund",
            "paid-action transaction",
        ],
        "docs/audit_refactor_notes.md": ["rev0136", "attack tap-cost lock", "attack_declaration_locked_tap_sources"],
        "docs/architecture/audit_refactor_notes.md": ["rev0136", "attack tap-cost lock", "attack_declaration_locked_tap_sources"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0136",
            "test_attack_cost_locks_nonvigilance_attackers_out_of_auto_mana_payment",
            "attack declaration tap lock",
        ],
        "README.md": ["rev0136", "Attack Tap-Cost Lock", "attack tap-cost lock"],
        "CHANGELOG.md": ["rev0136", "Attack Tap-Cost Lock", "attack tap-cost lock"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "attack_tap_cost_lock.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "attack_tap_cost_lock.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_mana_payment_plan_evidence_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the rev0137 typed auto-payment plan evidence remains wired."""
    probes = {
        "include/mtgsim/types.hpp": [
            "auto_payment_mana_ability_count",
            "auto_payment_locked_tap_source_count",
            "auto_payment",
        ],
        "src/engine.cpp": [
            "auto_payment_mana_ability_count",
            "auto_payment_locked_tap_source_count",
            "static_cast<u32>(plan.size())",
            "static_cast<u32>(locked_tap_sources.size())",
            "pay_mana_cost_with_mana_abilities_excluding_tap_sources",
        ],
        "src/validation.cpp": [
            "mana_change_record.auto_payment_on_nonpayment",
            "mana_change_record.plan_metadata_on_nonpayment",
            "mana_change_record.plan_metadata_without_auto_payment",
            "auto_payment_locked_tap_source_count",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_mana_change_record_links_production_payment_and_clearing",
            "test_activated_ability_tap_cost_locks_source_before_auto_mana_payment",
            "test_attack_cost_locks_nonvigilance_attackers_out_of_auto_mana_payment",
            "auto_payment_locked_tap_source_count",
            "attack-cost payment should record the locked nonvigilance attacker tap set",
        ],
        "docs/architecture/mana_payment_plan_evidence_rev0137.md": [
            "auto_payment_mana_ability_count",
            "auto_payment_locked_tap_source_count",
            "ManaChangeRecord",
            "cost-plan evidence",
        ],
        "docs/audit_refactor_notes.md": ["rev0137", "mana payment plan evidence", "auto_payment_locked_tap_source_count"],
        "docs/architecture/audit_refactor_notes.md": ["rev0137", "mana payment plan evidence", "auto_payment_locked_tap_source_count"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0137",
            "auto_payment_locked_tap_source_count",
            "auto_payment_mana_ability_count",
        ],
        "README.md": ["rev0137", "Mana Plan Evidence", "auto_payment_locked_tap_source_count"],
        "CHANGELOG.md": ["rev0137", "Mana Plan Evidence", "auto_payment_locked_tap_source_count"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_plan_evidence.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_plan_evidence.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_mana_payment_plan_hash_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the rev0138 stable auto-payment plan hash remains wired."""
    probes = {
        "include/mtgsim/types.hpp": [
            "auto_payment_plan_hash",
            "auto_payment_mana_ability_count",
            "auto_payment_locked_tap_source_count",
        ],
        "src/engine.cpp": [
            "mana_payment_plan_hash",
            "MTGSim.ManaAutoPaymentPlan.v",
            "auto_payment_plan_hash",
            "hash_into(h, value.auto_payment_plan_hash)",
            "const u64 plan_hash = mana_payment_plan_hash(game, player_id, cost, plan, locked_tap_sources)",
        ],
        "src/validation.cpp": [
            "mana_change_record.plan_hash_on_nonpayment",
            "mana_change_record.plan_hash_without_auto_payment",
            "mana_change_record.auto_payment_plan_hash_missing",
            "auto_payment_plan_hash",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_auto_payment_plan_hash_records_empty_plan_evidence",
            "auto_payment_plan_hash != 0U",
            "validator should reject automatic mana payments without a stable plan hash",
        ],
        "docs/architecture/mana_payment_plan_hash_rev0138.md": [
            "auto_payment_plan_hash",
            "ManaAutoPaymentPlan.v1",
            "locked-source set",
            "selected mana-ability steps",
        ],
        "docs/audit_refactor_notes.md": ["rev0138", "mana payment plan hash", "auto_payment_plan_hash"],
        "docs/architecture/audit_refactor_notes.md": ["rev0138", "mana payment plan hash", "auto_payment_plan_hash"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0138",
            "auto_payment_plan_hash",
            "test_auto_payment_plan_hash_records_empty_plan_evidence",
        ],
        "README.md": ["rev0138", "Mana Plan Hash", "auto_payment_plan_hash"],
        "CHANGELOG.md": ["rev0138", "Mana Plan Hash", "auto_payment_plan_hash"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_plan_hash.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_plan_hash.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_mana_payment_plan_record_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the rev0139 readable auto-payment plan record remains wired."""
    probes = {
        "include/mtgsim/types.hpp": [
            "ManaPaymentPlanRecord",
            "ManaPaymentPlanStepRecord",
            "ManaPaymentPlanLockedSourceRecord",
            "auto_payment_plan_record_index",
            "produced_mana_change_record_index",
            "mana_payment_plan_records",
            "ManaPaymentPlan",
        ],
        "include/mtgsim/engine.hpp": [
            "mana_payment_plan_record_count",
            "latest_mana_payment_plan_record",
            "mana_payment_plan_record_identity_hash",
        ],
        "src/engine.cpp": [
            "record_mana_payment_plan",
            "mana_payment_plan_hash_from_records",
            "MTGSim.ManaAutoPaymentPlan.v",
            "hash_vector(h, game.mana_payment_plan_records)",
            "paid_mana_change_record_index",
            "mana_auto_plan",
        ],
        "src/validation.cpp": [
            "mana_payment_plan_record.event_record_link_count",
            "event_record.invalid_mana_payment_plan_link",
            "mana_change_record.auto_payment_plan_record_missing",
            "mana_change_record.plan_record_backlink_mismatch",
            "mana_payment_plan_record.hash_mismatch",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_auto_payment_plan_record_links_locked_sources_steps_and_paid_record",
            "latest_mana_payment_plan_record",
            "auto_payment_plan_record_index",
            "mana_payment_plan_record.hash_mismatch",
        ],
        "docs/architecture/mana_payment_plan_record_rev0139.md": [
            "ManaPaymentPlanRecord",
            "auto_payment_plan_record_index",
            "paid_mana_change_record_index",
            "ManaAutoPaymentPlan.v3",
        ],
        "docs/audit_refactor_notes.md": ["rev0139", "mana payment plan record", "ManaPaymentPlanRecord"],
        "docs/architecture/audit_refactor_notes.md": ["rev0139", "mana payment plan record", "ManaPaymentPlanRecord"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0139",
            "ManaPaymentPlanRecord",
            "test_auto_payment_plan_record_links_locked_sources_steps_and_paid_record",
        ],
        "README.md": ["rev0139", "Mana Payment Plan Record", "ManaPaymentPlanRecord"],
        "CHANGELOG.md": ["rev0139", "Mana Payment Plan Record", "ManaPaymentPlanRecord"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_plan_record.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_plan_record.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_mana_payment_plan_step_witness_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0140 links readable payment-plan steps to executed mana production rows."""
    probes = {
        "include/mtgsim/types.hpp": [
            "produced_mana_change_record_index",
            "turning the plan into an execution witness",
        ],
        "include/mtgsim/engine.hpp": [
            "mana_payment_plan_record_identity_hash",
        ],
        "src/engine.cpp": [
            "produced_mana_change_record_index = produced_record_index",
            "hash_mana_payment_plan_step_identity",
            "selected mana ability produced no typed mana-change witness",
            "mana_payment_plan_record_identity_hash",
        ],
        "src/validation.cpp": [
            "mana_payment_plan_record.identity_hash_mismatch",
            "mana_payment_plan_record.step_missing_produced_link",
            "mana_payment_plan_record.step_link_not_production",
            "mana_payment_plan_record.step_production_pool_mismatch",
            "mana_payment_plan_record.step_production_order",
        ],
        "tests/cpp/test_engine.cpp": [
            "produced_mana_change_record_index",
            "mana_payment_plan_record.identity_hash_mismatch",
            "mana_payment_plan_record.step_missing_produced_link",
            "mana_payment_plan_record.step_link_not_production",
        ],
        "docs/architecture/mana_payment_plan_step_witness_rev0140.md": [
            "produced_mana_change_record_index",
            "execution witness",
            "identity hash",
            "Produced ManaChangeRecord",
        ],
        "docs/audit_refactor_notes.md": ["rev0140", "mana payment plan step witness", "produced_mana_change_record_index"],
        "docs/architecture/audit_refactor_notes.md": ["rev0140", "mana payment plan step witness", "produced_mana_change_record_index"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0140",
            "produced_mana_change_record_index",
            "step execution witness",
        ],
        "README.md": ["rev0140", "Mana Payment Step Witness", "produced_mana_change_record_index"],
        "CHANGELOG.md": ["rev0140", "Mana Payment Step Witness", "produced_mana_change_record_index"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_plan_step_witness.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_plan_step_witness.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_mana_payment_producer_backlink_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0141 keeps automatic mana production rows linked back to their plan steps."""
    probes = {
        "include/mtgsim/types.hpp": [
            "auto_payment_producer_plan_record_index",
            "auto_payment_producer_plan_step_index",
            "bidirectional",
        ],
        "src/engine.cpp": [
            "auto_payment_producer_plan_record_index = plan_record_index",
            "auto_payment_producer_plan_step_index = static_cast<u32>(step_index + 1U)",
            "hash_into(h, value.auto_payment_producer_plan_record_index)",
        ],
        "src/validation.cpp": [
            "mana_payment_plan_record.step_production_backlink_mismatch",
            "mana_change_record.incomplete_producer_plan_link",
            "mana_change_record.invalid_producer_plan_step_link",
            "mana_change_record.producer_plan_link_on_nonproduction",
            "mana_change_record.producer_plan_step_backlink_mismatch",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_auto_payment_produced_mana_records_bidirectional_plan_step_link",
            "auto_payment_producer_plan_record_index",
            "auto_payment_producer_plan_step_index",
        ],
        "docs/architecture/mana_payment_producer_backlink_rev0141.md": [
            "auto_payment_producer_plan_record_index",
            "auto_payment_producer_plan_step_index",
            "bidirectional",
        ],
        "docs/audit_refactor_notes.md": ["rev0141", "producer backlink", "auto_payment_producer_plan_record_index"],
        "docs/architecture/audit_refactor_notes.md": ["rev0141", "producer backlink", "auto_payment_producer_plan_record_index"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0141",
            "auto_payment_producer_plan_record_index",
            "test_auto_payment_produced_mana_records_bidirectional_plan_step_link",
        ],
        "README.md": ["rev0141", "Mana Payment Producer Backlink", "auto_payment_producer_plan_record_index"],
        "CHANGELOG.md": ["rev0141", "Mana Payment Producer Backlink", "auto_payment_producer_plan_record_index"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_producer_backlink.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_producer_backlink.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_mana_payment_tap_witness_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0142 keeps tap-cost auto-payment plan steps linked to the tap event that paid the source tap."""
    probes = {
        "include/mtgsim/types.hpp": [
            "tap_event_sequence",
            "tap-cost steps name the ordered tap Event sequence",
        ],
        "src/engine.cpp": [
            "find_tap_event_sequence_since",
            "plan_step_record.tap_event_sequence",
            "selected tap-cost mana ability did not leave a tap event witness",
            "hash_into(h, value.tap_event_sequence)",
        ],
        "src/validation.cpp": [
            "mana_payment_plan_record.step_missing_tap_event_witness",
            "mana_payment_plan_record.tap_event_witness_not_tap",
            "mana_payment_plan_record.step_tap_after_production",
            "mana_payment_plan_record.duplicate_step_tap_event_witness",
        ],
        "tests/cpp/test_engine.cpp": [
            "tap_event_sequence",
            "mana_payment_plan_record.step_missing_tap_event_witness",
            "mana_payment_plan_record.tap_event_witness_not_tap",
        ],
        "docs/architecture/mana_payment_tap_witness_rev0142.md": [
            "tap_event_sequence",
            "tap-event witness",
            "Produced ManaChangeRecord",
        ],
        "docs/audit_refactor_notes.md": ["rev0142", "tap-event witness", "tap_event_sequence"],
        "docs/architecture/audit_refactor_notes.md": ["rev0142", "tap-event witness", "tap_event_sequence"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0142",
            "tap_event_sequence",
            "test_auto_payment_plan_record_links_locked_sources_steps_and_paid_record",
        ],
        "README.md": ["rev0142", "Mana Payment Tap Witness", "tap_event_sequence"],
        "CHANGELOG.md": ["rev0142", "Mana Payment Tap Witness", "tap_event_sequence"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_tap_witness.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_tap_witness.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_mana_payment_pool_span_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0143 keeps automatic mana-payment plan pool-span witnesses wired."""
    probes = {
        "include/mtgsim/types.hpp": [
            "pool_before_plan",
            "pool_before_payment",
            "Pool-span snapshots",
        ],
        "src/engine.cpp": [
            "MTGSim.ManaAutoPaymentPlan.v",
            "record.pool_before_plan = player(game, player_id).mana_pool",
            "plan_record.pool_before_payment = player(game, player_id).mana_pool",
            "hash_into(h, value.pool_before_plan)",
        ],
        "src/validation.cpp": [
            "mana_payment_plan_record.pool_span_mismatch",
            "mana_payment_plan_record.pool_before_payment_mismatch",
            "mana_change_record.plan_record_pool_before_payment_mismatch",
            "add_mana_pool_for_validation",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_auto_payment_plan_record_preserves_pool_span_witness",
            "pool_before_plan",
            "pool_before_payment",
            "mana_payment_plan_record.pool_span_mismatch",
        ],
        "docs/architecture/mana_payment_pool_span_rev0143.md": [
            "pool_before_plan",
            "pool_before_payment",
            "ManaAutoPaymentPlan.v3",
        ],
        "docs/audit_refactor_notes.md": ["rev0143", "pool-span witness", "pool_before_plan"],
        "docs/architecture/audit_refactor_notes.md": ["rev0143", "pool-span witness", "pool_before_plan"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0143",
            "pool_before_plan",
            "test_auto_payment_plan_record_preserves_pool_span_witness",
        ],
        "README.md": ["rev0143", "Mana Payment Pool Span", "pool_before_plan"],
        "CHANGELOG.md": ["rev0143", "Mana Payment Pool Span", "pool_before_plan"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_pool_span.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_pool_span.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_tap_event_identity_anchor_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0144 keeps tap log rows anchored to object/player identity for payment-plan tap witnesses."""
    probes = {
        "src/engine.cpp": [
            "record_event_with_links(game,",
            "\"tap\"",
            ".object = object_id",
            ".player = controller",
        ],
        "src/validation.cpp": [
            "event_record.tap_log_missing_object",
            "event_record.tap_log_missing_player",
            "mana_payment_plan_record.tap_event_witness_source_mismatch",
            "mana_payment_plan_record.tap_event_witness_player_mismatch",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_tap_log_event_records_object_and_player_context",
            "tap_event_record->object == forest",
            "tap_event_record->player == mtgsim::PlayerId{1}",
            "mana_payment_plan_record.tap_event_witness_source_mismatch",
            "mana_payment_plan_record.tap_event_witness_player_mismatch",
        ],
        "docs/architecture/tap_event_identity_anchor_rev0144.md": [
            "tap log rows",
            "object/player anchors",
            "tap_event_sequence",
            "planned mana source",
        ],
        "docs/audit_refactor_notes.md": ["rev0144", "tap event identity anchor", "tap_event_witness_source_mismatch"],
        "docs/architecture/audit_refactor_notes.md": ["rev0144", "tap event identity anchor", "tap_event_witness_source_mismatch"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0144",
            "test_tap_log_event_records_object_and_player_context",
            "tap_event_witness_source_mismatch",
        ],
        "README.md": ["rev0144", "Tap Event Identity Anchor", "tap_event_witness_source_mismatch"],
        "CHANGELOG.md": ["rev0144", "Tap Event Identity Anchor", "tap_event_witness_source_mismatch"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "tap_event_identity_anchor.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "tap_event_identity_anchor.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_mana_payment_payer_hash_scope_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0145 keeps automatic mana-payment plan hashes scoped by payer identity."""
    probes = {
        "include/mtgsim/types.hpp": [
            "payer-scoped automatic payment plan hash",
            "hash is payer-scoped",
            "ManaPaymentPlanRecord",
        ],
        "src/engine.cpp": [
            "MTGSim.ManaAutoPaymentPlan.v4",
            "mana_payment_plan_hash_from_records(PlayerId player_id",
            "hash_into(h, player_id)",
            "mana_payment_plan_hash_from_records(record.player",
        ],
        "src/validation.cpp": [
            "mana_payment_plan_record.identity_hash_mismatch",
            "mana_payment_plan_record.player_mismatch",
            "mana_change_record.plan_record_player_mismatch",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_auto_payment_plan_hash_is_payer_scoped_for_empty_plans",
            "payer-scoped identity payload",
            "p1_hash != p2_hash",
            "mana_payment_plan_record.identity_hash_mismatch",
        ],
        "docs/architecture/mana_payment_payer_hash_scope_rev0145.md": [
            "MTGSim.ManaAutoPaymentPlan.v4",
            "PlayerId",
            "payer-scoped plan hash",
            "identical empty plans",
        ],
        "docs/audit_refactor_notes.md": ["rev0145", "payer", "ManaAutoPaymentPlan.v4"],
        "docs/architecture/audit_refactor_notes.md": ["rev0145", "payer", "ManaAutoPaymentPlan.v4"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0145",
            "test_auto_payment_plan_hash_is_payer_scoped_for_empty_plans",
            "payer identity",
        ],
        "README.md": ["rev0145", "Mana Payment Payer Hash Scope", "ManaAutoPaymentPlan.v4"],
        "CHANGELOG.md": ["rev0145", "Mana Payment Payer Hash Scope", "ManaAutoPaymentPlan.v4"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_payer_hash_scope.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_payer_hash_scope.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_mana_payment_locked_step_guard_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0146 rejects contradictory locked-source/tap-step payment-plan evidence."""
    probes = {
        "include/mtgsim/types.hpp": [
            "locked_tap_sources",
            "rejects any tap-cost step",
            "same payment plan",
        ],
        "src/validation.cpp": [
            "mana_payment_plan_record.locked_source_used_as_tap_step",
            "locked.source == step.source",
            "locked.source_zone_change_index == step.source_zone_change_index",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_validator_rejects_payment_plan_locked_tap_source_reused_as_step",
            "repaired_hash",
            "mana_payment_plan_record.locked_source_used_as_tap_step",
        ],
        "docs/architecture/mana_payment_locked_step_guard_rev0146.md": [
            "Mana Payment Locked Step Guard",
            "locked_tap_sources",
            "locked_source_used_as_tap_step",
            "repairs the plan hash",
        ],
        "docs/audit_refactor_notes.md": ["rev0146", "locked_source_used_as_tap_step", "lock/step consistency"],
        "docs/architecture/audit_refactor_notes.md": ["rev0146", "locked_source_used_as_tap_step", "lock/step consistency"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0146",
            "test_validator_rejects_payment_plan_locked_tap_source_reused_as_step",
            "locked_source_used_as_tap_step",
        ],
        "README.md": ["rev0146", "Mana Payment Locked Step Guard", "locked_source_used_as_tap_step"],
        "CHANGELOG.md": ["rev0146", "Mana Payment Locked Step Guard", "locked_source_used_as_tap_step"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mana_payment_locked_step_guard.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mana_payment_locked_step_guard.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_tap_event_zone_snapshot_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0147 preserves zone-change identity on tap events used by payment-plan tap witnesses."""
    probes = {
        "include/mtgsim/types.hpp": [
            "object_zone_change_index",
            "tap EventRecord object/player/zone-change anchors",
            "tap_event_sequence automatic mana tap-event witness",
        ],
        "src/engine.cpp": [
            ".object_zone_change_index = obj.zone_change_index",
            "hash_into(h, value.object_zone_change_index)",
            "EventRecordLinks",
        ],
        "src/validation.cpp": [
            "event_record.tap_log_missing_object_zone_index",
            "mana_payment_plan_record.tap_event_witness_zone_index_mismatch",
            "tap_event_record->object_zone_change_index != step.source_zone_change_index",
        ],
        "tests/cpp/test_engine.cpp": [
            "tap log row should preserve the tapped object zone-change snapshot",
            "event_record.tap_log_missing_object_zone_index",
            "mana_payment_plan_record.tap_event_witness_zone_index_mismatch",
        ],
        "docs/architecture/tap_event_zone_snapshot_rev0147.md": [
            "Tap Event Zone Snapshot",
            "object_zone_change_index",
            "tap_event_witness_zone_index_mismatch",
            "zone-change snapshot",
        ],
        "docs/audit_refactor_notes.md": ["rev0147", "tap event zone snapshot", "tap_event_witness_zone_index_mismatch"],
        "docs/architecture/audit_refactor_notes.md": ["rev0147", "tap event zone snapshot", "tap_event_witness_zone_index_mismatch"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0147",
            "tap_event_witness_zone_index_mismatch",
            "event_record.tap_log_missing_object_zone_index",
        ],
        "README.md": ["rev0147", "Tap Event Zone Snapshot", "tap_event_witness_zone_index_mismatch"],
        "CHANGELOG.md": ["rev0147", "Tap Event Zone Snapshot", "tap_event_witness_zone_index_mismatch"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "tap_event_zone_snapshot.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "tap_event_zone_snapshot.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_paid_action_phase_receipts_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0149 paid-action phase receipts stay wired across records, engine, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": [
            "paid_action_phase_recorded",
            "stack_object_entered_sequence",
            "choices_locked_sequence",
            "first_mana_payment_plan_record_index",
            "first_paid_action_zone_change_record_index",
            "paid_action_zone_change_record_count",
            "rev0149 paid-action phase evidence",
        ],
        "src/engine.cpp": [
            "PaidActionPhaseSnapshot",
            "stack_enter_sequence_for_context",
            "first_event_sequence_at_or_after",
            "capture_paid_action_phase_snapshot",
            "seal_paid_action_phase",
            "paid_action_events_before_stack_placement",
            "\"loyalty_ability_put_on_stack\"",
        ],
        "src/validation.cpp": [
            "stack_placement_record.paid_phase_missing",
            "stack_placement_record.paid_phase_missing_mana_plan",
            "stack_placement_record.paid_phase_missing_sacrifice_zone_change",
            "stack_placement_record.paid_phase_missing_tap_witness",
            "stack_placement_record.paid_phase_stack_object_not_on_stack",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_paid_action_phase_records_sacrifice_spell_cost_span",
            "test_paid_action_phase_records_mana_and_tap_receipts_for_activated_ability",
            "test_paid_action_phase_records_loyalty_stack_before_counter_payment",
            "paid-action phase receipt",
        ],
        "docs/architecture/paid_action_phase_receipts_rev0149.md": [
            "Paid Action Phase Receipts",
            "StackPlacementRecord",
            "choices_locked_sequence",
            "paid_action_zone_change_record_count",
            "loyalty stack object",
        ],
        "docs/audit_refactor_notes.md": ["rev0149", "paid action phase receipts", "seal_paid_action_phase"],
        "docs/architecture/audit_refactor_notes.md": ["rev0149", "paid action phase receipts", "seal_paid_action_phase"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0149",
            "test_paid_action_phase_records_sacrifice_spell_cost_span",
            "test_paid_action_phase_records_mana_and_tap_receipts_for_activated_ability",
            "test_paid_action_phase_records_loyalty_stack_before_counter_payment",
        ],
        "README.md": ["rev0149", "Paid Phase Receipts", "StackPlacementRecord"],
        "CHANGELOG.md": ["rev0149", "Paid Phase Receipts", "paid-action phase receipts"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "paid_action_phase_receipts.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "paid_action_phase_receipts.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_paid_action_cost_witness_receipts_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0150 paid-action cost-witness receipts stay wired across records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": [
            "first_paid_action_counter_change_record_index",
            "paid_action_counter_change_record_count",
            "tap_cost_event_sequence",
        ],
        "src/engine.cpp": [
            "counter_change_count_before",
            "tap_cost_event_sequence",
            "event_record.object_zone_change_index == record.source_zone_change_index_before",
        ],
        "src/validation.cpp": [
            "stack_placement_record.paid_phase_missing_loyalty_counter_change",
            "stack_placement_record.paid_phase_loyalty_counter_kind_mismatch",
            "stack_placement_record.paid_phase_tap_witness_zone_index_mismatch",
            "stack_placement_record.invalid_paid_phase_counter_change_range",
        ],
        "tests/cpp/test_engine.cpp": [
            "tap_cost_event_sequence",
            "paid_action_counter_change_record_count",
            "validator should reject paid loyalty costs without a counter-change range",
            "validator should reject tap-cost witnesses for the wrong source incarnation",
        ],
        "docs/architecture/paid_action_cost_witness_receipts_rev0150.md": [
            "Paid Action Cost Witness Receipts",
            "tap_cost_event_sequence",
            "paid_action_counter_change_record_count",
            "loyalty counter-change range",
        ],
        "docs/audit_refactor_notes.md": ["rev0150", "paid action cost witness receipts", "tap_cost_event_sequence"],
        "docs/architecture/audit_refactor_notes.md": ["rev0150", "paid action cost witness receipts", "tap_cost_event_sequence"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0150",
            "tap_cost_event_sequence",
            "paid_action_counter_change_record_count",
            "stack_placement_record.paid_phase_missing_loyalty_counter_change",
        ],
        "README.md": ["rev0150", "Cost Witness Receipts", "tap_cost_event_sequence"],
        "CHANGELOG.md": ["rev0150", "Cost Witness Receipts", "paid action cost witness receipts"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "paid_action_cost_witness_receipts.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "paid_action_cost_witness_receipts.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_sacrifice_cost_witness_receipts_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0151 sacrifice-cost witness receipts stay wired across records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": [
            "first_sacrifice_cost_zone_change_record_index",
            "sacrifice_cost_zone_change_record_count",
            "sacrifice_cost_event_sequence",
            "rev0151 narrows sacrifice costs",
        ],
        "src/engine.cpp": [
            "zone_change_looks_like_sacrifice_cost",
            "seal_sacrifice_cost_witness",
            "sacrifice_cost_event_sequence",
            "pay_sacrifice_cost",
        ],
        "src/validation.cpp": [
            "stack_placement_record.missing_sacrifice_cost_zone_change_witness",
            "stack_placement_record.sacrifice_cost_zone_change_shape_mismatch",
            "stack_placement_record.missing_sacrifice_cost_event_witness",
            "stack_placement_record.invalid_sacrifice_cost_zone_change_range",
        ],
        "tests/cpp/test_engine.cpp": [
            "first_sacrifice_cost_zone_change_record_index",
            "sacrifice_cost_event_sequence",
            "validator should reject sacrifice-cost receipts without an exact sacrifice witness range",
            "validator should reject sacrifice-cost receipts without the pay_sacrifice_cost event witness",
        ],
        "docs/architecture/sacrifice_cost_witness_receipts_rev0151.md": [
            "Sacrifice Cost Witness Receipts",
            "first_sacrifice_cost_zone_change_record_index",
            "sacrifice_cost_event_sequence",
            "pay_sacrifice_cost",
        ],
        "docs/audit_refactor_notes.md": ["rev0151", "sacrifice cost witness receipts", "seal_sacrifice_cost_witness"],
        "docs/architecture/audit_refactor_notes.md": ["rev0151", "sacrifice cost witness receipts", "seal_sacrifice_cost_witness"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0151",
            "first_sacrifice_cost_zone_change_record_index",
            "sacrifice_cost_event_sequence",
            "stack_placement_record.missing_sacrifice_cost_zone_change_witness",
        ],
        "README.md": ["rev0151", "Sacrifice Cost Witnesses", "first_sacrifice_cost_zone_change_record_index"],
        "CHANGELOG.md": ["rev0151", "Sacrifice Cost Witnesses", "sacrifice cost witness receipts"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "sacrifice_cost_witness_receipts.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "sacrifice_cost_witness_receipts.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_nonmana_cost_receipt_transaction_spine_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0195 keeps typed nonmana/return-to-hand cost receipts on the paid-action transaction spine."""
    probes = {
        "include/mtgsim/types.hpp": [
            "kPaidActionDeclarationRecordSchemaVersion = 7U",
            "kPaidActionTransactionRecordSchemaVersion = 11U",
            "kPaidActionTransactionJournalSchemaVersion = 9U",
            "DiscardCostPaymentRecord",
            "TapCostPaymentRecord",
            "LifeCostPaymentRecord",
            "LoyaltyCostPaymentRecord",
            "ReturnCostPaymentRecord",
            "ReturnCostDefinition",
            "first_return_cost_payment_record_index",
            "return_cost_payment_hash",
            "return_cost_zone_change_record_count",
            "rev0195 adds a first-class return-to-hand cost receipt range",
        ],
        "include/mtgsim/engine.hpp": [
            "return_cost_payment_record_count",
            "latest_return_cost_payment_record",
            "return_cost_payment_record_hash",
        ],
        "src/engine.cpp": [
            "MTGSim.ReturnCostPaymentRecord.v1",
            "MTGSim.PaidActionDeclarationRecord.v7",
            "MTGSim.PaidActionTransactionRecord.v11",
            "MTGSim.PaidActionTransactionJournal.v9",
            "return_payment_first",
            "return_cost_payment_record_identity_hash",
            "pay_return_cost",
            'write_paid_action_declaration_snapshot_text(out, "committed_snapshot"',
        ],
        "src/validation.cpp": [
            "return_cost_payment_record.hash_mismatch",
            "return_cost_payment_record.zone_change_shape_mismatch",
            "return_cost_payment_record.event_witness_not_payment",
            "stack_placement_record.missing_return_cost_payment_hash",
            "stack_placement_record.missing_return_cost_event_witness",
            "paid_action_transaction_record.return_payment_hash_mismatch",
            "rollback_unexpected_return_payment_receipt",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_paid_action_phase_records_return_cost_for_activated_ability",
            "one typed return-cost payment receipt should be appended",
            "return_cost_payment_record.hash_mismatch",
            "stack_placement_record.missing_return_cost_payment_hash",
            "paid_action_transaction_record.return_payment_hash_mismatch",
            "PaidActionTransactionJournal.v9",
        ],
        "docs/architecture/return_cost_payment_receipt_spine_rev0195.md": [
            "Return Cost Payment Receipt Spine",
            "PaidActionTransactionJournal.v9",
            "return-to-hand cost receipt",
            "generic battlefield-to-hand movement",
        ],
        "docs/audit_refactor_notes.md": [
            "rev0195",
            "return-to-hand cost receipt",
            "PaidActionTransactionJournal.v9",
        ],
        "docs/architecture/audit_refactor_notes.md": [
            "rev0195",
            "return-to-hand cost receipt",
            "PaidActionTransactionJournal.v9",
        ],
        "data/rules/coverage/rules_ledger.json": [
            "rev0195",
            "ReturnCostPaymentRecord",
            "PaidActionTransactionJournal.v9",
            "test_paid_action_phase_records_return_cost_for_activated_ability",
        ],
        "README.md": ["rev0195", "Return Cost Receipt Gate", "PaidActionTransactionJournal.v9"],
        "CHANGELOG.md": ["rev0195", "Return Cost Receipt Gate", "return-to-hand costs"],
        "ARTIFACT_REPORT.md": ["rev0195", "Return Cost Receipt Gate", "ReturnCostPaymentRecord"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "nonmana_cost_receipt_transaction_spine.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "nonmana_cost_receipt_transaction_spine.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_choice_lock_receipts_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0152 choice-lock receipts stay wired across records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": [
            "first_choice_event_sequence",
            "last_choice_event_sequence",
            "choice_event_count",
            "rev0152 makes the choice-lock seam explicit",
        ],
        "src/engine.cpp": [
            "seal_choice_lock_witness",
            "event_record_is_paid_choice_lock",
            "record_event_with_links",
            "choice_event_count",
        ],
        "src/validation.cpp": [
            "stack_placement_record.missing_choice_lock_event_witness",
            "stack_placement_record.choice_lock_event_object_mismatch",
            "stack_placement_record.choice_lock_event_count_mismatch",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_paid_action_choice_lock_receipts_record_mode_and_target_events",
            "missing_choice_lock_event_witness",
            "choice_lock_event_object_mismatch",
        ],
        "docs/architecture/choice_lock_receipts_rev0152.md": [
            "Choice Lock Receipts",
            "first_choice_event_sequence",
            "choice_event_count",
            "seal_choice_lock_witness",
        ],
        "docs/audit_refactor_notes.md": ["rev0152", "choice lock receipts", "seal_choice_lock_witness"],
        "docs/architecture/audit_refactor_notes.md": ["rev0152", "choice lock receipts", "seal_choice_lock_witness"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0152",
            "test_paid_action_choice_lock_receipts_record_mode_and_target_events",
            "first_choice_event_sequence",
            "stack_placement_record.choice_lock_event_object_mismatch",
        ],
        "README.md": ["rev0152", "Choice Lock Receipts", "first_choice_event_sequence"],
        "CHANGELOG.md": ["rev0152", "Choice Lock Receipts", "choice lock receipts"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "choice_lock_receipts.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "choice_lock_receipts.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_choice_payload_anchors_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0153 choice payload anchors stay wired across records, validation, tests, docs, and ledger."""
    probes = {
        "include/mtgsim/types.hpp": [
            "choice_mode_index",
            "choice_target_count",
            "mode_choice_event_sequence",
            "target_choice_event_sequence",
            "rev0153 splits the generic choice span",
        ],
        "src/engine.cpp": [
            "choice_mode_index = links.choice_mode_index",
            "choice_target_count = links.choice_target_count",
            "choice_mode_index = mode_index",
            "choice_target_count = static_cast<u32>(stack_obj.targets.size())",
            "choice_target_count = static_cast<u32>(stamped_targets.size())",
            "mode_choice_event_sequence",
            "target_choice_event_sequence",
        ],
        "src/validation.cpp": [
            "stack_placement_record.missing_mode_choice_event_anchor",
            "stack_placement_record.missing_target_choice_event_anchor",
            "stack_placement_record.mode_choice_event_index_mismatch",
            "stack_placement_record.target_choice_event_count_mismatch",
            "stack_placement_record.target_choice_event_target_mismatch",
        ],
        "tests/cpp/test_engine.cpp": [
            "choice_mode_index == 1U",
            "choice_target_count == 1U",
            "missing_mode_choice_event_anchor",
            "target_choice_event_count_mismatch",
            "target_choice_event_target_mismatch",
        ],
        "docs/architecture/choice_payload_anchors_rev0153.md": [
            "Choice Payload Anchors",
            "EventRecord::choice_mode_index",
            "StackPlacementRecord::mode_choice_event_sequence",
            "target_choice_event_target_mismatch",
        ],
        "docs/audit_refactor_notes.md": ["rev0153", "choice payload anchors", "mode_choice_event_sequence"],
        "docs/architecture/audit_refactor_notes.md": ["rev0153", "choice payload anchors", "target_choice_event_sequence"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0153",
            "choice_mode_index",
            "choice_target_count",
            "mode_choice_event_sequence",
            "target_choice_event_sequence",
            "stack_placement_record.target_choice_event_target_mismatch",
        ],
        "README.md": ["rev0153", "Choice Payload Anchors", "choice_mode_index", "target_choice_event_sequence"],
        "CHANGELOG.md": ["rev0153", "Choice Payload Anchors", "choice payload anchors"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "choice_payload_anchors.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "choice_payload_anchors.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}


def audit_choice_anchor_hash_seal_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0154 choice payload/anchor fields are sealed into the Journal hash."""
    probes = {
        "src/engine.cpp": [
            "hash_into(h, value.choice_mode_index)",
            "hash_into(h, value.choice_target_count)",
            "hash_into(h, value.mode_choice_event_sequence)",
            "hash_into(h, value.target_choice_event_sequence)",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_choice_payload_and_anchor_fields_are_journal_hash_sealed",
            "journal hash should seal EventRecord::choice_mode_index payloads",
            "journal hash should seal EventRecord::choice_target_count payloads",
            "journal hash should seal StackPlacementRecord::mode_choice_event_sequence anchors",
            "journal hash should seal StackPlacementRecord::target_choice_event_sequence anchors",
        ],
        "docs/architecture/choice_anchor_hash_seal_rev0154.md": [
            "Choice Anchor Hash Seal",
            "EventRecord::choice_mode_index",
            "StackPlacementRecord::mode_choice_event_sequence",
            "journal_hash",
        ],
        "docs/audit_refactor_notes.md": ["rev0154", "choice anchor hash seal", "journal_hash"],
        "docs/architecture/audit_refactor_notes.md": ["rev0154", "choice anchor hash seal", "journal_hash"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0154",
            "test_choice_payload_and_anchor_fields_are_journal_hash_sealed",
            "choice anchor hash seal",
            "EventRecord::choice_mode_index",
            "StackPlacementRecord::target_choice_event_sequence",
        ],
        "README.md": ["rev0154", "Choice Anchor Hash Seal", "journal_hash"],
        "CHANGELOG.md": ["rev0154", "Choice Anchor Hash Seal", "choice anchor hash seal"],
        "ARTIFACT_REPORT.md": ["rev0154", "Choice Anchor Hash Seal", "331/331"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "choice_anchor_hash_seal.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "choice_anchor_hash_seal.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}




def audit_target_set_hash_witness_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0155 ordered target-set hash witnesses stay wired across the cube."""
    probes = {
        "include/mtgsim/types.hpp": [
            "choice_target_set_hash",
            "rev0155 extends target choices with an ordered target-set hash",
        ],
        "include/mtgsim/engine.hpp": [
            "target_choice_set_hash",
        ],
        "src/engine.cpp": [
            "target_choice_set_hash_impl",
            "hash_into(h, value.choice_target_set_hash)",
            "target_choice_set_hash_impl(stack_obj.targets)",
            "target_choice_set_hash_impl(stamped_targets)",
        ],
        "src/validation.cpp": [
            "stack_placement_record.choice_lock_target_event_missing_set_hash",
            "stack_placement_record.target_choice_event_set_hash_mismatch",
            "target_choice_set_hash(record.chosen_targets)",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_multi_target_choice_anchor_hashes_ordered_target_set",
            "choice_target_set_hash",
            "journal hash should seal EventRecord::choice_target_set_hash payloads",
            "validator should reject reordered chosen_targets",
        ],
        "docs/architecture/target_set_hash_witness_rev0155.md": [
            "Target Set Hash Witness",
            "EventRecord::choice_target_set_hash",
            "target_choice_set_hash",
            "stack_placement_record.target_choice_event_set_hash_mismatch",
        ],
        "docs/audit_refactor_notes.md": ["rev0155", "target set hash witness", "choice_target_set_hash"],
        "docs/architecture/audit_refactor_notes.md": ["rev0155", "target set hash witness", "choice_target_set_hash"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0155",
            "EventRecord::choice_target_set_hash",
            "test_multi_target_choice_anchor_hashes_ordered_target_set",
            "stack_placement_record.target_choice_event_set_hash_mismatch",
        ],
        "README.md": ["rev0155", "Target Set Hash Witness", "choice_target_set_hash"],
        "CHANGELOG.md": ["rev0155", "Target Set Hash Witness", "choice_target_set_hash"],
        "ARTIFACT_REPORT.md": ["rev0155", "Target Set Hash Witness", "332/332"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "target_set_hash_witness.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "target_set_hash_witness.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}



def audit_mode_contract_hash_witness_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that rev0156 selected-mode contract hash witnesses stay wired across the cube."""
    probes = {
        "include/mtgsim/types.hpp": [
            "choice_mode_contract_hash",
            "rev0156 extends mode choices with a selected-mode contract hash",
        ],
        "include/mtgsim/engine.hpp": [
            "mode_choice_contract_hash",
        ],
        "src/engine.cpp": [
            "mode_choice_contract_hash_impl",
            "hash_into(h, value.choice_mode_contract_hash)",
            "choice_mode_contract_hash = links.choice_mode_contract_hash",
            "mode_choice_contract_hash_impl(mode)",
        ],
        "src/validation.cpp": [
            "stack_placement_record.choice_lock_mode_event_missing_contract_hash",
            "stack_placement_record.mode_choice_event_contract_hash_mismatch",
            "mode_choice_contract_hash(def->modes",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_mode_choice_anchor_hashes_selected_mode_contract",
            "choice_mode_contract_hash",
            "journal hash should seal EventRecord::choice_mode_contract_hash payloads",
            "validator should reject choose_mode anchors whose contract hash disagrees with the selected mode definition",
        ],
        "docs/architecture/mode_contract_hash_witness_rev0156.md": [
            "Mode Contract Hash Witness",
            "EventRecord::choice_mode_contract_hash",
            "mode_choice_contract_hash",
            "stack_placement_record.mode_choice_event_contract_hash_mismatch",
        ],
        "docs/audit_refactor_notes.md": ["rev0156", "mode contract hash witness", "choice_mode_contract_hash"],
        "docs/architecture/audit_refactor_notes.md": ["rev0156", "mode contract hash witness", "choice_mode_contract_hash"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0156",
            "EventRecord::choice_mode_contract_hash",
            "test_mode_choice_anchor_hashes_selected_mode_contract",
            "stack_placement_record.mode_choice_event_contract_hash_mismatch",
        ],
        "README.md": ["rev0156", "Mode Contract Hash Witness", "choice_mode_contract_hash"],
        "CHANGELOG.md": ["rev0156", "Mode Contract Hash Witness", "choice_mode_contract_hash"],
        "ARTIFACT_REPORT.md": ["rev0156", "Mode Contract Hash Witness", "333/333"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "mode_contract_hash_witness.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "mode_contract_hash_witness.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit_sacrifice_attachment_order_wiring(root: pathlib.Path, issues: list[AuditIssue]) -> dict[str, Any]:
    """Check that the rev0135 attachment-safe sacrifice payment order remains wired."""
    probes = {
        "src/engine.cpp": [
            "order_sacrifice_cost_objects_for_payment",
            "selected_attachment_depth",
            "pay_selected_sacrifice_cost",
        ],
        "tests/cpp/test_engine.cpp": [
            "test_sacrifice_cost_orders_attached_permanents_before_enchanted_sources",
            "attachment-safe payment order",
            "Aura should be sacrificed explicitly",
        ],
        "docs/architecture/sacrifice_attachment_order_rev0135.md": [
            "order_sacrifice_cost_objects_for_payment",
            "attached Aura",
            "enchanted permanent",
            "paid-action transaction",
        ],
        "docs/audit_refactor_notes.md": ["rev0135", "attachment-safe sacrifice order", "selected_attachment_depth"],
        "docs/architecture/audit_refactor_notes.md": ["rev0135", "attachment-safe sacrifice order", "selected_attachment_depth"],
        "data/rules/coverage/rules_ledger.json": [
            "rev0135",
            "test_sacrifice_cost_orders_attached_permanents_before_enchanted_sources",
            "attachment-safe sacrifice order",
        ],
        "README.md": ["rev0135", "Attached Sacrifice Order", "attachment-safe sacrifice order"],
        "CHANGELOG.md": ["rev0135", "Attached Sacrifice Order", "attachment-safe sacrifice order"],
    }
    probe_results: dict[str, dict[str, bool]] = {}
    for relpath, needles in probes.items():
        path = root / relpath
        if not path.exists():
            add(issues, "error", "sacrifice_attachment_order.probe_file_missing", relpath)
            probe_results[relpath] = {needle: False for needle in needles}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        probe_results[relpath] = {}
        for needle in needles:
            ok = needle in text
            probe_results[relpath][needle] = ok
            if not ok:
                add(issues, "error", "sacrifice_attachment_order.wiring_missing", f"{relpath} missing {needle!r}")
    return {"probes": probe_results}

def audit(root: pathlib.Path = ROOT, exe: pathlib.Path | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    issues: list[AuditIssue] = []
    revision = audit_revision(root, issues)
    revision_identity = audit_revision_identity(root, issues, revision)
    build_budget_guard = audit_build_budget_guard(root, issues)
    audit_official_rules_policy(root, issues)
    audit_filesystem_payload(root, issues)
    audit_python_syntax(root, issues)
    cpp_tests = audit_cpp_test_binary(root, issues, exe)
    ledger_alignment = audit_rule_ledger_alignment(root, issues, revision, cpp_tests)
    scenarios = audit_scenario_files(root, issues)
    fuzz_wiring = audit_fuzz_wiring(root, issues)
    trigger_wiring = audit_trigger_wiring(root, issues)
    prevention_wiring = audit_prevention_wiring(root, issues)
    zone_change_replacement_wiring = audit_zone_change_replacement_wiring(root, issues)
    zone_change_record_wiring = audit_zone_change_record_wiring(root, issues)
    zone_replacement_record_wiring = audit_zone_replacement_record_wiring(root, issues)
    damage_record_wiring = audit_damage_record_wiring(root, issues)
    damage_prevention_record_wiring = audit_damage_prevention_record_wiring(root, issues)
    life_change_record_wiring = audit_life_change_record_wiring(root, issues)
    mana_change_record_wiring = audit_mana_change_record_wiring(root, issues)
    counter_change_record_wiring = audit_counter_change_record_wiring(root, issues)
    discard_record_wiring = audit_discard_record_wiring(root, issues)
    action_receipt_wiring = audit_action_receipt_wiring(root, issues)
    transition_result_wiring = audit_transition_result_wiring(root, issues)
    action_trace_wiring = audit_action_trace_wiring(root, issues)
    choice_request_queue_wiring = audit_choice_request_queue_wiring(root, issues)
    legal_action_frontier_wiring = audit_legal_action_frontier_wiring(root, issues)
    state_checkpoint_wiring = audit_state_checkpoint_wiring(root, issues)
    state_core_snapshot_wiring = audit_state_core_snapshot_wiring(root, issues)
    cli_replay_artifact_wiring = audit_cli_replay_artifact_wiring(root, issues)
    replay_bundle_manifest_wiring = audit_replay_bundle_manifest_wiring(root, issues)
    replay_bundle_diagnostics_wiring = audit_replay_bundle_diagnostics_wiring(root, issues)
    replay_bundle_prefix_wiring = audit_replay_bundle_prefix_wiring(root, issues)
    replay_bundle_resume_wiring = audit_replay_bundle_resume_wiring(root, issues)
    trigger_record_wiring = audit_trigger_record_wiring(root, issues)
    event_record_wiring = audit_event_record_wiring(root, issues)
    draw_record_wiring = audit_draw_record_wiring(root, issues)
    mulligan_record_wiring = audit_mulligan_record_wiring(root, issues)
    mulligan_keep_record_wiring = audit_mulligan_keep_record_wiring(root, issues)
    stack_placement_record_wiring = audit_stack_placement_record_wiring(root, issues)
    stack_resolution_record_wiring = audit_stack_resolution_record_wiring(root, issues)
    priority_transition_record_wiring = audit_priority_transition_record_wiring(root, issues)
    state_based_action_record_wiring = audit_state_based_action_record_wiring(root, issues)
    combat_declaration_record_wiring = audit_combat_declaration_record_wiring(root, issues)
    combat_damage_assignment_record_wiring = audit_combat_damage_assignment_record_wiring(root, issues)
    destroy_regeneration_wiring = audit_destroy_regeneration_wiring(root, issues)
    counter_wiring = audit_counter_wiring(root, issues)
    keyword_wiring = audit_keyword_wiring(root, issues)
    attachment_wiring = audit_attachment_wiring(root, issues)
    token_exile_sacrifice_wiring = audit_token_exile_sacrifice_wiring(root, issues)
    planeswalker_loyalty_wiring = audit_planeswalker_loyalty_wiring(root, issues)
    battle_wiring = audit_battle_wiring(root, issues)
    modal_wiring = audit_modal_wiring(root, issues)
    timing_land_wiring = audit_timing_land_wiring(root, issues)
    activated_ability_wiring = audit_activated_ability_wiring(root, issues)
    mana_ability_payment_wiring = audit_mana_ability_payment_wiring(root, issues)
    sacrifice_cost_wiring = audit_sacrifice_cost_wiring(root, issues)
    static_effect_wiring = audit_static_effect_wiring(root, issues)
    temporary_continuous_wiring = audit_temporary_continuous_wiring(root, issues)
    copy_effect_wiring = audit_copy_effect_wiring(root, issues)
    layer_timestamp_wiring = audit_layer_timestamp_wiring(root, issues)
    layer_dependency_wiring = audit_layer_dependency_wiring(root, issues)
    target_identity_wiring = audit_target_identity_wiring(root, issues)
    multitarget_resolution_wiring = audit_multitarget_resolution_wiring(root, issues)
    stack_counterspell_wiring = audit_stack_counterspell_wiring(root, issues)
    type_color_layer_wiring = audit_type_color_layer_wiring(root, issues)
    control_change_wiring = audit_control_change_wiring(root, issues)
    test_matrix_inventory = audit_test_matrix_inventory(root, issues)
    card_db_wiring = audit_card_db_wiring(root, issues)
    paid_action_transaction_wiring = audit_paid_action_transaction_wiring(root, issues)
    sacrifice_attachment_order_wiring = audit_sacrifice_attachment_order_wiring(root, issues)
    attack_tap_cost_lock_wiring = audit_attack_tap_cost_lock_wiring(root, issues)
    mana_payment_plan_evidence_wiring = audit_mana_payment_plan_evidence_wiring(root, issues)
    mana_payment_plan_hash_wiring = audit_mana_payment_plan_hash_wiring(root, issues)
    mana_payment_plan_record_wiring = audit_mana_payment_plan_record_wiring(root, issues)
    mana_payment_plan_step_witness_wiring = audit_mana_payment_plan_step_witness_wiring(root, issues)
    mana_payment_producer_backlink_wiring = audit_mana_payment_producer_backlink_wiring(root, issues)
    mana_payment_tap_witness_wiring = audit_mana_payment_tap_witness_wiring(root, issues)
    mana_payment_pool_span_wiring = audit_mana_payment_pool_span_wiring(root, issues)
    tap_event_identity_anchor_wiring = audit_tap_event_identity_anchor_wiring(root, issues)
    mana_payment_payer_hash_scope_wiring = audit_mana_payment_payer_hash_scope_wiring(root, issues)
    mana_payment_locked_step_guard_wiring = audit_mana_payment_locked_step_guard_wiring(root, issues)
    tap_event_zone_snapshot_wiring = audit_tap_event_zone_snapshot_wiring(root, issues)
    paid_action_phase_receipts_wiring = audit_paid_action_phase_receipts_wiring(root, issues)
    paid_action_cost_witness_receipts_wiring = audit_paid_action_cost_witness_receipts_wiring(root, issues)
    sacrifice_cost_witness_receipts_wiring = audit_sacrifice_cost_witness_receipts_wiring(root, issues)
    nonmana_cost_receipt_transaction_spine_wiring = audit_nonmana_cost_receipt_transaction_spine_wiring(root, issues)
    choice_lock_receipts_wiring = audit_choice_lock_receipts_wiring(root, issues)
    choice_payload_anchors_wiring = audit_choice_payload_anchors_wiring(root, issues)
    choice_anchor_hash_seal_wiring = audit_choice_anchor_hash_seal_wiring(root, issues)
    target_set_hash_witness_wiring = audit_target_set_hash_witness_wiring(root, issues)
    mode_contract_hash_witness_wiring = audit_mode_contract_hash_witness_wiring(root, issues)
    errors = sum(1 for issue in issues if issue.severity == "error")
    warnings = sum(1 for issue in issues if issue.severity == "warning")
    return {
        "schema": "mtgsim.datacube_audit.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "duration_sec": time.perf_counter() - started,
        "root": str(root),
        "status": "passed" if errors == 0 else "failed",
        "summary": {
            "issues": len(issues),
            "errors": errors,
            "warnings": warnings,
            "cpp_tests": cpp_tests,
            "revision_identity": revision_identity,
            "build_budget_guard": build_budget_guard,
            "ledger_alignment": ledger_alignment,
            "scenarios": scenarios,
            "fuzz_wiring": fuzz_wiring,
            "trigger_wiring": trigger_wiring,
            "prevention_wiring": prevention_wiring,
            "zone_change_replacement_wiring": zone_change_replacement_wiring,
            "zone_change_record_wiring": zone_change_record_wiring,
            "zone_replacement_record_wiring": zone_replacement_record_wiring,
            "damage_record_wiring": damage_record_wiring,
            "damage_prevention_record_wiring": damage_prevention_record_wiring,
            "life_change_record_wiring": life_change_record_wiring,
            "mana_change_record_wiring": mana_change_record_wiring,
            "counter_change_record_wiring": counter_change_record_wiring,
            "discard_record_wiring": discard_record_wiring,
            "action_receipt_wiring": action_receipt_wiring,
            "transition_result_wiring": transition_result_wiring,
            "action_trace_wiring": action_trace_wiring,
            "choice_request_queue_wiring": choice_request_queue_wiring,
            "legal_action_frontier_wiring": legal_action_frontier_wiring,
            "state_checkpoint_wiring": state_checkpoint_wiring,
            "state_core_snapshot_wiring": state_core_snapshot_wiring,
            "cli_replay_artifact_wiring": cli_replay_artifact_wiring,
            "replay_bundle_manifest_wiring": replay_bundle_manifest_wiring,
            "replay_bundle_diagnostics_wiring": replay_bundle_diagnostics_wiring,
            "replay_bundle_prefix_wiring": replay_bundle_prefix_wiring,
            "replay_bundle_resume_wiring": replay_bundle_resume_wiring,
            "trigger_record_wiring": trigger_record_wiring,
            "event_record_wiring": event_record_wiring,
            "draw_record_wiring": draw_record_wiring,
            "mulligan_record_wiring": mulligan_record_wiring,
            "mulligan_keep_record_wiring": mulligan_keep_record_wiring,
            "stack_placement_record_wiring": stack_placement_record_wiring,
            "stack_resolution_record_wiring": stack_resolution_record_wiring,
            "priority_transition_record_wiring": priority_transition_record_wiring,
            "state_based_action_record_wiring": state_based_action_record_wiring,
            "combat_declaration_record_wiring": combat_declaration_record_wiring,
            "combat_damage_assignment_record_wiring": combat_damage_assignment_record_wiring,
            "destroy_regeneration_wiring": destroy_regeneration_wiring,
            "counter_wiring": counter_wiring,
            "keyword_wiring": keyword_wiring,
            "attachment_wiring": attachment_wiring,
            "token_exile_sacrifice_wiring": token_exile_sacrifice_wiring,
            "planeswalker_loyalty_wiring": planeswalker_loyalty_wiring,
            "battle_wiring": battle_wiring,
            "modal_wiring": modal_wiring,
            "timing_land_wiring": timing_land_wiring,
            "activated_ability_wiring": activated_ability_wiring,
            "mana_ability_payment_wiring": mana_ability_payment_wiring,
            "sacrifice_cost_wiring": sacrifice_cost_wiring,
            "static_effect_wiring": static_effect_wiring,
            "temporary_continuous_wiring": temporary_continuous_wiring,
            "copy_effect_wiring": copy_effect_wiring,
            "layer_timestamp_wiring": layer_timestamp_wiring,
            "layer_dependency_wiring": layer_dependency_wiring,
            "target_identity_wiring": target_identity_wiring,
            "multitarget_resolution_wiring": multitarget_resolution_wiring,
            "stack_counterspell_wiring": stack_counterspell_wiring,
            "type_color_layer_wiring": type_color_layer_wiring,
            "control_change_wiring": control_change_wiring,
            "test_matrix_inventory": test_matrix_inventory,
            "card_db_wiring": card_db_wiring,
            "paid_action_transaction_wiring": paid_action_transaction_wiring,
            "sacrifice_attachment_order_wiring": sacrifice_attachment_order_wiring,
            "attack_tap_cost_lock_wiring": attack_tap_cost_lock_wiring,
            "mana_payment_plan_evidence_wiring": mana_payment_plan_evidence_wiring,
            "mana_payment_plan_hash_wiring": mana_payment_plan_hash_wiring,
            "mana_payment_plan_record_wiring": mana_payment_plan_record_wiring,
            "mana_payment_plan_step_witness_wiring": mana_payment_plan_step_witness_wiring,
            "mana_payment_producer_backlink_wiring": mana_payment_producer_backlink_wiring,
            "mana_payment_tap_witness_wiring": mana_payment_tap_witness_wiring,
            "mana_payment_pool_span_wiring": mana_payment_pool_span_wiring,
            "tap_event_identity_anchor_wiring": tap_event_identity_anchor_wiring,
            "mana_payment_payer_hash_scope_wiring": mana_payment_payer_hash_scope_wiring,
            "mana_payment_locked_step_guard_wiring": mana_payment_locked_step_guard_wiring,
            "tap_event_zone_snapshot_wiring": tap_event_zone_snapshot_wiring,
            "paid_action_phase_receipts_wiring": paid_action_phase_receipts_wiring,
            "paid_action_cost_witness_receipts_wiring": paid_action_cost_witness_receipts_wiring,
            "sacrifice_cost_witness_receipts_wiring": sacrifice_cost_witness_receipts_wiring,
            "nonmana_cost_receipt_transaction_spine_wiring": nonmana_cost_receipt_transaction_spine_wiring,
            "choice_lock_receipts_wiring": choice_lock_receipts_wiring,
            "choice_payload_anchors_wiring": choice_payload_anchors_wiring,
            "choice_anchor_hash_seal_wiring": choice_anchor_hash_seal_wiring,
            "target_set_hash_witness_wiring": target_set_hash_witness_wiring,
            "mode_contract_hash_witness_wiring": mode_contract_hash_witness_wiring,
        },
        "issues": [asdict(issue) for issue in issues],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=pathlib.Path, default=ROOT)
    parser.add_argument("--test-exe", type=pathlib.Path, default=None)
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "datacube_audit_latest.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    exe = args.test_exe
    if exe is not None and not exe.is_absolute():
        exe = root / exe
    report = audit(root, exe)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(args.report.parent / "datacube_audit_history.jsonl", compact_history_record(report, args.report, root))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(f"datacube audit: status={report['status']} errors={summary['errors']} warnings={summary['warnings']} report={rel(args.report, root)}")
        for issue in report["issues"][:20]:
            print(f"{issue['severity'].upper()} {issue['code']}: {issue['detail']}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

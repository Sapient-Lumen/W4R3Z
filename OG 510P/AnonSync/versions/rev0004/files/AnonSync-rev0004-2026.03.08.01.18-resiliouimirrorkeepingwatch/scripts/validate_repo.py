#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def validate_json_schemas() -> list[str]:
    errors: list[str] = []
    pairs = [
        ("metadata/project-state.json", "schemas/project-state.schema.json"),
        ("metadata/link-registry.json", "schemas/link-registry.schema.json"),
        ("config/resource-profiles.yaml", "schemas/resource-profiles.schema.json"),
        ("config/discovery-policy.yaml", "schemas/discovery-policy.schema.json"),
    ]
    for data_rel, schema_rel in pairs:
        data_path = ROOT / data_rel
        if data_path.suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(data_path.read_text(encoding="utf-8"))
        else:
            data = load_json(data_path)
        schema = load_json(ROOT / schema_rel)
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{data_rel}: {exc.message}")
    return errors

def validate_required_files() -> list[str]:
    errors: list[str] = []
    required = [
        "README.md",
        "MUST_READ_FIRST.md",
        "AGENTS.md",
        "PROJECT_CHARTER.md",
        "ROADMAP.md",
        "docs/context/current-brief.md",
        "docs/runbooks/llm-runbook.md",
        "metadata/project-state.json",
        "metadata/link-registry.json",
        "config/resource-profiles.yaml",
        "config/discovery-policy.yaml",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")
    return errors

def validate_toml_and_yaml() -> list[str]:
    errors: list[str] = []
    for path in list(ROOT.rglob("*.toml")):
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - broad by design for validation
            errors.append(f"{path.relative_to(ROOT)} TOML parse error: {exc}")
    for path in list(ROOT.rglob("*.yml")) + list(ROOT.rglob("*.yaml")):
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - broad by design for validation
            errors.append(f"{path.relative_to(ROOT)} YAML parse error: {exc}")
    return errors

def validate_project_state_links() -> list[str]:
    errors: list[str] = []
    state = load_json(ROOT / "metadata/project-state.json")
    for rel in state["top_level_must_reads"]:
        if not (ROOT / rel).exists():
            errors.append(f"project-state top_level_must_reads missing file: {rel}")
    return errors

def run_link_check() -> list[str]:
    command = [sys.executable, str(ROOT / "scripts" / "check_links.py")]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return [line.removeprefix("ERROR: ").strip() for line in result.stdout.splitlines() if line.strip()]
    return []

def main() -> int:
    errors: list[str] = []
    errors.extend(validate_json_schemas())
    errors.extend(validate_required_files())
    errors.extend(validate_toml_and_yaml())
    errors.extend(validate_project_state_links())
    errors.extend(run_link_check())

    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

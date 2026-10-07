#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, json, re, sys
from collections import Counter
from pathlib import Path


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def parse_scalar(raw: str):
    v = raw.strip()
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1]
    low = v.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?\d+", v):
        try:
            return int(v)
        except ValueError:
            pass
    return v


def parse_frontmatter(p: Path) -> dict:
    txt = read_text(p)
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return {}
    out: dict[str, object] = {}
    current_key = None
    current_list: list[object] = []
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):
            if current_key is not None:
                current_list.append(parse_scalar(line[4:]))
            continue
        if current_key is not None:
            out[current_key] = current_list
            current_key = None
            current_list = []
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if v == "":
                current_key = k
                current_list = []
            else:
                out[k] = parse_scalar(v)
    if current_key is not None:
        out[current_key] = current_list
    return out


def csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def csv_header(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            return next(reader)
        except StopIteration:
            return []


def type_ok(value, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str) and value.strip() != ""
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "date-string":
        return isinstance(value, str) and re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", value) is not None
    if expected == "list[string]":
        return isinstance(value, list) and len(value) > 0 and all(isinstance(x, str) and x.strip() for x in value)
    return True


def validate_frontmatter(root: Path, contract: dict) -> list[dict]:
    findings = []
    schemas = contract.get("schemas", {})
    targets = [
        ("living_christ_figures_candidate_v1", [p for p in (root / "CANDIDATES").glob("*.txt") if not p.name.startswith("_REFRESH")]),
        ("living_christ_figures_office_card_v1", list((root / "OFFICE-CARDS").glob("*.txt"))),
        ("living_christ_figures_refresh_note_v1", list((root / "CANDIDATES").glob("_REFRESH*.txt"))),
    ]
    for schema_id, paths in targets:
        spec = schemas.get(schema_id, {})
        required = spec.get("required_fields", {})
        patterns = spec.get("patterns", {})
        invariants = spec.get("package_invariants", {})
        for p in paths:
            fm = parse_frontmatter(p)
            rel = str(p.relative_to(root))
            if not fm:
                findings.append({"severity": "high", "check": "frontmatter_present", "file": rel, "detail": "missing or unparsable front matter"})
                continue
            for field, typ in required.items():
                if field not in fm:
                    findings.append({"severity": "high", "check": "frontmatter_required_field", "file": rel, "detail": f"missing {field}"})
                elif not type_ok(fm[field], typ):
                    findings.append({"severity": "high", "check": "frontmatter_type", "file": rel, "detail": f"{field} expected {typ}, got {type(fm[field]).__name__}"})
            for field, expected in invariants.items():
                if fm.get(field) != expected:
                    findings.append({"severity": "high", "check": "frontmatter_invariant", "file": rel, "detail": f"{field}={fm.get(field)!r} expected {expected!r}"})
            for field, pat in patterns.items():
                if field.endswith("[]"):
                    base = field[:-2]
                    for item in fm.get(base, []) if isinstance(fm.get(base), list) else []:
                        if not re.fullmatch(pat, str(item)):
                            findings.append({"severity": "high", "check": "frontmatter_pattern", "file": rel, "detail": f"{base} item {item!r} fails {pat}"})
                else:
                    val = fm.get(field)
                    if val is not None and not re.fullmatch(pat, str(val)):
                        findings.append({"severity": "high", "check": "frontmatter_pattern", "file": rel, "detail": f"{field}={val!r} fails {pat}"})
    return findings


def validate_ledger_contract(root: Path, contract: dict) -> list[dict]:
    findings = []
    for rel, spec in contract.get("ledgers", {}).items():
        p = root / rel
        if not p.exists():
            findings.append({"severity": "high", "check": "ledger_exists", "file": rel, "detail": "missing"})
            continue
        got = csv_header(p)
        expected = spec.get("columns", [])
        if got != expected:
            findings.append({"severity": "high", "check": "ledger_header", "file": rel, "detail": f"header drift: got {got}, expected {expected}"})
        mirror = spec.get("json_mirror")
        if mirror:
            jp = root / mirror
            if not jp.exists():
                findings.append({"severity": "high", "check": "json_mirror_exists", "file": mirror, "detail": f"missing JSON mirror for {rel}"})
            else:
                try:
                    data = json.loads(jp.read_text(encoding="utf-8"))
                    rows = csv_rows(p)
                    if not isinstance(data, list):
                        findings.append({"severity": "high", "check": "json_mirror_type", "file": mirror, "detail": "JSON mirror is not a list"})
                    elif len(data) != len(rows):
                        findings.append({"severity": "high", "check": "json_mirror_row_count", "file": mirror, "detail": f"{len(data)} JSON rows != {len(rows)} CSV rows"})
                    elif rows:
                        csv_keys = set(rows[0].keys())
                        bad = [i for i, row in enumerate(data[:20]) if set(row.keys()) != csv_keys]
                        if bad:
                            findings.append({"severity": "high", "check": "json_mirror_keys", "file": mirror, "detail": f"row key mismatch at rows {bad[:5]}"})
                except Exception as e:
                    findings.append({"severity": "high", "check": "json_mirror_parse", "file": mirror, "detail": str(e)})
    return findings


def validate_source_vocabulary(root: Path) -> list[dict]:
    findings = []
    vocab_path = root / "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv"
    if not vocab_path.exists():
        return [{"severity": "high", "check": "source_type_vocab_exists", "file": str(vocab_path.relative_to(root)), "detail": "missing"}]
    vocab = csv_rows(vocab_path)
    source_rows = csv_rows(root / "Source-Registry-current.csv")
    mapped = {r.get("source_type", ""): r for r in vocab}
    got = Counter(r.get("source_type", "") for r in source_rows)
    for st, count in got.items():
        row = mapped.get(st)
        if row is None:
            findings.append({"severity": "high", "check": "source_type_mapped", "file": "Source-Registry-current.csv", "detail": f"{st!r} appears {count} times but is absent from controlled vocabulary"})
        elif row.get("rev0031_action") != "mapped" or row.get("normalized_source_class") in {"", "UNMAPPED"}:
            findings.append({"severity": "high", "check": "source_type_mapped", "file": "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv", "detail": f"{st!r} is not mapped"})
    extras = sorted(set(mapped) - set(got))
    for st in extras:
        if st:
            findings.append({"severity": "low", "check": "source_type_vocab_extra", "file": "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv", "detail": f"{st!r} is mapped but not currently used"})
    return findings


def validate_public_manifest(root: Path) -> list[dict]:
    findings = []
    manifest_path = root / "manifest.json"
    public_manifest_path = root / "PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        public_manifest = json.loads(public_manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [{"severity": "high", "check": "manifest_parse", "file": "manifest/public manifest", "detail": str(e)}]
    if public_manifest.get("revision") != manifest.get("revision"):
        findings.append({"severity": "high", "check": "public_manifest_revision", "file": "PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json", "detail": f"public revision {public_manifest.get('revision')} != manifest revision {manifest.get('revision')}"})
    allowed = set((root / "SCHEMA/Package-Release-Contract-current.json").exists() and json.loads((root / "SCHEMA/Package-Release-Contract-current.json").read_text(encoding="utf-8")).get("allowed_public_layer_files", []) or [])
    if allowed:
        actual = {str(p.relative_to(root)) for p in (root / "PUBLIC").glob("*") if p.is_file()}
        extra = sorted(actual - allowed)
        missing = sorted(allowed - actual)
        if extra:
            findings.append({"severity": "medium", "check": "public_layer_extra_files", "file": "PUBLIC/", "detail": "; ".join(extra)})
        if missing:
            findings.append({"severity": "high", "check": "public_layer_missing_files", "file": "PUBLIC/", "detail": "; ".join(missing)})
    return findings


def validate_required_schema_files(root: Path) -> list[dict]:
    required = [
        "SCHEMA/README-schema-current.md",
        "SCHEMA/Frontmatter-Contract-current.json",
        "SCHEMA/Ledger-Contract-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.md",
        "SCHEMA/Package-Release-Contract-current.json",
        "SCHEMA/Schema-Validation-Report-current.csv",
        "SCHEMA/Schema-Validation-Report-current.json",
        "SCHEMA/Schema-Validation-Report-current.md",
    ]
    findings = []
    for rel in required:
        if not (root / rel).exists():
            findings.append({"severity": "high", "check": "schema_file_exists", "file": rel, "detail": "missing"})
    return findings


def run(root: Path) -> list[dict]:
    findings = []
    # Some report files are generated after the first pass; don't require them until write_report has run.
    for rel in [
        "SCHEMA/README-schema-current.md",
        "SCHEMA/Frontmatter-Contract-current.json",
        "SCHEMA/Ledger-Contract-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.md",
        "SCHEMA/Package-Release-Contract-current.json",
    ]:
        if not (root / rel).exists():
            findings.append({"severity": "high", "check": "schema_file_exists", "file": rel, "detail": "missing"})
    if findings:
        return findings
    front = json.loads((root / "SCHEMA/Frontmatter-Contract-current.json").read_text(encoding="utf-8"))
    ledgers = json.loads((root / "SCHEMA/Ledger-Contract-current.json").read_text(encoding="utf-8"))
    findings += validate_frontmatter(root, front)
    findings += validate_ledger_contract(root, ledgers)
    findings += validate_source_vocabulary(root)
    findings += validate_public_manifest(root)
    return findings


def write_report(root: Path, findings: list[dict]):
    report_rows = findings
    if not report_rows:
        report_rows = [{"severity": "info", "check": "schema_validation", "file": ".", "detail": "PASS schema/frontmatter/ledger/source-type/public-manifest contract checks"}]
    fields = ["severity", "check", "file", "detail"]
    csv_path = root / "SCHEMA/Schema-Validation-Report-current.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in report_rows:
            w.writerow({k: r.get(k, "") for k in fields})
    (root / "SCHEMA/Schema-Validation-Report-current.json").write_text(json.dumps(report_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    high = [r for r in findings if r.get("severity") == "high"]
    med = [r for r in findings if r.get("severity") == "medium"]
    low = [r for r in findings if r.get("severity") == "low"]
    lines = [
        "# Schema Validation Report — current",
        "",
        f"High findings: {len(high)}",
        f"Medium findings: {len(med)}",
        f"Low findings: {len(low)}",
        "",
    ]
    if findings:
        lines += ["## Findings", ""]
        for r in findings:
            lines.append(f"- **{r.get('severity')}** `{r.get('check')}` `{r.get('file')}` — {r.get('detail')}")
    else:
        lines.append("PASS: schema/frontmatter/ledger/source-type/public-manifest contract checks.")
    (root / "SCHEMA/Schema-Validation-Report-current.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--write-report", action="store_true")
    ap.add_argument("--fail-on-high", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    findings = run(root)
    if args.write_report:
        write_report(root, findings)
    high = [r for r in findings if r.get("severity") == "high"]
    if findings:
        for r in findings[:50]:
            print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('file')}: {r.get('detail')}")
        if len(findings) > 50:
            print(f"... {len(findings)-50} more findings")
    else:
        print("PASS schema/frontmatter/ledger/source-type/public-manifest contract checks")
    if args.fail_on_high and high:
        sys.exit(1)


if __name__ == "__main__":
    main()

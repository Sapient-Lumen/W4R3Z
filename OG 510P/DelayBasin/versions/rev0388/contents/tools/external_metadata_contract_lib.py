import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

REV_RE = re.compile(r"rev\d{4}")
BUNDLE_RE = re.compile(r"DelayBasin-rev\d{4}-[^\s`\"']+?\.zip")
EXTERNAL_METADATA_SURFACES = ["LICENSE", "CITATION.cff", "codemeta.json", "ro-crate-metadata.json", "SBOM.spdx.json"]


def _load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _status(observed: Any, expected: Any) -> str:
    return "pass" if observed == expected else "fail"


def release_identity(root: pathlib.Path) -> dict[str, str]:
    manifest = _load_json(root, "RELEASE-MANIFEST.json")
    receipt = _load_json(root, "REVISION-RECEIPT.json")
    stamp = manifest.get("timestamp") or receipt.get("stamp")
    updated_at = receipt.get("updated_at") or receipt.get("created_at")
    if not isinstance(stamp, str):
        raise ValueError("release manifest missing timestamp")
    if not isinstance(updated_at, str):
        raise ValueError("revision receipt missing updated_at/created_at")
    try:
        local_dt = datetime.strptime(stamp, "%Y.%m.%d.%H.%M")
    except ValueError as exc:
        raise ValueError(f"invalid release timestamp {stamp!r}") from exc
    try:
        receipt_dt = datetime.fromisoformat(updated_at)
    except ValueError as exc:
        raise ValueError(f"invalid receipt timestamp {updated_at!r}") from exc
    if receipt_dt.tzinfo is None:
        raise ValueError("receipt timestamp must include an offset")
    return {
        "revision": manifest["revision"],
        "bundle": manifest["bundle"],
        "stamp": stamp,
        "release_date": local_dt.date().isoformat(),
        "created_utc": receipt_dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z",
    }


def expected_external_metadata(root: pathlib.Path) -> dict[str, str]:
    identity = release_identity(root)
    revision = identity["revision"]
    bundle = identity["bundle"]
    release_date = identity["release_date"]
    created_utc = identity["created_utc"]
    contributor = "DelayBasin project contributors"
    description = f"DelayBasin research archive release {revision}, packaged as {bundle}."
    license_text = (
        f"DelayBasin research archive release {revision}\n\n"
        f"This package identifies the frozen citable archive bundle `{bundle}`.\n\n"
        "The archive is provided as research material and method provenance. No warranty is made about completeness, fitness for a particular purpose, or legal status.\n"
    )
    citation = (
        "cff-version: 1.2.0\n"
        "authors:\n"
        f"  - name: \"{contributor}\"\n"
        "title: DelayBasin research archive\n"
        "message: \"Cite the frozen package identity for this DelayBasin archive release.\"\n"
        "type: dataset\n"
        f"version: {revision}\n"
        f"date-released: \"{release_date}\"\n"
        "identifiers:\n"
        "  - type: other\n"
        f"    value: {bundle}\n"
        f"abstract: \"{description}\"\n"
    )
    codemeta = json.dumps({
        "@context": "https://doi.org/10.5063/schema/codemeta-3.0",
        "@type": "SoftwareSourceCode",
        "name": "DelayBasin research archive",
        "version": revision,
        "identifier": bundle,
        "url": "./",
        "codeRepository": "./",
        "dateModified": release_date,
        "author": [{"@type": "Organization", "name": contributor}],
        "description": description,
        "license": "LICENSE",
    }, ensure_ascii=False, indent=2) + "\n"
    ro_crate = json.dumps({
        "@context": "https://w3id.org/ro/crate/1.2/context",
        "@graph": [
            {
                "@id": "ro-crate-metadata.json",
                "@type": "CreativeWork",
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.2"},
                "about": {"@id": "./"},
            },
            {
                "@id": "./",
                "@type": "Dataset",
                "name": "DelayBasin research archive",
                "version": revision,
                "identifier": bundle,
                "datePublished": release_date,
                "author": {"@id": "#delaybasin-contributors"},
                "license": {"@id": "LICENSE"},
                "hasPart": [
                    {"@id": "REVISION-RECEIPT.json"},
                    {"@id": "RELEASE-MANIFEST.json"},
                    {"@id": "FILE-MANIFEST.json"},
                    {"@id": "CHECKSUMS.sha256"},
                ],
                "description": description,
            },
            {
                "@id": "#delaybasin-contributors",
                "@type": "Organization",
                "name": contributor,
            },
            {
                "@id": "LICENSE",
                "@type": "CreativeWork",
                "name": "DelayBasin research archive package notice",
                "description": "Local license and warranty notice shipped with this archive package.",
            },
            {"@id": "REVISION-RECEIPT.json", "@type": "File", "name": "Revision receipt"},
            {"@id": "RELEASE-MANIFEST.json", "@type": "File", "name": "Release manifest"},
            {"@id": "FILE-MANIFEST.json", "@type": "File", "name": "File manifest"},
            {"@id": "CHECKSUMS.sha256", "@type": "File", "name": "SHA256 checksum manifest"},
        ],
    }, ensure_ascii=False, indent=2) + "\n"
    sbom = json.dumps({
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"DelayBasin research archive {revision}",
        "documentNamespace": f"urn:delaybasin:{revision}:sbom",
        "creationInfo": {
            "created": created_utc,
            "creators": ["Tool: DelayBasin package identity audit"],
        },
        "packages": [
            {
                "name": "DelayBasin research archive",
                "SPDXID": "SPDXRef-Package-DelayBasin",
                "versionInfo": revision,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "primaryPackagePurpose": "DATA",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "summary": description,
                "description": f"DelayBasin research archive release {revision}.",
            }
        ],
    }, ensure_ascii=False, indent=2) + "\n"
    return {
        "LICENSE": license_text,
        "CITATION.cff": citation,
        "codemeta.json": codemeta,
        "ro-crate-metadata.json": ro_crate,
        "SBOM.spdx.json": sbom,
    }


def write_external_metadata(root: pathlib.Path) -> None:
    for rel, text in expected_external_metadata(root).items():
        (root / rel).write_text(text, encoding="utf-8")


def external_metadata_rows(root: pathlib.Path) -> list[dict[str, Any]]:
    identity = release_identity(root)
    revision = identity["revision"]
    bundle = identity["bundle"]
    release_date = identity["release_date"]
    created_utc = identity["created_utc"]
    rows: list[dict[str, Any]] = []
    for rel in EXTERNAL_METADATA_SURFACES:
        path = root / rel
        if not path.exists():
            rows.append({"surface": rel, "path": "<file>", "expected": "present", "observed": "missing", "status": "fail"})
            continue
        text = path.read_text(encoding="utf-8")
        revs = sorted(set(REV_RE.findall(text)))
        bundles = sorted(set(BUNDLE_RE.findall(text)))
        rows.append({"surface": rel, "path": "revision_tokens", "expected": [revision], "observed": revs, "status": _status(revs, [revision])})
        if rel != "SBOM.spdx.json":
            rows.append({"surface": rel, "path": "bundle_tokens", "expected": [bundle], "observed": bundles, "status": _status(bundles, [bundle])})
        if rel == "LICENSE":
            first = text.splitlines()[0] if text.splitlines() else ""
            expected = f"DelayBasin research archive release {revision}"
            rows.append({"surface": rel, "path": "line[0]", "expected": expected, "observed": first, "status": _status(first, expected)})
        if rel == "CITATION.cff":
            observed = None
            match = re.search(r'^date-released:\s+"(?P<date>\d{4}-\d{2}-\d{2})"\s*$', text, re.M)
            if match:
                observed = match.group("date")
            rows.append({"surface": rel, "path": "date-released", "expected": release_date, "observed": observed, "status": _status(observed, release_date)})
            rows.append({"surface": rel, "path": "authors", "expected": "present", "observed": "present" if re.search(r"^authors:\s*$", text, re.M) else "missing", "status": "pass" if re.search(r"^authors:\s*$", text, re.M) else "fail"})
        elif rel == "codemeta.json":
            data = json.loads(text)
            rows.append({"surface": rel, "path": "dateModified", "expected": release_date, "observed": data.get("dateModified"), "status": _status(data.get("dateModified"), release_date)})
            rows.append({"surface": rel, "path": "@context", "expected": "https://doi.org/10.5063/schema/codemeta-3.0", "observed": data.get("@context"), "status": _status(data.get("@context"), "https://doi.org/10.5063/schema/codemeta-3.0")})
            rows.append({"surface": rel, "path": "codeRepository", "expected": "./", "observed": data.get("codeRepository"), "status": _status(data.get("codeRepository"), "./")})
            rows.append({"surface": rel, "path": "author", "expected": "present", "observed": "present" if data.get("author") else "missing", "status": "pass" if data.get("author") else "fail"})
        elif rel == "ro-crate-metadata.json":
            data = json.loads(text)
            graph = data.get("@graph", [])
            descriptor = next((row for row in graph if row.get("@id") == "ro-crate-metadata.json"), {})
            dataset = next((row for row in graph if row.get("@id") == "./"), {})
            rows.append({"surface": rel, "path": "@context", "expected": "https://w3id.org/ro/crate/1.2/context", "observed": data.get("@context"), "status": _status(data.get("@context"), "https://w3id.org/ro/crate/1.2/context")})
            rows.append({"surface": rel, "path": "descriptor.conformsTo.@id", "expected": "https://w3id.org/ro/crate/1.2", "observed": (descriptor.get("conformsTo") or {}).get("@id"), "status": _status((descriptor.get("conformsTo") or {}).get("@id"), "https://w3id.org/ro/crate/1.2")})
            rows.append({"surface": rel, "path": "@graph[@id='./'].datePublished", "expected": release_date, "observed": dataset.get("datePublished"), "status": _status(dataset.get("datePublished"), release_date)})
            rows.append({"surface": rel, "path": "@graph[@id='./'].license.@id", "expected": "LICENSE", "observed": (dataset.get("license") or {}).get("@id"), "status": _status((dataset.get("license") or {}).get("@id"), "LICENSE")})
        elif rel == "SBOM.spdx.json":
            data = json.loads(text)
            rows.append({"surface": rel, "path": "creationInfo.created", "expected": created_utc, "observed": data.get("creationInfo", {}).get("created"), "status": _status(data.get("creationInfo", {}).get("created"), created_utc)})
            rows.append({"surface": rel, "path": "documentNamespace_prefix", "expected": f"urn:delaybasin:{revision}:sbom", "observed": data.get("documentNamespace"), "status": _status(data.get("documentNamespace"), f"urn:delaybasin:{revision}:sbom")})
    return rows


def assert_external_metadata(root: pathlib.Path) -> None:
    rows = external_metadata_rows(root)
    failures = [row for row in rows if row.get("status") != "pass"]
    if failures:
        first = failures[0]
        raise SystemExit(
            f"{first['surface']} {first['path']} drifted: observed {first.get('observed')!r}, expected {first.get('expected')!r}"
        )
    for rel in ["codemeta.json", "ro-crate-metadata.json", "SBOM.spdx.json"]:
        json.loads((root / rel).read_text(encoding="utf-8"))

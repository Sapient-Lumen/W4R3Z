import json
import pathlib
from typing import Any

NON_CLAIM = "basis-provenance-court, session-underlier-sovereign, reread-notary, anchor-freshness-tribunal, basis-waiver-board, resync-authority-senate, provenance-certification-court, and underlier-currentness-oracle are forbidden; this surface checks receipt basis/head alignment and session-provenance cues but does not certify semantic truth, full historical review, release legitimacy, legal status, minimality, or continuation authority."


def _load(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _row(name: str, expected: Any, observed: Any, rationale: str) -> dict[str, Any]:
    return {
        "check": name,
        "expected": expected,
        "observed": observed,
        "status": "pass" if observed == expected else "fail",
        "rationale": rationale,
    }


def build_basis_provenance_audit(root: pathlib.Path) -> dict[str, Any]:
    receipt = _load(root, "REVISION-RECEIPT.json")
    status = _load(root, "SURFACE-STATUS.json")
    manifest = _load(root, "RELEASE-MANIFEST.json")
    basis = receipt.get("basis_witness", {})
    previous = receipt.get("previous_revision")
    rows: list[dict[str, Any]] = []
    rows.append(_row("expected_head_matches_previous_revision", previous, basis.get("expected_head"), "the expected basis head for an ordinary continuation should name the immediate underlier release"))
    rows.append(_row("observed_head_matches_previous_revision", previous, basis.get("observed_head"), "the observed reread basis should name the immediate underlier release rather than an older carryover"))
    rows.append(_row("expected_observed_heads_match", basis.get("expected_head"), basis.get("observed_head"), "basis exactness requires expected and observed heads to match before currentness language can be used"))
    rows.append(_row("anchor_precision_direct_underlier", "direct-underlier", basis.get("basis_anchor_precision"), "the current release claims direct-underlier review rather than wrapper-only or packet-only routing"))
    state_ok = basis.get("basis_state") in {"current", "resynced"}
    rows.append({"check":"basis_state_allows_current_underlier","expected":["current","resynced"],"observed":basis.get("basis_state"),"status":"pass" if state_ok else "fail","rationale":"a same-underlier basis may be current or explicitly resynced, but stale/partial/mismatched states cannot pass the audit"})
    provenance = basis.get("session_provenance", "")
    provenance_ok = isinstance(provenance, str) and previous in provenance and "rev0328" not in provenance and "rev0330" not in provenance and "rev0331" not in provenance
    rows.append({"check":"session_provenance_names_current_underlier","expected":f"mentions {previous} and no older source-only carryover", "observed": provenance, "status":"pass" if provenance_ok else "fail", "rationale":"session provenance should not silently inherit older package names after later releases"})
    rows.append(_row("status_previous_citation_head_matches_previous", previous, status.get("previous_citation_head", {}).get("revision"), "status surface should expose the same immediate underlier used by the receipt basis"))
    rows.append(_row("manifest_revision_matches_receipt", receipt.get("revision"), manifest.get("revision"), "basis audit is meaningful only against the packaged manifest revision"))
    failures=[row for row in rows if row.get("status") != "pass"]
    return {
        "project":"DelayBasin",
        "revision":receipt.get("revision"),
        "surface":"BASIS-PROVENANCE-AUDIT.json",
        "guide_surface":"docs/00-meta/basis-provenance-audit.md",
        "state":"generated-basis-provenance-audit",
        "generated_from":["REVISION-RECEIPT.json","SURFACE-STATUS.json","RELEASE-MANIFEST.json","innovation-packet.json"],
        "policy":{
            "expected_head":"must match REVISION-RECEIPT.previous_revision for direct-underlier ordinary continuation",
            "observed_head":"must match the same immediate underlier, not an older historical carryover",
            "session_provenance":"must name the current underlier and avoid stale source-only carryover phrasing",
            "non_authority":"audit detects basis drift; it does not certify semantic truth or full historical review",
        },
        "non_claim":NON_CLAIM,
        "basis_rows":rows,
        "counts":{"checks":len(rows),"failures":len(failures)},
        "failures":failures,
    }


def render_basis_provenance_markdown(audit: dict[str, Any]) -> str:
    lines=[
        "# Basis provenance audit",
        "",
        "This generated surface checks whether the revision receipt's basis witness names the immediate underlier release instead of silently carrying an older session anchor.",
        "It exists because a package can pass many currentness checks while the innovation packet still inherits stale `basis_witness.expected_head`, `observed_head`, or `session_provenance` fields from an earlier revision.",
        "",
        "## Non-authority boundary",
        "",
        "This is not a basis-provenance-court, session-underlier-sovereign, reread-notary, anchor-freshness-tribunal, basis-waiver-board, resync-authority-senate, provenance-certification-court, or underlier-currentness-oracle.",
        "Basis provenance is session-underlier hygiene only; it does not certify semantic truth, full historical review, legal status, release legitimacy, minimality, or continuation authority.",
        "",
        "## Counts",
        "",
        f"- Checks: `{audit['counts']['checks']}`",
        f"- Failures: `{audit['counts']['failures']}`",
        "",
        "## Rows",
    ]
    for row in audit["basis_rows"]:
        lines.append(f"- `{row['check']}` — status `{row['status']}`; expected `{row['expected']}`; observed `{row['observed']}`")
    if audit["failures"]:
        lines.append("")
        lines.append("## Failures")
        for row in audit["failures"]:
            lines.append(f"- `{row['check']}` expected `{row['expected']}` observed `{row['observed']}`")
    return "\n".join(lines).rstrip()+"\n"


def write_basis_provenance_audit(root: pathlib.Path) -> dict[str, Any]:
    audit=build_basis_provenance_audit(root)
    (root/"BASIS-PROVENANCE-AUDIT.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (root/"docs/00-meta/basis-provenance-audit.md").write_text(render_basis_provenance_markdown(audit), encoding="utf-8")
    return audit

"""Shared mission-kernel live-closeout constants and small helpers.

The live workqueue and evidence-intake validator used to keep the evidence-class
map in one tool.  Keep it in this stdlib-only module so future intake tooling can
share the same operator contract without copying the blocker/evidence taxonomy.
"""
from __future__ import annotations

from typing import Iterable

BOUNDARY = (
    "Synthetic/live-intake control surface only; not live election evidence, not authorization, "
    "not certification, not outcome proof, not current voter instruction, and not legal advice."
)

WORKQUEUE_BOUNDARY = (
    "Synthetic workqueue only; not live election evidence, not authorization, "
    "not certification, not outcome proof, not current voter instruction, and not legal advice."
)

LIVE_EVIDENCE_SOURCE_MODE = "LIVE_AUTHORIZED_LOCAL_RECORD"
DRILL_EVIDENCE_SOURCE_MODE = "AUTHORIZED_NONPRODUCTION_DRILL_RECORD"
EMPTY_SOURCE_MODES = {"", "MISSING", "NOT_SUBMITTED", "SYNTHETIC_EMPTY_TEMPLATE"}
NON_LIVE_SOURCE_MODES = {"SYNTHETIC_FIXTURE", "DERIVED_PUBLIC_SUMMARY", "GENERATED_SYNTHETIC_REPORT"}
ALLOWED_SOURCE_MODES = {LIVE_EVIDENCE_SOURCE_MODE, DRILL_EVIDENCE_SOURCE_MODE, *EMPTY_SOURCE_MODES, *NON_LIVE_SOURCE_MODES}

PUBLIC_BOUNDARY_VALUES = {
    "",
    "PUBLIC_RELEASED",
    "REDACTED_PUBLIC_DERIVATIVE",
    "PRIVATE_SOURCE_RECORD",
    "WITHHELD_LEGAL_OR_PRIVACY",
}

REDACTION_STATUS_VALUES = {
    "",
    "NOT_REVIEWED",
    "APPROVED_PUBLIC",
    "APPROVED_PRIVATE",
    "WITHHELD",
}

ELEMENT_LABELS = {
    "K01_AUTHORIZED_ELECTION_DEFINITION": "authority and election definition",
    "K02_BALLOT_ACCOUNTING_AND_CUSTODY": "ballot accounting and custody",
    "K03_STANDARDIZED_RESULTS_EXPORTS": "standards-based export replay",
    "K04_AUDIT_RECOUNT_ADJUDICATION": "audit adjudication and dispute remedy",
    "K05_AUTHENTICATED_OFFICIAL_NOTICES": "public release approval",
    "K06_INDEPENDENT_VERIFIER_DISAGREEMENT_FAILURE": "independent verifier review",
    "K07_INCIDENT_DISPUTE_REMEDY_CLOSEOUT": "incident remedy closeout",
}

INTAKE_CLASSES = {
    "MKB-001": [
        "signed authority-scope adoption record",
        "locally approved official-channel roster",
        "production election definition export",
        "source-precedence and correction authority note",
    ],
    "MKB-002": [
        "reporting-unit ballot accounting totals",
        "custody transfer or seal record",
        "exception and reconciliation log",
        "records-custodian approval and disposition note",
    ],
    "MKB-003": [
        "raw CVR export bytes or approved equivalent",
        "raw election-results export bytes",
        "adapter replay transcript",
        "independent verifier transcript from exported bytes",
    ],
    "MKB-004": [
        "audit or recount setup record",
        "adjudication or review decision record",
        "dissent and issue-resolution transcript",
        "remedy closeout and retest record",
    ],
    "MKB-005": [
        "external reviewer scope statement",
        "conflict disclosure",
        "clean-checkout verifier transcript",
        "dissent, remediation, and retest record",
    ],
    "MKB-006": [
        "redaction approval record",
        "accessibility and language-access review record",
        "plain-language/fallback/help review record",
        "local public-release approval record",
    ],
    "MKB-007": [
        "incident or dispute trigger record",
        "owner decision and remedy record",
        "public/private boundary decision",
        "retention, disposition, and final closeout record",
    ],
}

STANDARD_ALIGNMENT = {
    "MKB-001": ["NIST Ballot Definition CDF", "NIST Election Results Reporting CDF"],
    "MKB-002": ["EAC election-audit principles", "local canvass and retention rules"],
    "MKB-003": ["NIST Cast Vote Records CDF", "NIST Election Results Reporting CDF"],
    "MKB-004": ["EAC election-audit principles", "risk-limiting or jurisdiction audit method"],
    "MKB-005": ["independent verifier transcript", "conflict disclosure and dissent route"],
    "MKB-006": ["local official-channel policy", "accessibility and language-access review"],
    "MKB-007": ["incident response playbook", "retention and public-records boundary"],
}

GOVERNED_SYNTHETIC_PREFIXES = (
    "artifacts/",
    "docs/",
    "schemas/",
    "scripts/",
    "tools/",
    "observer-kit/",
    "evidence/lock/",
)


def source_mode_is_external_record(source_mode: str) -> bool:
    """Return True for modes that must reference operator-supplied records outside ROOT."""

    return str(source_mode or "").strip() in {LIVE_EVIDENCE_SOURCE_MODE, DRILL_EVIDENCE_SOURCE_MODE}


def evidence_classes_for(blocker_id: str, fallback: str = "missing live evidence") -> list[str]:
    """Return minimum evidence classes for a mission-kernel blocker."""

    values = INTAKE_CLASSES.get(blocker_id)
    return list(values) if values else [fallback]


def standard_alignment_for(blocker_id: str) -> list[str]:
    """Return standards/interchange anchors for a mission-kernel blocker."""

    return list(STANDARD_ALIGNMENT.get(blocker_id, []))


def element_label(element_id: str) -> str:
    """Return a human label for a kernel element id."""

    return ELEMENT_LABELS.get(element_id, element_id)


def is_governed_synthetic_locator(locator: str) -> bool:
    """Return True when a locator points back into this governed synthetic tree."""

    clean = str(locator or "").strip().replace("\\", "/")
    if clean.startswith("./"):
        clean = clean[2:]
    return any(clean.startswith(prefix) for prefix in GOVERNED_SYNTHETIC_PREFIXES)


def missing_classes(required: Iterable[str], supplied: Iterable[str]) -> list[str]:
    """Return required evidence classes not represented by supplied live records."""

    have = {str(x).strip() for x in supplied if str(x).strip()}
    return [str(x) for x in required if str(x) not in have]

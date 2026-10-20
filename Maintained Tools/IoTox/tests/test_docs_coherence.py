#!/usr/bin/env python3
"""Coherence checks for front-door IoTox docs and native help text."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REQUIRED_ARCHITECTURE_DOCS = (
    "BOOTSTRAPROSE.md",
    "README.md",
    "docs/architecture.md",
    "docs/governance/change-control.md",
    "docs/open-questions.md",
    "docs/product-page.md",
    "docs/roadmap.md",
    "docs/threat-model-draft.md",
)

FRONT_DOOR_DOCS = REQUIRED_ARCHITECTURE_DOCS + (
    "docs/architectural-change-intake.md",
    "docs/everyday-sync-plan.md",
    "docs/human-ergonomics-plan.md",
    "docs/peer-invitations.md",
    "docs/person-multidevice.md",
    "docs/pragmatic-guardrails.md",
    "docs/quickstart.md",
    "docs/replace-resilio-sync.md",
    "docs/self-mode.md",
)

INTAKE_HEADINGS = (
    "## One-page dossier",
    "## Layer check",
    "## Authority check",
    "## Storage and freshness check",
    "## Route and privacy check",
    "## Terminal/process check",
    "## Diagnostics/support check",
    "## Evidence check",
    "## Documentation check",
    "## Rejection tests",
)

DOSSIER_FIELDS = (
    "name:",
    "human story:",
    "new capability:",
    "affected layers:",
    "new durable state:",
    "new authority or capability bits:",
    "new local/remote inputs:",
    "new outputs/artifacts:",
    "failure modes:",
    "rollback/freshness story:",
    "support/diagnostics story:",
    "evidence target:",
    "nonclaims:",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(repo: Path, relative: str) -> str:
    path = repo / relative
    require(path.exists(), f"missing expected doc: {relative}")
    return path.read_text(encoding="utf-8")


def run(iotox: Path, *args: str) -> str:
    completed = subprocess.run(
        [str(iotox), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {iotox} {' '.join(args)}\n"
            f"{completed.stdout}"
        )
    return completed.stdout


def check_architectural_intake_links(repo: Path) -> None:
    for relative in REQUIRED_ARCHITECTURE_DOCS:
        text = read(repo, relative)
        require(
            "docs/architectural-change-intake.md" in text,
            f"{relative} does not link the architectural change intake",
        )

    intake = read(repo, "docs/architectural-change-intake.md")
    for heading in INTAKE_HEADINGS:
        require(heading in intake, f"intake missing heading: {heading}")
    for field in DOSSIER_FIELDS:
        require(field in intake, f"intake missing dossier field: {field}")
    require(
        "friendship" in intake and "authority" in intake,
        "intake lost friendship/authority boundary language",
    )
    require(
        "Remote-selected exec" in intake and "automatic sudo" in intake,
        "intake lost terminal refusal language",
    )


def check_public_spelling(repo: Path) -> None:
    for relative in FRONT_DOOR_DOCS:
        text = read(repo, relative)
        require(
            "sync_subscribe" not in text and "sync_publish" not in text,
            f"{relative} uses internal sync capability spelling",
        )
        require(
            "RECALL_ROOT_PHRASE" not in text,
            f"{relative} suggests RecallRoot through an environment variable",
        )

    quickstart = read(repo, "docs/quickstart.md")
    require(
        "cat RECALLROOT.txt |" in quickstart,
        "quickstart lost stdin RecallRoot ceremony",
    )
    require(
        "sync.subscribe,sync.publish" in quickstart,
        "quickstart lost public sync capability spelling",
    )

    self_mode = read(repo, "docs/self-mode.md")
    require(
        "--mode self" in self_mode and "interactive.terminal" in self_mode,
        "self-mode doc lost activation/authority boundary",
    )
    require(
        "Tox multidevice" in self_mode and "profile binding" in self_mode,
        "self-mode doc lost multidevice/profile-boundary language",
    )
    require(
        "iotox self-swarm verify" in self_mode
        and "--expect-route" in self_mode
        and "grant-recall-stdin" in self_mode
        and "revoke-retired-recall-stdin" in self_mode,
        "self-mode doc lost signed roster verify/grant/revoke commands",
    )
    person = read(repo, "docs/person-multidevice.md")
    require(
        "card-recall-stdin" in person
        and "message-fanout-recall-stdin" in person
        and "delegate-recall-stdin" in person
        and "group-fanout-plan" in person
        and "Still not claimed" in person,
        "person multidevice doc lost card/fanout/groupchat boundary",
    )

    everyday = read(repo, "docs/everyday-sync-plan.md")
    require(
        "cat A_RECALLROOT.txt |" in everyday
        and "cat B_RECALLROOT.txt |" in everyday
        and "cat C_RECALLROOT.txt |" in everyday,
        "everyday sync plan lost multi-node stdin RecallRoot examples",
    )
    require(
        "do not pass the phrase as an argument or environment variable"
        in everyday,
        "everyday sync plan lost RecallRoot secrecy warning",
    )


def check_help_output(iotox: Path) -> None:
    root_help = run(iotox, "help")
    require(
        "iotox help all" in root_help
        and "iotox doctor binary" in root_help
        and "iotox person quickstart" in root_help,
        "root help lost human front door/provenance/person porch",
    )
    require(
        "routes      evidence  shipping  support  storage-readiness"
        in root_help,
        "root help lost claim/evidence/support topic row",
    )
    require(
        "sync-namespace-template" not in root_help
        and "witness-service-serve" not in root_help,
        "root help should stay short; exhaustive inventory belongs to help all",
    )
    help_all = run(iotox, "help", "all")
    require(
        "sync-namespace-template" in help_all
        and "witness-service-serve" in help_all,
        "help all lost full command inventory",
    )
    binary_doctor = run(iotox, "doctor", "binary")
    require(
        "iotox-binary-source-v1" in binary_doctor
        and "revision=rev0051" in binary_doctor
        and "cwd-revision-matches-compiled=" in binary_doctor,
        "doctor binary lost binary/source provenance",
    )

    for topic in ("quickstart", "sync", "terminal", "service", "pairing",
                  "self", "person", "routes", "evidence", "shipping",
                  "support", "storage-readiness"):
        output = run(iotox, "help", topic)
        require(
            "sync_subscribe" not in output and "sync_publish" not in output,
            f"help {topic} uses internal sync capability spelling",
        )
        require(
            "RECALL_ROOT_PHRASE" not in output,
            f"help {topic} suggests RecallRoot through an environment variable",
        )

    sync_help = run(iotox, "help", "sync")
    require(
        "cat RECALLROOT.txt | iotox sync share" in sync_help,
        "sync help lost stdin RecallRoot ceremony",
    )
    pairing_help = run(iotox, "help", "pairing")
    require(
        "sync.subscribe,sync.publish" in pairing_help
        and "operator sync.subscribe" in pairing_help,
        "pairing help lost public capability spelling",
    )
    self_help = run(iotox, "help", "self")
    require(
        "--mode self" in self_help and "interactive.terminal" in self_help,
        "self help lost self-mode terminal authority path",
    )
    routes_help = run(iotox, "help", "routes")
    require(
        "route-qualification-check --scope all" in routes_help
        and "does not silently fall back" in routes_help,
        "routes help lost route qualification/nonfallback boundary",
    )
    evidence_help = run(iotox, "help", "evidence")
    require(
        "evidence dossier-plan" in evidence_help
        and "evidence collect terminal" in evidence_help
        and "evidence manifest" in evidence_help,
        "evidence help lost dossier/collector/manifest route",
    )
    shipping_help = run(iotox, "help", "shipping")
    require(
        "ship-check all stable" in shipping_help
        and "release-check founder-preview" in shipping_help,
        "shipping help lost release gate/package route",
    )
    support_help = run(iotox, "help", "support")
    require(
        "support-bundle plan" in support_help
        and "content-free, not information-free" in support_help,
        "support help lost support-bundle nonclaim",
    )
    require(
        "iotox self-swarm verify" in self_help
        and "--expect-route" in self_help
        and "self-swarm grant-recall-stdin" in self_help,
        "self help lost signed self-swarm verify/grant path",
    )
    self_swarm_help = run(iotox, "self-swarm", "help")
    require(
        "iotox-self-swarm-help-v1" in self_swarm_help
        and "create-recall-stdin" in self_swarm_help
        and "grant-recall-stdin" in self_swarm_help
        and "revoke-retired-recall-stdin" in self_swarm_help
        and "--expect-route" in self_swarm_help,
        "self-swarm help lost roster command surface",
    )
    require(
        "floor-commit" in self_swarm_help
        and "fanout-plan" in self_swarm_help
        and "readiness-command=" in self_swarm_help
        and "--prove-routes" in self_swarm_help,
        "self-swarm help lost floor/fanout/readiness/route-proof surface",
    )
    person_help = run(iotox, "person", "help")
    require(
        "iotox-person-help-v1" in person_help
        and "card-recall-stdin" in person_help
        and "message-fanout-recall-stdin" in person_help,
        "person help lost public-card/fanout surface",
    )
    require(
        "first-steps=" in person_help
        and "quickstart-command=iotox person quickstart" in person_help
        and "plain-english=" in person_help,
        "person help lost recipe-first explanation",
    )
    require(
        "graduation-check-command=" in person_help
        and "tox-bridge-graduation-check-command=" in person_help,
        "person help lost graduation surfaces",
    )
    terminal_help = run(iotox, "help", "terminal")
    require(
        "terminal daily-plan" in terminal_help
        or "terminal profile plan" in terminal_help,
        "terminal help lost grouped setup porch",
    )
    service_help = run(iotox, "help", "service")
    require(
        "iotox service plan --target all" in service_help
        and "iotox service status-receipt --target all" in service_help
        and "--manager monsternix" in service_help
        and "person background-run" in service_help,
        "service help lost resident service command surface",
    )
    sync_help = run(iotox, "help", "sync")
    require(
        "sync-dataset-readiness" in sync_help,
        "sync help lost dataset readiness porch",
    )


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: test_docs_coherence.py REPO_ROOT IOTOX", file=sys.stderr)
        return 2
    repo = Path(sys.argv[1]).resolve()
    iotox = Path(sys.argv[2]).resolve()
    check_architectural_intake_links(repo)
    check_public_spelling(repo)
    check_help_output(iotox)
    print("IoTox docs coherence test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

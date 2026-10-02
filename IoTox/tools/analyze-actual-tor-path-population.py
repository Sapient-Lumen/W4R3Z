#!/usr/bin/env python3
"""Count target-circuit populations in verified compact actual-Tor proofs.

Relay fingerprints are used only to construct normalized, domain-separated set
commitments. They are never emitted by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "iotox.actual-tor-path-population.v1"
COMPACT_SCHEMA = "iotox.sandwurm-pair-compact-export.v0"
PURPOSES = {"GENERAL", "CONFLUX_LINKED"}
FINGERPRINT = re.compile(r"\$([0-9A-Fa-f]{40})(?:[~=][^, ]+)?")
PAIR_NAME = re.compile(r"pair\.[A-Za-z0-9_]+")
SHA256 = re.compile(r"[0-9a-f]{64}")

VERIFIER_PATH = Path(__file__).with_name("verify-sandwurm-pair.py")
SPEC = importlib.util.spec_from_file_location(
    "iotox_sandwurm_pair_verifier", VERIFIER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load the Sandwurm pair verifier")
PAIR_VERIFIER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PAIR_VERIFIER
SPEC.loader.exec_module(PAIR_VERIFIER)


class AnalysisError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AnalysisError(detail)


def load(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), f"missing regular file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AnalysisError(f"cannot read JSON {path}: {error}") from error
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def set_commitment(label: str, values: set[str]) -> str:
    require(bool(values), f"cannot commit an empty {label} set")
    canonical = label.encode("ascii") + b"\0"
    canonical += "\n".join(sorted(values)).encode("ascii") + b"\n"
    return digest_bytes(canonical)


def parse_circuit_line(line: str) -> dict[str, object] | None:
    fields = line.split()
    if len(fields) >= 6 and fields[:2] == ["650", "CIRC"]:
        state = fields[3]
        path = fields[4]
        attributes = fields[5:]
    elif len(fields) >= 4 and fields[0].isdecimal():
        state = fields[1]
        path = fields[2]
        attributes = fields[3:]
    else:
        return None
    if state not in {"BUILT", "CLOSED"}:
        return None
    purposes = [
        field.split("=", 1)[1]
        for field in attributes
        if field.startswith("PURPOSE=")
    ]
    if len(purposes) != 1 or purposes[0] not in PURPOSES:
        return None
    hops = path.split(",")
    identities: list[str] = []
    for hop in hops:
        match = FINGERPRINT.fullmatch(hop)
        require(match is not None, "Tor circuit path identity is noncanonical")
        identities.append(match.group(1).upper())
    if len(identities) < 3 and any(
        field.startswith("BUILD_FLAGS=")
        and "ONEHOP_TUNNEL" in field.split("=", 1)[1].split(",")
        for field in attributes
    ):
        return None
    require(len(identities) >= 3, "Tor application circuit has fewer than three hops")
    path_value = ",".join(identities)
    return {
        "first_hop": identities[0],
        "last_hop": identities[-1],
        "hop_count": len(identities),
        "path": path_value,
        "raw_path_sha256": digest_bytes(path.encode("ascii")),
        "purpose": purposes[0],
    }


def parse_circuit_file(path: Path) -> list[dict[str, object]]:
    require(path.is_file() and not path.is_symlink(), f"missing Tor evidence: {path}")
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as error:
        raise AnalysisError(f"cannot read ASCII Tor evidence {path}: {error}") from error
    records = [record for line in lines if (record := parse_circuit_line(line))]
    return records


def summarize_records(records: list[dict[str, object]]) -> dict[str, object]:
    require(bool(records), "Tor evidence contains no target circuit")
    paths = {str(record["path"]) for record in records}
    first_hops = {str(record["first_hop"]) for record in records}
    last_hops = {str(record["last_hop"]) for record in records}
    first_last = {
        f"{record['first_hop']}:{record['last_hop']}" for record in records
    }
    purposes = Counter(str(record["purpose"]) for record in records)
    hops = [int(record["hop_count"]) for record in records]
    return {
        "target_circuit_observation_count": len(records),
        "unique_target_path_count": len(paths),
        "path_set_sha256": set_commitment("tor-path-set-v1", paths),
        "unique_first_hop_count": len(first_hops),
        "first_hop_set_sha256": set_commitment(
            "tor-first-hop-set-v1", first_hops
        ),
        "unique_last_hop_count": len(last_hops),
        "last_hop_set_sha256": set_commitment(
            "tor-last-hop-set-v1", last_hops
        ),
        "unique_first_last_hop_count": len(first_last),
        "first_last_hop_set_sha256": set_commitment(
            "tor-first-last-hop-set-v1", first_last
        ),
        "minimum_hop_count": min(hops),
        "maximum_hop_count": max(hops),
        "purpose_counts": {purpose: purposes.get(purpose, 0) for purpose in sorted(PURPOSES)},
    }


def expected_path_declarations(manifest: dict) -> list[dict[str, str]]:
    declarations: list[dict[str, str]] = []
    role_evidence = manifest.get("actual_tor_role_evidence")
    require(
        isinstance(role_evidence, list) and role_evidence,
        "actual-Tor role evidence is absent",
    )
    for index, evidence in enumerate(role_evidence):
        require(isinstance(evidence, dict), "actual-Tor role evidence is invalid")
        role = evidence.get("role")
        phase = evidence.get("phase", "continuous")
        path_sha256 = evidence.get("circuit_path_sha256")
        purpose = evidence.get("circuit_purpose")
        require(
            role in {"client", "device"}
            and isinstance(phase, str)
            and phase
            and SHA256.fullmatch(str(path_sha256)) is not None
            and purpose in PURPOSES,
            "actual-Tor role path declaration is invalid",
        )
        declarations.append(
            {
                "source": f"role:{role}:{phase}:{index}",
                "raw_path_sha256": str(path_sha256),
                "purpose": str(purpose),
            }
        )

    churn = manifest.get("actual_tor_ratox_churn")
    if churn:
        require(isinstance(churn, dict), "actual-Tor churn evidence is invalid")
        transitions = churn.get("churns")
        require(
            isinstance(transitions, list) and transitions,
            "actual-Tor churn transitions are absent",
        )
        for index, transition in enumerate(transitions):
            require(
                isinstance(transition, dict),
                "actual-Tor churn transition is invalid",
            )
            role = transition.get("role")
            require(role in {"client", "device"},
                    "actual-Tor churn role is invalid")
            for side in ("before", "after"):
                evidence = transition.get(side)
                require(isinstance(evidence, dict),
                        "actual-Tor churn circuit is invalid")
                path_sha256 = evidence.get("circuit_path_sha256")
                purpose = evidence.get("circuit_purpose")
                require(
                    SHA256.fullmatch(str(path_sha256)) is not None
                    and purpose in PURPOSES,
                    "actual-Tor churn path declaration is invalid",
                )
                declarations.append(
                    {
                        "source": f"churn:{role}:{index}:{side}",
                        "raw_path_sha256": str(path_sha256),
                        "purpose": str(purpose),
                    }
                )
    return declarations


def evidence_file_names(export: dict) -> list[str]:
    files = export.get("files")
    require(isinstance(files, dict), "compact file inventory is absent")
    names = sorted(
        name
        for name in files
        if name.startswith("tor-")
        and name.endswith(("-control-events.txt", "-circuit-status.txt"))
    )
    require(bool(names), "compact proof has no Tor circuit/control evidence")
    return names


def analyze_proof(root: Path) -> tuple[dict[str, object], dict[str, set[str]]]:
    root = root.resolve()
    require(PAIR_NAME.fullmatch(root.name) is not None,
            f"invalid pair proof name: {root.name}")
    try:
        PAIR_VERIFIER.verify_pair(root)
    except (OSError, RuntimeError, ValueError) as error:
        raise AnalysisError(f"pair verification failed for {root}: {error}") from error
    manifest_path = root / "pair-manifest.json"
    export_path = root / "compact-export.json"
    manifest = load(manifest_path)
    export = load(export_path)
    require(
        manifest.get("actual_tor") is True
        and export.get("schema") == COMPACT_SCHEMA
        and export.get("status") == "passed"
        and export.get("source_proof_id") == root.name,
        f"{root.name} is not a verified compact actual-Tor proof",
    )
    names = evidence_file_names(export)
    available_records: list[dict[str, object]] = []
    for name in names:
        path = (root / name).resolve()
        require(path.parent == root, f"Tor evidence escaped compact root: {name}")
        available_records.extend(parse_circuit_file(path))
    records_by_raw_hash: dict[str, list[dict[str, object]]] = {}
    for record in available_records:
        records_by_raw_hash.setdefault(
            str(record["raw_path_sha256"]), []
        ).append(record)
    declarations = expected_path_declarations(manifest)
    records: list[dict[str, object]] = []
    for declaration in declarations:
        matches = [
            record
            for record in records_by_raw_hash.get(
                declaration["raw_path_sha256"], []
            )
            if record["purpose"] == declaration["purpose"]
        ]
        require(
            bool(matches),
            f"{root.name} target path declaration lacks raw evidence",
        )
        normalized = {
            (str(record["path"]), int(record["hop_count"]))
            for record in matches
        }
        require(
            len(normalized) == 1,
            f"{root.name} target path declaration is ambiguous",
        )
        records.append(matches[0])
    summary = summarize_records(records)
    target = manifest.get("actual_tor_node")
    require(isinstance(target, dict), "actual-Tor target record is absent")
    target_record = (
        f"{target.get('address')}:{target.get('port')}:{target.get('public_key')}"
    )
    receipt_digests = {
        str(entry.get("binary_sha256"))
        for entry in manifest.get("receipts", {}).values()
        if isinstance(entry, dict)
    }
    require(
        len(receipt_digests) == 1
        and SHA256.fullmatch(next(iter(receipt_digests))) is not None,
        "IoTox binary identity is ambiguous",
    )
    tor_sha256 = manifest.get("actual_tor_sha256")
    require(
        SHA256.fullmatch(str(tor_sha256)) is not None,
        "Tor binary identity is invalid",
    )
    sets = {
        "paths": {str(record["path"]) for record in records},
        "first_hops": {str(record["first_hop"]) for record in records},
        "last_hops": {str(record["last_hop"]) for record in records},
        "first_last": {
            f"{record['first_hop']}:{record['last_hop']}" for record in records
        },
    }
    return (
        {
            "proof_id": root.name,
            "scenario": manifest.get("scenario"),
            "manifest_sha256": digest_file(manifest_path),
            "source_manifest_sha256": export.get("source_manifest_sha256"),
            "target_record_sha256": digest_bytes(target_record.encode("ascii")),
            "tor_sha256": tor_sha256,
            "iotox_binary_sha256": next(iter(receipt_digests)),
            "evidence_file_count": len(names),
            "available_application_circuit_observation_count": len(
                available_records
            ),
            **summary,
        },
        sets,
    )


def analyze(roots: list[Path]) -> dict[str, object]:
    require(len(roots) >= 2, "path-population analysis requires at least two proofs")
    require(len({root.resolve() for root in roots}) == len(roots), "duplicate proof root")
    proofs: list[dict[str, object]] = []
    proof_sets: dict[str, dict[str, set[str]]] = {}
    for root in roots:
        proof, sets = analyze_proof(root)
        proof_id = str(proof["proof_id"])
        require(proof_id not in proof_sets, "duplicate proof identity")
        proofs.append(proof)
        proof_sets[proof_id] = sets
    proofs.sort(key=lambda proof: str(proof["proof_id"]))
    aggregate_sets = {
        name: set().union(*(sets[name] for sets in proof_sets.values()))
        for name in ("paths", "first_hops", "last_hops", "first_last")
    }
    observation_count = sum(
        int(proof["target_circuit_observation_count"]) for proof in proofs
    )
    purpose_counts = {
        purpose: sum(int(proof["purpose_counts"][purpose]) for proof in proofs)
        for purpose in sorted(PURPOSES)
    }
    pairs: list[dict[str, object]] = []
    for index, left in enumerate(proofs):
        for right in proofs[index + 1 :]:
            left_id = str(left["proof_id"])
            right_id = str(right["proof_id"])
            pairs.append(
                {
                    "left": left_id,
                    "right": right_id,
                    "shared_path_count": len(
                        proof_sets[left_id]["paths"] & proof_sets[right_id]["paths"]
                    ),
                    "shared_first_hop_count": len(
                        proof_sets[left_id]["first_hops"]
                        & proof_sets[right_id]["first_hops"]
                    ),
                    "shared_last_hop_count": len(
                        proof_sets[left_id]["last_hops"]
                        & proof_sets[right_id]["last_hops"]
                    ),
                    "shared_first_last_hop_count": len(
                        proof_sets[left_id]["first_last"]
                        & proof_sets[right_id]["first_last"]
                    ),
                }
            )
    scenarios = {str(proof["scenario"]) for proof in proofs}
    targets = {str(proof["target_record_sha256"]) for proof in proofs}
    tor_binaries = {str(proof["tor_sha256"]) for proof in proofs}
    iotox_binaries = {str(proof["iotox_binary_sha256"]) for proof in proofs}
    return {
        "schema": SCHEMA,
        "status": "passed",
        "contains_secrets": False,
        "proof_count": len(proofs),
        "scenario_count": len(scenarios),
        "scenario_set_sha256": set_commitment("tor-scenario-set-v1", scenarios),
        "target_record_count": len(targets),
        "target_record_set_sha256": set_commitment("tox-target-set-v1", targets),
        "tor_binary_count": len(tor_binaries),
        "tor_binary_set_sha256": set_commitment("tor-binary-set-v1", tor_binaries),
        "iotox_binary_count": len(iotox_binaries),
        "iotox_binary_set_sha256": set_commitment(
            "iotox-binary-set-v1", iotox_binaries
        ),
        "evidence_file_count": sum(int(proof["evidence_file_count"]) for proof in proofs),
        "available_application_circuit_observation_count": sum(
            int(proof["available_application_circuit_observation_count"])
            for proof in proofs
        ),
        "target_circuit_observation_count": observation_count,
        "unique_target_path_count": len(aggregate_sets["paths"]),
        "path_set_sha256": set_commitment("tor-path-set-v1", aggregate_sets["paths"]),
        "unique_first_hop_count": len(aggregate_sets["first_hops"]),
        "first_hop_set_sha256": set_commitment(
            "tor-first-hop-set-v1", aggregate_sets["first_hops"]
        ),
        "unique_last_hop_count": len(aggregate_sets["last_hops"]),
        "last_hop_set_sha256": set_commitment(
            "tor-last-hop-set-v1", aggregate_sets["last_hops"]
        ),
        "unique_first_last_hop_count": len(aggregate_sets["first_last"]),
        "first_last_hop_set_sha256": set_commitment(
            "tor-first-last-hop-set-v1", aggregate_sets["first_last"]
        ),
        "minimum_hop_count": min(int(proof["minimum_hop_count"]) for proof in proofs),
        "maximum_hop_count": max(int(proof["maximum_hop_count"]) for proof in proofs),
        "purpose_counts": purpose_counts,
        "pairwise_reuse": pairs,
        "last_hop_population_diversity_observed": len(
            aggregate_sets["last_hops"]
        ) >= 2,
        "independent_exit_diversity_qualified": False,
        "time_window_count": 0,
        "time_window_separation_evidenced": False,
        "proofs": proofs,
    }


def self_test() -> None:
    a = "$" + "A" * 40
    b = "$" + "B" * 40
    c = "$" + "C" * 40
    d = "$" + "D" * 40
    built = parse_circuit_line(
        f"650 CIRC 7 BUILT {a}~one,{b}~two,{c}~three PURPOSE=GENERAL"
    )
    closed = parse_circuit_line(
        f"8 CLOSED {a}~one,{d}~middle,{c}~three PURPOSE=CONFLUX_LINKED"
    )
    require(built is not None and closed is not None, "valid circuits were rejected")
    summary = summarize_records([built, closed])
    require(
        summary["target_circuit_observation_count"] == 2
        and summary["unique_target_path_count"] == 2
        and summary["unique_first_hop_count"] == 1
        and summary["unique_last_hop_count"] == 1
        and summary["minimum_hop_count"] == 3
        and summary["maximum_hop_count"] == 3
        and summary["purpose_counts"] == {"CONFLUX_LINKED": 1, "GENERAL": 1},
        "circuit population summary drifted",
    )
    require(parse_circuit_line("650 STREAM 1 NEW 0 1.2.3.4:5") is None,
            "non-circuit event was accepted")
    require(
        parse_circuit_line(
            f"650 CIRC 1 CLOSED {a} BUILD_FLAGS=ONEHOP_TUNNEL "
            "PURPOSE=GENERAL"
        ) is None,
        "one-hop directory circuit was accepted",
    )
    try:
        parse_circuit_line(
            f"650 CIRC 9 BUILT {a},{b} PURPOSE=GENERAL"
        )
    except AnalysisError:
        pass
    else:
        raise AnalysisError("two-hop circuit was accepted")
    print("actual-Tor path-population analyzer self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof", nargs="*", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify-report", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        require(
            not arguments.proof
            and arguments.output is None
            and arguments.verify_report is None,
            "--self-test accepts no proof or report",
        )
        self_test()
        return 0
    require(
        arguments.output is not None or arguments.verify_report is not None,
        "--output or --verify-report is required",
    )
    result = analyze(arguments.proof)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.verify_report is not None:
        require(
            load(arguments.verify_report) == result
            and arguments.verify_report.read_bytes() == rendered.encode("utf-8"),
            "path-population report does not match the verified proof corpus",
        )
        print("actual-Tor path-population report verification: PASS")
        return 0
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AnalysisError, OSError) as error:
        print(f"actual-Tor path-population analysis failed: {error}", file=sys.stderr)
        raise SystemExit(1)

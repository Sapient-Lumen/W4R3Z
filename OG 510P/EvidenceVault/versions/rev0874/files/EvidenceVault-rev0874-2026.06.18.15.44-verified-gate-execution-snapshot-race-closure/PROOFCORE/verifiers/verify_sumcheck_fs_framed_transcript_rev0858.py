#!/usr/bin/env python3
"""Verify the rev0858 framed transcript-operation sumcheck fixture.

rev0857 bound challenges to prior public transcript-message hashes.  rev0858
makes the toy transcript surface less ambiguous by turning the transcript into an
explicit operation log: labeled absorb operations and labeled challenge
operations are processed in a fixed order, with every challenge derived from the
current framed transcript state.  This remains a tiny transparent harness: not a
SNARK verifier, not zero knowledge, not succinct, and not a production
Fiat-Shamir transcript implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0858"


class FramedTranscriptError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise FramedTranscriptError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise FramedTranscriptError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise FramedTranscriptError(f"{field} must be a POSIX relative path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise FramedTranscriptError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        raise FramedTranscriptError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise FramedTranscriptError(f"{field} invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise FramedTranscriptError(f"{field} must contain a JSON object")
    return data


def load_ref(fixture: dict[str, Any], key: str) -> tuple[str, str, dict[str, Any] | None]:
    ref = fixture.get(key)
    if not isinstance(ref, dict):
        raise FramedTranscriptError(f"fixture missing {key} reference")
    rel = clean_archive_path(ref.get("path"), f"{key}.path")
    observed = sha256_file(ROOT / rel)
    if ref.get("sha256") != observed:
        raise FramedTranscriptError(f"{key} hash mismatch")
    parsed = load_json_rel(rel, key) if rel.endswith(".json") else None
    return rel, observed, parsed


def as_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise FramedTranscriptError(f"{field} must be an integer")
    return value


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in {2, 3}:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def eval_univariate(coeffs: list[int], x: int, p: int) -> int:
    acc = 0
    power = 1
    for coeff in coeffs:
        acc = (acc + coeff * power) % p
        power = (power * x) % p
    return acc


def eval_multivariate(terms: list[dict[str, Any]], point: list[int], p: int) -> int:
    total = 0
    for idx, term in enumerate(terms):
        coeff = as_int(term.get("coefficient"), f"polynomial_terms[{idx}].coefficient") % p
        exponents = term.get("exponents")
        if not isinstance(exponents, list) or len(exponents) != len(point):
            raise FramedTranscriptError(f"polynomial_terms[{idx}].exponents length mismatch")
        value = coeff
        for j, exponent in enumerate(exponents):
            exp = as_int(exponent, f"polynomial_terms[{idx}].exponents[{j}]")
            if exp < 0:
                raise FramedTranscriptError(f"polynomial_terms[{idx}].exponents[{j}] must be non-negative")
            value = (value * pow(point[j] % p, exp, p)) % p
        total = (total + value) % p
    return total


def direct_boolean_sum(terms: list[dict[str, Any]], variable_count: int, p: int) -> int:
    if variable_count > 12:
        raise FramedTranscriptError("direct Boolean-hypercube check is capped at 12 variables for this verifier")
    total = 0
    for point in itertools.product([0, 1], repeat=variable_count):
        total = (total + eval_multivariate(terms, list(point), p)) % p
    return total


def normalize_coefficients(raw: Any, degree_bound: int, p: int, field: str) -> list[int]:
    if not isinstance(raw, list) or not raw:
        raise FramedTranscriptError(f"{field} must be a non-empty list")
    if len(raw) > degree_bound + 1:
        raise FramedTranscriptError(f"{field} exceeds declared degree bound {degree_bound}")
    return [as_int(value, f"{field}[{idx}]") % p for idx, value in enumerate(raw)]


def check_non_claims(items: Any, field: str) -> None:
    text = "\n".join(str(item) for item in (items or []))
    for phrase in ["not a SNARK", "not zero knowledge", "not succinct", "not a production Fiat-Shamir"]:
        if phrase.lower() not in text.lower():
            raise FramedTranscriptError(f"{field} missing non-claim: {phrase}")


def verify_refs(fixture: dict[str, Any], p: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    contract_path, contract_sha, contract = load_ref(fixture, "transcript_operation_contract")
    profile_path, profile_sha, profile = load_ref(fixture, "protocol_profile")
    full_receipt_path, full_receipt_sha, full_receipt = load_ref(fixture, "payload_receipt_full")
    minimum_receipt_path, minimum_receipt_sha, minimum_receipt = load_ref(fixture, "payload_receipt_minimum")
    receipt_contract_path, receipt_contract_sha, receipt_contract = load_ref(fixture, "payload_receipt_contract")
    receipt_verifier_path, receipt_verifier_sha, _ = load_ref(fixture, "payload_receipt_verifier")
    transcript_verifier_path, transcript_verifier_sha, _ = load_ref(fixture, "transcript_framed_verifier")
    if contract is None or profile is None or receipt_contract is None or full_receipt is None or minimum_receipt is None:
        raise FramedTranscriptError("JSON references failed to parse")
    for label, data in [("contract", contract), ("profile", profile), ("receipt_contract", receipt_contract), ("full_receipt", full_receipt), ("minimum_receipt", minimum_receipt)]:
        if data.get("revision") != REVISION:
            raise FramedTranscriptError(f"{label} revision mismatch")
    if profile.get("field", {}).get("modulus") != p:
        raise FramedTranscriptError("protocol profile field modulus mismatch")
    if contract.get("operation_model") != "labeled_absorb_then_labeled_challenge_state_machine":
        raise FramedTranscriptError("unsupported transcript operation model")
    check_non_claims(contract.get("non_claims"), "contract")
    check_non_claims(profile.get("non_claims"), "profile")
    check_non_claims(receipt_contract.get("non_claims"), "receipt_contract")
    return contract, profile, {
        "transcript_operation_contract_path": contract_path,
        "transcript_operation_contract_sha256": contract_sha,
        "protocol_profile_path": profile_path,
        "protocol_profile_sha256": profile_sha,
        "payload_receipt_full_path": full_receipt_path,
        "payload_receipt_full_sha256": full_receipt_sha,
        "payload_receipt_minimum_path": minimum_receipt_path,
        "payload_receipt_minimum_sha256": minimum_receipt_sha,
        "payload_receipt_contract_path": receipt_contract_path,
        "payload_receipt_contract_sha256": receipt_contract_sha,
        "payload_receipt_verifier_path": receipt_verifier_path,
        "payload_receipt_verifier_sha256": receipt_verifier_sha,
        "transcript_framed_verifier_path": transcript_verifier_path,
        "transcript_framed_verifier_sha256": transcript_verifier_sha,
    }


def verify_context(contract: dict[str, Any], fixture: dict[str, Any], refs: dict[str, str], p: int, claimed_sum: int) -> dict[str, Any]:
    context = fixture.get("transcript_context")
    if not isinstance(context, dict):
        raise FramedTranscriptError("fixture missing transcript_context")
    required = contract.get("must_bind_public_context_fields")
    if not isinstance(required, list) or not required:
        raise FramedTranscriptError("contract must declare required public context fields")
    missing = [field for field in required if field not in context]
    if missing:
        raise FramedTranscriptError("transcript_context missing required fields: " + ", ".join(missing))
    if context.get("revision") != REVISION:
        raise FramedTranscriptError("transcript_context revision mismatch")
    if context.get("domain_separator") != contract.get("domain_separator"):
        raise FramedTranscriptError("domain separator mismatch")
    if context.get("field_modulus") != p or context.get("claimed_sum_mod_p") != claimed_sum:
        raise FramedTranscriptError("field/claim context mismatch")
    if context.get("canonical_payloads_missing_in_overlay") != 17:
        raise FramedTranscriptError("missing payload count drifted")
    if context.get("rights_status") != "publication_blocked_pending_rights_decision":
        raise FramedTranscriptError("rights status drifted")
    for key, value in refs.items():
        if key.endswith("_sha256") and context.get(key) != value:
            raise FramedTranscriptError(f"transcript_context does not bind {key}")
    check_non_claims(context.get("non_claims"), "transcript_context")
    return context


def init_state(domain: str, contract_id: str) -> str:
    return sha256_obj({"event": "init", "domain_separator": domain, "contract_id": contract_id, "revision": REVISION})


def absorb_state(state: str, op_index: int, label: str, message: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    message_sha = sha256_obj(message)
    frame = {
        "op_index": op_index,
        "operation": "absorb",
        "label": label,
        "message_sha256": message_sha,
        "previous_state_sha256": state,
    }
    return sha256_obj(frame), message_sha, frame


def challenge_state(state: str, op_index: int, label: str, round_no: int, p: int, domain: str) -> tuple[str, int, str, dict[str, Any]]:
    input_frame = {
        "op_index": op_index,
        "operation": "challenge",
        "label": label,
        "round": round_no,
        "field_modulus": p,
        "domain_separator": domain,
        "previous_state_sha256": state,
    }
    input_sha = sha256_obj(input_frame)
    challenge = int(input_sha, 16) % p
    state_frame = {
        "op_index": op_index,
        "operation": "challenge_result",
        "label": label,
        "round": round_no,
        "challenge": challenge,
        "challenge_input_sha256": input_sha,
        "previous_state_sha256": state,
    }
    return sha256_obj(state_frame), challenge, input_sha, input_frame


def expected_absorb_message(label: str, fixture: dict[str, Any], context: dict[str, Any], claim: dict[str, Any], rounds_by_no: dict[int, dict[str, Any]], running_claim_by_round: dict[int, int], final_message: dict[str, Any]) -> dict[str, Any]:
    if label == "ev.context":
        return context
    if label == "sumcheck.claim":
        return claim
    if label == "payload.receipt.full":
        return fixture["payload_receipt_full"]
    if label == "payload.receipt.minimum":
        return fixture["payload_receipt_minimum"]
    if label.startswith("sumcheck.round.") and label.endswith(".polynomial"):
        try:
            round_no = int(label.split(".")[2])
        except Exception as exc:
            raise FramedTranscriptError(f"cannot parse round from label {label!r}") from exc
        round_data = rounds_by_no.get(round_no)
        if not isinstance(round_data, dict):
            raise FramedTranscriptError(f"round {round_no} absent from transcript rounds")
        return {
            "round": round_no,
            "variable": round_data.get("variable"),
            "running_claim_before_round": running_claim_by_round[round_no],
            "polynomial_coefficients": round_data.get("polynomial_coefficients"),
        }
    if label == "sumcheck.final_evaluation":
        return final_message
    raise FramedTranscriptError(f"unsupported absorb label: {label}")


def verify_operation_log(contract: dict[str, Any], fixture: dict[str, Any], context: dict[str, Any], claim: dict[str, Any], p: int) -> dict[str, Any]:
    transcript = fixture.get("transcript")
    if not isinstance(transcript, dict):
        raise FramedTranscriptError("fixture missing transcript")
    rounds = transcript.get("rounds")
    operations = transcript.get("operations")
    if not isinstance(rounds, list) or not rounds:
        raise FramedTranscriptError("transcript.rounds must be a non-empty list")
    if not isinstance(operations, list) or not operations:
        raise FramedTranscriptError("transcript.operations must be a non-empty list")
    required_sequence = contract.get("required_operation_sequence")
    if operations != [] and (not isinstance(required_sequence, list) or len(required_sequence) != len(operations)):
        raise FramedTranscriptError("operation sequence length mismatch")
    degree_bounds = claim.get("degree_bounds")
    variables = claim.get("variables")
    terms = claim.get("polynomial_terms")
    claimed_sum = as_int(claim.get("claimed_sum"), "claim.claimed_sum") % p
    if not isinstance(degree_bounds, list) or not isinstance(variables, list) or not isinstance(terms, list):
        raise FramedTranscriptError("claim is missing degree bounds, variables, or polynomial terms")
    if len(degree_bounds) != len(variables) or len(rounds) != len(variables):
        raise FramedTranscriptError("round count does not match variables")
    direct = direct_boolean_sum(terms, len(variables), p)
    if direct != claimed_sum:
        raise FramedTranscriptError(f"direct Boolean-hypercube sum {direct} != claimed sum {claimed_sum}")
    rounds_by_no: dict[int, dict[str, Any]] = {}
    for idx, round_data in enumerate(rounds, start=1):
        if not isinstance(round_data, dict):
            raise FramedTranscriptError(f"round {idx} is not an object")
        round_no = as_int(round_data.get("round"), f"rounds[{idx}].round")
        if round_no != idx:
            raise FramedTranscriptError(f"round sequence mismatch at {idx}")
        rounds_by_no[round_no] = round_data
    running_claim = claimed_sum
    running_claim_by_round: dict[int, int] = {}
    challenges: list[int] = []
    for idx, round_data in enumerate(rounds, start=1):
        bound = as_int(degree_bounds[idx - 1], f"degree_bounds[{idx - 1}]")
        coeffs = normalize_coefficients(round_data.get("polynomial_coefficients"), bound, p, f"round {idx} coefficients")
        before = as_int(round_data.get("running_claim_before_round"), f"round {idx} running_claim_before_round") % p
        if before != running_claim:
            raise FramedTranscriptError(f"round {idx} running claim mismatch")
        if (eval_univariate(coeffs, 0, p) + eval_univariate(coeffs, 1, p)) % p != running_claim:
            raise FramedTranscriptError(f"round {idx} sumcheck consistency failed")
        running_claim_by_round[idx] = running_claim
        # Challenge values are verified during operation-log processing below.
        challenges.append(as_int(round_data.get("challenge"), f"round {idx} challenge") % p)
        running_claim = eval_univariate(coeffs, challenges[-1], p)
    final_eval = as_int(transcript.get("final_evaluation"), "transcript.final_evaluation") % p
    direct_final = eval_multivariate(terms, challenges, p)
    if final_eval != running_claim or final_eval != direct_final:
        raise FramedTranscriptError(f"final evaluation mismatch: final={final_eval} running={running_claim} direct={direct_final}")
    final_message = {"final_evaluation": final_eval, "challenges": challenges, "running_claim_after_last_round": running_claim}

    state = init_state(contract.get("domain_separator"), contract.get("contract_id"))
    observed_challenges: list[int] = []
    for op_index, (expected, op) in enumerate(zip(required_sequence, operations), start=1):
        if not isinstance(expected, dict) or not isinstance(op, dict):
            raise FramedTranscriptError(f"operation {op_index} is not an object")
        for key in ["op", "label"]:
            if op.get(key) != expected.get(key):
                raise FramedTranscriptError(f"operation {op_index} {key} mismatch: got {op.get(key)!r}, expected {expected.get(key)!r}")
        label = str(op.get("label"))
        if op.get("op") == "absorb":
            expected_message = expected_absorb_message(label, fixture, context, claim, rounds_by_no, running_claim_by_round, final_message)
            if op.get("message") != expected_message:
                raise FramedTranscriptError(f"operation {op_index} absorb message mismatch for {label}")
            state, message_sha, _frame = absorb_state(state, op_index, label, expected_message)
            if op.get("message_sha256") != message_sha:
                raise FramedTranscriptError(f"operation {op_index} message hash mismatch")
            if op.get("state_sha256") != state:
                raise FramedTranscriptError(f"operation {op_index} state hash mismatch")
        elif op.get("op") == "challenge":
            round_no = as_int(expected.get("round"), f"operation {op_index} expected round")
            if op.get("round") != round_no:
                raise FramedTranscriptError(f"operation {op_index} round mismatch")
            state, challenge, input_sha, _frame = challenge_state(state, op_index, label, round_no, p, contract.get("domain_separator"))
            if op.get("challenge_input_sha256") != input_sha:
                raise FramedTranscriptError(f"operation {op_index} challenge input hash mismatch")
            if op.get("challenge") != challenge:
                raise FramedTranscriptError(f"operation {op_index} challenge mismatch")
            if rounds_by_no[round_no].get("challenge") != challenge:
                raise FramedTranscriptError(f"round {round_no} challenge not bound to operation log")
            if op.get("state_sha256") != state:
                raise FramedTranscriptError(f"operation {op_index} challenge state hash mismatch")
            observed_challenges.append(challenge)
        else:
            raise FramedTranscriptError(f"unsupported operation kind at {op_index}: {op.get('op')!r}")
    if transcript.get("final_transcript_state_sha256") != state:
        raise FramedTranscriptError("final transcript state hash mismatch")
    if observed_challenges != challenges:
        raise FramedTranscriptError("operation-derived challenges do not match transcript rounds")
    return {"ok": True, "challenges": challenges, "final_evaluation": final_eval, "final_transcript_state_sha256": state, "operation_count": len(operations)}


def verify_fixture_data(fixture: dict[str, Any]) -> dict[str, Any]:
    if fixture.get("fixture_type") != "transparent_framed_fiat_shamir_sumcheck_transcript_fixture":
        raise FramedTranscriptError("unsupported fixture_type")
    if fixture.get("revision") != REVISION:
        raise FramedTranscriptError("fixture revision mismatch")
    check_non_claims(fixture.get("non_claims"), "fixture")
    field = fixture.get("field")
    if not isinstance(field, dict):
        raise FramedTranscriptError("fixture missing field")
    p = as_int(field.get("modulus"), "field.modulus")
    if not is_prime(p):
        raise FramedTranscriptError("field modulus is not prime")
    claim = fixture.get("claim")
    if not isinstance(claim, dict) or claim.get("protocol") != "sumcheck":
        raise FramedTranscriptError("fixture claim must be a sumcheck object")
    claimed_sum = as_int(claim.get("claimed_sum"), "claim.claimed_sum") % p
    contract, _profile, refs = verify_refs(fixture, p)
    context = verify_context(contract, fixture, refs, p, claimed_sum)
    transcript = verify_operation_log(contract, fixture, context, claim, p)
    return {"ok": True, "fixture_id": fixture.get("fixture_id"), "transcript": transcript, "refs": refs}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify rev0858 framed transcript-operation toy sumcheck fixture")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    fixture_rel = clean_archive_path(args.fixture, "--fixture")
    try:
        fixture = load_json_rel(fixture_rel, "fixture")
        result = verify_fixture_data(fixture)
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "fixture": fixture_rel, "failure": str(exc)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("sumcheck-fs-framed-transcript-rev0858: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-fs-framed-transcript-rev0858: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-fs-framed-transcript-rev0858: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("sumcheck-fs-framed-transcript-rev0858: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

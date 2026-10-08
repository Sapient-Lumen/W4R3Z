#!/usr/bin/env python3
"""Verify the rev0857 transparent sumcheck transcript with prefix-bound challenges.

rev0856 stopped trusting prover-supplied challenges, but only prior challenge
values were directly carried into later challenge derivation.  This rev0857
verifier binds the previous public transcript-message hashes, running claims,
payload admission contract identity, and verifier identity into each challenge.
It remains a tiny transparent harness: not a SNARK verifier, not zero knowledge,
not succinct, and not a production Fiat-Shamir transform.
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
REVISION = "rev0857"


class PrefixVerifyError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise PrefixVerifyError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise PrefixVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise PrefixVerifyError(f"{field} must be a POSIX relative path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise PrefixVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        raise PrefixVerifyError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PrefixVerifyError(f"{field} is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PrefixVerifyError(f"{field} must contain a JSON object")
    return data


def as_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise PrefixVerifyError(f"{field} must be an integer")
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
            raise PrefixVerifyError(f"polynomial_terms[{idx}].exponents length mismatch")
        value = coeff
        for j, exponent in enumerate(exponents):
            exp = as_int(exponent, f"polynomial_terms[{idx}].exponents[{j}]")
            if exp < 0:
                raise PrefixVerifyError(f"polynomial_terms[{idx}].exponents[{j}] must be non-negative")
            value = (value * pow(point[j] % p, exp, p)) % p
        total = (total + value) % p
    return total


def direct_boolean_sum(terms: list[dict[str, Any]], variable_count: int, p: int) -> int:
    if variable_count > 12:
        raise PrefixVerifyError("direct Boolean-hypercube check is capped at 12 variables for this verifier")
    total = 0
    for point in itertools.product([0, 1], repeat=variable_count):
        total = (total + eval_multivariate(terms, list(point), p)) % p
    return total


def normalize_coefficients(raw: Any, degree_bound: int, p: int, field: str) -> list[int]:
    if not isinstance(raw, list) or not raw:
        raise PrefixVerifyError(f"{field} must be a non-empty list")
    if len(raw) > degree_bound + 1:
        raise PrefixVerifyError(f"{field} exceeds declared degree bound {degree_bound}")
    return [as_int(value, f"{field}[{idx}]") % p for idx, value in enumerate(raw)]


def hash_to_field(obj: dict[str, Any], p: int) -> int:
    return int.from_bytes(hashlib.sha256(canonical_json(obj)).digest(), "big") % p


def load_ref(fixture: dict[str, Any], key: str) -> tuple[str, str, dict[str, Any] | None]:
    ref = fixture.get(key)
    if not isinstance(ref, dict):
        raise PrefixVerifyError(f"fixture missing {key} reference")
    rel = clean_archive_path(ref.get("path"), f"{key}.path")
    observed = sha256_file(ROOT / rel)
    if ref.get("sha256") != observed:
        raise PrefixVerifyError(f"{key} hash mismatch")
    parsed = None
    if rel.endswith(".json"):
        parsed = load_json_rel(rel, key)
    return rel, observed, parsed


def verify_contract_profile_and_refs(fixture: dict[str, Any], p: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    contract_path, contract_sha, contract = load_ref(fixture, "transcript_prefix_contract")
    profile_path, profile_sha, profile = load_ref(fixture, "protocol_profile")
    admission_path, admission_sha, admission = load_ref(fixture, "payload_admission_contract")
    payload_verifier_path, payload_verifier_sha, _ = load_ref(fixture, "payload_candidate_verifier")
    transcript_verifier_path, transcript_verifier_sha, _ = load_ref(fixture, "transcript_prefix_verifier")
    if contract is None or profile is None or admission is None:
        raise PrefixVerifyError("contract/profile/admission references must be JSON objects")
    for label, data in [("contract", contract), ("profile", profile), ("admission", admission)]:
        if data.get("revision") != REVISION:
            raise PrefixVerifyError(f"{label} revision mismatch")
    if contract.get("challenge_function", {}).get("name") != "sha256_canonical_json_to_field":
        raise PrefixVerifyError("unsupported challenge function")
    if profile.get("field", {}).get("modulus") != p:
        raise PrefixVerifyError("profile field modulus mismatch")
    non_claims = "\n".join(str(x) for x in list(contract.get("non_claims") or []) + list(profile.get("non_claims") or []) + list(admission.get("non_claims") or []))
    for phrase in ["not a SNARK", "not zero knowledge", "not a production Fiat-Shamir transform", "not a rights grant"]:
        if phrase.lower() not in non_claims.lower():
            raise PrefixVerifyError(f"contract/profile/admission missing non-claim: {phrase}")
    return contract, profile, {
        "transcript_prefix_contract_path": contract_path,
        "transcript_prefix_contract_sha256": contract_sha,
        "protocol_profile_path": profile_path,
        "protocol_profile_sha256": profile_sha,
        "payload_admission_contract_path": admission_path,
        "payload_admission_contract_sha256": admission_sha,
        "payload_candidate_verifier_path": payload_verifier_path,
        "payload_candidate_verifier_sha256": payload_verifier_sha,
        "transcript_prefix_verifier_path": transcript_verifier_path,
        "transcript_prefix_verifier_sha256": transcript_verifier_sha,
    }


def verify_context(contract: dict[str, Any], fixture: dict[str, Any], refs: dict[str, str], p: int, claimed_sum: int) -> dict[str, Any]:
    context = fixture.get("transcript_context")
    if not isinstance(context, dict):
        raise PrefixVerifyError("fixture missing transcript_context")
    required = contract.get("must_bind_public_context_fields")
    if not isinstance(required, list) or not required:
        raise PrefixVerifyError("contract must declare required public context fields")
    missing = [field for field in required if field not in context]
    if missing:
        raise PrefixVerifyError("transcript_context missing required bindings: " + ", ".join(missing))
    if context.get("revision") != REVISION:
        raise PrefixVerifyError("transcript_context revision mismatch")
    if context.get("domain_separator") != contract.get("domain_separator"):
        raise PrefixVerifyError("transcript_context domain separator mismatch")
    if context.get("canonical_payloads_missing_in_overlay") != 17:
        raise PrefixVerifyError("transcript_context missing-payload count drifted")
    if context.get("rights_status") != "publication_blocked_pending_rights_decision":
        raise PrefixVerifyError("transcript_context rights status drifted")
    if context.get("field_modulus") != p or context.get("claimed_sum_mod_p") != claimed_sum:
        raise PrefixVerifyError("transcript_context field/claim binding mismatch")
    for key, value in refs.items():
        if key.endswith("_sha256") and context.get(key) != value:
            raise PrefixVerifyError(f"transcript_context does not bind {key}")
    return context


def verify_fixture_data(fixture: dict[str, Any]) -> dict[str, Any]:
    if fixture.get("fixture_type") != "transparent_prefix_bound_fiat_shamir_sumcheck_transcript_fixture":
        raise PrefixVerifyError("unsupported fixture_type")
    if fixture.get("revision") != REVISION:
        raise PrefixVerifyError("fixture revision mismatch")
    non_claims = "\n".join(str(item) for item in fixture.get("non_claims") or [])
    for phrase in ["not a SNARK", "not zero knowledge", "not a production Fiat-Shamir transform"]:
        if phrase.lower() not in non_claims.lower():
            raise PrefixVerifyError(f"required non-claim missing: {phrase}")
    field = fixture.get("field")
    if not isinstance(field, dict):
        raise PrefixVerifyError("missing field object")
    p = as_int(field.get("modulus"), "field.modulus")
    if not is_prime(p):
        raise PrefixVerifyError("field.modulus must be prime for this verifier")
    contract, _profile, refs = verify_contract_profile_and_refs(fixture, p)
    claim = fixture.get("claim")
    transcript = fixture.get("transcript")
    if not isinstance(claim, dict) or not isinstance(transcript, dict):
        raise PrefixVerifyError("missing claim or transcript object")
    if claim.get("protocol") != "sumcheck":
        raise PrefixVerifyError("claim.protocol must be sumcheck")
    variables = claim.get("variables")
    degree_bounds = claim.get("degree_bounds")
    terms = claim.get("polynomial_terms")
    if not isinstance(variables, list) or not variables or not all(isinstance(x, str) and x for x in variables):
        raise PrefixVerifyError("claim.variables must be a non-empty list of names")
    if not isinstance(degree_bounds, list) or len(degree_bounds) != len(variables):
        raise PrefixVerifyError("claim.degree_bounds length mismatch")
    degree_bounds_int = [as_int(value, f"claim.degree_bounds[{idx}]") for idx, value in enumerate(degree_bounds)]
    if any(value < 0 for value in degree_bounds_int):
        raise PrefixVerifyError("degree bounds must be non-negative")
    if not isinstance(terms, list) or not terms:
        raise PrefixVerifyError("claim.polynomial_terms must be non-empty")
    claimed_sum = as_int(claim.get("claimed_sum"), "claim.claimed_sum") % p
    context = verify_context(contract, fixture, refs, p, claimed_sum)
    if direct_boolean_sum(terms, len(variables), p) != claimed_sum:
        raise PrefixVerifyError("direct Boolean sum does not match claimed sum")
    rounds = transcript.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != len(variables):
        raise PrefixVerifyError("transcript.rounds length must equal variable count")
    running_claim = claimed_sum
    challenges: list[int] = []
    previous_round_message_hashes: list[str] = []
    context_hash = sha256_obj(context)
    claim_hash = sha256_obj(claim)
    domain_separator = contract.get("domain_separator")
    contract_id = contract.get("contract_id")
    round_summaries = []
    for idx, round_obj in enumerate(rounds):
        if not isinstance(round_obj, dict):
            raise PrefixVerifyError(f"transcript.rounds[{idx}] must be an object")
        expected_round = idx + 1
        if round_obj.get("round") != expected_round:
            raise PrefixVerifyError(f"round index mismatch at {idx}")
        if round_obj.get("variable") != variables[idx]:
            raise PrefixVerifyError(f"round variable mismatch at {idx}")
        coeffs = normalize_coefficients(round_obj.get("polynomial_coefficients"), degree_bounds_int[idx], p, f"rounds[{idx}].polynomial_coefficients")
        if round_obj.get("running_claim_before_round") != running_claim:
            raise PrefixVerifyError(f"round {expected_round} running claim binding mismatch")
        if round_obj.get("previous_round_message_hashes") != previous_round_message_hashes:
            raise PrefixVerifyError(f"round {expected_round} previous transcript prefix mismatch")
        lhs = (eval_univariate(coeffs, 0, p) + eval_univariate(coeffs, 1, p)) % p
        if lhs != running_claim:
            raise PrefixVerifyError(f"round {expected_round} consistency failed: g(0)+g(1)={lhs}, expected {running_claim}")
        challenge_input = {
            "contract_id": contract_id,
            "domain_separator": domain_separator,
            "revision": REVISION,
            "field_modulus": p,
            "transcript_context_hash": context_hash,
            "claim_hash": claim_hash,
            "transcript_prefix_contract_sha256": refs["transcript_prefix_contract_sha256"],
            "protocol_profile_sha256": refs["protocol_profile_sha256"],
            "payload_admission_contract_sha256": refs["payload_admission_contract_sha256"],
            "payload_candidate_verifier_sha256": refs["payload_candidate_verifier_sha256"],
            "transcript_prefix_verifier_sha256": refs["transcript_prefix_verifier_sha256"],
            "round": expected_round,
            "variable": variables[idx],
            "degree_bound": degree_bounds_int[idx],
            "running_claim_before_round": running_claim,
            "previous_round_message_hashes": previous_round_message_hashes,
            "round_polynomial_coefficients": coeffs,
        }
        expected_input_hash = sha256_obj(challenge_input)
        if round_obj.get("expected_challenge_input_sha256") != expected_input_hash:
            raise PrefixVerifyError(f"round {expected_round} challenge input hash mismatch")
        expected_challenge = hash_to_field(challenge_input, p)
        observed_challenge = as_int(round_obj.get("challenge"), f"rounds[{idx}].challenge")
        if observed_challenge != expected_challenge:
            raise PrefixVerifyError(f"round {expected_round} challenge mismatch: observed {observed_challenge}, expected {expected_challenge}")
        if not 0 <= observed_challenge < p:
            raise PrefixVerifyError(f"round {expected_round} challenge outside field")
        running_after = eval_univariate(coeffs, observed_challenge, p)
        message = {
            "round": expected_round,
            "variable": variables[idx],
            "degree_bound": degree_bounds_int[idx],
            "running_claim_before_round": round_obj.get("running_claim_before_round"),
            "polynomial_coefficients": coeffs,
            "challenge_input_sha256": expected_input_hash,
            "challenge": observed_challenge,
            "running_claim_after_round": running_after,
        }
        message_hash = sha256_obj(message)
        if round_obj.get("round_message_sha256") != message_hash:
            raise PrefixVerifyError(f"round {expected_round} message hash mismatch")
        running_claim = running_after
        challenges.append(observed_challenge)
        previous_round_message_hashes.append(message_hash)
        round_summaries.append({"round": expected_round, "challenge": observed_challenge, "next_claim": running_claim, "round_message_sha256": message_hash})
    final_eval = as_int(transcript.get("final_evaluation"), "transcript.final_evaluation") % p
    public_eval = eval_multivariate(terms, challenges, p)
    if running_claim != final_eval:
        raise PrefixVerifyError(f"final transcript value {final_eval} != last round claim {running_claim}")
    if public_eval != final_eval:
        raise PrefixVerifyError(f"public polynomial evaluation {public_eval} != final transcript value {final_eval}")
    if transcript.get("final_transcript_prefix_sha256") != sha256_obj({"round_message_hashes": previous_round_message_hashes, "final_evaluation": final_eval}):
        raise PrefixVerifyError("final transcript prefix hash mismatch")
    return {
        "ok": True,
        "fixture_id": fixture.get("fixture_id"),
        "field_modulus": p,
        "claimed_sum": claimed_sum,
        "transcript_context_hash": context_hash,
        "claim_hash": claim_hash,
        "challenges": challenges,
        "final_evaluation": final_eval,
        "rounds": round_summaries,
        "final_transcript_prefix_sha256": transcript.get("final_transcript_prefix_sha256"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a transparent sumcheck transcript with prefix-bound deterministic challenges")
    parser.add_argument("--fixture", required=True, help="fixture JSON path relative to repository root")
    parser.add_argument("--expect-fail", action="store_true", help="succeed only if verification fails")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)
    fixture_rel = clean_archive_path(args.fixture, "--fixture")
    try:
        result = verify_fixture_data(load_json_rel(fixture_rel, "fixture"))
    except Exception as exc:
        if args.expect_fail:
            payload = {"ok": True, "expected_failure_observed": True, "fixture": fixture_rel, "failure": str(exc)}
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print("sumcheck-fs-prefix-transcript-rev0857: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-fs-prefix-transcript-rev0857: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-fs-prefix-transcript-rev0857: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("sumcheck-fs-prefix-transcript-rev0857: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

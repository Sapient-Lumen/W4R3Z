#!/usr/bin/env python3
"""Verify the rev0856 transparent sumcheck transcript with deterministic challenge binding.

This verifier closes a specific harness risk from rev0855: accepting explicit
prover-supplied challenge values without recomputing them from public context,
prior transcript material, and the current round polynomial.  It is intentionally
small and transparent.  It is not a SNARK verifier, not zero knowledge, not
succinct, and not a production Fiat-Shamir transform.
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
REVISION = "rev0856"


class FSVerifyError(Exception):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def sha256_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise FSVerifyError(f"cannot hash non-regular file: {path}")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise FSVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise FSVerifyError(f"{field} must be a POSIX relative path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise FSVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        raise FSVerifyError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise FSVerifyError(f"{field} is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise FSVerifyError(f"{field} must contain a JSON object")
    return data


def as_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise FSVerifyError(f"{field} must be an integer")
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
            raise FSVerifyError(f"polynomial_terms[{idx}].exponents length mismatch")
        value = coeff
        for j, exponent in enumerate(exponents):
            exp = as_int(exponent, f"polynomial_terms[{idx}].exponents[{j}]")
            if exp < 0:
                raise FSVerifyError(f"polynomial_terms[{idx}].exponents[{j}] must be non-negative")
            value = (value * pow(point[j] % p, exp, p)) % p
        total = (total + value) % p
    return total


def direct_boolean_sum(terms: list[dict[str, Any]], variable_count: int, p: int) -> int:
    if variable_count > 12:
        raise FSVerifyError("direct Boolean-hypercube check is capped at 12 variables for this verifier")
    total = 0
    for point in itertools.product([0, 1], repeat=variable_count):
        total = (total + eval_multivariate(terms, list(point), p)) % p
    return total


def normalize_coefficients(raw: Any, degree_bound: int, p: int, field: str) -> list[int]:
    if not isinstance(raw, list) or not raw:
        raise FSVerifyError(f"{field} must be a non-empty list")
    if len(raw) > degree_bound + 1:
        raise FSVerifyError(f"{field} exceeds declared degree bound {degree_bound}")
    return [as_int(value, f"{field}[{idx}]") % p for idx, value in enumerate(raw)]


def hash_to_field(obj: dict[str, Any], p: int) -> int:
    return int.from_bytes(hashlib.sha256(canonical_json(obj)).digest(), "big") % p


def verify_contract_and_profile(fixture: dict[str, Any], p: int) -> tuple[dict[str, Any], dict[str, Any]]:
    contract_ref = fixture.get("transcript_contract")
    profile_ref = fixture.get("protocol_profile")
    if not isinstance(contract_ref, dict) or not isinstance(profile_ref, dict):
        raise FSVerifyError("fixture must include transcript_contract and protocol_profile references")
    contract_path = clean_archive_path(contract_ref.get("path"), "transcript_contract.path")
    profile_path = clean_archive_path(profile_ref.get("path"), "protocol_profile.path")
    if contract_ref.get("sha256") != sha256_file(ROOT / contract_path):
        raise FSVerifyError("transcript challenge contract hash mismatch")
    if profile_ref.get("sha256") != sha256_file(ROOT / profile_path):
        raise FSVerifyError("protocol profile hash mismatch")
    contract = load_json_rel(contract_path, "transcript challenge contract")
    profile = load_json_rel(profile_path, "protocol profile")
    if contract.get("revision") != REVISION or profile.get("revision") != REVISION:
        raise FSVerifyError("contract/profile revision mismatch")
    if contract.get("challenge_function", {}).get("name") != "sha256_canonical_json_to_field":
        raise FSVerifyError("unsupported challenge function")
    if profile.get("field", {}).get("modulus") != p:
        raise FSVerifyError("profile field modulus mismatch")
    non_claims = "\n".join(str(x) for x in list(contract.get("non_claims") or []) + list(profile.get("non_claims") or []))
    for phrase in ["not a SNARK", "not zero knowledge", "not a production Fiat-Shamir transform"]:
        if phrase.lower() not in non_claims.lower():
            raise FSVerifyError(f"contract/profile missing non-claim: {phrase}")
    return contract, profile


def verify_context(contract: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    context = fixture.get("transcript_context")
    if not isinstance(context, dict):
        raise FSVerifyError("fixture missing transcript_context")
    required = contract.get("must_bind_public_context_fields")
    if not isinstance(required, list) or not required:
        raise FSVerifyError("contract must declare required public context fields")
    missing = [field for field in required if field not in context]
    if missing:
        raise FSVerifyError("transcript_context missing required bindings: " + ", ".join(missing))
    if context.get("revision") != REVISION:
        raise FSVerifyError("transcript_context revision mismatch")
    if context.get("domain_separator") != contract.get("domain_separator"):
        raise FSVerifyError("transcript_context domain separator mismatch")
    if context.get("canonical_payloads_missing_in_overlay") != 17:
        raise FSVerifyError("transcript_context missing-payload count drifted")
    if context.get("rights_status") != "publication_blocked_pending_rights_decision":
        raise FSVerifyError("transcript_context rights status drifted")
    return context


def verify_fixture_data(fixture: dict[str, Any]) -> dict[str, Any]:
    if fixture.get("fixture_type") != "transparent_fiat_shamir_sumcheck_transcript_fixture":
        raise FSVerifyError("unsupported fixture_type")
    if fixture.get("revision") != REVISION:
        raise FSVerifyError("fixture revision mismatch")
    non_claims = "\n".join(str(item) for item in fixture.get("non_claims") or [])
    for phrase in ["not a SNARK", "not zero knowledge", "not a production Fiat-Shamir transform"]:
        if phrase.lower() not in non_claims.lower():
            raise FSVerifyError(f"required non-claim missing: {phrase}")
    field = fixture.get("field")
    if not isinstance(field, dict):
        raise FSVerifyError("missing field object")
    p = as_int(field.get("modulus"), "field.modulus")
    if not is_prime(p):
        raise FSVerifyError("field.modulus must be prime for this verifier")
    contract, profile = verify_contract_and_profile(fixture, p)
    context = verify_context(contract, fixture)
    claim = fixture.get("claim")
    transcript = fixture.get("transcript")
    if not isinstance(claim, dict) or not isinstance(transcript, dict):
        raise FSVerifyError("missing claim or transcript object")
    if claim.get("protocol") != "sumcheck":
        raise FSVerifyError("claim.protocol must be sumcheck")
    variables = claim.get("variables")
    degree_bounds = claim.get("degree_bounds")
    terms = claim.get("polynomial_terms")
    if not isinstance(variables, list) or not variables or not all(isinstance(x, str) and x for x in variables):
        raise FSVerifyError("claim.variables must be a non-empty list of names")
    if not isinstance(degree_bounds, list) or len(degree_bounds) != len(variables):
        raise FSVerifyError("claim.degree_bounds length mismatch")
    degree_bounds_int = [as_int(value, f"claim.degree_bounds[{idx}]") for idx, value in enumerate(degree_bounds)]
    if any(value < 0 for value in degree_bounds_int):
        raise FSVerifyError("degree bounds must be non-negative")
    if not isinstance(terms, list) or not terms:
        raise FSVerifyError("claim.polynomial_terms must be non-empty")
    claimed_sum = as_int(claim.get("claimed_sum"), "claim.claimed_sum") % p
    if context.get("claimed_sum_mod_p") != claimed_sum or context.get("field_modulus") != p:
        raise FSVerifyError("transcript_context field/claim binding mismatch")
    if direct_boolean_sum(terms, len(variables), p) != claimed_sum:
        raise FSVerifyError("direct Boolean sum does not match claimed sum")
    rounds = transcript.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != len(variables):
        raise FSVerifyError("transcript.rounds length must equal variable count")
    running_claim = claimed_sum
    challenges: list[int] = []
    context_hash = sha256_obj(context)
    claim_hash = sha256_obj(claim)
    domain_separator = contract.get("domain_separator")
    contract_id = contract.get("contract_id")
    round_summaries = []
    for idx, round_obj in enumerate(rounds):
        if not isinstance(round_obj, dict):
            raise FSVerifyError(f"transcript.rounds[{idx}] must be an object")
        expected_round = idx + 1
        if round_obj.get("round") != expected_round:
            raise FSVerifyError(f"round index mismatch at {idx}")
        if round_obj.get("variable") != variables[idx]:
            raise FSVerifyError(f"round variable mismatch at {idx}")
        coeffs = normalize_coefficients(round_obj.get("polynomial_coefficients"), degree_bounds_int[idx], p, f"rounds[{idx}].polynomial_coefficients")
        lhs = (eval_univariate(coeffs, 0, p) + eval_univariate(coeffs, 1, p)) % p
        if lhs != running_claim:
            raise FSVerifyError(f"round {expected_round} consistency failed: g(0)+g(1)={lhs}, expected {running_claim}")
        challenge_input = {
            "contract_id": contract_id,
            "domain_separator": domain_separator,
            "revision": REVISION,
            "field_modulus": p,
            "transcript_context_hash": context_hash,
            "claim_hash": claim_hash,
            "round": expected_round,
            "variable": variables[idx],
            "prior_challenges": challenges,
            "round_polynomial_coefficients": coeffs,
        }
        expected_input_hash = sha256_obj(challenge_input)
        if round_obj.get("expected_challenge_input_sha256") != expected_input_hash:
            raise FSVerifyError(f"round {expected_round} challenge input hash mismatch")
        expected_challenge = hash_to_field(challenge_input, p)
        observed_challenge = as_int(round_obj.get("challenge"), f"rounds[{idx}].challenge")
        if observed_challenge != expected_challenge:
            raise FSVerifyError(f"round {expected_round} challenge mismatch: observed {observed_challenge}, expected {expected_challenge}")
        if not 0 <= observed_challenge < p:
            raise FSVerifyError(f"round {expected_round} challenge outside field")
        running_claim = eval_univariate(coeffs, observed_challenge, p)
        challenges.append(observed_challenge)
        round_summaries.append({"round": expected_round, "challenge": observed_challenge, "next_claim": running_claim})
    final_eval = as_int(transcript.get("final_evaluation"), "transcript.final_evaluation") % p
    public_eval = eval_multivariate(terms, challenges, p)
    if running_claim != final_eval:
        raise FSVerifyError(f"final transcript value {final_eval} != last round claim {running_claim}")
    if public_eval != final_eval:
        raise FSVerifyError(f"public polynomial evaluation {public_eval} != final transcript value {final_eval}")
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
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a transparent sumcheck transcript with deterministic challenge binding")
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
                print("sumcheck-fs-transcript-rev0856: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-fs-transcript-rev0856: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-fs-transcript-rev0856: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("sumcheck-fs-transcript-rev0856: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

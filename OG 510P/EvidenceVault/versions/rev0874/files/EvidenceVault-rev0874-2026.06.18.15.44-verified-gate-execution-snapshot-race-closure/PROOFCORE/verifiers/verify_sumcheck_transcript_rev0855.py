#!/usr/bin/env python3
"""Verify a transparent toy sumcheck transcript for the rev0855 streamfold lane.

This is deliberately a tiny public-field verifier.  It is useful because it
turns the selected sumcheck lane into executable proof work, but it is not a
SNARK verifier, is not zero knowledge, and does not verify the absent canonical
streamfold payloads.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REVISION = "rev0855"


class SumcheckVerifyError(Exception):
    pass


def clean_archive_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise SumcheckVerifyError(f"{field} must be a non-empty string")
    if "\x00" in text or "\\" in text:
        raise SumcheckVerifyError(f"{field} must be a POSIX relative path: {text!r}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise SumcheckVerifyError(f"{field} must be clean and relative: {text!r}")
    return pure.as_posix()


def load_json_rel(path_text: str, field: str) -> dict[str, Any]:
    rel = clean_archive_path(path_text, field)
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        raise SumcheckVerifyError(f"{field} is not a regular file: {rel}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SumcheckVerifyError(f"{field} is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SumcheckVerifyError(f"{field} must contain a JSON object")
    return data


def as_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise SumcheckVerifyError(f"{field} must be an integer")
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


def mod(value: int, p: int) -> int:
    return value % p


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
            raise SumcheckVerifyError(f"polynomial_terms[{idx}].exponents length mismatch")
        value = coeff
        for j, exponent in enumerate(exponents):
            exp = as_int(exponent, f"polynomial_terms[{idx}].exponents[{j}]")
            if exp < 0:
                raise SumcheckVerifyError(f"polynomial_terms[{idx}].exponents[{j}] must be non-negative")
            value = (value * pow(point[j] % p, exp, p)) % p
        total = (total + value) % p
    return total


def direct_boolean_sum(terms: list[dict[str, Any]], variable_count: int, p: int) -> int:
    if variable_count > 12:
        raise SumcheckVerifyError("direct Boolean-hypercube check is capped at 12 variables for this toy verifier")
    total = 0
    for point in itertools.product([0, 1], repeat=variable_count):
        total = (total + eval_multivariate(terms, list(point), p)) % p
    return total


def normalize_coefficients(raw: Any, degree_bound: int, p: int, field: str) -> list[int]:
    if not isinstance(raw, list) or not raw:
        raise SumcheckVerifyError(f"{field} must be a non-empty list")
    if len(raw) > degree_bound + 1:
        raise SumcheckVerifyError(f"{field} exceeds declared degree bound {degree_bound}")
    return [as_int(value, f"{field}[{idx}]") % p for idx, value in enumerate(raw)]


def verify_fixture_data(fixture: dict[str, Any]) -> dict[str, Any]:
    if fixture.get("fixture_type") != "transparent_sumcheck_transcript_fixture":
        raise SumcheckVerifyError("unsupported fixture_type")
    if fixture.get("revision") != REVISION:
        raise SumcheckVerifyError("fixture revision mismatch")
    non_claims = "\n".join(str(item) for item in fixture.get("non_claims") or [])
    for phrase in ["not a SNARK", "not zero knowledge"]:
        if phrase.lower() not in non_claims.lower():
            raise SumcheckVerifyError(f"required non-claim missing: {phrase}")

    field = fixture.get("field")
    if not isinstance(field, dict):
        raise SumcheckVerifyError("missing field object")
    p = as_int(field.get("modulus"), "field.modulus")
    if not is_prime(p):
        raise SumcheckVerifyError("field.modulus must be prime for this verifier")

    claim = fixture.get("claim")
    transcript = fixture.get("transcript")
    if not isinstance(claim, dict) or not isinstance(transcript, dict):
        raise SumcheckVerifyError("missing claim or transcript object")
    if claim.get("protocol") != "sumcheck":
        raise SumcheckVerifyError("claim.protocol must be sumcheck")
    variables = claim.get("variables")
    degree_bounds = claim.get("degree_bounds")
    terms = claim.get("polynomial_terms")
    if not isinstance(variables, list) or not variables or not all(isinstance(x, str) and x for x in variables):
        raise SumcheckVerifyError("claim.variables must be a non-empty list of names")
    if not isinstance(degree_bounds, list) or len(degree_bounds) != len(variables):
        raise SumcheckVerifyError("claim.degree_bounds length mismatch")
    degree_bounds_int = [as_int(value, f"claim.degree_bounds[{idx}]") for idx, value in enumerate(degree_bounds)]
    if any(value < 0 for value in degree_bounds_int):
        raise SumcheckVerifyError("degree bounds must be non-negative")
    if not isinstance(terms, list) or not terms:
        raise SumcheckVerifyError("claim.polynomial_terms must be non-empty")
    claimed_sum = as_int(claim.get("claimed_sum"), "claim.claimed_sum") % p

    direct_sum = direct_boolean_sum(terms, len(variables), p)
    if direct_sum != claimed_sum:
        raise SumcheckVerifyError(f"direct Boolean sum {direct_sum} != claimed sum {claimed_sum}")

    rounds = transcript.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != len(variables):
        raise SumcheckVerifyError("transcript.rounds length must equal variable count")

    running_claim = claimed_sum
    challenges: list[int] = []
    round_summaries = []
    for idx, round_obj in enumerate(rounds):
        if not isinstance(round_obj, dict):
            raise SumcheckVerifyError(f"transcript.rounds[{idx}] must be an object")
        expected_round = idx + 1
        if round_obj.get("round") != expected_round:
            raise SumcheckVerifyError(f"round index mismatch at {idx}")
        if round_obj.get("variable") != variables[idx]:
            raise SumcheckVerifyError(f"round variable mismatch at {idx}")
        coeffs = normalize_coefficients(round_obj.get("polynomial_coefficients"), degree_bounds_int[idx], p, f"rounds[{idx}].polynomial_coefficients")
        lhs = (eval_univariate(coeffs, 0, p) + eval_univariate(coeffs, 1, p)) % p
        if lhs != running_claim:
            raise SumcheckVerifyError(f"round {expected_round} consistency failed: g(0)+g(1)={lhs}, expected {running_claim}")
        challenge = as_int(round_obj.get("challenge"), f"rounds[{idx}].challenge")
        if not 0 <= challenge < p:
            raise SumcheckVerifyError(f"round {expected_round} challenge outside field")
        running_claim = eval_univariate(coeffs, challenge, p)
        challenges.append(challenge)
        round_summaries.append({"round": expected_round, "next_claim": running_claim})

    final_eval = as_int(transcript.get("final_evaluation"), "transcript.final_evaluation") % p
    public_eval = eval_multivariate(terms, challenges, p)
    if running_claim != final_eval:
        raise SumcheckVerifyError(f"final transcript value {final_eval} != last round claim {running_claim}")
    if public_eval != final_eval:
        raise SumcheckVerifyError(f"public polynomial evaluation {public_eval} != final transcript value {final_eval}")

    return {
        "ok": True,
        "fixture_id": fixture.get("fixture_id"),
        "field_modulus": p,
        "claimed_sum": claimed_sum,
        "challenges": challenges,
        "final_evaluation": final_eval,
        "rounds": round_summaries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a transparent toy sumcheck transcript")
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
                print("sumcheck-transcript-rev0855: expected failure observed")
            return 0
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-transcript-rev0855: FAIL: {exc}", file=sys.stderr)
        return 1
    if args.expect_fail:
        message = "fixture unexpectedly verified successfully"
        if args.json:
            print(json.dumps({"ok": False, "fixture": fixture_rel, "error": message}, indent=2, sort_keys=True))
        else:
            print(f"sumcheck-transcript-rev0855: FAIL: {message}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("sumcheck-transcript-rev0855: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

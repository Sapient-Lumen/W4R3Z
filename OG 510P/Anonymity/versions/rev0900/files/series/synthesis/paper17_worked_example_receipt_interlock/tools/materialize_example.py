#!/usr/bin/env python3
import copy
import gzip
import hashlib
import io
import json
import math
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, getcontext
from fractions import Fraction
from pathlib import Path

from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

CLAIM_ID = "anondht.reader_privacy.workedexample.v0"
TW_NAME = "tw.reader_24h.q500.v1"
RELEASE_ID = "worked-example-draft-199"
NOTE_VERSION = "1.99"
PRIMARY_EXPOSURE_LABEL = "enf.primary.linkability.v1"
PLAN_CATALOG_VERSION = "worked-example-plan-catalog-v2"
COMPARE_PROFILE_ID = "worked-example-compare-profile-v1"
INVENTORY_ID = "worked-example-artifact-inventory-v1"
MANIFEST_ID = "worked-example-support-manifest-v1"

Q = 500
FALLBACK_RATE_HAT = 0.05
R_PI_UPPER = 1.2
P_OBS_UPPER = 0.02
RHO_UPPER = 0.01
RAW_TIERS = [
    {"tier": "CSET", "raw_b": 1.40},
    {"tier": "TIME", "raw_b": 0.30},
    {"tier": "CONG", "raw_b": 0.15},
]
PRIMARY_LINKABILITY_BOUND = 0.0

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


POINTER_FORMAT = "worked-example-json-payload-pointer-v1"
OFFLOADED_JSON_ARTIFACTS = {
    "example_public_request_response_packet_refresh_response_menus.json",
    "example_public_request_response_packet_refresh_response_packet_closure_verdicts.json",
    "example_public_request_response_packet_refresh_response_packets.json",
    "example_question_routes.json",
    "example_series_spine.json",
    "example_successor_challenge_answer_review_menus.json",
    "example_verifier_report.json",
}
COMPACT_JSON_ARTIFACTS = {
    "example_public_request_response_packet_refresh_response_menus.json",
    "example_public_request_response_packet_refresh_response_packet_closure_verdicts.json",
    "example_public_request_response_packet_refresh_response_packets.json",
    "example_question_routes.json",
    "example_series_spine.json",
}


def logical_json_bytes(name: str, obj) -> bytes:
    if name in COMPACT_JSON_ARTIFACTS:
        return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


def deterministic_gzip(data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, compresslevel=9, mtime=0) as handle:
        handle.write(data)
    return buffer.getvalue()


def write_json(path: Path, obj) -> str:
    """Write one artifact while preserving the large-payload split.

    Earlier rebuilds regenerated seven offloaded JSON objects inline and silently
    erased more than 7.5 MB of hot-path savings.  The generator now owns the
    pointer contract: logical JSON bytes determine the returned digest, while a
    deterministic mtime-zero gzip payload and small pointer occupy the archive.
    """
    name = path.name
    data = logical_json_bytes(name, obj)
    logical_sha = sha256_bytes(data)
    if path.parent.resolve() == ART.resolve() and name in OFFLOADED_JSON_ARTIFACTS:
        payload_dir = ART / "offloaded_payloads"
        payload_dir.mkdir(exist_ok=True)
        payload_rel = f"offloaded_payloads/{name}.gz"
        payload = deterministic_gzip(data)
        (ART / payload_rel).write_bytes(payload)
        pointer = {
            "encoding": "gzip-json-utf8-mtime0",
            "logical_bytes": len(data),
            "logical_path": name,
            "logical_sha256": logical_sha,
            "offloaded_payload_pointer": True,
            "payload_bytes": len(payload),
            "payload_path": payload_rel,
            "payload_sha256": sha256_bytes(payload),
            "pointer_format": POINTER_FORMAT,
            "publication_authorized": False,
            "storage_reason": "Paper17 high-volume generated JSON is kept out of the hot edit path while preserving the original logical byte digest for validator and support-manifest checks.",
        }
        path.write_bytes((json.dumps(pointer, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    else:
        path.write_bytes(data)
    return logical_sha


def manifest_entry(path: str, digest: str) -> dict:
    """Return a digest row with explicit path-base semantics.

    The historic support manifest used paths relative to artifacts/ and ../ for
    helper files. Keep that spelling for compatibility, but also write the
    base and repo-relative path so future validators never guess the resolver.
    """
    if path.startswith("../"):
        base = "paper_root"
        repo_rel = (ROOT / path[3:]).relative_to(ROOT.parents[2]).as_posix()
    else:
        base = "artifact_root"
        repo_rel = (ART / path).relative_to(ROOT.parents[2]).as_posix()
    return {"path": path, "base": base, "repo_relative_path": repo_rel, "sha256": digest}


def decorate_payload_pointer_manifest(manifest: dict) -> None:
    """Rebuild support-manifest storage rows from the authoritative pointers."""
    rows = [
        row for row in manifest.get("files", [])
        if not (isinstance(row, dict) and str(row.get("path", "")).startswith("offloaded_payloads/"))
    ]
    by_path = {str(row.get("path")): row for row in rows if isinstance(row, dict)}
    summaries = []
    for name in sorted(OFFLOADED_JSON_ARTIFACTS):
        pointer_path = ART / name
        if not pointer_path.exists():
            continue
        try:
            pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not (isinstance(pointer, dict) and pointer.get("offloaded_payload_pointer") is True and pointer.get("pointer_format") == POINTER_FORMAT):
            continue
        payload_rel = str(pointer["payload_path"])
        logical_row = by_path.get(name)
        if logical_row is None:
            logical_row = manifest_entry(name, str(pointer["logical_sha256"]))
            rows.append(logical_row)
            by_path[name] = logical_row
        logical_row.update({
            "sha256": pointer["logical_sha256"],
            "logical_bytes": pointer["logical_bytes"],
            "payload_pointer_format": POINTER_FORMAT,
            "storage_path": payload_rel,
            "storage_bytes": pointer["payload_bytes"],
            "storage_sha256": pointer["payload_sha256"],
        })
        payload_row = manifest_entry(payload_rel, str(pointer["payload_sha256"]))
        payload_row.update({
            "logical_bytes": pointer["logical_bytes"],
            "logical_path": name,
            "logical_sha256": pointer["logical_sha256"],
            "payload_pointer_format": POINTER_FORMAT,
            "role": f"offloaded gzip payload for logical artifact {name}",
        })
        rows.append(payload_row)
        summaries.append({
            "byte_reduction_on_hot_path": int(pointer["logical_bytes"]) - pointer_path.stat().st_size,
            "logical_bytes": pointer["logical_bytes"],
            "logical_path": name,
            "logical_sha256": pointer["logical_sha256"],
            "payload_bytes": pointer["payload_bytes"],
            "payload_path": payload_rel,
            "payload_sha256": pointer["payload_sha256"],
        })
    manifest["files"] = sorted(rows, key=lambda row: str(row.get("path", "")))
    manifest["payload_pointer_policy"] = {
        "format": POINTER_FORMAT,
        "logical_digest_rule": "For pointer rows, the file row sha256 remains the SHA-256 of the decompressed logical JSON bytes, not the small pointer file.",
        "publication_authorized": False,
        "storage_digest_rule": "Payload files are listed separately with their gzip byte SHA-256.",
    }
    manifest["offloaded_payload_summary"] = sorted(summaries, key=lambda row: (-int(row["byte_reduction_on_hot_path"]), row["logical_path"]))



def canon_bytes(obj) -> bytes:
    # Stable canonicalization for ids: sorted keys, no whitespace.
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_id(obj) -> str:
    return "sha256:" + sha256_bytes(canon_bytes(obj))


FALLBACK_CONTACT_SURFACE = {
    "method": "GET",
    "url": "https://cid.contact/routing/v1/providers",
    "filter_protocols": ["transport-bitswap"],
    "timeouts": {"http_router": "30s", "routing": "60s"},
}
FALLBACK_CONTACT_SURFACE_ID = sha256_id(FALLBACK_CONTACT_SURFACE)

FALLBACK_EMPTY_RESULT_EQUIVALENCE = {
    "server_preferred_status": 200,
    "client_must_treat_404_as_empty_result": True,
    "source": "Routing V1 interoperability / IPIP-0513",
}


# Human-facing labels for the worked example (used in the paper); ids are digest-bound claim fields.
FALLBACK_CCT_LABEL = "enf.fallback.cct.v1"
FALLBACK_VECTOR_LABEL = "enf.fallback.vector.v1"
PATHSELECT_LABEL = "enf.pathselect.fallbackbit.v1"

PROFILING_LABEL = "enf.profiling.retrybucket.v1"

PROFILING_PREFIXFETCH_LABEL = "enf.profiling.prefixfetch.v1"
PROFILING_PREFIXFETCH_STATECOND_LABEL = "enf.profiling.prefixfetch.statecond.v1"

PROFILING_CONTACT_COARSENED_LABEL = "enf.profiling.contact.coarsened.v1"

ENF_DECLS = {
    PRIMARY_EXPOSURE_LABEL: {
        "enf_schema": "enf.v1",
        "label": PRIMARY_EXPOSURE_LABEL,
        "tier": "primary_surface",
        "projection": "identity_to_destination_linkability",
        "unit": "lookup",
        "conditioning": {"separation_class": "sep.nr1"},
        "note": "Assumption-qualified primary-path surface for the worked example.",
    },
    FALLBACK_CCT_LABEL: {
        "enf_schema": "enf.v1",
        "label": FALLBACK_CCT_LABEL,
        "tier": "Tier2",
        "projection": "committee_contact_trace_failures",
        "unit": "lookup",
        "conditioning": {"committee_partition": "public"},
        "note": "Fallback ordered contact/failure trace (Tier 2) for the worked example.",
    },
    FALLBACK_VECTOR_LABEL: {
        "enf_schema": "enf.v1",
        "label": FALLBACK_VECTOR_LABEL,
        "tier": "TieredVector",
        "projection": "fallback_vector_contact_time_congestion",
        "unit": "lookup",
        "conditioning": {"bucket_coarsening": "public"},
        "note": "Tiered fallback observation vector (contact/time/congestion) for the worked example.",
    },
    PATHSELECT_LABEL: {
        "enf_schema": "enf.v1",
        "label": PATHSELECT_LABEL,
        "tier": "Tier0",
        "projection": "fallback_indicator_stream",
        "unit": "lookup",
        "conditioning": {"policy": "primary_or_fallback"},
        "note": "Fallback-indicator witness stream used by the path-selection tax.",
    },
    PROFILING_LABEL: {
        "enf_schema": "enf.v1",
        "label": PROFILING_LABEL,
        "tier": "Tier1",
        "projection": "retry_bucket_trace",
        "unit": "lookup",
        "conditioning": {"bucket_width": "250ms", "window": "24h"},
        "note": "Profiling/equalization surface: a coarse retry-bucket trace used only to exercise the evidence_id interface in the worked example.",
    },

    PROFILING_PREFIXFETCH_LABEL: {
        "enf_schema": "enf.v1",
        "label": PROFILING_PREFIXFETCH_LABEL,
        "tier": "Tier1",
        "projection": "prefix_fetch_signature",
        "unit": "lookup",
        "conditioning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix"},
        "note": "Profiling/equalization surface: a toy prefix-fetch signature used only to exercise a second evidence_id wiring path in the worked example (variant receipt).",
    },

    PROFILING_PREFIXFETCH_STATECOND_LABEL: {
        "enf_schema": "enf.v1",
        "label": PROFILING_PREFIXFETCH_STATECOND_LABEL,
        "tier": "Tier1",
        "projection": "prefix_fetch_signature",
        "unit": "lookup",
        "conditioning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "state_witness": "bucket_staleness_class:fresh|stale"},
        "note": "Profiling/equalization surface: prefix-fetch signature conditioned on a published bucket-staleness witness; used only to exercise conditional-witness plumbing (state-conditioned variant receipt).",
    },
PROFILING_CONTACT_COARSENED_LABEL: {
    "enf_schema": "enf.v1",
    "label": PROFILING_CONTACT_COARSENED_LABEL,
    "tier": "Tier1",
    "projection": "contact_set_hash (coarsened)",
    "unit": "lookup",
    "conditioning": {"source_projection": "contact_set_hash", "coarsening": "sig2 = first2bits(sha256(serialized_contact_set))"},
    "note": "Profiling/equalization surface illustrating Synthesis~28: a high-cardinality contact-set hash is declared, but audits are performed on a deterministic coarsening (2-bit signature) to keep the alphabet sample-feasible (coarsening variant receipt).",
},




}

ENF_IDS = {label: sha256_id(decl) for label, decl in ENF_DECLS.items()}

PRIMARY_EXPOSURE = ENF_IDS[PRIMARY_EXPOSURE_LABEL]
FALLBACK_CCT_EXPOSURE = ENF_IDS[FALLBACK_CCT_LABEL]
FALLBACK_VECTOR_EXPOSURE = ENF_IDS[FALLBACK_VECTOR_LABEL]
PATHSELECT_EXPOSURE = ENF_IDS[PATHSELECT_LABEL]
PROFILING_EXPOSURE = ENF_IDS[PROFILING_LABEL]
PREFIXFETCH_EXPOSURE = ENF_IDS[PROFILING_PREFIXFETCH_LABEL]
PREFIXFETCH_STATECOND_EXPOSURE = ENF_IDS[PROFILING_PREFIXFETCH_STATECOND_LABEL]
PROFILING_CONTACT_COARSENED_EXPOSURE = ENF_IDS[PROFILING_CONTACT_COARSENED_LABEL]

TW_DECL = {
    "tw_schema": "tw.v1",
    "label": TW_NAME,
    "secret": "queried_content_id_bucket",
    "unit": "lookup",
    "window": {"type": "sliding", "duration": "24h"},
    "usage": {"Q_upper": Q, "status": "policy_bound"},
    "active": {"template": "BossFight_B", "selective_failure_in_scope": True},
    "background": {"Q": "none", "note": "Worked example treats primary separation as a policy declaration and budgets only fallback surfaces."},
}
TW_ID = sha256_id(TW_DECL)

exposure_registry = {
    "registry_id": "worked-example-enf-registry-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "entries": [
        {"label": label, "exposure_nf_id": ENF_IDS[label], "enf": ENF_DECLS[label]}
        for label in sorted(ENF_DECLS.keys())
    ],
    "note": "Label-to-ENF-ID binding for the worked example. Labels are human-facing; exposure_nf_id is the digest-bound claim field.",
}
exposure_registry_digest = write_json(ART / "example_exposure_nf_registry.json", exposure_registry)

tw_decl_obj = {
    "tw_decl_id": "worked-example-tw-decl-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "label": TW_NAME,
    "tw_id": TW_ID,
    "tw": TW_DECL,
    "note": "Threat/window declaration for the worked example; tw_id is the digest-bound claim field.",
}
tw_decl_digest = write_json(ART / "example_tw_decl.json", tw_decl_obj)

def attenuated_bits(raw_b: float, p: float) -> float:
    return math.log2((1.0 - p) + p * (2.0 ** raw_b))


def dec_fraction(value) -> Fraction:
    """Parse a public decimal/rational-looking input as an exact fraction."""
    return Fraction(str(value))


def fraction_payload(value: Fraction) -> dict:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def ceil_div(n: int, d: int) -> int:
    return -(-n // d)


def dyadic_pow2_upper_witness(exponent: Fraction, scale_bits: int = 96) -> dict:
    """Return a dyadic upper bound for 2**exponent plus an integer-checkable witness.

    The generator may use Decimal to find a tight candidate, but the emitted
    witness is accepted only by the validator's integer inequality
    upper_numerator**den >= 2**(num + scale_bits*den).
    """
    getcontext().prec = 120
    approx = Decimal(2) ** (Decimal(exponent.numerator) / Decimal(exponent.denominator))
    upper_numerator = int((approx * (Decimal(2) ** scale_bits)).to_integral_value(rounding=ROUND_CEILING))
    assert pow(upper_numerator, exponent.denominator) >= (1 << (exponent.numerator + scale_bits * exponent.denominator))
    return {
        "exponent_decimal": format(float(exponent), ".12g"),
        "exponent_fraction": fraction_payload(exponent),
        "upper_dyadic_numerator": str(upper_numerator),
        "upper_dyadic_denominator_power_of_two": scale_bits,
        "integer_verification_rule": "upper_dyadic_numerator**exponent_denominator >= 2**(exponent_numerator + scale_bits*exponent_denominator)",
    }


def ln2_bounds_via_atanh(terms: int) -> tuple[Fraction, Fraction]:
    # ln(2)=2*atanh(1/3)=2*sum_{k>=0} (1/3)^(2k+1)/(2k+1).
    partial = Fraction(0)
    for k in range(terms):
        partial += Fraction(1, (2 * k + 1) * (3 ** (2 * k + 1)))
    n = terms
    tail = Fraction(1, (2 * n + 1) * (3 ** (2 * n + 1))) * Fraction(9, 8)
    return 2 * partial, 2 * (partial + tail)


def ln1p_upper_alt(x: Fraction, terms: int) -> Fraction:
    # For 0<=x<=1, odd partial sums of the alternating log(1+x) series
    # are upper bounds.  Force an odd count so the certificate is monotone safe.
    if terms % 2 == 0:
        terms += 1
    acc = Fraction(0)
    power = x
    for k in range(1, terms + 1):
        term = power / k
        acc = acc + term if k % 2 else acc - term
        power *= x
    return acc


def exp_upper_taylor(x: Fraction, terms: int) -> Fraction:
    # Positive-term Taylor upper bound with a geometric tail bound.
    acc = Fraction(1)
    term = Fraction(1)
    for k in range(1, terms + 1):
        term *= x
        term /= k
        acc += term
    first_omitted = term * x / Fraction(terms + 1)
    ratio_bound = x / Fraction(terms + 2)
    assert ratio_bound < 1
    return acc + first_omitted / (1 - ratio_bound)


def ln_ratio_upper_atanh(numerator: Fraction, denominator: Fraction, terms: int) -> Fraction:
    """Upper-bound ln(numerator/denominator) for numerator >= denominator > 0.

    Uses ln(a/b)=2*atanh((a-b)/(a+b)) with a rational geometric tail.
    This converges quickly for the profiling ratios and keeps the certificate
    independent of host floating point.
    """
    assert numerator >= denominator > 0
    z = (numerator - denominator) / (numerator + denominator)
    partial = Fraction(0)
    for k in range(terms):
        partial += Fraction(2, 1) * (z ** (2 * k + 1)) / (2 * k + 1)
    tail = Fraction(2, 1) * (z ** (2 * terms + 1)) / ((2 * terms + 1) * (1 - z * z))
    return partial + tail


def decimal_floor_string(value: float, places: int = 12) -> str:
    quantum = Decimal(1).scaleb(-places)
    return format(Decimal(str(value)).quantize(quantum, rounding=ROUND_FLOOR), f'.{places}f')


def decimal_ceil_string(value: float, places: int = 12) -> str:
    quantum = Decimal(1).scaleb(-places)
    return format(Decimal(str(value)).quantize(quantum, rounding=ROUND_CEILING), f'.{places}f')


def decimal_ceil_fraction_string(value: Fraction, places: int = 6) -> str:
    getcontext().prec = max(80, places + 20)
    quantum = Decimal(1).scaleb(-places)
    dec = Decimal(value.numerator) / Decimal(value.denominator)
    return format(dec.quantize(quantum, rounding=ROUND_CEILING), f'.{places}f')


def binomial_tail_ge_le_alpha_decimal(n: int, x: int, p_decimal: str, alpha_num: int = 1, alpha_den: int = 3000) -> bool:
    """Check Pr_{p_decimal}[Bin(n,p)>=x] <= alpha exactly for decimal p."""
    frac = Fraction(p_decimal)
    if frac == 0:
        return x > 0
    if frac == 1:
        return x <= 0 and alpha_den <= alpha_num
    a = frac.numerator
    d = frac.denominator
    q = d - a
    term = pow(q, n)
    total = 0
    denom_pow = pow(d, n)
    for i in range(0, n + 1):
        if i >= x:
            total += term
        if i == n:
            break
        term = term * (n - i) * a // ((i + 1) * q)
    return total * alpha_den <= alpha_num * denom_pow


def binomial_cdf_le_alpha_decimal(n: int, x: int, p_decimal: str, alpha_num: int = 1, alpha_den: int = 3000) -> bool:
    """Check Pr_{p_decimal}[Bin(n,p)<=x] <= alpha exactly for decimal p."""
    frac = Fraction(p_decimal)
    if frac == 0:
        return x < 0 and alpha_den <= alpha_num
    if frac == 1:
        return x >= n and alpha_den <= alpha_num
    a = frac.numerator
    d = frac.denominator
    q = d - a
    term = pow(q, n)
    total = 0
    denom_pow = pow(d, n)
    for i in range(0, n + 1):
        if i <= x:
            total += term
        else:
            break
        if i == n:
            break
        term = term * (n - i) * a // ((i + 1) * q)
    return total * alpha_den <= alpha_num * denom_pow


# Rev0865 changes the worked-example numeric public surface from host-float
# rounded diagnostics to explicit conservative decimal upper bounds.  The raw
# Python recomputation is still useful smoke evidence, but receipt/verifier
# publication rows must be upper bounds that can be checked with exact rational
# arithmetic over their decimal strings.
OUTWARD_EFFECTIVE_BITS_BY_TIER = {
    "CSET": "0.046533410000",
    "TIME": "0.006654049337",
    "CONG": "0.003158047686",
}
FALLBACK_SUMMARY_BITS_UPPER = "0.056345507023"
SELECTION_TAX_BITS_UPPER = "0.263034405834"
TOTAL_SUMMARY_BITS_UPPER = "0.265904562929"
PRIMARY_LINKABILITY_BITS_UPPER = "0.000000000000"
PROFILING_ETA_BITS_UPPER = "0.821760"
PROFILING_DELTA_UPPER = "0.007464"

vector = []
for item in RAW_TIERS:
    raw_diagnostic = attenuated_bits(item["raw_b"], P_OBS_UPPER)
    upper_bits_decimal = OUTWARD_EFFECTIVE_BITS_BY_TIER[item["tier"]]
    vector.append({
        "tier": item["tier"],
        "p": P_OBS_UPPER,
        "raw_b": item["raw_b"],
        "effective_b": float(upper_bits_decimal),
        "effective_b_decimal_upper": upper_bits_decimal,
        "diagnostic_host_float_effective_b": raw_diagnostic,
        "status": {
            "p": "policy_upper_bound",
            "raw_b": "illustrative_input",
            "effective_b": "conservative_decimal_upper_bound_rev0865",
        },
    })

fallback_cset_bits = float(OUTWARD_EFFECTIVE_BITS_BY_TIER["CSET"])
fallback_summary_bits = float(FALLBACK_SUMMARY_BITS_UPPER)
selection_tax_bits = float(SELECTION_TAX_BITS_UPPER)
total_summary_bits = float(TOTAL_SUMMARY_BITS_UPPER)

state_decl_core = {
    "claim_id": CLAIM_ID,
    "tw_id": TW_ID,
    "state_contract_id": "stateadj.publicbucket.v1",
    "cache_policy": {
        "bucket_coarsening": "kademlia_prefix_bucket",
        "staleness_trigger": "public_bucket_staleness",
        "cache_key_scope": "bucket_level",
    },
    "routing_state": {
        "refresh_schedule": "6h_public_timer",
        "refresh_trigger": "time_only",
    },
    "rate_limit": {
        "Q_upper": Q,
        "window": "24h",
        "status": "policy_bound",
    },
    "included_state_surfaces": [
        "bucket_level_cache_staleness",
        "public_timer_routing_refresh",
        "24h_rate_limit_counter",
    ],
    "excluded_state_surfaces": [
        "long_lived_routing_table_content_beyond_public_refresh_schedule",
        "persistent_per_client_randomness_beyond_the_24h_window",
        "provider_side_or_server_side_state_not_named_in_the_receipt_bundle",
    ],
    "accounting_scope": "24h receipt-level summary with public-bucket fallback triggers and declared public timers only",
    "caveat": "Published summaries are 24h receipt-level summaries, not lifetime state-aware theorems. Persistent state may correlate successive lookups.",
}
state_decl_id = sha256_id(state_decl_core)
state_decl = dict(state_decl_core)
state_decl["state_decl_id"] = state_decl_id
state_decl_digest = write_json(ART / "example_state_decl.json", state_decl)

state_decl_registry = {
    "registry_id": "worked-example-state-decl-registry-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "entries": [
        {
            "state_contract_id": state_decl_core["state_contract_id"],
            "state_decl_id": state_decl_id,
            "state_decl": state_decl_core,
        }
    ],
    "canonicalization": "state_decl_id = sha256(canon(state_decl_core)) where canon uses sorted keys and no whitespace",
    "note": "State-declaration binding for the worked example; state_contract_id is human-facing, state_decl_id is the digest-bound claim field.",
}
state_decl_registry_digest = write_json(ART / "example_state_decl_registry.json", state_decl_registry)

effective_surface_resolution = {
    "resolution_id": "worked-example-effective-surface-resolution-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "state_decl_id": state_decl_id,
    "precedence_stack": [
        {"layer": "process_environment", "example_knobs": ["IPFS_HTTP_ROUTERS", "IPFS_HTTP_ROUTERS_FILTER_PROTOCOLS"], "owner": "Synthesis~30"},
        {"layer": "explicit_config", "example_knobs": ["Routing.DelegatedRouters", "HTTPRetrieval.Allowlist", "HTTPRetrieval.Denylist", "Routing.IgnoreProviders"], "owner": "Synthesis~30"},
        {"layer": "autoconf_auto_expansion", "example_knobs": ["AutoConf.URL", "AutoConf.RefreshInterval", "RAINBOW_AUTOCONF_URL", "RAINBOW_AUTOCONF_REFRESH"], "owner": "Synthesis~30"},
        {"layer": "receipt_line_item", "example_knobs": ["contact_surface_id", "contact_surface"], "owner": "Synthesis~12"},
        {"layer": "projection_schema", "example_knobs": ["exposure_nf_id", "empty_result_equivalence", "streaming_or_status_semantics"], "owner": "Synthesis~3"},
    ],
    "resolved_state_defaults": {
        "router_selection_source": "autoconf+explicit pinning under state_decl_id",
        "request_shaping_defaults": {
            "filter_protocols": ["transport-bitswap"],
            "timeouts": {"http_router": "30s", "routing": "60s"},
            "empty_result_equivalence": FALLBACK_EMPTY_RESULT_EQUIVALENCE,
        },
        "note": "Long-lived control-plane selectors and fallback rules live under state_decl_id; per-contact service semantics stay with contact_surface_id.",
    },
    "line_item_bindings": [
        {
            "name": "fallback_contact_surface",
            "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
            "contact_surface_id": FALLBACK_CONTACT_SURFACE_ID,
            "effective_contact_surface": FALLBACK_CONTACT_SURFACE,
            "effective_contact_surface_digest_rule": "sha256(canon(effective_contact_surface))",
            "ownership_partition": {
                "state_decl_id_owns": ["router selection precedence", "allow/deny and ignore-provider policy", "autoconf refresh and downgrade rules"],
                "contact_surface_id_owns": ["HTTP method", "full path-scoped URL", "declared request-shaping defaults", "declared time budgets"],
                "exposure_nf_id_owns": ["committee-contact trace schema", "response/status interpretation", "empty-result equivalence", "streaming/pacing semantics"],
            },
        }
    ],
    "note": "Digest-bound worked-example adjunct for assembling the effective replay surface. It is not a new receipt primitive. Response/status semantics (for example 200-empty vs client-interpreted 404-empty compatibility) are treated as ENF/projection semantics, not state drift.",
}
effective_surface_resolution_digest = write_json(ART / "example_effective_surface_resolution.json", effective_surface_resolution)

primary_surface_manifest = {
    "claim_id": CLAIM_ID,
    "exposure_nf_id": PRIMARY_EXPOSURE,
    "surface": "identity_to_destination_linkability",
    "separation_class": "sep.nr1",
    "declared_value_bits_per_lookup": PRIMARY_LINKABILITY_BOUND,
    "rho_upper": RHO_UPPER,
    "rho_status": "policy_upper_bound",
    "status": "policy_declaration",
    "valid_if": [
        "relay and router operator sets are declared disjoint within the threat window",
        "relay egress telemetry is not joined with router request logs within the threat window",
        "relay rotation stays at or below the declared 24h horizon",
        "primary traffic is served only through the declared relay set",
    ],
    "invalidators": [
        "declared relay-router collusion within the threat window",
        "shared telemetry or common log joins across relay and router",
        "relay stickiness exceeds the declared 24h horizon without lineage update",
        "primary traffic bypasses the declared relay set",
    ],
    "evidence_hooks": {
        "operator_roster": "support://primary/operators.example",
        "config_snapshot": "support://primary/config.example",
        "telemetry_separation_attestation": "support://primary/telemetry.example",
    },
}
primary_surface_digest = write_json(ART / "example_primary_surface_manifest.json", primary_surface_manifest)

CONTACT_COARSENED_EVIDENCE_ID_CURRENT_CUT = "sha256:22666e9853213a11356f4b863aa9e0dba88bcdd56306ac345acd80e1f09d36fa"
CONTACT_COARSENING_MAP_ID_CURRENT_CUT = "sha256:4c447e40d9e29e41ffa313f41edd5b2d54ad296c5a9f58b01d26ac220db5bbc1"

user_watch_policy = {
    "claim_id": CLAIM_ID,
    "primary_user_surface_exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
    "compare_fields": [
        "claim_pointer",
        "exposure_nf_id",
        "receipt_digest",
        "log_anchor.log_id",
        "consistency_context.checkpoint",
    ],
    "alarms": [
        {
            "when": "claim_pointer changes without a lineage note in the release-bound claim objects",
            "severity": "high",
            "action": "inspect new claim lineage before trusting the deployment",
        },
        {
            "when": "exposure_nf_id changes while claim_pointer remains the same",
            "severity": "high",
            "action": "treat as claim-surface drift and compare the new lineage relation",
        },
        {
            "when": "receipt_digest changes but no newer anchored checkpoint is supplied",
            "severity": "high",
            "action": "treat as an anchoring failure until the log context is refreshed",
        },
        {
            "when": "log_anchor.log_id changes",
            "severity": "medium",
            "action": "require a fresh trust decision and a new consistency chain",
        },
        {
            "when": "consistency proofs cannot be fetched for successive checkpoints",
            "severity": "medium",
            "action": "treat as a publication-integrity problem",
        },
    ],
    "note": "Operational client watch policy adjunct; not part of the minimal UVI tuple.",
}
user_watch_digest = write_json(ART / "example_user_watch_policy.json", user_watch_policy)

change_control = {
    "claim_id": CLAIM_ID,
    "change_control_id": "chgctl.receiptchain.v1",
    "release_action_matrix_id": "worked-example-release-action-matrix-v1",
    "release_id": RELEASE_ID,
    "interface_guard": {
        "required_exposures": [
            PRIMARY_EXPOSURE,
            FALLBACK_CCT_EXPOSURE,
            FALLBACK_VECTOR_EXPOSURE,
            PATHSELECT_EXPOSURE,
            PROFILING_EXPOSURE,
        ],
        "tw_id": TW_ID,
        "primary_separation_class": "sep.nr1",
        "primary_rho_upper": RHO_UPPER,
        "state_contract_id": state_decl["state_contract_id"],
        "state_decl_id": state_decl["state_decl_id"],
    },
    "refresh_only_if": [
        "required exposures are unchanged",
        "tw_id is unchanged",
        "primary separation class remains sep.nr1",
        "state_decl_id remains stable for stateadj.publicbucket.v1",
        "published total summary stays at or below 0.30 bits/lookup",
    ],
    "replay_changed_surfaces_if": [
        "budget_value changes on enf.fallback.vector.v1",
        "fallback trigger class changes",
        "p_obs upper bound changes",
        "watch-policy or replay-plan digests change",
    ],
    "full_recertify_if": [
        "any required exposure is removed or renamed",
        "tw_id changes",
        "primary separation class changes",
        "state_decl_id changes (state surface drift)",
        "lineage relation for a required exposure is new-interface",
        "published total summary exceeds 0.30 bits/lookup",
    ],
    "workflow_owner": "CertifiedC_disagreement_gated_recertification",
    "notes": [
        "Refresh-only means rebind the release receipt and transparency anchor without changing the certified interface.",
        "Changed-surface replay means rerun the named Evaluation2/Evaluation3 plans on the changed slices and issue a fresh notarized comparison.",
        "Full recertification means the certified interface changed and the deployment should not rely on a zero-label shortcut without a Certified C style disagreement gate or a fresh audit.",
        "Field-family-to-action defaults are published separately in example_release_action_matrix.json so users and auditors can classify a diff without re-reading every owner note.",
        "Per-action publication duties are published separately in example_release_obligation_profile.json so maintainers can tell what public outputs must be refreshed after classification.",
    ],
}
change_control_digest = write_json(ART / "example_change_control.json", change_control)

release_action_matrix = {
    "action_matrix_id": "worked-example-release-action-matrix-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "severity_order": ["refresh_only", "replay_changed_surfaces", "full_recertification"],
    "resolution_rule": "Match changed fields against rule match_terms; the highest-severity matched rule wins. If a contact-surface change also changes reader-visible transcript semantics, escalate by minting a new exposure_nf_id and let the interface-drift rule dominate.",
    "rules": [
        {
            "rule_id": "publication-refresh-only",
            "match_terms": ["log_checkpoint", "user_watch_policy"],
            "owner_notes": ["Synthesis~9", "Synthesis~13"],
            "default_classification": "refresh_only",
            "why": "Transparency-anchor refreshes and watch-text updates change publication/discovery metadata, not the certified privacy interface.",
        },
        {
            "rule_id": "plan-or-proof-replay",
            "match_terms": ["plan_spec_id", "plan_catalog_digest", "replay-plan", "watch-policy or replay-plan digests change"],
            "owner_notes": ["Synthesis~18", "Synthesis~20"],
            "default_classification": "replay_changed_surfaces",
            "escalate_if": ["the plan change is P2 claim-affecting semantics under Synthesis~18"],
            "why": "A changed replay promise forces at least a rerun/republication even when the interface ids are stable.",
        },
        {
            "rule_id": "contact-or-budget-replay",
            "match_terms": ["contact_surface_id", "obs_model.vector[*].p", "obs_model.p_obs_upper", "budget_value", "knobs", "evidence_id", "fallback trigger class"],
            "owner_notes": ["Synthesis~12", "Synthesis~18", "Synthesis~30"],
            "default_classification": "replay_changed_surfaces",
            "escalate_if": ["the changed contact surface induces a new reader-visible transcript semantics and therefore a new exposure_nf_id"],
            "why": "Same certified interface, but new effective service surface, evidence, or declared budget arithmetic requires replay and a fresh notarized comparison.",
        },
        {
            "rule_id": "interface-or-state-recertify",
            "match_terms": ["tw_id", "state_decl_id", "exposure_nf_id", "required exposure", "new-interface", "primary separation class"],
            "owner_notes": ["Synthesis~3", "Synthesis~4", "Synthesis~18", "Synthesis~30", "Certified~C"],
            "default_classification": "full_recertification",
            "why": "Threat-window, state-surface, projection, or primary-separation changes alter the certified interface or its guard and break zero-label continuity.",
        },
    ],
    "case_resolution_examples": [
        {
            "case_id": "refresh-only-A",
            "matched_rule_ids": ["publication-refresh-only"],
            "classification": "refresh_only",
        },
        {
            "case_id": "replay-required-B",
            "matched_rule_ids": ["contact-or-budget-replay"],
            "classification": "replay_changed_surfaces",
        },
        {
            "case_id": "full-recertification-C",
            "matched_rule_ids": ["interface-or-state-recertify"],
            "classification": "full_recertification",
        },
    ],
    "note": "Worked-example adjunct turning field-family diffs into default release actions. It instantiates the Synthesis~18 drift taxonomy for this bundle and is intended for user/auditor diff triage, not as a new receipt primitive.",
}
release_action_matrix_digest = write_json(ART / "example_release_action_matrix.json", release_action_matrix)

release_obligation_profile = {
    "obligation_profile_id": "worked-example-release-obligation-profile-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "release_action_matrix_id": release_action_matrix["action_matrix_id"],
    "resolution_rule": "Classify the diff first using the release-action matrix, then publish at least the output roles listed for the winning action class. Later notes can cite the obligation profile instead of rephrasing release-management duties.",
    "classes": [
        {
            "action_class": "refresh_only",
            "minimum_output_roles": [
                {"role": "fresh_release_binding", "binding": "example_release_receipt.json"},
                {"role": "fresh_user_pointer_or_watch_text", "binding": "example_uvi.json or example_user_watch_policy.json when changed"},
                {"role": "fresh_log_lineage", "binding": "transparency checkpoint / consistency context"},
            ],
            "continuity_status": "same_certified_interface_no_replay_needed",
            "note": "Publication metadata changed, but the certified interface and replay evidence remain reusable.",
        },
        {
            "action_class": "replay_changed_surfaces",
            "minimum_output_roles": [
                {"role": "fresh_release_binding", "binding": "example_release_receipt.json"},
                {"role": "fresh_compare_report", "binding": "example_compare_report.json"},
                {"role": "fresh_replay_verdict", "binding": "example_verifier_report.json"},
                {"role": "fresh_successor_continuity_verdict", "binding": "example_successor_continuity_verdict.json"},
                {"role": "fresh_successor_lineage_notice", "binding": "example_successor_lineage_notice.json"},
            ],
            "continuity_status": "same_certified_interface_replayed_surfaces",
            "note": "Same interface, changed budget-bearing surfaces: rerun the declared evaluators and publish the small cross-release outcome objects.",
        },
        {
            "action_class": "full_recertification",
            "minimum_output_roles": [
                {"role": "fresh_release_binding", "binding": "example_release_receipt.json"},
                {"role": "fresh_interface_ids", "binding": "tw_id / state_decl_id / exposure_nf_id family"},
                {"role": "recertification_packet", "binding": "Certified~C style disagreement gate or fresh audit packet"},
                {"role": "user_facing_lineage_notice", "binding": "release note / continuity stop notice"},
            ],
            "continuity_status": "no_automatic_continuity",
            "note": "Interface or guard drift breaks zero-label continuity and must be published as a new certified surface, not just a replay delta.",
        },
    ],
    "case_resolution_examples": [
        {
            "case_id": "refresh-only-A",
            "action_class": "refresh_only",
            "minimum_roles": ["fresh_release_binding", "fresh_log_lineage"],
        },
        {
            "case_id": "replay-required-B",
            "action_class": "replay_changed_surfaces",
            "minimum_roles": ["fresh_release_binding", "fresh_compare_report", "fresh_replay_verdict", "fresh_successor_continuity_verdict", "fresh_successor_lineage_notice"],
        },
        {
            "case_id": "full-recertification-C",
            "action_class": "full_recertification",
            "minimum_roles": ["fresh_release_binding", "fresh_interface_ids", "recertification_packet", "user_facing_lineage_notice"],
        },
    ],
    "note": "Worked-example adjunct mapping action classes to the minimal public outputs that should be refreshed after classification. It is publication policy, not a new receipt primitive.",
}
release_obligation_profile_digest = write_json(ART / "example_release_obligation_profile.json", release_obligation_profile)

successor_tw_decl_C = copy.deepcopy(TW_DECL)
successor_tw_decl_C["label"] = "tw.reader_24h.q750.v2"
successor_tw_decl_C["usage"] = {"Q_upper": 750, "status": "policy_bound"}
successor_tw_id_C = sha256_id(successor_tw_decl_C)
successor_state_decl_core_C = copy.deepcopy(state_decl_core)
successor_state_decl_core_C["tw_id"] = successor_tw_id_C
successor_state_decl_core_C["state_contract_id"] = "stateadj.prefixcache.v2"
successor_state_decl_core_C["cache_policy"]["staleness_trigger"] = "prefix_level_staleness"
successor_state_decl_id_C = sha256_id(successor_state_decl_core_C)

drift_cases = {
    "catalog_id": "worked-example-drift-cases-v1",
    "claim_id": CLAIM_ID,
    "base_release_id": RELEASE_ID,
    "cases": [
        {
            "case_id": "refresh-only-A",
            "classification": "refresh_only",
            "successor_release_id": RELEASE_ID + "a",
            "changed_fields": [
                "release_receipt.log_checkpoint",
                "example_user_watch_policy.json text only",
            ],
            "unchanged_guard_fields": change_control["interface_guard"],
            "published_total_summary_bits_per_lookup": total_summary_bits,
            "required_action": "rebind release receipt, publish fresh checkpoint lineage, keep prior certification surface",
        },
        {
            "case_id": "replay-required-B",
            "classification": "replay_changed_surfaces",
            "successor_release_id": RELEASE_ID + "b",
            "changed_fields": [
                "example_receipt.json: enf.fallback.vector.v1 obs_model.vector[*].p",
                "example_receipt.json: enf.fallback.cct.v1 obs_model.p_obs_upper",
            ],
            "old_values": {"p_obs_upper": 0.02},
            "new_values": {"p_obs_upper": 0.015},
            "unchanged_guard_fields": change_control["interface_guard"],
            "required_action": "rerun eval-fallback-cct-v1 and eval-fallback-vector-v1, publish fresh notarized comparison, update release lineage",
        },
        {
            "case_id": "full-recertification-C",
            "classification": "full_recertification",
            "successor_release_id": RELEASE_ID + "c",
            "changed_fields": [
                "tw_id",
                "example_state_decl.json: state_decl_id",
                "example_state_decl.json: cache_policy.staleness_trigger",
            ],
            "old_values": {
                "tw_id": TW_ID,
                "state_contract_id": state_decl["state_contract_id"],
                "state_decl_id": state_decl["state_decl_id"],
                "staleness_trigger": "public_bucket_staleness"
            },
            "new_values": {
                "tw_id": successor_tw_id_C,
                "state_contract_id": successor_state_decl_core_C["state_contract_id"],
                "state_decl_id": successor_state_decl_id_C,
                "staleness_trigger": successor_state_decl_core_C["cache_policy"]["staleness_trigger"]
            },
            "required_action": "treat as certified-interface change and require disagreement-gated recertification before continuity claims",
        },
    ],
}
drift_cases_digest = write_json(ART / "example_drift_cases.json", drift_cases)


# Replay plans: plan_id is a stable workflow handle; plan_spec_id digest-binds the replay semantics.
# This prevents ``same plan_id, different replay'' drift from hiding in prose.
PLAN_SPECS = [
    {
        "plan_id": "eval-primary-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation1_notarized_certificate_checks",
            "checks": [
                "exposure-id and separation-class match manifest",
                "relay/router policy identities match declared knobs",
                "attempt lineage matches release receipt",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_release_receipt.json",
                "example_primary_surface_manifest.json",
            ],
            "expected_output": "surface-bound notarized validation record for enf.primary.linkability.v1",
        },
    },
    {
        "plan_id": "eval-fallback-cct-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation3_calibration_plus_Evaluation1_notarization",
            "checks": [
                "recompute attenuated contact-surface bound from raw_b and p_obs",
                "check Q window and retry policy against declared knobs",
                "bind replay output to receipt digest",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_state_decl.json",
                "notarized attempt log (support artifact on request)",
            ],
            "expected_output": "recomputed fallback contact-surface budget and notarized comparison",
        },
    },
    {
        "plan_id": "eval-fallback-vector-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation3_calibration_plus_Evaluation1_notarization",
            "checks": [
                "recompute each observation-attenuation term from raw_b and the activation-probability upper bound",
                "verify conservative decimal upper bounds and their exact sum",
                "verify the state declaration digest, schedule form, and assumption-only composition status",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_state_decl.json",
                "timing and observation-attenuation references named by the support bundle",
            ],
            "expected_output": "recomputed illustrative fallback observation-vector summary and non-MC-EQ scope verdict",
        },
    },
    {
        "plan_id": "eval-pathselect-v1",
        "plan_spec": {
            "workflow_owner": "Evaluation2_advantage_contracts_plus_Evaluation1_notarization",
            "checks": [
                "recompute selection-tax term log2(R_pi)",
                "compare audit/live fallback-indicator behavior under the declared trigger class",
                "bind the monitored fallback-rate estimate to the declared state contract",
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_state_decl.json",
                "audit/live fallback-indicator logs (support artifact on request)",
            ],
            "expected_output": "selection-tax replay record plus audit/live comparability note",
        },
    },
    {
        "plan_id": "eval-profiling-eq-v1",
        "plan_spec": {
            "workflow_owner": "AnonymityB_profiling_audit_plus_Evaluation1_notarization",
            "checks": [
                "verify evidence_id binds the published evidence object",
                "recompute (eta,delta) from the evidence table under the declared finite-sample recipe",
                "confirm the projection schema (ENF-ID) and TW-ID match the receipt"
            ],
            "required_inputs": [
                "example_receipt.json",
                "example_profiling_evidence.json"
            ],
            "expected_output": "recomputed (eta,delta) equalization summary and notarized comparison"
        },
    },

    {
        "plan_id": "eval-profiling-prefixfetch-v1",
        "plan_spec": {
            "workflow_owner": "AnonymityB_prefixfetch_audit_plus_Evaluation1_notarization",
            "checks": [
                "verify evidence_id binds the published prefix-fetch evidence object",
                "recompute (eta,delta) from the prefix evidence table under the declared finite-sample recipe",
                "confirm the projection schema (ENF-ID) and TW-ID match the variant receipt"
            ],
            "required_inputs": [
                "example_receipt_prefixfetch_variant.json",
                "example_profiling_evidence_prefixfetch.json"
            ],
            "expected_output": "recomputed (eta,delta) prefix-fetch equalization summary and notarized comparison"
        },
    },

    {
        "plan_id": "eval-profiling-prefixfetch-statecond-v1",
        "plan_spec": {
            "workflow_owner": "AnonymityB_prefixfetch_statecond_audit_plus_Evaluation1_notarization",
            "checks": [
                "verify evidence_id binds the published state-conditioned prefix-fetch evidence object",
                "recompute (eta,delta) from the evidence table under the declared finite-sample recipe",
                "confirm the projection schema (ENF-ID), TW-ID, and witness semantics match the variant receipt"
            ],
            "required_inputs": [
                "example_receipt_prefixfetch_statecond_variant.json",
                "example_profiling_evidence_prefixfetch_statecond.json"
            ],
            "expected_output": "recomputed (eta,delta) state-conditioned prefix-fetch equalization summary and notarized comparison"
        },
    },

{
    "plan_id": "eval-profiling-contact-coarsened-v1",
    "plan_spec": {
        "workflow_owner": "AnonymityB_contact_coarsening_audit_plus_Evaluation1_notarization",
        "checks": [
            "verify evidence_id binds the published coarsened-contact evidence object",
            "verify coarsening_map_id binds the declared deterministic partition map",
            "recompute (eta,delta) from the evidence table under the declared finite-sample recipe",
            "confirm the projection schema (ENF-ID), TW-ID, and coarsening map match the variant receipt"
        ],
        "required_inputs": [
            "example_receipt_contact_coarsened_variant.json",
            "example_profiling_evidence_contact_coarsened.json",
            "example_coarsening_map_contact.json"
        ],
        "expected_output": "recomputed (eta,delta) coarsened-contact equalization summary and notarized comparison"
    },
},


]
for _p in PLAN_SPECS:
    _p["plan_spec_id"] = sha256_id(_p["plan_spec"])
PLAN_SPEC_ID_BY_PLAN_ID = {_p["plan_id"]: _p["plan_spec_id"] for _p in PLAN_SPECS}


# Profiling/equalization evidence object (receipt-grade via evidence_id).
# Profiling/equalization evidence object (receipt-grade via evidence_id).
# We treat the projection as a finite alphabet X (bucketed retry-trace summary),
# and publish a conservative (eta, delta_slack) max-divergence-style equalization summary
# derived from exact binomial (Clopper--Pearson) intervals + a union bound.

PROF_BINS = ["0-250ms", "250-500ms", "500-750ms", "750-1000ms", "1000ms+"]
PROF_COUNTS = {
    "k0": [1460, 550, 240, 145, 5],
    "k1": [1390, 600, 264, 146, 0],
    "k2": [1438, 576, 240, 144, 2],
}
PROF_N = {k: sum(v) for k, v in PROF_COUNTS.items()}
assert len(set(PROF_N.values())) == 1
_PROF_N = next(iter(PROF_N.values()))

PROFILING_FIXED_SAMPLE_LOCK_ID = "worked-example-profiling-fixed-sample-lock-v1"
PROFILING_REFRESH_POLICY_TOKEN = "successor_evidence_id_or_time_uniform_certificate_required"

def profiling_count_table_core() -> dict:
    return {
        "classes": sorted(PROF_COUNTS.keys()),
        "bins": list(PROF_BINS),
        "counts": {k: [int(v) for v in PROF_COUNTS[k]] for k in sorted(PROF_COUNTS.keys())},
        "n_per_class": {k: int(PROF_N[k]) for k in sorted(PROF_N.keys())},
    }

PROFILING_COUNT_TABLE_DIGEST = sha256_id(profiling_count_table_core())

def profiling_fixed_sample_plan() -> dict:
    return {
        "sampling_plan_id": PROFILING_FIXED_SAMPLE_LOCK_ID,
        "count_table_digest": PROFILING_COUNT_TABLE_DIGEST,
        "sample_generation": 1,
        "look_index": 1,
        "look_count_allowed": 1,
        "planned_n_per_class": {k: int(PROF_N[k]) for k in sorted(PROF_N.keys())},
        "analysis_trigger": "single analysis after all declared class/bin counts are frozen",
        "time_uniform_status": "not_time_uniform_fixed_sample_only",
        "optional_stopping_status": "disallowed_by_certificate",
        "alpha_spend_status": "delta_stat_0.01_spent_once_for_this_evidence_id_only",
        "future_refresh_policy": PROFILING_REFRESH_POLICY_TOKEN,
        "invalidators": [
            "adding or deleting samples before publishing this evidence_id",
            "peeking at intermediate counts to choose whether to stop",
            "refreshing counts under the same evidence_id",
            "changing projection, bins, classes, rare-support rule, or confidence spend",
        ],
        "successor_requirement": "Any repeated refresh, adaptive rerun, or monitoring stream must publish a successor evidence_id with a fresh fixed-sample lock or a declared time-uniform/e-value spending certificate.",
    }

def clopper_pearson_interval(k: int, n: int, alpha: float):
    # Two-sided Clopper--Pearson interval with per-cell miscoverage alpha.
    # The returned floats are diagnostics only; public evidence uses the
    # outward-rounded decimal strings below.
    a = alpha / 2.0
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1.0 - a, k + 1, n - k))
    return lo, hi


def clopper_pearson_interval_outward_decimal(k: int, n: int, alpha: float, places: int = 12):
    lo, hi = clopper_pearson_interval(k, n, alpha)
    lo_s = "0." + ("0" * places) if k == 0 else decimal_floor_string(lo, places)
    hi_s = "1." + ("0" * places) if k == n else decimal_ceil_string(hi, places)
    # Exact rational binomial-tail checks certify that rounding went in the
    # conservative direction.  For a lower endpoint L, Pr_L[X>=x] must be at
    # most alpha/2; for an upper endpoint U, Pr_U[X<=x] must be at most alpha/2.
    assert k == 0 or binomial_tail_ge_le_alpha_decimal(n, k, lo_s)
    assert k == n or binomial_cdf_le_alpha_decimal(n, k, hi_s)
    return lo_s, hi_s

PROF_DELTA_STAT = 0.01
m = len(PROF_BINS)
K = len(PROF_COUNTS)
PROF_ALPHA = PROF_DELTA_STAT / (m * K)

# Compute per-(k,bin) intervals.  _prof_intervals are exact Fraction
# endpoints parsed from outward-rounded public decimal strings; this prevents
# the previous rounded-nearest CP rows from understating eta.
_prof_interval_decimals = {
    k: [clopper_pearson_interval_outward_decimal(PROF_COUNTS[k][i], _PROF_N, PROF_ALPHA) for i in range(m)]
    for k in PROF_COUNTS.keys()
}
_prof_intervals = {
    k: [(dec_fraction(lo), dec_fraction(hi)) for (lo, hi) in rows]
    for k, rows in _prof_interval_decimals.items()
}

# Rare-support set B: bins where at least one class has zero lower support.
_prof_rare_idx = [i for i in range(m) if min(_prof_intervals[k][i][0] for k in PROF_COUNTS.keys()) == 0.0]

# Deterministic summaries (see Anonymity~B).
def _eta_bits():
    eta = 0.0
    for k in PROF_COUNTS.keys():
        for kp in PROF_COUNTS.keys():
            if k == kp:
                continue
            worst = Fraction(0)
            for i in range(m):
                if i in _prof_rare_idx:
                    continue
                lo = _prof_intervals[kp][i][0]
                hi = _prof_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(float(worst), 2))
    return float(eta)

def _delta_slack_fraction():
    # Worst-case upper bound on numerator mass that lands in the rare-support set.
    return max(sum(_prof_intervals[k][i][1] for i in _prof_rare_idx) for k in PROF_COUNTS.keys())

def _delta_slack():
    return float(_delta_slack_fraction())

PROF_ETA_BITS = _eta_bits()
PROF_DELTA_SLACK = _delta_slack()
PROF_DELTA_PLUS_DECIMAL = decimal_ceil_fraction_string(_delta_slack_fraction(), 6)
assert dec_fraction(PROFILING_DELTA_UPPER) >= dec_fraction(PROF_DELTA_PLUS_DECIMAL)

profiling_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": ENF_IDS[PROFILING_LABEL],
    "tw_id": TW_ID,
    "projection": "retry_bucket_trace",
    "binning": {"bucket_width": "250ms", "max_span": "5s", "alphabet": "finite"},
    "classes": {k: {"n": _PROF_N} for k in PROF_COUNTS.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared projection",
        "delta_stat": PROF_DELTA_STAT,
        "alpha_per_bin": PROF_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "sampling_plan": profiling_fixed_sample_plan(),
    "count_table_digest": PROFILING_COUNT_TABLE_DIGEST,
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound_exact_rational_decimal_envelope",
        "eta_bits": float(PROFILING_ETA_BITS_UPPER),
        "eta_plus_decimal": PROFILING_ETA_BITS_UPPER,
        "delta_slack": float(PROFILING_DELTA_UPPER),
        "delta_plus_decimal": PROF_DELTA_PLUS_DECIMAL,
        "rare_bins": [PROF_BINS[i] for i in _prof_rare_idx],
        "note": "Synthetic toy counts; outward-rounded CP intervals and the eta/delta summary are now checked by an exact-rational binomial-tail/union-bound certificate under the fixed-sample stop/refresh lock; no deployment inference or repeated-monitoring validity is made."
    },
    "table": [
        {
            "bin": PROF_BINS[i],
            "count": {k: int(PROF_COUNTS[k][i]) for k in PROF_COUNTS.keys()},
            "p_hat": {k: round(PROF_COUNTS[k][i] / _PROF_N, 6) for k in PROF_COUNTS.keys()},
            "cp_interval": {k: [float(_prof_interval_decimals[k][i][0]), float(_prof_interval_decimals[k][i][1])] for k in PROF_COUNTS.keys()},
            "cp_interval_decimal": {k: list(_prof_interval_decimals[k][i]) for k in PROF_COUNTS.keys()},
        }
        for i in range(m)
    ],
}
profiling_evidence_id = sha256_id(profiling_evidence_core)
profiling_evidence_obj = {"evidence_id": profiling_evidence_id, "evidence": profiling_evidence_core}
profiling_evidence_digest = write_json(ART / "example_profiling_evidence.json", profiling_evidence_obj)


# Optional second profiling evidence object: prefix-fetch signature (variant receipt).
PFX_BINS = ["pf:00", "pf:01", "pf:10", "pf:11", "other"]
PFX_COUNTS = {
    "k0": [1000, 1000, 1000, 995, 5],
    "k1": [1005, 995, 1000, 1000, 0],
    "k2": [990, 1010, 1000, 998, 2],
}
PFX_N = {k: sum(v) for k, v in PFX_COUNTS.items()}
assert len(set(PFX_N.values())) == 1
_PFX_N = next(iter(PFX_N.values()))
PFX_DELTA_STAT = 0.01
m2 = len(PFX_BINS)
K2 = len(PFX_COUNTS)
PFX_ALPHA = PFX_DELTA_STAT / (m2 * K2)

_pfx_intervals = {k: [clopper_pearson_interval(PFX_COUNTS[k][i], _PFX_N, PFX_ALPHA) for i in range(m2)]
                  for k in PFX_COUNTS.keys()}
_pfx_rare_idx = [i for i in range(m2) if min(_pfx_intervals[k][i][0] for k in PFX_COUNTS.keys()) == 0.0]

def _pfx_eta_bits():
    eta = 0.0
    for k in PFX_COUNTS.keys():
        for kp in PFX_COUNTS.keys():
            if k == kp:
                continue
            worst = 0.0
            for i in range(m2):
                if i in _pfx_rare_idx:
                    continue
                lo = _pfx_intervals[kp][i][0]
                hi = _pfx_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(worst, 2))
    return float(eta)

def _pfx_delta_slack():
    return float(max(sum(_pfx_intervals[k][i][1] for i in _pfx_rare_idx) for k in PFX_COUNTS.keys()))

PFX_ETA_BITS = _pfx_eta_bits()
PFX_DELTA_SLACK = _pfx_delta_slack()

profiling_prefix_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": PREFIXFETCH_EXPOSURE,
    "tw_id": TW_ID,
    "projection": "prefix_fetch_signature",
    "binning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "alphabet": "finite"},
    "classes": {k: {"n": _PFX_N} for k in PFX_COUNTS.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared projection",
        "delta_stat": PFX_DELTA_STAT,
        "alpha_per_bin": PFX_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound",
        "eta_bits": round(PFX_ETA_BITS, 6),
        "delta_slack": round(PFX_DELTA_SLACK, 6),
        "rare_bins": [PFX_BINS[i] for i in _pfx_rare_idx],
        "note": "Synthetic toy counts; the purpose is to exercise a second evidence_id wiring path (prefix-fetch) in the worked example, not to claim a real deployment bound."
    },
    "table": [
        {
            "bin": PFX_BINS[i],
            "count": {k: int(PFX_COUNTS[k][i]) for k in PFX_COUNTS.keys()},
            "p_hat": {k: round(PFX_COUNTS[k][i] / _PFX_N, 6) for k in PFX_COUNTS.keys()},
            "cp_interval": {k: [round(_pfx_intervals[k][i][0], 6), round(_pfx_intervals[k][i][1], 6)] for k in PFX_COUNTS.keys()},
        }
        for i in range(m2)
    ],
}
profiling_prefix_evidence_id = sha256_id(profiling_prefix_evidence_core)
profiling_prefix_evidence_obj = {"evidence_id": profiling_prefix_evidence_id, "evidence": profiling_prefix_evidence_core}
profiling_prefix_evidence_digest = write_json(ART / "example_profiling_evidence_prefixfetch.json", profiling_prefix_evidence_obj)



# Optional third profiling evidence object: prefix-fetch signature conditioned on a published state witness (second variant receipt).
PFXSC_WITNESS = ["fresh", "stale"]
PFXSC_BASE_BINS = ["pf:00", "pf:01", "pf:10", "pf:11", "other"]
PFXSC_BINS = [f"w:{w}/{b}" for w in PFXSC_WITNESS for b in PFXSC_BASE_BINS]

# Split the toy prefix-fetch counts into two witness classes.
PFXSC_COUNTS = {
    "k0": {"fresh": [500, 500, 500, 498, 2], "stale": [500, 500, 500, 497, 3]},
    "k1": {"fresh": [503, 497, 500, 500, 0], "stale": [502, 498, 500, 500, 0]},
    "k2": {"fresh": [495, 505, 500, 499, 1], "stale": [495, 505, 500, 499, 1]},
}

_pfxsc_flat = {k: [PFXSC_COUNTS[k][w][i] for w in PFXSC_WITNESS for i in range(len(PFXSC_BASE_BINS))] for k in PFXSC_COUNTS.keys()}
PFXSC_N = {k: sum(v) for k, v in _pfxsc_flat.items()}
assert len(set(PFXSC_N.values())) == 1
_PFXSC_N = next(iter(PFXSC_N.values()))

PFXSC_DELTA_STAT = 0.01
m3 = len(PFXSC_BINS)
K3 = len(_pfxsc_flat)
PFXSC_ALPHA = PFXSC_DELTA_STAT / (m3 * K3)

_pfxsc_intervals = {k: [clopper_pearson_interval(_pfxsc_flat[k][i], _PFXSC_N, PFXSC_ALPHA) for i in range(m3)]
                  for k in _pfxsc_flat.keys()}
_pfxsc_rare_idx = [i for i in range(m3) if min(_pfxsc_intervals[k][i][0] for k in _pfxsc_flat.keys()) == 0.0]


def _pfxsc_eta_bits():
    eta = 0.0
    for k in _pfxsc_flat.keys():
        for kp in _pfxsc_flat.keys():
            if k == kp:
                continue
            worst = 0.0
            for i in range(m3):
                if i in _pfxsc_rare_idx:
                    continue
                lo = _pfxsc_intervals[kp][i][0]
                hi = _pfxsc_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(worst, 2))
    return float(eta)


def _pfxsc_delta_slack():
    return float(max(sum(_pfxsc_intervals[k][i][1] for i in _pfxsc_rare_idx) for k in _pfxsc_flat.keys()))


PFXSC_ETA_BITS = _pfxsc_eta_bits()
PFXSC_DELTA_SLACK = _pfxsc_delta_slack()

profiling_statecond_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": PREFIXFETCH_STATECOND_EXPOSURE,
    "tw_id": TW_ID,
    "projection": "prefix_fetch_signature",
    "binning": {"prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "state_witness": "bucket_staleness_class", "witness_values": PFXSC_WITNESS, "alphabet": "finite"},
    "classes": {k: {"n": _PFXSC_N} for k in _pfxsc_flat.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared projection, conditioned on the published witness",
        "delta_stat": PFXSC_DELTA_STAT,
        "alpha_per_bin": PFXSC_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound",
        "eta_bits": round(PFXSC_ETA_BITS, 6),
        "delta_slack": round(PFXSC_DELTA_SLACK, 6),
        "rare_bins": [PFXSC_BINS[i] for i in _pfxsc_rare_idx],
        "note": "Synthetic toy counts split across a published witness; exercises conditional-witness plumbing (state-conditioned variant receipt) in the worked example."
    },
    "table": [
        {
            "bin": PFXSC_BINS[i],
            "count": {k: int(_pfxsc_flat[k][i]) for k in _pfxsc_flat.keys()},
            "p_hat": {k: round(_pfxsc_flat[k][i] / _PFXSC_N, 6) for k in _pfxsc_flat.keys()},
            "cp_interval": {k: [round(_pfxsc_intervals[k][i][0], 6), round(_pfxsc_intervals[k][i][1], 6)] for k in _pfxsc_flat.keys()},
        }
        for i in range(m3)
    ],
}
profiling_statecond_evidence_id = sha256_id(profiling_statecond_evidence_core)
profiling_statecond_evidence_obj = {"evidence_id": profiling_statecond_evidence_id, "evidence": profiling_statecond_evidence_core}
profiling_statecond_evidence_digest = write_json(ART / "example_profiling_evidence_prefixfetch_statecond.json", profiling_statecond_evidence_obj)


receipt = {
    "claim_id": CLAIM_ID,
    "tw_id": TW_ID,
    "state_decl_id": state_decl_id,
    "line_items": [
        {
            "name": "primary_path_declaration",
            "exposure_nf_id": PRIMARY_EXPOSURE,
            "witness_tier": "split_identity_destination_surface",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "assumption_qualified_MaxL_bits_per_lookup",
            "budget_value": PRIMARY_LINKABILITY_BOUND,
            "budget_value_qualifier": "valid only on the identity-to-destination linkability surface under separation class sep.nr1",
            "obs_model": {
                "separation_class": "sep.nr1",
                "relay_sees": ["client_identity", "timing", "sizes"],
                "router_sees": ["query_destination", "timing", "sizes"],
                "collusion_assumption": "no_declared_relay_router_collusion_within_TW",
                "rho_upper": RHO_UPPER,
                "rho_status": "policy_upper_bound",
                "status": "policy_declaration",
            },
            "knobs": {
                "relay_set_id": "relay-set-A",
                "relay_rotation": "24h",
                "router_key_id": "router-key-2026-02",
                "primary_surface_digest": primary_surface_digest,
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-primary-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-primary-v1"], "artifact_bundle": "bundle://worked-example/primary"},
        },
        {
            "name": "fallback_contact_surface",
            "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
            "witness_tier": "Tier2_contact_failure_trace",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "MaxL_bits_per_lookup",
            "budget_value": fallback_cset_bits,
            "contact_surface_id": FALLBACK_CONTACT_SURFACE_ID,
            "contact_surface": FALLBACK_CONTACT_SURFACE,
            "obs_model": {
                "p_obs_upper": P_OBS_UPPER,
                "status": {"p_obs_upper": "policy_upper_bound"},
            },
            "knobs": {
                "raw_b": RAW_TIERS[0]["raw_b"],
                "raw_b_status": "illustrative_input",
                "dummy_width_w": 4,
                "effective_bucket_K": 256,
                "retry_policy": "schedule_only",
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-fallback-cct-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-fallback-cct-v1"], "artifact_bundle": "bundle://worked-example/fallback-cct"},
        },
        {
            "name": "fallback_tiered_vector",
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "witness_tier": "tiered_vector",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "tiered_MaxL_summary",
            "budget_value": fallback_summary_bits,
            "obs_model": {"vector": vector},
            "knobs": {
                "observation_activation_probability_upper": P_OBS_UPPER,
                "composition_contract": "sum_under_declared_conditional_independence_assumption",
                "composition_evidence_status": "assumption_only_no_joint_channel_witness",
                "semantic_scope": "illustrative_tiered_observation_attenuation_not_mceq",
                "publication_eligible": False,
                "schedule_form": "deadline_normal_form",
                "state_decl_id": state_decl_id,
                "tier_count": len(vector),
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-fallback-vector-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-fallback-vector-v1"], "artifact_bundle": "bundle://worked-example/fallback-vector"},
        },
        {
            "name": "path_selection_indicator",
            "exposure_nf_id": PATHSELECT_EXPOSURE,
            "witness_tier": "fallback_indicator",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "selection_tax_bits",
            "budget_value": selection_tax_bits,
            "obs_model": {
                "fallback_rate_hat": FALLBACK_RATE_HAT,
                "fallback_rate_status": "empirical_estimate",
                "R_pi_upper": R_PI_UPPER,
                "R_pi_status": "policy_upper_bound",
            },
            "knobs": {
                "trigger_class": ["availability", "public_bucket_staleness", "cid_independent_audit_sampling"],
                "state_decl_id": state_decl_id,
            },
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-pathselect-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-pathselect-v1"], "artifact_bundle": "bundle://worked-example/pathselect"},
        },
        {
            "name": "profiling_equalization",
            "exposure_nf_id": PROFILING_EXPOSURE,
            "witness_tier": "Tier1_retry_bucket_trace",
            "tw_id": TW_ID,
            "usage": f"Q<={Q}/24h",
            "budget_type": "pairwise_equalization_eta_delta_bits",
            "budget_value": {"eta_bits": profiling_evidence_core["certificate_summary"]["eta_bits"], "delta": profiling_evidence_core["certificate_summary"]["delta_slack"]},
            "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; one-vs-mixture conversion is imported from Anonymity~B",
            "obs_model": {
                "audit_assumption": "i.i.d. samples within each class for the declared projection",
                "audit_delta_stat": profiling_evidence_core["audit_params"]["delta_stat"],
                "alpha_per_bin": profiling_evidence_core["audit_params"]["alpha_per_bin"],
                "rare_bins": profiling_evidence_core["certificate_summary"]["rare_bins"],
                "rare_bin_mass_upper": profiling_evidence_core["certificate_summary"]["delta_slack"],
            },
            "knobs": {
                "projection": "retry_bucket_trace",
                "bucket_width": "250ms",
            },
            "evidence_id": profiling_evidence_id,
            "lineage": {"relation": "new-interface", "prev": None},
            "replay_hook": {"plan_id": "eval-profiling-eq-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-eq-v1"], "artifact_bundle": "bundle://worked-example/profiling-eq"},
        }
    ],
}
receipt_digest = write_json(ART / "example_receipt.json", receipt)

line_item_owner_map = {
    "owner_map_id": "worked-example-line-item-owner-map-v1",
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "note": "Digest-bound, non-schema adjunct naming which archive note owns each worked-example line item and which published wiki-note import point (if any) is the intended mathematical root.",
    "entries": [
        {
            "name": "primary_path_declaration",
            "exposure_nf_id": PRIMARY_EXPOSURE,
            "materialization_status": "base_receipt_current_cut",
            "receipt_file": "example_receipt.json",
            "replay_plan_id": "eval-primary-v1",
            "support_bundle_id": "bundle://worked-example/primary",
            "public_objects": [
                "example_receipt.json",
                "example_release_receipt.json",
                "example_primary_surface_manifest.json",
                "example_state_decl.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~22", "path": "series/synthesis/paper22_primary_separation_manifests", "role": "guard object / separation-class declaration"},
                {"id": "Synthesis~23", "path": "series/synthesis/paper23_probabilistic_separation_budgets", "role": "guarded (0,rho) adjunct"},
                {"id": "Synthesis~30", "path": "series/synthesis/paper30_deployed_surfaces_control_plane", "role": "deployed control-plane surfaces that must be pinned"},
                {"id": "Anonymity~D", "path": "series/anonymity_series/paperD_spectral_delegation_certificates", "role": "receipt-grade delegation budget when the primary path is backed by a delegation witness"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:spectral", "link": "[[2026.01.23 - Mathematics: Spectral Anonymity and Optimal Distinguishing Bounds for Random-Walk Delegation in (Possibly Directed) Overlays]]", "role": "direct mathematical root when the primary path is delegation-certified"}
            ],
        },
        {
            "name": "fallback_contact_surface",
            "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
            "materialization_status": "base_receipt_current_cut",
            "receipt_file": "example_receipt.json",
            "contact_surface_id": FALLBACK_CONTACT_SURFACE_ID,
            "replay_plan_id": "eval-fallback-cct-v1",
            "support_bundle_id": "bundle://worked-example/fallback-cct",
            "public_objects": [
                "example_receipt.json",
                "example_state_decl.json",
                "example_effective_surface_resolution.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~3", "path": "series/synthesis/paper3_trace_interfaces_dht", "role": "committee-contact ENF semantics"},
                {"id": "Synthesis~11", "path": "series/synthesis/paper11_observation_attenuation", "role": "attenuation by activation probability"},
                {"id": "Synthesis~14", "path": "series/synthesis/paper14_fallback_selection_tax", "role": "fallback activation and selection-tax semantics"},
                {"id": "Synthesis~30", "path": "series/synthesis/paper30_deployed_surfaces_control_plane", "role": "semantic contact-surface and request-shaping semantics"},
            ],
            "backbone_wikilinks": [],
        },
        {
            "name": "fallback_tiered_vector",
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "materialization_status": "base_receipt_current_cut",
            "receipt_file": "example_receipt.json",
            "replay_plan_id": "eval-fallback-vector-v1",
            "support_bundle_id": "bundle://worked-example/fallback-vector",
            "public_objects": [
                "example_receipt.json",
                "example_state_decl.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~15", "path": "series/synthesis/paper15_tiered_observation_vectors", "role": "tier-vector packing and conservative composition surface"},
                {"id": "Synthesis~11", "path": "series/synthesis/paper11_observation_attenuation", "role": "attenuation of the raw tier budgets"},
                {"id": "Synthesis~5", "path": "series/synthesis/paper5_endpoint_metrics_bridge", "role": "bridge from per-lookup summary to endpoint-consumable units"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:scheduling", "link": "[[2026.01.22 - Mathematics: Scheduling and Compiler Techniques for Metadata-Hiding Overlay Lookups]]", "role": "root import when the timing component is derived from schedule/termination-time hiding"},
                {"bibkey": "wiki:stopadd", "link": "[[2026.01.26 - Mathematics: Stop-Time Padding Addendum, Max-Mixture Separations and Tail-Sign Deadline Normal Forms]]", "role": "normal-form import for deadline-shaped timing witnesses"}
            ],
        },
        {
            "name": "path_selection_indicator",
            "exposure_nf_id": PATHSELECT_EXPOSURE,
            "materialization_status": "base_receipt_current_cut",
            "receipt_file": "example_receipt.json",
            "replay_plan_id": "eval-pathselect-v1",
            "support_bundle_id": "bundle://worked-example/pathselect",
            "public_objects": [
                "example_receipt.json",
                "example_state_decl.json",
                "example_change_control.json",
                "example_compare_profile.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~14", "path": "series/synthesis/paper14_fallback_selection_tax", "role": "fallback-indicator witness semantics and activation cap"},
                {"id": "Synthesis~19", "path": "series/synthesis/paper19_receipt_accounting_rulebook", "role": "how the selection term composes in release summaries"},
            ],
            "backbone_wikilinks": [],
        },
        {
            "name": "profiling_equalization",
            "exposure_nf_id": PROFILING_EXPOSURE,
            "materialization_status": "base_receipt_current_cut",
            "receipt_file": "example_receipt.json",
            "evidence_id": profiling_evidence_id,
            "replay_plan_id": "eval-profiling-eq-v1",
            "support_bundle_id": "bundle://worked-example/profiling-eq",
            "public_objects": [
                "example_receipt.json",
                "example_profiling_evidence.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Anonymity~B", "path": "series/anonymity_series/paperB_anonymous_dht_profiling", "role": "equalization contract and one-vs-mixture interpretation"},
                {"id": "Synthesis~25", "path": "series/synthesis/paper25_discrete_equalization_audits", "role": "finite-sample menu-level audit certificate"},
                {"id": "Synthesis~26", "path": "series/synthesis/paper26_anytime_menu_spending", "role": "change-control-safe confidence spending"},
                {"id": "Synthesis~28", "path": "series/synthesis/paper28_coarsening_large_alphabet", "role": "coarsening rule when the projection alphabet is too large"},
                {"id": "Synthesis~29", "path": "series/synthesis/paper29_selection_discipline_datadependent", "role": "selection discipline for data-dependent bucket maps"},
            ],
            "backbone_wikilinks": [],
        },
    ],
    "variant_entries": [
        {
            "name": "profiling_equalization_prefixfetch",
            "exposure_nf_id": PREFIXFETCH_EXPOSURE,
            "materialization_status": "optional_variant_receipt_current_cut",
            "receipt_variant_file": "example_receipt_prefixfetch_variant.json",
            "evidence_id": profiling_prefix_evidence_id,
            "replay_plan_id": "eval-profiling-prefixfetch-v1",
            "support_bundle_id": "bundle://worked-example/profiling-prefixfetch",
            "public_objects": [
                "example_receipt_prefixfetch_variant.json",
                "example_profiling_evidence_prefixfetch.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Anonymity~B", "path": "series/anonymity_series/paperB_anonymous_dht_profiling", "role": "equalization contract for a prefix-fetch projection"},
                {"id": "Synthesis~25", "path": "series/synthesis/paper25_discrete_equalization_audits", "role": "log-audit certificate shape"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:prefixcap", "link": "[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]", "role": "mathematical root when the prefix-fetch variant is justified by shared-kernel prefix/privacy arguments"}
            ],
        },
        {
            "name": "profiling_equalization_prefixfetch_statecond",
            "exposure_nf_id": PREFIXFETCH_STATECOND_EXPOSURE,
            "materialization_status": "optional_variant_receipt_current_cut",
            "receipt_variant_file": "example_receipt_prefixfetch_statecond_variant.json",
            "evidence_id": profiling_statecond_evidence_id,
            "replay_plan_id": "eval-profiling-prefixfetch-statecond-v1",
            "support_bundle_id": "bundle://worked-example/profiling-prefixfetch-statecond",
            "public_objects": [
                "example_receipt_prefixfetch_statecond_variant.json",
                "example_profiling_evidence_prefixfetch_statecond.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Anonymity~B", "path": "series/anonymity_series/paperB_anonymous_dht_profiling", "role": "equalization contract"},
                {"id": "Synthesis~18", "path": "series/synthesis/paper18_plan_and_state_equivalence", "role": "state-conditioned witness discipline"},
                {"id": "Synthesis~25", "path": "series/synthesis/paper25_discrete_equalization_audits", "role": "log-audit certificate shape"},
            ],
            "backbone_wikilinks": [
                {"bibkey": "wiki:prefixcap", "link": "[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]", "role": "shared-kernel prefix/privacy root for the state-conditioned prefix-fetch variant"}
            ],
        },
        {
            "name": "profiling_equalization_contact_coarsened",
            "exposure_nf_id": PROFILING_CONTACT_COARSENED_EXPOSURE,
            "materialization_status": "optional_variant_receipt_current_cut",
            "receipt_variant_file": "example_receipt_contact_coarsened_variant.json",
            "evidence_id": CONTACT_COARSENED_EVIDENCE_ID_CURRENT_CUT,
            "coarsening_map_id": CONTACT_COARSENING_MAP_ID_CURRENT_CUT,
            "replay_plan_id": "eval-profiling-contact-coarsened-v1",
            "support_bundle_id": "bundle://worked-example/profiling-contact-coarsened",
            "public_objects": [
                "example_receipt_contact_coarsened_variant.json",
                "example_profiling_evidence_contact_coarsened.json",
                "example_coarsening_map_contact.json",
                "example_replay_plans.json",
                "example_support_bundle_map.json",
            ],
            "owner_notes": [
                {"id": "Synthesis~28", "path": "series/synthesis/paper28_coarsening_large_alphabet", "role": "coarsening map and data-processing-safe audit surface"},
                {"id": "Synthesis~29", "path": "series/synthesis/paper29_selection_discipline_datadependent", "role": "selection discipline if the map family is data-tuned"},
            ],
            "backbone_wikilinks": [],
        },
    ],
}

line_item_owner_map_extra_entries = [
    {
        "name": "retry_schedule_packet",
        "claim_id": CLAIM_ID,
        "exposure_nf_id": PRIMARY_EXPOSURE,
        "tw_id": TW_ID,
        "replay_plan_id": "eval-retry-schedule-v1",
        "public_objects": [
            "example_receipt.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
        ],
        "owner_notes": [
            {"id": "Anonymity~B", "path": "series/anonymity_series/paperB_anonymous_dht_profiling", "role": "imported retry-projection / equalization claim beneath the owner-map / series-spine retry route"},
            {"id": "Operational~A", "path": "series/operational_series/paperA_schedule_only_retries_anondht", "role": "public wrapper-theorem stop; current worked cut names only an owner-map / series-spine retry route"},
            {"id": "Operational~B", "path": "series/operational_series/paperB_auditable_trace_privacy", "role": "deployment conformance packet beneath the same retry card"},
            {"id": "Boss Fight~A", "path": "series/bossfight_series/paperA_bossfight_budgets", "role": "repeated-use horizon accountant once the live issue leaves one retry card"},
            {"id": "Eval~2", "path": "series/evaluation_series/paper2_advantage_contracts_stealth_audits", "role": "audit/live detectability companion once canary or audit bias becomes live"},
            {"id": "Release~A", "path": "series/release_and_destination/paperA_release_property_ledger_receipts", "role": "lineage-tagged publication receipts above the owner-map / series-spine retry route"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "runtime_conformance_packet",
        "claim_id": CLAIM_ID,
        "line_item": "fallback_contact_surface",
        "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
        "tw_id": FALLBACK_CONTACT_SURFACE_ID,
        "replay_plan_id": "eval-runtime-conformance-v1",
        "public_objects": [
            "example_uvi.json",
            "example_receipt.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
        ],
        "owner_notes": [
            {"id": "Operational~A", "path": "series/operational_series/paperA_schedule_only_retries_anondht", "role": "declared retry theorem and public schedule card beneath the owner-map / series-spine runtime-conformance route"},
            {"id": "Operational~B", "path": "series/operational_series/paperB_auditable_trace_privacy", "role": "PTL/epoch-receipt stop; current worked cut names only an owner-map / series-spine runtime-conformance route"},
            {"id": "Boss Fight~A", "path": "series/bossfight_series/paperA_bossfight_budgets", "role": "repeated-use horizon accountant once the live issue leaves one epoch conformance packet"},
            {"id": "Eval~2", "path": "series/evaluation_series/paper2_advantage_contracts_stealth_audits", "role": "audit/live detectability companion once canary or audit bias becomes live"},
            {"id": "Release~A", "path": "series/release_and_destination/paperA_release_property_ledger_receipts", "role": "lineage-tagged publication receipts above the owner-map / series-spine runtime-conformance route"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "notary_replay_packet",
        "claim_id": CLAIM_ID,
        "exposure_nf_id": PRIMARY_EXPOSURE,
        "tw_id": TW_ID,
        "materialization_status": "verifier_report_current_cut",
        "verifier_report_file": "example_verifier_report.json",
        "replay_plan_id": "eval-fallback-cct-v1",
        "support_bundle_id": "bundle://worked-example/fallback-cct",
        "public_objects": [
            "example_receipt.json",
            "example_state_decl.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
            "example_verifier_report.json",
            "example_uvi.json",
            "example_release_closure_ledger.json",
        ],
        "owner_notes": [
            {"id": "Operational~A", "path": "series/operational_series/paperA_schedule_only_retries_anondht", "role": "declared retry wrapper and schedule-only public card beneath the notary packet"},
            {"id": "Operational~B", "path": "series/operational_series/paperB_auditable_trace_privacy", "role": "deployment conformance packet beneath the retry-safe replay verdict"},
            {"id": "Eval~1", "path": "series/evaluation_series/paper1_notarized_anonymity_certificates", "role": "retry-safe notary packet and exact worked-bundle carrier stop"},
            {"id": "Eval~1A", "path": "series/evaluation_series/paper1A_notarized_certificates_addendum", "role": "optional checkpoint / witness-policy hardening packet for the same replay hook"},
            {"id": "Eval~2", "path": "series/evaluation_series/paper2_advantage_contracts_stealth_audits", "role": "audit/live transfer sentence once detectability bias becomes live"},
            {"id": "Eval~3", "path": "series/evaluation_series/paper3_calibration_recipes_anondht", "role": "cadence-facing horizon / alert-tax conversions after the notary packet is fixed"},
            {"id": "Release~A", "path": "series/release_and_destination/paperA_release_property_ledger_receipts", "role": "fresh replay verdict closure role and lineage-tagged publication receipts above the notary packet"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "calibration_recipe_packet",
        "exposure_nf_id": FALLBACK_CCT_EXPOSURE,
        "tw_id": FALLBACK_CONTACT_SURFACE_ID,
        "replay_plan_id": "eval-calibration-recipe-v1",
        "public_objects": [
            "example_verifier_report.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
        ],
        "owner_notes": [
            {"id": "State~1", "path": "series/anondht_state_series/paper1_state_dependent_anonymity", "role": "generic amplification root imported by the witness-gap formula"},
            {"id": "State~2", "path": "series/anondht_state_series/paper2_mucc_committee_contact_privacy", "role": "committee-contact specialization imported by the owner-map / series-spine calibration route"},
            {"id": "State~3", "path": "series/anondht_state_series/paper3_closed_view_auditing_cppc", "role": "closed-view alert-policy neighbor once the alert-target row must be compared to public monitoring semantics"},
            {"id": "MC-EQ", "path": "series/release_and_destination/paperB_mceq_coversketch_destination_privacy", "role": "hold-only theorem neighbor; no current worked packet is an MC-EQ certificate"},
            {"id": "Eval~3", "path": "series/evaluation_series/paper3_calibration_recipes_anondht", "role": "horizon/alert-tax conversion stop; current worked cut names only an owner-map / series-spine calibration route"},
            {"id": "Eval~1", "path": "series/evaluation_series/paper1_notarized_anonymity_certificates", "role": "retry-safe evaluator companion once attempted-evaluation notarization rather than the carried conversion row is live"},
            {"id": "Eval~2", "path": "series/evaluation_series/paper2_advantage_contracts_stealth_audits", "role": "audit/live transfer companion once detectability bias rather than the carried conversion row is live"},
            {"id": "Release~A", "path": "series/release_and_destination/paperA_release_property_ledger_receipts", "role": "lineage-tagged publication receipts above the owner-map / series-spine calibration route"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "congestion_epoch_contract",
        "exposure_nf_id": "sha256:dbfbd8fa9248004a1da68129016a5df03d1f4b7badff2d166663045785867b99",
        "replay_plan_id": "eval-congestion-eq-v1",
        "public_objects": [
            "example_replay_plans.json",
            "example_verifier_report.json",
        ],
        "owner_notes": [
            {"id": "Congestion~1", "path": "series/congestion_series/paper1_congestion_eq", "role": "congestion witness/accountant root and exact stage-to-epoch packet"},
            {"id": "PSC-Q", "path": "series/congestion_series/paper2_psc_q", "role": "declared mechanism packet intended to meet the maintained congestion contract"},
            {"id": "W-Congestion-EQ", "path": "series/congestion_series/paper3_w_congestion_eq", "role": "replayable checker bundle for the same maintained congestion packet"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "pscq_mechanism_packet",
        "exposure_nf_id": "sha256:dbfbd8fa9248004a1da68129016a5df03d1f4b7badff2d166663045785867b99",
        "replay_plan_id": "eval-pscq-v1",
        "public_objects": [
            "example_replay_plans.json",
            "example_support_bundle_map.json",
            "example_verifier_report.json",
        ],
        "owner_notes": [
            {"id": "Congestion~1", "path": "series/congestion_series/paper1_congestion_eq", "role": "theorem/accountant root the mechanism packet is intended to meet"},
            {"id": "PSC-Q", "path": "series/congestion_series/paper2_psc_q", "role": "declared calendar/substitution/observer mechanism packet and exact public stop"},
            {"id": "W-Congestion-EQ", "path": "series/congestion_series/paper3_w_congestion_eq", "role": "replayable checker bundle that consumes the same mechanism packet"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "bossfight_dialsheet_packet",
        "claim_id": CLAIM_ID,
        "tw_id": TW_ID,
        "replay_plan_id": "eval-bossfight-dialsheet-v1",
        "public_objects": [
            "example_receipt.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
        ],
        "owner_notes": [
            {"id": "BossFight~A", "path": "series/bossfight_series/paperA_bossfight_budgets", "role": "repeated-use horizon/accountant root upstream of the owner-map / series-spine dial-sheet route"},
            {"id": "BossFight~B", "path": "series/bossfight_series/paperB_anondht_dial_sheet", "role": "declared anonymous-DHT knob surface; current worked cut names only an owner-map / series-spine dial-sheet route"},
            {"id": "BossFight~B-A", "path": "series/bossfight_series/paperB_addendum_evidence_tables", "role": "optional representative-scale evidence tables if a future materialized support packet becomes live"},
            {"id": "BossFight~C", "path": "series/bossfight_series/paperC_proof_carrying_budgets", "role": "replayable verifier object that consumes the same line-item set after the dial-sheet packet is fixed"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "bossfight_verifier_bundle",
        "claim_id": CLAIM_ID,
        "tw_id": TW_ID,
        "replay_plan_id": "eval-bossfight-verifier-v1",
        "public_objects": [
            "example_receipt.json",
            "example_verifier_report.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
            "example_release_closure_ledger.json",
        ],
        "owner_notes": [
            {"id": "BossFight~A", "path": "series/bossfight_series/paperA_bossfight_budgets", "role": "repeated-use horizon/accountant root upstream of the owner-map / series-spine verifier route"},
            {"id": "BossFight~B", "path": "series/bossfight_series/paperB_anondht_dial_sheet", "role": "declared anonymous-DHT knob surface and plan family upstream of the owner-map / series-spine verifier route"},
            {"id": "BossFight~C", "path": "series/bossfight_series/paperC_proof_carrying_budgets", "role": "replayable verifier object; current worked cut names only an owner-map / series-spine verifier route"},
            {"id": "Eval~1", "path": "series/evaluation_series/paper1_notarized_anonymity_certificates", "role": "notarized attempted-evaluation discipline once the verifier object is fixed"},
            {"id": "Release~A", "path": "series/release_and_destination/paperA_release_property_ledger_receipts", "role": "fresh_replay_verdict closure role and lineage-tagged publication receipts above the verifier object"},
        ],
        "backbone_wikilinks": [],
    },
    {
        "name": "routing_signature_manifest",
        "contact_surface_id": FALLBACK_CONTACT_SURFACE_ID,
        "exposure_nf_id": PRIMARY_EXPOSURE,
        "replay_plan_id": "eval-routing-signature-v1",
        "public_objects": [
            "example_effective_surface_resolution.json",
            "example_replay_plans.json",
        ],
        "owner_notes": [
            {"id": "Certified~A", "path": "series/certified_series/paperA_certified_menus_anonymous_dht", "role": "baseline certified-menu theorem and raw multiplicity accounting"},
            {"id": "Certified~B", "path": "series/certified_series/paperB_routing_signature_compression", "role": "routing-signature quotient map and effective multiplicity witness"},
            {"id": "Certified~C", "path": "series/certified_series/paperC_disagreement_gated_recertification", "role": "remanifest / drift / recertify boundary once the compression card changes"},
            {"id": "Synthesis~3", "path": "series/synthesis/paper3_trace_interfaces_dht", "role": "committee-contact ENF semantics for the declared projection"},
            {"id": "Synthesis~30", "path": "series/synthesis/paper30_deployed_surfaces_control_plane", "role": "contact-surface and context-support semantics for replay"},
        ],
        "backbone_wikilinks": [],
    },
]

OWNER_MAP_SPINE_ONLY_CURRENT_CUT = {
    "retry_schedule_packet",
    "runtime_conformance_packet",
    "calibration_recipe_packet",
    "congestion_epoch_contract",
    "pscq_mechanism_packet",
    "bossfight_dialsheet_packet",
    "bossfight_verifier_bundle",
    "routing_signature_manifest",
}
OWNER_MAP_SPINE_ONLY_NOT_MATERIALIZED_IN = {
    name: [
        "example_receipt.json",
        "example_uvi.json",
        "example_verifier_report.json",
        "example_replay_plans.json",
        "example_support_bundle_map.json",
    ]
    for name in OWNER_MAP_SPINE_ONLY_CURRENT_CUT
}
OWNER_MAP_SPINE_ONLY_NOT_MATERIALIZED_IN["routing_signature_manifest"] = [
    "example_receipt.json",
    "example_uvi.json",
    "example_effective_surface_resolution.json",
    "example_verifier_report.json",
    "example_replay_plans.json",
    "example_support_bundle_map.json",
]

for entry in line_item_owner_map_extra_entries:
    if entry.get("name") in OWNER_MAP_SPINE_ONLY_CURRENT_CUT:
        entry["current_cut_role"] = "owner_map_series_spine_boundary"
        entry["materialization_status"] = "owner_map_spine_only_current_cut"
        entry["materialized_in_current_cut"] = [
            "example_line_item_owner_map.json",
            "example_series_spine.json",
        ]
        entry["not_materialized_as_packet_in"] = OWNER_MAP_SPINE_ONLY_NOT_MATERIALIZED_IN[entry["name"]]
        entry["replay_plan_id_status"] = "route_target_only_not_plan_catalog_row_current_cut"
        entry["public_objects_status"] = "route_context_only_not_packet_materialization_evidence"
        entry["boundary_note"] = (
            "This owner-map row names the intended review/replay route only. In the current cut, "
            "public_objects and replay_plan_id are route-context labels, not evidence that a receipt, "
            "UVI, verifier, replay-plan, or support-bundle packet has been emitted."
        )

line_item_owner_map_entries_by_name = {entry["name"]: entry for entry in line_item_owner_map["entries"]}
for entry in line_item_owner_map_extra_entries:
    line_item_owner_map_entries_by_name[entry["name"]] = entry
line_item_owner_map["entries"] = [
    line_item_owner_map_entries_by_name[name]
    for name in [
        "primary_path_declaration",
        "fallback_contact_surface",
        "retry_schedule_packet",
        "runtime_conformance_packet",
        "notary_replay_packet",
        "calibration_recipe_packet",
        "fallback_tiered_vector",
        "congestion_epoch_contract",
        "pscq_mechanism_packet",
        "path_selection_indicator",
        "bossfight_dialsheet_packet",
        "bossfight_verifier_bundle",
        "routing_signature_manifest",
        "profiling_equalization",
    ]
]
line_item_owner_map_digest = write_json(ART / "example_line_item_owner_map.json", line_item_owner_map)

# Variant receipt that appends a second profiling line item for prefix-fetch signatures.
variant_receipt = copy.deepcopy(receipt)
variant_receipt["variant_of"] = "example_receipt.json"
variant_receipt["variant_note"] = "Optional extension exercising prefix-fetch profiling equalization plumbing; does not alter any schemas."
variant_receipt["line_items"] = list(variant_receipt["line_items"]) + [
    {
        "name": "profiling_equalization_prefixfetch",
        "exposure_nf_id": PREFIXFETCH_EXPOSURE,
        "witness_tier": "Tier1_prefix_fetch_signature",
        "tw_id": TW_ID,
        "usage": f"Q<={Q}/24h",
        "budget_type": "pairwise_equalization_eta_delta_bits",
        "budget_value": {"eta_bits": round(PFX_ETA_BITS, 6), "delta": round(PFX_DELTA_SLACK, 6)},
        "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; one-vs-mixture conversion is imported from Anonymity~B",
        "evidence_id": profiling_prefix_evidence_id,
        "obs_model": {
            "audit_assumption": "i.i.d. samples within each class for the declared projection",
            "audit_delta_stat": PFX_DELTA_STAT,
            "alpha_per_bin": PFX_ALPHA,
            "rare_bin_mass_upper": round(PFX_DELTA_SLACK, 6),
            "rare_bins": [PFX_BINS[i] for i in _pfx_rare_idx],
        },
        "knobs": {"projection": "prefix_fetch_signature", "prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix"},
        "lineage": {"relation": "optional_extension", "prev": None},
        "replay_hook": {"plan_id": "eval-profiling-prefixfetch-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-prefixfetch-v1"], "artifact_bundle": "bundle://worked-example/profiling-prefixfetch"},
    }
]
variant_receipt_digest = write_json(ART / "example_receipt_prefixfetch_variant.json", variant_receipt)


# Second variant receipt that appends a state-conditioned prefix-fetch profiling line item (conditional witness).
statecond_receipt = copy.deepcopy(receipt)
statecond_receipt["variant_of"] = "example_receipt.json"
statecond_receipt["variant_note"] = "Optional extension exercising prefix-fetch equalization conditioned on a published state witness; does not alter any schemas."
statecond_receipt["line_items"] = list(statecond_receipt["line_items"]) + [
    {
        "name": "profiling_equalization_prefixfetch_statecond",
        "exposure_nf_id": PREFIXFETCH_STATECOND_EXPOSURE,
        "witness_tier": "Tier1_prefix_fetch_signature_conditional",
        "tw_id": TW_ID,
        "usage": f"Q<={Q}/24h",
        "budget_type": "pairwise_equalization_eta_delta_bits",
        "budget_value": {"eta_bits": round(PFXSC_ETA_BITS, 6), "delta": round(PFXSC_DELTA_SLACK, 6)},
        "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; conditional-witness lifting is imported from Synthesis~18 and Anonymity~B",
        "evidence_id": profiling_statecond_evidence_id,
        "obs_model": {
            "audit_assumption": "i.i.d. samples within each class for the declared projection, conditioned on the published witness",
            "audit_delta_stat": PFXSC_DELTA_STAT,
            "alpha_per_bin": PFXSC_ALPHA,
            "rare_bin_mass_upper": round(PFXSC_DELTA_SLACK, 6),
            "rare_bins": [PFXSC_BINS[i] for i in _pfxsc_rare_idx],
            "state_witness": {"name": "bucket_staleness_class", "values": PFXSC_WITNESS, "declared_public": True},
        },
        "knobs": {"projection": "prefix_fetch_signature", "prefix_bits": 2, "fetch_rule": "all_siblings_under_prefix", "state_witness": "bucket_staleness_class"},
        "lineage": {"relation": "optional_extension", "prev": None},
        "replay_hook": {"plan_id": "eval-profiling-prefixfetch-statecond-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-prefixfetch-statecond-v1"], "artifact_bundle": "bundle://worked-example/profiling-prefixfetch-statecond"},
    }
]


# Third variant receipt: coarsening a large-alphabet contact-set hash to a sample-feasible signature (Synthesis~28).
COARSENING_MAP_CORE = {
    "coarsening_schema": "coarsening_map.v1",
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "source_projection": "contact_set_hash",
    "target_projection": "contact_hash_sig2",
    "rule": "sig2 = first2bits(sha256(serialized_contact_set))",
    "alphabet": ["00", "01", "10", "11"],
    "note": "Toy coarsening used only for the worked example: a huge contact-set hash alphabet is made audit-feasible by declaring a deterministic 2-bit signature partition (Synthesis~28).",
}
COARSENING_MAP_ID = sha256_id(COARSENING_MAP_CORE)
coarsening_map_obj = {"coarsening_map_id": COARSENING_MAP_ID, "coarsening_map": COARSENING_MAP_CORE}
coarsening_map_digest = write_json(ART / "example_coarsening_map_contact.json", coarsening_map_obj)

CONTACT_COARSENED_EXPOSURE = ENF_IDS[PROFILING_CONTACT_COARSENED_LABEL]

CC_BINS = ["00", "01", "10", "11"]
CC_COUNTS = {
    "k0": [630, 590, 600, 580],
    "k1": [610, 610, 590, 590],
    "k2": [620, 600, 600, 580],
}
CC_N = {k: sum(v) for k, v in CC_COUNTS.items()}
assert len(set(CC_N.values())) == 1
_CC_N = next(iter(CC_N.values()))
CC_DELTA_STAT = 0.01
m3 = len(CC_BINS)
K3 = len(CC_COUNTS)
CC_ALPHA = CC_DELTA_STAT / (m3 * K3)

_cc_intervals = {k: [clopper_pearson_interval(CC_COUNTS[k][i], _CC_N, CC_ALPHA) for i in range(m3)]
                 for k in CC_COUNTS.keys()}
_cc_rare_idx = [i for i in range(m3) if min(_cc_intervals[k][i][0] for k in CC_COUNTS.keys()) == 0.0]

def _cc_eta_bits():
    eta = 0.0
    for k in CC_COUNTS.keys():
        for kp in CC_COUNTS.keys():
            if k == kp:
                continue
            worst = 0.0
            for i in range(m3):
                if i in _cc_rare_idx:
                    continue
                lo = _cc_intervals[kp][i][0]
                hi = _cc_intervals[k][i][1]
                worst = max(worst, hi / lo)
            eta = max(eta, math.log(worst, 2))
    return float(eta)

def _cc_delta_slack():
    return float(max(sum(_cc_intervals[k][i][1] for i in _cc_rare_idx) for k in CC_COUNTS.keys()))

CC_ETA_BITS = _cc_eta_bits()
CC_DELTA_SLACK = _cc_delta_slack()

contact_coarsened_evidence_core = {
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "evidence_schema": "profiling_equalization_evidence.v2",
    "exposure_nf_id": CONTACT_COARSENED_EXPOSURE,
    "tw_id": TW_ID,
    "projection": "contact_hash_sig2 (coarsening of contact_set_hash)",
    "coarsening_map_id": COARSENING_MAP_ID,
    "classes": {k: {"n": _CC_N} for k in CC_COUNTS.keys()},
    "audit_params": {
        "assumption": "i.i.d. samples within each class for the declared coarsened projection",
        "delta_stat": CC_DELTA_STAT,
        "alpha_per_bin": CC_ALPHA,
        "interval_method": "clopper_pearson_two_sided",
        "rare_support_rule": "B = {bin : min_k lower_cp(k,bin)=0}"
    },
    "certificate_summary": {
        "method": "finite_sample_cp_union_bound",
        "eta_bits": round(CC_ETA_BITS, 6),
        "delta_slack": round(CC_DELTA_SLACK, 6),
        "rare_bins": [CC_BINS[i] for i in _cc_rare_idx],
        "note": "Synthetic toy counts; demonstrates a digest-bound coarsening map + audit-feasible alphabet, not a real deployment bound.",
    },
    "table": [
        {
            "bin": CC_BINS[i],
            "count": {k: int(CC_COUNTS[k][i]) for k in CC_COUNTS.keys()},
            "p_hat": {k: round(CC_COUNTS[k][i] / _CC_N, 6) for k in CC_COUNTS.keys()},
            "cp_interval": {k: [round(_cc_intervals[k][i][0], 6), round(_cc_intervals[k][i][1], 6)] for k in CC_COUNTS.keys()},
        }
        for i in range(m3)
    ],
}
contact_coarsened_evidence_id = sha256_id(contact_coarsened_evidence_core)
if contact_coarsened_evidence_id != CONTACT_COARSENED_EVIDENCE_ID_CURRENT_CUT:
    raise RuntimeError(f"contact coarsened evidence id drift: {contact_coarsened_evidence_id}")
if COARSENING_MAP_ID != CONTACT_COARSENING_MAP_ID_CURRENT_CUT:
    raise RuntimeError(f"contact coarsening map id drift: {COARSENING_MAP_ID}")
contact_coarsened_evidence_obj = {"evidence_id": contact_coarsened_evidence_id, "evidence": contact_coarsened_evidence_core}
contact_coarsened_evidence_digest = write_json(ART / "example_profiling_evidence_contact_coarsened.json", contact_coarsened_evidence_obj)

contact_coarsened_receipt = copy.deepcopy(receipt)
contact_coarsened_receipt["variant_of"] = "example_receipt.json"
contact_coarsened_receipt["variant_note"] = "Optional extension exercising Synthesis~28: a large-alphabet contact-set hash is made audit-feasible by declaring a digest-bound coarsening map (2-bit signature) and auditing only the coarsened projection."
contact_coarsened_receipt["line_items"] = list(contact_coarsened_receipt["line_items"]) + [
    {
        "name": "profiling_equalization_contact_coarsened",
        "exposure_nf_id": CONTACT_COARSENED_EXPOSURE,
        "witness_tier": "Tier1_contact_hash_sig2",
        "tw_id": TW_ID,
        "usage": f"Q<={Q}/24h",
        "budget_type": "pairwise_equalization_eta_delta_bits",
        "budget_value": {"eta_bits": round(CC_ETA_BITS, 6), "delta": round(CC_DELTA_SLACK, 6)},
        "budget_value_qualifier": "synthetic toy counts; CP+union-bound audit summary; coarsening is declared via coarsening_map_id (Synthesis~28)",
        "evidence_id": contact_coarsened_evidence_id,
        "obs_model": {
            "audit_assumption": "i.i.d. samples within each class for the declared coarsened projection",
            "audit_delta_stat": CC_DELTA_STAT,
            "alpha_per_bin": CC_ALPHA,
            "rare_bin_mass_upper": round(CC_DELTA_SLACK, 6),
            "rare_bins": [CC_BINS[i] for i in _cc_rare_idx],
            "coarsening_map_id": COARSENING_MAP_ID,
        },
        "knobs": {"source_projection": "contact_set_hash", "coarsened_projection": "contact_hash_sig2", "coarsening_map_id": COARSENING_MAP_ID},
        "lineage": {"relation": "optional_extension", "prev": None},
        "replay_hook": {"plan_id": "eval-profiling-contact-coarsened-v1", "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-profiling-contact-coarsened-v1"], "artifact_bundle": "bundle://worked-example/profiling-contact-coarsened"},
    }
]
contact_coarsened_receipt_digest = write_json(ART / "example_receipt_contact_coarsened_variant.json", contact_coarsened_receipt)

statecond_receipt_digest = write_json(ART / "example_receipt_prefixfetch_statecond_variant.json", statecond_receipt)



plan_catalog = {
    "catalog_id": PLAN_CATALOG_VERSION,
    "claim_id": CLAIM_ID,
    "canonicalization": "plan_spec_id = sha256(canon(plan_spec)) where canon uses sorted keys and no whitespace.",
    "plans": PLAN_SPECS,
}
plan_catalog_digest = write_json(ART / "example_replay_plans.json", plan_catalog)

support_bundle_map = {
    "bundle_map_id": "worked-example-support-bundles-v1",
    "claim_id": CLAIM_ID,
    "bundles": [
        {
            "bundle_id": "bundle://worked-example/primary",
            "consumed_by": ["eval-primary-v1"],
            "required_artifacts": [
                "example_receipt.json",
                "example_release_receipt.json",
                "example_primary_surface_manifest.json",
            ],
            "support_pointers": [
                "support://primary/operators.example",
                "support://primary/config.example",
                "support://primary/telemetry.example",
            ],
            "failure_if_missing": "cannot validate sep.nr1 identity-to-destination separation declaration",
        },
        {
            "bundle_id": "bundle://worked-example/fallback-cct",
            "consumed_by": ["eval-fallback-cct-v1"],
            "required_artifacts": ["example_receipt.json", "example_state_decl.json"],
            "support_pointers": ["support://fallback/notarized-attempt-log.example"],
            "failure_if_missing": "cannot replay fallback contact-surface bound against notarized evidence",
        },
        {
            "bundle_id": "bundle://worked-example/fallback-vector",
            "consumed_by": ["eval-fallback-vector-v1"],
            "required_artifacts": [
                "example_receipt.json",
                "example_state_decl.json",
                "example_support_bundle_map.json",
            ],
            "support_pointers": [
                "support://fallback/timing-certificates.example",
                "support://fallback/observation-attenuation-slice.example",
            ],
            "failure_if_missing": "cannot replay the illustrative tiered observation summary or verify timing/observation-attenuation references",
        },
        {
            "bundle_id": "bundle://worked-example/pathselect",
            "consumed_by": ["eval-pathselect-v1"],
            "required_artifacts": [
                "example_receipt.json",
                "example_state_decl.json",
                "example_change_control.json",
            ],
            "support_pointers": ["support://pathselect/audit-live-fallback-indicators.example"],
            "failure_if_missing": "cannot compare audit/live fallback-indicator behavior under the declared trigger class",
        },
        {
            "bundle_id": "bundle://worked-example/profiling-eq",
            "consumed_by": ["eval-profiling-eq-v1"],
            "required_artifacts": ["example_receipt.json", "example_profiling_evidence.json"],
            "support_pointers": ["support://profiling/log-slice.example"],
            "failure_if_missing": "cannot validate profiling/equalization evidence_id against the published receipt"
        },
        {
            "bundle_id": "bundle://worked-example/profiling-prefixfetch",
            "consumed_by": ["eval-profiling-prefixfetch-v1"],
            "required_artifacts": [
                "example_receipt_prefixfetch_variant.json",
                "example_profiling_evidence_prefixfetch.json",
            ],
            "support_pointers": ["support://profiling/prefixfetch-log-slice.example"],
            "failure_if_missing": "cannot validate prefix-fetch profiling evidence_id against the variant receipt",
        },

        {
            "bundle_id": "bundle://worked-example/profiling-prefixfetch-statecond",
            "consumed_by": ["eval-profiling-prefixfetch-statecond-v1"],
            "required_artifacts": [
                "example_receipt_prefixfetch_statecond_variant.json",
                "example_profiling_evidence_prefixfetch_statecond.json"
            ],
            "support_pointers": ["support://profiling/prefixfetch-statecond-log-slice.example"],
            "failure_if_missing": "cannot validate state-conditioned prefix-fetch evidence_id against the variant receipt",
        },

{
    "bundle_id": "bundle://worked-example/profiling-contact-coarsened",
    "consumed_by": ["eval-profiling-contact-coarsened-v1"],
    "required_artifacts": [
        "example_receipt_contact_coarsened_variant.json",
        "example_profiling_evidence_contact_coarsened.json",
        "example_coarsening_map_contact.json"
    ],
    "support_pointers": ["support://profiling/contactset-hash.example"],
    "failure_if_missing": "cannot validate coarsening_map_id or recompute (eta,delta) for coarsened contact-set equalization claim",
},


    ],
    "note": "Operational map from artifact_bundle ids to concrete archive artifacts and off-bundle support pointers; not a new receipt primitive.",
}

# Close the resolver-payload surface for materialized receipt, verifier, and
# variant bundles.  Bundles are not one-to-one with owner-map rows in this cut:
# bundle://worked-example/fallback-cct resolves both fallback_contact_surface
# and the verifier-carried notary_replay_packet.  Therefore the support-bundle
# map must expose multiplicity explicitly instead of using singleton shortcut
# fields that can silently drop a co-resident carrier.
def _support_resolver_payload(owner_row, bundle_row):
    out = {
        "line_item_name": owner_row.get("name"),
        "materialization_status": owner_row.get("materialization_status"),
        "support_bundle_id": owner_row.get("support_bundle_id"),
        "replay_plan_id": owner_row.get("replay_plan_id"),
        "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID.get(owner_row.get("replay_plan_id")),
        "support_consumed_by": bundle_row.get("consumed_by", []),
        "support_required_artifacts": bundle_row.get("required_artifacts", []),
        "support_pointers": bundle_row.get("support_pointers", []),
        "public_objects": owner_row.get("public_objects", []),
    }
    for key in (
        "receipt_file",
        "receipt_variant_file",
        "verifier_report_file",
        "evidence_id",
        "coarsening_map_id",
        "contact_surface_id",
    ):
        if owner_row.get(key) is not None:
            out[key] = owner_row.get(key)
    return out

_support_resolver_owner_rows = [
    row for row in line_item_owner_map["entries"]
    if row.get("materialization_status") in {"base_receipt_current_cut", "verifier_report_current_cut"}
]
_support_resolver_owner_rows.extend(
    row for row in line_item_owner_map.get("variant_entries", [])
    if row.get("materialization_status") == "optional_variant_receipt_current_cut"
)
_support_resolver_owner_rows_by_bundle = {}
for _owner_row in _support_resolver_owner_rows:
    _support_resolver_owner_rows_by_bundle.setdefault(_owner_row.get("support_bundle_id"), []).append(_owner_row)

for _bundle_row in support_bundle_map["bundles"]:
    _owner_rows = _support_resolver_owner_rows_by_bundle.get(_bundle_row.get("bundle_id"), [])
    if not _owner_rows:
        continue
    _bundle_row["resolved_owner_map_row_names"] = [row.get("name") for row in _owner_rows]
    _bundle_row["resolved_owner_map_rows"] = [
        _support_resolver_payload(row, _bundle_row) for row in _owner_rows
    ]
    _bundle_row["resolver_multiplicity_note"] = (
        "This resolver is row-multiplicity-safe: a support bundle can back more than "
        "one current-cut carrier, so resolved_owner_map_rows is authoritative and "
        "singleton line_item_name/materialization fields are intentionally omitted."
    )

support_bundle_map_digest = write_json(ART / "example_support_bundle_map.json", support_bundle_map)

# Mirror replay-plan and support-bundle payloads into materialized owner-map rows.
# The owner map is intentionally non-schema adjunct data, but materialized rows
# should still be self-describing enough that a later reviewer can distinguish
# a real receipt/verifier/variant carrier from a route-context label without
# reverse-engineering the replay catalog and support-bundle map.
_replay_plan_index_for_owner_map = {entry["plan_id"]: entry for entry in plan_catalog["plans"]}
_support_bundle_index_for_owner_map = {entry["bundle_id"]: entry for entry in support_bundle_map["bundles"]}

def _enrich_materialized_owner_row(row):
    plan = _replay_plan_index_for_owner_map.get(row.get("replay_plan_id"))
    if plan is not None:
        row["plan_spec_id"] = plan.get("plan_spec_id")
    bundle = _support_bundle_index_for_owner_map.get(row.get("support_bundle_id"))
    if bundle is not None:
        row["support_consumed_by"] = bundle.get("consumed_by", [])
        row["support_required_artifacts"] = bundle.get("required_artifacts", [])
        row["support_pointers"] = bundle.get("support_pointers", [])
    return row

for _owner_row in line_item_owner_map["entries"]:
    if _owner_row.get("materialization_status") in {"base_receipt_current_cut", "verifier_report_current_cut"}:
        _enrich_materialized_owner_row(_owner_row)
for _variant_owner_row in line_item_owner_map.get("variant_entries", []):
    if _variant_owner_row.get("materialization_status") == "optional_variant_receipt_current_cut":
        _enrich_materialized_owner_row(_variant_owner_row)
line_item_owner_map_digest = write_json(ART / "example_line_item_owner_map.json", line_item_owner_map)

compare_profile = {
    "compare_profile_id": COMPARE_PROFILE_ID,
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "primary_compare_surface": {
        "exposure_nf_id": PRIMARY_EXPOSURE,
        "budget_type": "assumption_qualified_MaxL_bits_per_lookup",
        "budget_value": PRIMARY_LINKABILITY_BOUND,
        "qualifier": "under separation class sep.nr1",
        "manifest_digest": primary_surface_digest,
        "rho_upper": RHO_UPPER,
    },
    "user_compare_surface": {
        "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
        "budget_type": "tiered_MaxL_summary",
        "budget_value": fallback_summary_bits,
        "selection_tax_bits": selection_tax_bits,
        "total_summary_bits_per_lookup": total_summary_bits,
        "tw_id": TW_ID,
        "state_contract_id": state_decl["state_contract_id"],
        "state_decl_id": state_decl["state_decl_id"],
        "receipt_digest": receipt_digest,
    },
    "diff_views": {
        "user_fast_diff": [
            "claim_id",
            "user_compare_surface.exposure_nf_id",
            "user_compare_surface.budget_value",
            "user_compare_surface.selection_tax_bits",
            "user_compare_surface.total_summary_bits_per_lookup",
            "user_compare_surface.receipt_digest",
        ],
        "auditor_fast_diff": [
            "claim_id",
            "tw_id",
            "covered_exposures",
            "primary_compare_surface.manifest_digest",
            "primary_compare_surface.rho_upper",
            "user_compare_surface.state_decl_id",
            "receipt_digest",
            "plan_catalog_digest",
            "change_control_id",
        ],
        "release_guard_fields": [
            "tw_id",
            "covered_exposures",
            "primary_separation_class",
            "state_decl_id",
            "max_total_budget_bits_per_lookup",
        ],
    },
    "source_fields": {
        "abom": [
            "covered_exposures",
            "budget_summary.primary_surface",
            "budget_summary.fallback_summary",
            "budget_summary.selection_tax",
            "budget_summary.total_summary",
        ],
        "receipt": [
            "tw_id",
            "line_items[*].exposure_nf_id",
            "line_items[*].budget_value",
            "line_items[*].lineage.relation",
        ],
        "release_receipt": [
            "policy_gate.change_control_id",
            "policy_gate.max_total_budget_bits_per_lookup",
            "policy_gate.required_exposures",
            "adjunct_digests.state_decl",
            "adjunct_digests.primary_surface_manifest",
        ],
        "uvi": [
            "claim_pointer",
            "exposure_nf_id",
            "receipt_digest",
            "log_anchor.log_id",
            "consistency_context.checkpoint",
        ],
    },
    "note": "Operational diff profile for OINL-style release comparison; not a new receipt or UVI primitive.",
}
compare_profile_digest = write_json(ART / "example_compare_profile.json", compare_profile)

successor_p = 0.015
successor_vector = []
for item in RAW_TIERS:
    eff = attenuated_bits(item["raw_b"], successor_p)
    successor_vector.append({
        "tier": item["tier"],
        "p": successor_p,
        "raw_b": item["raw_b"],
        "effective_b": eff,
        "status": {"p": "policy_upper_bound", "raw_b": "illustrative_input"},
    })
successor_cset_bits = successor_vector[0]["effective_b"]
successor_fallback_summary_bits = sum(v["effective_b"] for v in successor_vector)
successor_total_summary_bits = math.log2(
    FALLBACK_RATE_HAT * (2.0 ** successor_fallback_summary_bits)
    + (1.0 - FALLBACK_RATE_HAT) * (2.0 ** PRIMARY_LINKABILITY_BOUND)
) + selection_tax_bits
successor_receipt = copy.deepcopy(receipt)
for item in successor_receipt["line_items"]:
    if item["exposure_nf_id"] == FALLBACK_CCT_EXPOSURE:
        item["budget_value"] = successor_cset_bits
        item["obs_model"]["p_obs_upper"] = successor_p
    elif item["exposure_nf_id"] == FALLBACK_VECTOR_EXPOSURE:
        item["budget_value"] = successor_fallback_summary_bits
        item["obs_model"]["vector"] = successor_vector
successor_receipt_digest = sha256_bytes(json.dumps(successor_receipt, indent=2, sort_keys=True).encode() + b"\n")

compare_walkthrough = {
    "walkthrough_id": "worked-example-compare-walkthrough-v1",
    "claim_id": CLAIM_ID,
    "base_release_id": RELEASE_ID,
    "focus_case": "replay-required-B",
    "compare_profile_id": COMPARE_PROFILE_ID,
    "release_action_matrix_id": release_action_matrix["action_matrix_id"],
    "release_obligation_profile_id": release_obligation_profile["obligation_profile_id"],
    "successor_receipt_digest_basis": "synthetic_case_B_successor_receipt",
    "changed_line_items": ["fallback_contact_surface", "fallback_tiered_vector"],
    "replay_plan_ids": ["eval-fallback-cct-v1", "eval-fallback-vector-v1"],
    "continuity_decision": "same_certified_interface_replayed_surfaces",
    "continuity_basis": [
        "tw_id is unchanged",
        "state_decl_id is unchanged",
        "required exposures remain unchanged",
        "primary separation class remains sep.nr1",
        "only the fallback contact/budget surface was replayed"
    ],
    "base_fields": {
        "user_fast_diff": {
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "budget_value": fallback_summary_bits,
            "selection_tax_bits": selection_tax_bits,
            "total_summary_bits_per_lookup": total_summary_bits,
            "receipt_digest": receipt_digest,
        },
        "auditor_fast_diff": {
            "tw_id": TW_ID,
            "covered_exposures": [
                PRIMARY_EXPOSURE,
                FALLBACK_CCT_EXPOSURE,
                FALLBACK_VECTOR_EXPOSURE,
                PATHSELECT_EXPOSURE,
            ],
            "primary_surface_manifest_digest": primary_surface_digest,
            "primary_rho_upper": RHO_UPPER,
            "state_contract_id": state_decl["state_contract_id"],
            "state_decl_id": state_decl["state_decl_id"],
            "plan_catalog_digest": plan_catalog_digest,
            "change_control_id": change_control["change_control_id"],
        },
    },
    "successor_fields": {
        "release_id": RELEASE_ID + "b",
        "user_fast_diff": {
            "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
            "budget_value": successor_fallback_summary_bits,
            "selection_tax_bits": selection_tax_bits,
            "total_summary_bits_per_lookup": successor_total_summary_bits,
            "receipt_digest": successor_receipt_digest,
        },
        "auditor_fast_diff": {
            "tw_id": TW_ID,
            "covered_exposures": [
                PRIMARY_EXPOSURE,
                FALLBACK_CCT_EXPOSURE,
                FALLBACK_VECTOR_EXPOSURE,
                PATHSELECT_EXPOSURE,
            ],
            "primary_surface_manifest_digest": primary_surface_digest,
            "primary_rho_upper": RHO_UPPER,
            "state_contract_id": state_decl["state_contract_id"],
            "state_decl_id": state_decl["state_decl_id"],
            "plan_catalog_digest": plan_catalog_digest,
            "change_control_id": change_control["change_control_id"],
        },
    },
    "observed_diffs": [
        "fallback obs_model.p_obs_upper decreases from 0.02 to 0.015",
        "fallback-vector budget_value decreases accordingly",
        "total-summary field decreases accordingly",
        "receipt digest changes",
        "guard fields tw_id, covered exposures, separation class, and state_decl_id remain stable",
    ],
    "user_first_alarm": "receipt digest changed; compare-profile then shows the fallback summary improved while exposure_nf_id and log family are stable",
    "auditor_first_alarm": "receipt digest changed with stable guard fields; change-control classifies this as replay_changed_surfaces, so rerun eval-fallback-cct-v1 and eval-fallback-vector-v1",
    "classification_result": "replay_changed_surfaces",
    "matched_rule_ids": ["contact-or-budget-replay"],
    "required_action": "publish fresh notarized comparison for the changed fallback surfaces and update release lineage without full recertification",
    "required_publication_roles": [
        "fresh_release_binding",
        "fresh_compare_report",
        "fresh_replay_verdict",
        "fresh_successor_continuity_verdict",
        "fresh_successor_lineage_notice",
    ],
    "note": "Concrete compare walk-through for the compare profile; explanatory adjunct rather than a new receipt primitive.",
}
compare_walkthrough_digest = write_json(ART / "example_compare_walkthrough.json", compare_walkthrough)

abom = {
    "abom_version": "0.3-worked-example",
    "claim_id": CLAIM_ID,
    "tw_id": TW_ID,
    "release_label": RELEASE_ID,
    "covered_exposures": [
        PRIMARY_EXPOSURE,
        FALLBACK_CCT_EXPOSURE,
        FALLBACK_VECTOR_EXPOSURE,
        PATHSELECT_EXPOSURE,
        PROFILING_EXPOSURE,
    ],
    "budget_summary": {
        "type": "MaxL_bits_per_lookup",
        "primary_surface": {
            "exposure_nf_id": PRIMARY_EXPOSURE,
            "value": PRIMARY_LINKABILITY_BOUND,
            "qualifier": "under separation class sep.nr1",
        },
        "fallback_summary": fallback_summary_bits,
        "selection_tax": selection_tax_bits,
        "total_summary": total_summary_bits,
        "window": "24h",
        "usage": f"Q<={Q}",
    },
    "artifacts": [
        {"name": "example_exposure_nf_registry.json", "sha256": exposure_registry_digest, "availability": "in_archive"},
        {"name": "example_tw_decl.json", "sha256": tw_decl_digest, "availability": "in_archive"},
        {"name": "example_receipt.json", "sha256": receipt_digest, "availability": "in_archive"},
        {"name": "example_state_decl.json", "sha256": state_decl_digest, "availability": "in_archive"},
        {"name": "example_state_decl_registry.json", "sha256": state_decl_registry_digest, "availability": "in_archive"},
        {"name": "example_effective_surface_resolution.json", "sha256": effective_surface_resolution_digest, "availability": "in_archive"},
        {"name": "example_primary_surface_manifest.json", "sha256": primary_surface_digest, "availability": "in_archive"},
        {"name": "example_user_watch_policy.json", "sha256": user_watch_digest, "availability": "in_archive"},
        {"name": "example_change_control.json", "sha256": change_control_digest, "availability": "in_archive"},
        {"name": "example_release_action_matrix.json", "sha256": release_action_matrix_digest, "availability": "in_archive"},
        {"name": "example_release_obligation_profile.json", "sha256": release_obligation_profile_digest, "availability": "in_archive"},
        {"name": "example_replay_plans.json", "sha256": plan_catalog_digest, "availability": "in_archive"},
        {"name": "example_support_bundle_map.json", "sha256": support_bundle_map_digest, "availability": "in_archive"},
        {"name": "example_profiling_evidence.json", "sha256": profiling_evidence_digest, "availability": "in_archive"},
        {"name": "example_compare_profile.json", "sha256": compare_profile_digest, "availability": "in_archive"},
        {"name": "example_drift_cases.json", "sha256": drift_cases_digest, "availability": "in_archive"},
        {"name": "example_compare_walkthrough.json", "sha256": compare_walkthrough_digest, "availability": "in_archive"},
        {"name": "example_line_item_owner_map.json", "sha256": line_item_owner_map_digest, "availability": "in_archive"},
    ],
    "signing": {"scheme": "ed25519", "key_id": "worked-example-key", "signature": "EXAMPLE_ONLY"},
}
abom_digest = write_json(ART / "example_abom.json", abom)

release_receipt = {
    "release_id": RELEASE_ID,
    "claim_id": CLAIM_ID,
    "abom_digest": abom_digest,
    "receipt_digest": receipt_digest,
    "plan_catalog_digest": plan_catalog_digest,
    "adjunct_digests": {
        "primary_surface_manifest": primary_surface_digest,
        "state_decl": state_decl_digest,
        "effective_surface_resolution": effective_surface_resolution_digest,
        "user_watch_policy": user_watch_digest,
        "change_control": change_control_digest,
        "release_action_matrix": release_action_matrix_digest,
        "release_obligation_profile": release_obligation_profile_digest,
        "support_bundle_map": support_bundle_map_digest,
        "compare_profile": compare_profile_digest,
        "compare_walkthrough": compare_walkthrough_digest,
        "line_item_owner_map": line_item_owner_map_digest,
    },
    "policy_gate": {
        "change_control_id": change_control["change_control_id"],
        "max_total_budget_bits_per_lookup": 0.30,
        "required_exposures": [FALLBACK_VECTOR_EXPOSURE, PATHSELECT_EXPOSURE],
        "require_uvi": True,
        "require_state_decl": True,
    },
    "pvsa": {
        "summary": "worked-example release binding",
        "digest": "EXAMPLE_ONLY",
    },
}
release_digest = write_json(ART / "example_release_receipt.json", release_receipt)

uvi = {
    "claim_pointer": CLAIM_ID,
    "exposure_nf_id": FALLBACK_VECTOR_EXPOSURE,
    "receipt_digest": receipt_digest,
    "log_anchor": {
        "log_id": "example-transparency-log",
        "checkpoint": "tree_size=42 root=EXAMPLE_ONLY",
        "inclusion_proof": ["EXAMPLE_ONLY"],
    },
    "consistency_context": {
        "checkpoint": "tree_size=42 root=EXAMPLE_ONLY",
        "proof_pointer": "consistency://example-transparency-log/41-42",
    },
}
uvi_digest = write_json(ART / "example_uvi.json", uvi)

BASE_VERIFIER_PLAN_ORDER = [
    "eval-primary-v1",
    "eval-fallback-cct-v1",
    "eval-fallback-vector-v1",
    "eval-pathselect-v1",
    "eval-profiling-eq-v1",
]
_base_owner_row_by_plan_id = {
    row["replay_plan_id"]: row
    for row in line_item_owner_map["entries"]
    if row.get("materialization_status") == "base_receipt_current_cut"
}
OPTIONAL_VARIANT_VERIFIER_PLAN_ORDER = [
    "eval-profiling-prefixfetch-v1",
    "eval-profiling-prefixfetch-statecond-v1",
    "eval-profiling-contact-coarsened-v1",
]
_variant_owner_row_by_plan_id = {
    row["replay_plan_id"]: row
    for row in line_item_owner_map.get("variant_entries", [])
    if row.get("materialization_status") == "optional_variant_receipt_current_cut"
}

def _public_object_digest_entries(paths):
    entries = []
    for relpath in paths:
        path = ART / relpath
        entries.append({
            "path": relpath,
            "sha256": sha256_bytes(path.read_bytes()) if path.exists() else None,
        })
    return entries

VERIFIER_CONTRACT_VERSION = "worked-example-verifier-contract-v2"
VERIFIER_PROOF_CARRYING_STATUS = "formal_exact_rational_budget_closure_log_endpoint_derivations_and_profiling_cp_union_bound_present"
VERIFIER_ARITHMETIC_MODE = "exact_rational_decimal_budget_closure plus exact_rational_integer_series_log_endpoint_derivations plus exact_rational_binomial_tail_profiling_envelope; python3_json_float_diagnostic_smoke excluded from formal proof"
VERIFIER_FORMAL_ACCEPTANCE_RULE = "The formal_rational_verifier_bundle parses public decimal budget endpoints as exact fractions, transcendental_endpoint_derivation_bundle proves maintained log2 endpoint upper bounds with integer/rational series certificates, and profiling_statistical_derivation_bundle proves the base profiling eta/delta envelope with exact binomial-tail and log-ratio inequalities under a fixed-sample stop/refresh lock; host-float recomputation remains diagnostic smoke."
FORMAL_RATIONAL_BUNDLE_ID = "worked-example-rational-budget-closure-v1"
TRANSCENDENTAL_ENDPOINT_BUNDLE_ID = "worked-example-log-endpoint-derivation-v1"
PROFILING_STATISTICAL_BUNDLE_ID = "worked-example-profiling-cp-union-bound-v1"
FORMAL_RATIONAL_ACCEPTANCE_RULE = "Parse every decimal string as an exact rational; for scalar rows require p_plus_decimal <= declared_upper_decimal <= receipt_budget_decimal; for vector rows also require sum(term_upper_decimals)=declared_upper_decimal; for eta/delta rows require eta_plus<=eta_receipt and delta_plus<=delta_receipt, with eta_plus/delta_plus supplied by profiling_statistical_derivation_bundle."


def _tool_source_digest(relpath):
    return sha256_bytes((ROOT / relpath).read_bytes())


def _verifier_contract(plan_id, public_objects):
    return {
        "contract_version": VERIFIER_CONTRACT_VERSION,
        "proof_carrying_status": VERIFIER_PROOF_CARRYING_STATUS,
        "arithmetic_mode": VERIFIER_ARITHMETIC_MODE,
        "formal_acceptance_rule": VERIFIER_FORMAL_ACCEPTANCE_RULE,
        "log_units": "bits_log2_where_numeric_budget_rows_are_used",
        "canonical_input_order": public_objects,
        "public_object_digest_binding": "public_object_digest_entries",
        "evaluator_source": "../tools/validate_example.py",
        "evaluator_source_sha256": _tool_source_digest("tools/validate_example.py"),
        "materializer_source": "../tools/materialize_example.py",
        "materializer_source_sha256": _tool_source_digest("tools/materialize_example.py"),
        "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID[plan_id],
        "support_pointer_status": "on_request_support_pointers_not_in_archive",
    }



def _verifier_plan_check(plan_id):
    row = _base_owner_row_by_plan_id[plan_id]
    public_objects = row.get("public_objects", [])
    return {
        "line_item_name": row["name"],
        "plan_id": plan_id,
        "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID[plan_id],
        "receipt_file": row.get("receipt_file"),
        "support_bundle_id": row.get("support_bundle_id"),
        "support_consumed_by": row.get("support_consumed_by", []),
        "support_required_artifacts": row.get("support_required_artifacts", []),
        "support_pointers": row.get("support_pointers", []),
        "public_objects": public_objects,
        "public_object_digest_entries": _public_object_digest_entries(public_objects),
        "verifier_contract": _verifier_contract(plan_id, public_objects),
    }


def _verifier_optional_variant_plan_check(plan_id):
    row = _variant_owner_row_by_plan_id[plan_id]
    public_objects = row.get("public_objects", [])
    out = {
        "line_item_name": row["name"],
        "plan_id": plan_id,
        "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID[plan_id],
        "receipt_variant_file": row.get("receipt_variant_file"),
        "evidence_id": row.get("evidence_id"),
        "support_bundle_id": row.get("support_bundle_id"),
        "support_consumed_by": row.get("support_consumed_by", []),
        "support_required_artifacts": row.get("support_required_artifacts", []),
        "support_pointers": row.get("support_pointers", []),
        "public_objects": public_objects,
        "public_object_digest_entries": _public_object_digest_entries(public_objects),
        "verifier_contract": _verifier_contract(plan_id, public_objects),
    }
    if row.get("coarsening_map_id") is not None:
        out["coarsening_map_id"] = row.get("coarsening_map_id")
    return out

def _formal_rational_budget_closure():
    scalar_rows = [
        {
            "plan_id": "eval-primary-v1",
            "line_item_name": "primary_path_declaration",
            "quantity": "primary_linkability_bits_per_lookup",
            "p_plus_decimal": PRIMARY_LINKABILITY_BITS_UPPER,
            "declared_upper_decimal": PRIMARY_LINKABILITY_BITS_UPPER,
            "receipt_budget_decimal": PRIMARY_LINKABILITY_BITS_UPPER,
            "acceptance_inequality": "p_plus_decimal <= declared_upper_decimal <= receipt_budget_decimal",
            "endpoint_origin": "policy-declared zero primary linkability contribution under sep.nr1; rho adjunct is carried separately in the receipt obs_model",
            "accepted": True,
        },
        {
            "plan_id": "eval-fallback-cct-v1",
            "line_item_name": "fallback_contact_surface",
            "quantity": "fallback_contact_bits_per_lookup",
            "p_plus_decimal": OUTWARD_EFFECTIVE_BITS_BY_TIER["CSET"],
            "declared_upper_decimal": OUTWARD_EFFECTIVE_BITS_BY_TIER["CSET"],
            "receipt_budget_decimal": OUTWARD_EFFECTIVE_BITS_BY_TIER["CSET"],
            "acceptance_inequality": "p_plus_decimal <= declared_upper_decimal <= receipt_budget_decimal",
            "endpoint_origin": "rev0865 conservative decimal upper bound for log2((1-p)+p*2^raw_b) with p=0.02 and raw_b=1.4; diagnostic host-float value is not a public upper bound",
            "accepted": True,
        },
        {
            "plan_id": "eval-pathselect-v1",
            "line_item_name": "path_selection_indicator",
            "quantity": "selection_tax_bits",
            "p_plus_decimal": SELECTION_TAX_BITS_UPPER,
            "declared_upper_decimal": SELECTION_TAX_BITS_UPPER,
            "receipt_budget_decimal": SELECTION_TAX_BITS_UPPER,
            "acceptance_inequality": "p_plus_decimal <= declared_upper_decimal <= receipt_budget_decimal",
            "endpoint_origin": "rev0865 conservative decimal upper bound for log2(R_pi) with R_pi<=1.2",
            "accepted": True,
        },
        {
            "plan_id": "eval-total-summary-v1",
            "line_item_name": "release_summary_envelope",
            "quantity": "total_summary_bits_per_lookup",
            "p_plus_decimal": TOTAL_SUMMARY_BITS_UPPER,
            "declared_upper_decimal": TOTAL_SUMMARY_BITS_UPPER,
            "receipt_budget_decimal": TOTAL_SUMMARY_BITS_UPPER,
            "acceptance_inequality": "p_plus_decimal <= declared_upper_decimal <= receipt_budget_decimal",
            "endpoint_origin": "rev0865 conservative decimal upper bound for the fixed-horizon fallback-rate summary using fallback_summary_bits and selection_tax_bits upper endpoints",
            "accepted": True,
        },
    ]
    vector_row = {
        "plan_id": "eval-fallback-vector-v1",
        "line_item_name": "fallback_tiered_vector",
        "quantity": "fallback_summary_bits_per_lookup",
        "term_upper_decimals": [
            OUTWARD_EFFECTIVE_BITS_BY_TIER["CSET"],
            OUTWARD_EFFECTIVE_BITS_BY_TIER["TIME"],
            OUTWARD_EFFECTIVE_BITS_BY_TIER["CONG"],
        ],
        "declared_upper_decimal": FALLBACK_SUMMARY_BITS_UPPER,
        "receipt_budget_decimal": FALLBACK_SUMMARY_BITS_UPPER,
        "acceptance_inequality": "sum(term_upper_decimals) == declared_upper_decimal <= receipt_budget_decimal",
        "endpoint_origin": "rev0865 exact-rational sum of the three conservative per-tier decimal upper bounds",
        "accepted": True,
    }
    eta_delta_row = {
        "plan_id": "eval-profiling-eq-v1",
        "line_item_name": "profiling_equalization",
        "quantity": "pairwise_equalization_eta_delta_bits",
        "eta_plus_decimal": PROFILING_ETA_BITS_UPPER,
        "eta_receipt_decimal": PROFILING_ETA_BITS_UPPER,
        "delta_plus_decimal": PROFILING_DELTA_UPPER,
        "delta_receipt_decimal": PROFILING_DELTA_UPPER,
        "acceptance_inequality": "eta_plus_decimal <= eta_receipt_decimal and delta_plus_decimal <= delta_receipt_decimal",
        "endpoint_origin": "synthetic CP/union-bound toy endpoint certified by profiling_statistical_derivation_bundle; no deployment inference is made",
        "accepted": True,
    }
    return {
        "bundle_id": FORMAL_RATIONAL_BUNDLE_ID,
        "bundle_version": 1,
        "claim_id": CLAIM_ID,
        "release_id": RELEASE_ID,
        "note_version": NOTE_VERSION,
        "proof_carrying_status": VERIFIER_PROOF_CARRYING_STATUS,
        "arithmetic_mode": "exact_rational_decimal_strings_no_float_tolerance",
        "acceptance_rule": FORMAL_RATIONAL_ACCEPTANCE_RULE,
        "scope": "formal closure of public decimal budget endpoints and receipt/report inequalities; log2 endpoint upper bounds are separately proved by transcendental_endpoint_derivation_bundle and profiling eta/delta endpoints are supplied by profiling_statistical_derivation_bundle",
        "related_transcendental_bundle_id": TRANSCENDENTAL_ENDPOINT_BUNDLE_ID,
        "related_profiling_statistical_bundle_id": PROFILING_STATISTICAL_BUNDLE_ID,
        "canonical_input_order": [
            "example_receipt.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
            "example_verifier_report.json",
        ],
        "tool_source_digests": {
            "evaluator_source": "../tools/validate_example.py",
            "evaluator_source_sha256": _tool_source_digest("tools/validate_example.py"),
            "materializer_source": "../tools/materialize_example.py",
            "materializer_source_sha256": _tool_source_digest("tools/materialize_example.py"),
        },
        "scalar_rows": scalar_rows,
        "vector_rows": [vector_row],
        "eta_delta_rows": [eta_delta_row],
        "accepted": True,
    }



def _pow2_upper_fraction(witness: dict) -> Fraction:
    return Fraction(int(witness["upper_dyadic_numerator"]), 1 << int(witness["upper_dyadic_denominator_power_of_two"]))


def _decimal_string_for_fraction(value: Fraction, places: int = 18) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    scale = 10 ** places
    integer = value.numerator // value.denominator
    frac = (value.numerator % value.denominator) * scale // value.denominator
    return f"{sign}{integer}.{frac:0{places}d}"


def _log2_one_plus_upper_check(y_upper: Fraction, bits_upper: Fraction, ln2_lower: Fraction, log1p_terms: int) -> dict:
    ln1p_upper = ln1p_upper_alt(y_upper, log1p_terms)
    rhs = bits_upper * ln2_lower
    return {
        "accepted": ln1p_upper <= rhs,
        "log1p_upper_terms": log1p_terms if log1p_terms % 2 else log1p_terms + 1,
        "lhs_ln1p_upper_fraction": fraction_payload(ln1p_upper),
        "rhs_bits_times_ln2_lower_fraction": fraction_payload(rhs),
        "margin_lower_bound_decimal": _decimal_string_for_fraction(rhs - ln1p_upper, 24),
    }


def _transcendental_endpoint_derivation_bundle():
    ln2_terms = 40
    ln2_lower, ln2_upper = ln2_bounds_via_atanh(ln2_terms)
    pow2_scale_bits = 96
    raw_rows = []
    for item in RAW_TIERS:
        tier = item["tier"]
        raw_fraction = dec_fraction(str(item["raw_b"]))
        pow2_witness = dyadic_pow2_upper_witness(raw_fraction, pow2_scale_bits)
        pow2_upper = _pow2_upper_fraction(pow2_witness)
        y_upper = dec_fraction(str(P_OBS_UPPER)) * (pow2_upper - 1)
        public_upper = dec_fraction(OUTWARD_EFFECTIVE_BITS_BY_TIER[tier])
        check = _log2_one_plus_upper_check(y_upper, public_upper, ln2_lower, 9)
        raw_rows.append({
            "row_id": f"fallback_{tier.lower()}_attenuated_log2_upper",
            "tier": tier,
            "formula": "log2(1 + p_obs_upper*(2^raw_b - 1)) <= public_effective_bits_upper",
            "p_obs_upper_decimal": str(P_OBS_UPPER),
            "raw_b_decimal": str(item["raw_b"]),
            "public_effective_bits_upper_decimal": OUTWARD_EFFECTIVE_BITS_BY_TIER[tier],
            "pow2_raw_b_upper_witness": pow2_witness,
            "y_upper_fraction": fraction_payload(y_upper),
            "acceptance_inequality": "ln1p_upper_alt(y_upper, odd_terms) <= public_effective_bits_upper*ln2_lower",
            **check,
        })

    selection_y = dec_fraction(str(R_PI_UPPER)) - 1
    selection_check = _log2_one_plus_upper_check(selection_y, dec_fraction(SELECTION_TAX_BITS_UPPER), ln2_lower, 21)
    selection_row = {
        "row_id": "path_selection_tax_log2_upper",
        "formula": "log2(R_pi_upper) = log2(1+(R_pi_upper-1)) <= selection_tax_bits_upper",
        "R_pi_upper_decimal": str(R_PI_UPPER),
        "selection_tax_bits_upper_decimal": SELECTION_TAX_BITS_UPPER,
        "y_upper_fraction": fraction_payload(selection_y),
        "acceptance_inequality": "ln1p_upper_alt(R_pi_upper-1, odd_terms) <= selection_tax_bits_upper*ln2_lower",
        **selection_check,
    }

    fallback_summary_upper = dec_fraction(FALLBACK_SUMMARY_BITS_UPPER)
    selection_upper = dec_fraction(SELECTION_TAX_BITS_UPPER)
    total_upper = dec_fraction(TOTAL_SUMMARY_BITS_UPPER)
    total_delta_bits = total_upper - selection_upper
    exp_argument_upper = fallback_summary_upper * ln2_upper
    exp_terms = 8
    exp_s_upper = exp_upper_taylor(exp_argument_upper, exp_terms)
    total_y_upper = dec_fraction(str(FALLBACK_RATE_HAT)) * (exp_s_upper - 1)
    total_check = _log2_one_plus_upper_check(total_y_upper, total_delta_bits, ln2_lower, 5)
    total_row = {
        "row_id": "fallback_rate_total_summary_log2_upper",
        "formula": "log2(1+fallback_rate_hat*(2^fallback_summary_bits_upper-1)) + selection_tax_bits_upper <= total_summary_bits_upper",
        "fallback_rate_hat_decimal": str(FALLBACK_RATE_HAT),
        "fallback_summary_bits_upper_decimal": FALLBACK_SUMMARY_BITS_UPPER,
        "selection_tax_bits_upper_decimal": SELECTION_TAX_BITS_UPPER,
        "total_summary_bits_upper_decimal": TOTAL_SUMMARY_BITS_UPPER,
        "residual_bits_upper_decimal": _decimal_string_for_fraction(total_delta_bits, 18),
        "exp_argument_upper_fraction": fraction_payload(exp_argument_upper),
        "exp_upper_terms": exp_terms,
        "exp_fallback_summary_upper_fraction": fraction_payload(exp_s_upper),
        "y_upper_fraction": fraction_payload(total_y_upper),
        "acceptance_inequality": "ln1p_upper_alt(fallback_rate_hat*(exp_upper(S*ln2_upper)-1), odd_terms) <= (total_summary_bits_upper-selection_tax_bits_upper)*ln2_lower",
        **total_check,
    }

    all_rows = raw_rows + [selection_row, total_row]
    return {
        "bundle_id": TRANSCENDENTAL_ENDPOINT_BUNDLE_ID,
        "bundle_version": 1,
        "claim_id": CLAIM_ID,
        "release_id": RELEASE_ID,
        "note_version": NOTE_VERSION,
        "proof_carrying_status": VERIFIER_PROOF_CARRYING_STATUS,
        "arithmetic_mode": "exact_rational_integer_series_bounds_no_float_tolerance",
        "scope": "formal exact-rational upper-bound certificate for the maintained worked-example log2 endpoint rows: fallback tier attenuation, selection tax, and total summary; profiling eta/delta is certified separately by profiling_statistical_derivation_bundle",
        "ln2_bound": {
            "method": "ln(2)=2*atanh(1/3) positive series with rational geometric tail",
            "terms": ln2_terms,
            "lower_bound_fraction": fraction_payload(ln2_lower),
            "upper_bound_fraction": fraction_payload(ln2_upper),
        },
        "raw_fallback_rows": raw_rows,
        "selection_tax_row": selection_row,
        "total_summary_row": total_row,
        "accepted": all(row.get("accepted") is True for row in all_rows),
    }

def _profiling_statistical_derivation_bundle():
    ln2_terms = 40
    ln2_lower, _ln2_upper = ln2_bounds_via_atanh(ln2_terms)
    alpha_per_cell_fraction = Fraction(1, 1500)
    two_sided_tail_fraction = Fraction(1, 3000)
    cell_count = len(PROF_BINS) * len(PROF_COUNTS)
    interval_rows = []
    for bin_index, bin_name in enumerate(PROF_BINS):
        for klass in sorted(PROF_COUNTS.keys()):
            count = int(PROF_COUNTS[klass][bin_index])
            lo_s, hi_s = _prof_interval_decimals[klass][bin_index]
            lower_ok = count == 0 or binomial_tail_ge_le_alpha_decimal(_PROF_N, count, lo_s)
            upper_ok = count == _PROF_N or binomial_cdf_le_alpha_decimal(_PROF_N, count, hi_s)
            interval_rows.append({
                "row_id": f"{klass}:{bin_name}",
                "class": klass,
                "bin": bin_name,
                "n": _PROF_N,
                "count": count,
                "lower_decimal": lo_s,
                "upper_decimal": hi_s,
                "two_sided_tail_alpha_fraction": fraction_payload(two_sided_tail_fraction),
                "lower_acceptance_inequality": "count==0 or Pr_{p=lower_decimal}[Bin(n,p)>=count] <= alpha_per_cell/2",
                "upper_acceptance_inequality": "count==n or Pr_{p=upper_decimal}[Bin(n,p)<=count] <= alpha_per_cell/2",
                "accepted": bool(lower_ok and upper_ok),
            })

    ratio_terms = 12
    ratio_rows = []
    eta_public = dec_fraction(PROFILING_ETA_BITS_UPPER)
    eta_rhs = eta_public * ln2_lower
    for bin_index, bin_name in enumerate(PROF_BINS):
        if bin_index in _prof_rare_idx:
            continue
        for numerator_class in sorted(PROF_COUNTS.keys()):
            for denominator_class in sorted(PROF_COUNTS.keys()):
                if numerator_class == denominator_class:
                    continue
                numerator_upper = _prof_intervals[numerator_class][bin_index][1]
                denominator_lower = _prof_intervals[denominator_class][bin_index][0]
                lhs = ln_ratio_upper_atanh(numerator_upper, denominator_lower, ratio_terms)
                ratio_rows.append({
                    "row_id": f"{numerator_class}_over_{denominator_class}:{bin_name}",
                    "bin": bin_name,
                    "numerator_class": numerator_class,
                    "denominator_class": denominator_class,
                    "numerator_upper_decimal": _prof_interval_decimals[numerator_class][bin_index][1],
                    "denominator_lower_decimal": _prof_interval_decimals[denominator_class][bin_index][0],
                    "eta_public_decimal": PROFILING_ETA_BITS_UPPER,
                    "ln_ratio_upper_terms": ratio_terms,
                    "acceptance_inequality": "ln_ratio_upper_atanh(numerator_upper/denominator_lower) <= eta_public*ln2_lower",
                    "margin_lower_bound_decimal": _decimal_string_for_fraction(eta_rhs - lhs, 24),
                    "accepted": bool(lhs <= eta_rhs),
                })

    rare_mass_rows = []
    for klass in sorted(PROF_COUNTS.keys()):
        mass = sum(_prof_intervals[klass][i][1] for i in _prof_rare_idx)
        rare_mass_rows.append({
            "class": klass,
            "rare_mass_upper_decimal": _decimal_string_for_fraction(mass, 12),
            "rare_bins": [PROF_BINS[i] for i in _prof_rare_idx],
        })

    all_rows = interval_rows + ratio_rows
    return {
        "bundle_id": PROFILING_STATISTICAL_BUNDLE_ID,
        "bundle_version": 1,
        "claim_id": CLAIM_ID,
        "release_id": RELEASE_ID,
        "note_version": NOTE_VERSION,
        "proof_carrying_status": VERIFIER_PROOF_CARRYING_STATUS,
        "arithmetic_mode": "exact_rational_binomial_tail_and_log_ratio_bounds_no_float_tolerance",
        "scope": "formal exact-rational finite-sample envelope for the maintained base profiling_equalization eta/delta row; optional profiling variants remain separate worked-example carriers",
        "acceptance_rule": "Outward CP decimal intervals must pass exact binomial-tail inequalities; a union bound over cells spends delta_stat; non-rare bin ratios must satisfy ln(upper/lower)<=eta_public*ln2_lower; rare-bin upper mass must be <= delta_public.",
        "projection": "retry_bucket_trace",
        "delta_stat_fraction": fraction_payload(Fraction(1, 100)),
        "cell_count": cell_count,
        "alpha_per_cell_fraction": fraction_payload(alpha_per_cell_fraction),
        "two_sided_tail_alpha_fraction": fraction_payload(two_sided_tail_fraction),
        "union_bound_accepted": bool(cell_count * alpha_per_cell_fraction <= Fraction(1, 100)),
        "ln2_bound": {
            "method": "ln(2)=2*atanh(1/3) positive series with rational geometric tail",
            "terms": ln2_terms,
            "lower_bound_fraction": fraction_payload(ln2_lower),
        },
        "interval_rows": interval_rows,
        "ratio_rows": ratio_rows,
        "rare_support": {
            "rare_bins": [PROF_BINS[i] for i in _prof_rare_idx],
            "rare_mass_rows": rare_mass_rows,
            "delta_plus_decimal": PROF_DELTA_PLUS_DECIMAL,
            "delta_public_decimal": PROFILING_DELTA_UPPER,
            "accepted": bool(dec_fraction(PROF_DELTA_PLUS_DECIMAL) <= dec_fraction(PROFILING_DELTA_UPPER)),
        },
        "fixed_sample_stop_rule": {
            **profiling_fixed_sample_plan(),
            "evidence_file": "example_profiling_evidence.json",
            "evidence_id": profiling_evidence_id,
            "acceptance_inequality": "look_count_allowed == 1 and count_table_digest == digest(classes,bins,counts,n_per_class) and optional_stopping_status == disallowed_by_certificate",
            "validity_scope": "single frozen maintained toy-count table only; no anytime-valid or repeated-refresh guarantee",
            "accepted": True,
        },
        "eta_public_decimal": PROFILING_ETA_BITS_UPPER,
        "accepted": bool(all(row.get("accepted") is True for row in all_rows) and dec_fraction(PROF_DELTA_PLUS_DECIMAL) <= dec_fraction(PROFILING_DELTA_UPPER) and cell_count * alpha_per_cell_fraction <= Fraction(1, 100)),
    }


verifier_report = {
    "claim_id": CLAIM_ID,
    "plans_checked": [_verifier_plan_check(plan_id) for plan_id in BASE_VERIFIER_PLAN_ORDER],
    "optional_variant_plans_checked": [_verifier_optional_variant_plan_check(plan_id) for plan_id in OPTIONAL_VARIANT_VERIFIER_PLAN_ORDER],
    "recomputed": {
        "fallback_contact_bits_per_lookup": fallback_cset_bits,
        "fallback_summary_bits_per_lookup": fallback_summary_bits,
        "selection_tax_bits": selection_tax_bits,
        "total_summary_bits_per_lookup": total_summary_bits,
    },
    "formal_rational_verifier_bundle": _formal_rational_budget_closure(),
    "transcendental_endpoint_derivation_bundle": _transcendental_endpoint_derivation_bundle(),
    "profiling_statistical_derivation_bundle": _profiling_statistical_derivation_bundle(),
    "notary_replay_packet": {
        "packet_id": "notary_replay_packet",
        "claim_id": CLAIM_ID,
        "receipt_digest": receipt_digest,
        "release_id": RELEASE_ID,
        "note_version": NOTE_VERSION,
        "line_item_name": "fallback_contact_surface",
        "plan_id": "eval-fallback-cct-v1",
        "plan_spec_id": PLAN_SPEC_ID_BY_PLAN_ID["eval-fallback-cct-v1"],
        "attempts_present": [1, 2],
        "first_passing_attempt": 2,
        "retry_budget": "1e-6 total across sched.delta.4step.v1",
        "metric_family_size": 5,
        "bonferroni_threshold": "6e-8",
        "reported_p_value": "4e-8",
        "support_bundle": "bundle://worked-example/fallback-cct",
        "support_pointer": "support://fallback/notarized-attempt-log.example",
        "optional_support_packet": "example_uvi.json",
        "release_handoff_role": "fresh_replay_verdict",
        "quotable_output": {
            "fallback_contact_bits_per_lookup": fallback_cset_bits,
        },
        "public_objects": [
            "example_receipt.json",
            "example_state_decl.json",
            "example_replay_plans.json",
            "example_support_bundle_map.json",
            "example_verifier_report.json",
            "example_uvi.json",
            "example_release_closure_ledger.json",
        ],
    },
    "support_artifacts": {
        "state_decl_id": state_decl_id,
        "state_decl_digest": state_decl_digest,
        "state_decl_registry_digest": state_decl_registry_digest,
        "plan_catalog_digest": plan_catalog_digest,
        "primary_surface_digest": primary_surface_digest,
        "change_control_digest": change_control_digest,
        "profiling_evidence_digest": profiling_evidence_digest,
        "support_bundle_map_digest": support_bundle_map_digest,
        "compare_profile_digest": compare_profile_digest,
        "compare_walkthrough_digest": compare_walkthrough_digest,
        "effective_surface_resolution_digest": effective_surface_resolution_digest,
        "line_item_owner_map_digest": line_item_owner_map_digest,
        "release_receipt_digest": release_digest,
        "user_watch_policy_digest": user_watch_digest,
        "uvi_digest": uvi_digest,
        "drift_cases_digest": drift_cases_digest,
    },
    "notes": [
        "Worked example only; no live deployment evidence implied.",
        "Primary-path contribution is assumption-qualified and valid only on the identity-to-destination linkability surface under sep.nr1.",
        "Primary-path line item also publishes rho_upper as a policy upper bound on separation failure (interpreted as a guarded (0,rho) adjunct).",
        "Path-selection term uses log2(R_pi) with R_pi<=1.2.",
        "Fallback-rate hat value is treated as an empirical estimate; p_obs and R_pi are policy upper bounds.",
        "User-facing drift checks are externalized to example_user_watch_policy.json rather than the minimal UVI tuple.",
        "Release-side drift handling is externalized to example_change_control.json so refresh-only updates can be distinguished from replay-required or full-recertification updates.",
        "example_drift_cases.json gives one tiny refresh-only case, one replay-required case, and one full-recertification case so the change-control categories are visible on concrete field diffs.",
        "example_support_bundle_map.json resolves artifact_bundle ids to the concrete in-archive artifacts and off-bundle support pointers each replay plan expects.",
        "plans_checked enumerates all materialized base receipt replay plans in this cut, including eval-profiling-eq-v1 for profiling_equalization.",
        "Each plans_checked row mirrors the line_item_name, support_bundle_id, support_required_artifacts, support_pointers, and public_objects from the materialized owner-map row so verifier closure does not require a second support-map lookup.",
        "Each plans_checked row also carries public_object_digest_entries so the verifier surface binds every named public object to the current in-archive SHA-256 digest.",
        "Each plans_checked row carries verifier_contract so host-float recomputation is separated from the rev0865 exact-rational budget-closure certificate.",
        "formal_rational_verifier_bundle gives exact-fraction acceptance checks over public decimal budget endpoints, transcendental_endpoint_derivation_bundle proves the maintained log2 endpoint upper bounds by exact rational series/integer witnesses, and profiling_statistical_derivation_bundle proves the base profiling eta/delta CP+union-bound envelope with exact binomial-tail/log-ratio checks under a fixed-sample stop/refresh lock.",
        "optional_variant_plans_checked enumerates the three optional profiling variant replay hooks separately from base plans_checked.",
        "Each optional_variant_plans_checked row mirrors receipt_variant_file, evidence_id, support_bundle_id, support_required_artifacts, support_pointers, public_objects, public_object_digest_entries, and verifier_contract from the variant owner-map row.",
        "Each materialized support bundle in example_support_bundle_map.json carries resolved_owner_map_row_names and resolved_owner_map_rows; the resolver is multiplicity-safe, so bundle://worked-example/fallback-cct resolves both fallback_contact_surface and notary_replay_packet without singleton line_item_name/materialization shortcut fields.",
        "support_artifacts.profiling_evidence_digest binds the profiling evidence object used by eval-profiling-eq-v1.",
        "example_compare_profile.json names the fastest cross-release diff surfaces for users and auditors without changing the core receipt tuple.",
        "example_compare_walkthrough.json shows one concrete prior-vs-current comparison using those diff fields so the compare profile is not just a list of names.",
    ],
}
verifier_digest = write_json(ART / "example_verifier_report.json", verifier_report)

artifact_inventory = {
    "inventory_id": INVENTORY_ID,
    "support_manifest_id": MANIFEST_ID,
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "groups": [
        {
            "group": "claim_objects",
            "visibility": "published",
            "entries": [
                {"path": "example_receipt.json", "role": "receipt tuple", "consumed_by": ["abom", "release_receipt", "uvi", "auditor"]},
                {"path": "example_receipt_prefixfetch_variant.json", "role": "optional variant receipt (prefix-fetch profiling extension)", "consumed_by": ["auditor"]},
                {"path": "example_receipt_prefixfetch_statecond_variant.json", "role": "optional variant receipt (state-conditioned prefix-fetch profiling extension)", "consumed_by": ["auditor"]},
                {"path": "example_receipt_contact_coarsened_variant.json", "role": "optional variant receipt (coarsened contact-set profiling extension)", "consumed_by": ["auditor"]},
                {"path": "example_abom.json", "role": "claim manifest", "consumed_by": ["release_receipt", "user", "auditor"]},
                {"path": "example_exposure_nf_registry.json", "role": "label-to-ENF-ID binding registry", "consumed_by": ["user", "auditor"]},
                {"path": "example_tw_decl.json", "role": "threat/window declaration (label-to-TW-ID binding)", "consumed_by": ["user", "auditor"]},
                {"path": "example_state_decl_registry.json", "role": "label-to-state-decl-id binding registry", "consumed_by": ["user", "auditor"]},
                {"path": "example_release_receipt.json", "role": "release binding", "consumed_by": ["auditor", "user"]},
                {"path": "example_uvi.json", "role": "minimal user discovery object", "consumed_by": ["user"]},
            ],
        },
        {
            "group": "guard_and_compare_adjuncts",
            "visibility": "published_adjunct",
            "entries": [
                {"path": "example_primary_surface_manifest.json", "role": "primary declaration guard surface", "consumed_by": ["auditor", "release_receipt"]},
                {"path": "example_state_decl.json", "role": "scoped state declaration", "consumed_by": ["auditor", "replay_plans"]},
                {"path": "example_effective_surface_resolution.json", "role": "effective replay-surface assembly adjunct", "consumed_by": ["auditor", "validator", "maintainer"]},
                {"path": "example_change_control.json", "role": "release drift policy", "consumed_by": ["release_receipt", "auditor"]},
                {"path": "example_release_action_matrix.json", "role": "field-family diff-to-action matrix", "consumed_by": ["user", "auditor", "maintainer"]},
                {"path": "example_release_obligation_profile.json", "role": "action-class to publication-duty profile", "consumed_by": ["maintainer", "auditor", "user"]},
                {"path": "example_compare_profile.json", "role": "cross-release diff profile", "consumed_by": ["user", "auditor"]},
                {"path": "example_compare_walkthrough.json", "role": "illustrative prior-vs-current diff", "consumed_by": ["user", "auditor"]},
                {"path": "example_successor_continuity_verdict.json", "role": "base-to-successor continuity verdict adjunct", "consumed_by": ["user", "auditor", "maintainer"]},
                {"path": "example_publication_closure_verdict.json", "role": "successor publication-package closure verdict adjunct", "consumed_by": ["user", "auditor", "maintainer"]},
                {"path": "example_successor_status_envelope.json", "role": "narrow summary-stage status envelope for one successor comparison", "consumed_by": ["user", "referee", "release_note"]},
                {"path": "example_successor_lineage_notice.json", "role": "outward-facing successor lineage notice adjunct", "consumed_by": ["user", "maintainer", "release_note"]},
                {"path": "example_successor_derivation_graph.json", "role": "maintenance DAG for one successor comparison", "consumed_by": ["maintainer", "referee", "auditor"]},
                {"path": "example_release_spine.json", "role": "stable stage map for successor maintenance", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_release_stage_walkthrough.json", "role": "stage-by-stage worked release walk for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_successor_claim_support_map.json", "role": "statement-to-evidence support map for one successor comparison", "consumed_by": ["user", "referee", "maintainer"]},
                {"path": "example_successor_citation_map.json", "role": "minimal-citation map for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_successor_challenge_routes.json", "role": "audience-keyed challenge routes for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note", "auditor"]},
                {"path": "example_successor_challenge_branches.json", "role": "piece-keyed challenge branches for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note", "auditor"]},
                {"path": "example_successor_quote_map.json", "role": "exact-field quote map for one successor comparison", "consumed_by": ["maintainer", "referee", "release_note"]},
                {"path": "example_successor_clause_pack.json", "role": "canonical clause pack for one successor comparison", "consumed_by": ["maintainer", "release_note", "referee"]},
                {"path": "example_successor_sentence_locks.json", "role": "pair-anchored sentence-lock ledger for one successor comparison", "consumed_by": ["maintainer", "release_note", "referee"]},
                {"path": "example_line_item_owner_map.json", "role": "line-item owner/import crosswalk", "consumed_by": ["referee", "auditor", "maintainer"]},
                {"path": "example_drift_cases.json", "role": "tiny successor-release catalog", "consumed_by": ["auditor", "maintainer"]},
                {"path": "example_user_watch_policy.json", "role": "client drift alarms", "consumed_by": ["user"]},
            ],
        },
        {
            "group": "replay_and_evidence_adjuncts",
            "visibility": "published_adjunct",
            "entries": [
                {"path": "example_replay_plans.json", "role": "plan-id catalog", "consumed_by": ["auditor", "validator"]},
                {"path": "example_support_bundle_map.json", "role": "artifact-bundle resolver", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence.json", "role": "profiling/equalization audit evidence table", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence_prefixfetch.json", "role": "prefix-fetch profiling/equalization audit evidence table (variant receipt)", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence_prefixfetch_statecond.json", "role": "state-conditioned prefix-fetch profiling/equalization audit evidence table (variant receipt)", "consumed_by": ["auditor", "validator"]},
                {"path": "example_profiling_evidence_contact_coarsened.json", "role": "coarsened-contact profiling/equalization audit evidence table (variant receipt)", "consumed_by": ["auditor", "validator"]},
                {"path": "example_coarsening_map_contact.json", "role": "declared coarsening/partition map for contact-set hash", "consumed_by": ["auditor", "validator"]},
                {"path": "example_verifier_report.json", "role": "worked replay summary", "consumed_by": ["maintainer", "auditor"]},
            ],
        },
        {
            "group": "maintenance_outputs",
            "visibility": "maintenance_only",
            "entries": [
                {"path": "example_artifact_inventory.json", "role": "machine-readable artifact inventory", "consumed_by": ["maintainer", "validator"]},
                {"path": "example_compare_report.json", "role": "machine-readable cross-release diff report", "consumed_by": ["maintainer", "validator"]},
                {"path": "support_manifest.json", "role": "digest manifest for support artifacts", "consumed_by": ["maintainer", "validator"]},
                {"path": "example_validation_report.json", "role": "validator output", "consumed_by": ["maintainer"]},
            ],
        },
        {
            "group": "maintenance_helpers",
            "visibility": "maintenance_only",
            "entries": [
                {"path": "README.md", "role": "human maintenance guide", "consumed_by": ["maintainer"]},
                {"path": "paper.tex", "role": "worked-note source", "consumed_by": ["maintainer"]},
                {"path": "tools/materialize_example.py", "role": "deterministic artifact generator", "consumed_by": ["maintainer"]},
                {"path": "tools/emit_compare_report.py", "role": "compare-report emitter", "consumed_by": ["maintainer"]},
                {"path": "tools/validate_example.py", "role": "local consistency validator", "consumed_by": ["maintainer"]},
                {"path": "tools/refine_terminal_witnesses.py", "role": "terminal-witness ledger refiner", "consumed_by": ["maintainer"]},
                {"path": "tools/rebuild_example.sh", "role": "one-shot rebuild helper", "consumed_by": ["maintainer"]},
            ],
        },
    ],
    "note": "Maintenance inventory for the worked-example support bundle maintained alongside the worked note. It groups published adjuncts, the note source, and local maintenance helpers by operational role without making them part of the receipt schema, and it points back to the companion support manifest for the same maintained bundle cut.",
}
artifact_inventory_digest = write_json(ART / "example_artifact_inventory.json", artifact_inventory)

support_manifest = {
    "manifest_id": MANIFEST_ID,
    "artifact_inventory_id": INVENTORY_ID,
    "claim_id": CLAIM_ID,
    "release_id": RELEASE_ID,
    "note_version": NOTE_VERSION,
    "note": "Digest-bound maintenance manifest for the worked-example support bundle. It points back to the companion artifact inventory for the same maintained bundle cut.",
    "path_semantics": {
        "artifact_root": "series/synthesis/paper17_worked_example_receipt_interlock/artifacts",
        "paper_root": "series/synthesis/paper17_worked_example_receipt_interlock",
        "repo_root": ".",
        "row_contract": "Each file row keeps the historical path spelling, but base and repo_relative_path are authoritative for validation."
    },
    "files": [
        manifest_entry("example_abom.json", abom_digest),
        manifest_entry("example_exposure_nf_registry.json", exposure_registry_digest),
        manifest_entry("example_tw_decl.json", tw_decl_digest),
        manifest_entry("example_state_decl_registry.json", state_decl_registry_digest),
        manifest_entry("example_receipt.json", receipt_digest),
        manifest_entry("example_receipt_prefixfetch_variant.json", variant_receipt_digest),
        manifest_entry("example_receipt_prefixfetch_statecond_variant.json", statecond_receipt_digest),
        manifest_entry("example_receipt_contact_coarsened_variant.json", contact_coarsened_receipt_digest),
        manifest_entry("example_release_receipt.json", release_digest),
        manifest_entry("example_primary_surface_manifest.json", primary_surface_digest),
        manifest_entry("example_replay_plans.json", plan_catalog_digest),
        manifest_entry("example_support_bundle_map.json", support_bundle_map_digest),
        manifest_entry("example_profiling_evidence.json", profiling_evidence_digest),
        manifest_entry("example_profiling_evidence_prefixfetch.json", profiling_prefix_evidence_digest),
        manifest_entry("example_profiling_evidence_prefixfetch_statecond.json", profiling_statecond_evidence_digest),
        manifest_entry("example_profiling_evidence_contact_coarsened.json", contact_coarsened_evidence_digest),
        manifest_entry("example_coarsening_map_contact.json", coarsening_map_digest),
        manifest_entry("example_compare_profile.json", compare_profile_digest),
        manifest_entry("example_compare_walkthrough.json", compare_walkthrough_digest),
        manifest_entry("example_successor_derivation_graph.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_status_envelope.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_release_spine.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_release_stage_walkthrough.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_claim_support_map.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_citation_map.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_challenge_stop_profiles.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_challenge_routes.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_challenge_branches.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_quote_map.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_clause_pack.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_successor_sentence_locks.json", "EMITTED_BY_COMPARE_HELPER"),
        manifest_entry("example_line_item_owner_map.json", line_item_owner_map_digest),
        manifest_entry("example_effective_surface_resolution.json", effective_surface_resolution_digest),
        manifest_entry("example_state_decl.json", state_decl_digest),
        manifest_entry("example_user_watch_policy.json", user_watch_digest),
        manifest_entry("example_change_control.json", change_control_digest),
        manifest_entry("example_release_action_matrix.json", release_action_matrix_digest),
        manifest_entry("example_release_obligation_profile.json", release_obligation_profile_digest),
        manifest_entry("example_drift_cases.json", drift_cases_digest),
        manifest_entry("example_uvi.json", uvi_digest),
        manifest_entry("example_verifier_report.json", verifier_digest),
        manifest_entry("example_artifact_inventory.json", artifact_inventory_digest),
        manifest_entry("../README.md", sha256_bytes((ROOT / "README.md").read_bytes())),
        manifest_entry("../paper.tex", sha256_bytes((ROOT / "paper.tex").read_bytes())),
        manifest_entry("../tools/materialize_example.py", sha256_bytes((ROOT / "tools" / "materialize_example.py").read_bytes())),
        manifest_entry("../tools/emit_compare_report.py", sha256_bytes((ROOT / "tools" / "emit_compare_report.py").read_bytes())),
        manifest_entry("../tools/validate_example.py", sha256_bytes((ROOT / "tools" / "validate_example.py").read_bytes())),
        manifest_entry("../tools/refine_terminal_witnesses.py", sha256_bytes((ROOT / "tools" / "refine_terminal_witnesses.py").read_bytes())),
        manifest_entry("../tools/rebuild_example.sh", sha256_bytes((ROOT / "tools" / "rebuild_example.sh").read_bytes())),
    ]
}
decorate_payload_pointer_manifest(support_manifest)
write_json(ART / "support_manifest.json", support_manifest)

#!/usr/bin/env python3
"""Guard the cube's shared restricted-JCS canonical JSON digest helper.

The risky failure mode is quiet drift back to per-checker
``json.dumps(sort_keys=True)`` helpers while ADR-0022 and digest fields claim a
portable byte identity.  This check keeps the shared helper executable by
example and ratchets down local helper sprawl without forcing a huge historical
rewrite in one cut.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from cube_digest_lib import (  # noqa: E402
    CanonicalJsonError,
    canonical_json_profile,
    canonical_json_text,
    load_json_strict_text,
    pretty_json_text,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROFILE = "derivebsd-jcs-ijson-no-float-v1"
MAX_LEGACY_LOCAL_DIGEST_HELPERS = 0
LEGACY_HELPER_RE = re.compile(
    r"def\s+_?jcs_bytes\b|json\.dumps\([^\n]*sort_keys=True[^\n]*separators\s*=",
    re.MULTILINE,
)


def _expect_raises(label: str, fn: Callable[[], object], errors: list[str]) -> None:
    try:
        fn()
    except CanonicalJsonError:
        return
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{label}: raised {type(exc).__name__}, expected CanonicalJsonError")
        return
    errors.append(f"{label}: did not raise CanonicalJsonError")


def _legacy_helper_files() -> list[str]:
    files: list[str] = []
    for path in sorted((ROOT / "tools").glob("check_*.py")):
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if LEGACY_HELPER_RE.search(text):
            files.append(path.relative_to(ROOT).as_posix())
    return files


def main() -> int:
    errors: list[str] = []

    if canonical_json_profile() != EXPECTED_PROFILE:
        errors.append(f"canonical profile {canonical_json_profile()!r} != {EXPECTED_PROFILE!r}")

    sample = {
        "string": "\u20ac$\u000f\nA'B\"\\\\\"/",
        "literals": [None, True, False],
        "integers": [0, -1, 9007199254740991],
    }
    expected_sample = (
        '{"integers":[0,-1,9007199254740991],"literals":[null,true,false],'
        '"string":"€$\\u000f\\nA\'B\\"\\\\\\\\\\"/"}'
    )
    if canonical_json_text(sample) != expected_sample:
        errors.append("restricted-JCS primitive/sample canonicalization vector drifted")

    if pretty_json_text({"b": 1, "a": 2}) != '{\n  "a": 2,\n  "b": 1\n}\n':
        errors.append("pretty JSON writer drifted; examples/validation receipts need deterministic sorted indentation")


    # RFC 8785 Section 3.2.3 key-order vector.  The assertion checks decoded
    # value order so the carriage-return key can stay escaped in source.  The
    # emoji key sorts before U+FB33 under UTF-16 code units, but after it under
    # Python/Unicode-code-point ordering.
    sort_vector = {
        "\u20ac": "Euro Sign",
        "\r": "Carriage Return",
        "\ufb33": "Hebrew Letter Dalet With Dagesh",
        "1": "One",
        "\U0001f600": "Emoji: Grinning Face",
        "\u0080": "Control",
        "\u00f6": "Latin Small Letter O With Diaeresis",
    }
    ordered_pairs = json.loads(canonical_json_text(sort_vector), object_pairs_hook=list)
    observed_order = [value for _key, value in ordered_pairs]
    expected_order = [
        "Carriage Return",
        "One",
        "Control",
        "Latin Small Letter O With Diaeresis",
        "Euro Sign",
        "Emoji: Grinning Face",
        "Hebrew Letter Dalet With Dagesh",
    ]
    if observed_order != expected_order:
        errors.append(f"UTF-16 member ordering drifted: {observed_order!r}")

    _expect_raises("duplicate object member", lambda: load_json_strict_text('{"a":1,"a":2}'), errors)
    _expect_raises("NaN token", lambda: load_json_strict_text('{"n":NaN}'), errors)
    _expect_raises("JSON float", lambda: canonical_json_text({"n": 0.0}), errors)
    _expect_raises("unsafe integer", lambda: canonical_json_text({"n": 9007199254740992}), errors)
    _expect_raises("non-string object member", lambda: canonical_json_text({1: "bad"}), errors)
    _expect_raises("lone surrogate", lambda: canonical_json_text({"\ud800": "bad"}), errors)

    boot_contract = (ROOT / "tools" / "check_boot_contract.py").read_text(encoding="utf-8", errors="replace")
    if "from cube_digest_lib import canonical_digest" not in boot_contract:
        errors.append("tools/check_boot_contract.py must use cube_digest_lib.canonical_digest")
    microvm_contract = (ROOT / "tools" / "check_microvm_example_plan_digests.py").read_text(
        encoding="utf-8", errors="replace"
    )
    if "from cube_digest_lib import canonical_digest" not in microvm_contract:
        errors.append("tools/check_microvm_example_plan_digests.py must use cube_digest_lib.canonical_digest")

    refactored_digest_checkers = [
        "tools/check_release_transparency_contract.py",
        "tools/check_keyless_identity_contract.py",
        "tools/check_content_origin_contract.py",
        "tools/check_supplychain_verification_contract.py",
        "tools/check_time_sync_bundle_contract.py",
        "tools/check_attestation_admission_contract.py",
        "tools/check_attestation_action_verification_contract.py",
        "tools/check_reset_contract.py",
        "tools/check_boot_bless_bundle_contract.py",
        "tools/check_breakglass_bundle_contract.py",
        "tools/check_support_session_bundle_contract.py",
        "tools/check_packet_capture_normalization_contract.py",
        "tools/check_packet_capture_summary_contract.py",
        "tools/check_role_binding_policy_consumption_digest_contract.py",
        "tools/check_hw_support_qualification_profile_contract.py",
        "tools/check_store_gc_contract.py",
        "tools/check_removable_media_local_ingest_firstcut.py",
    ]
    for rel in refactored_digest_checkers:
        checker_text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        if not (
            "from cube_digest_lib import canonical_digest" in checker_text
            or "from cube_digest_lib import file_json_digest" in checker_text
            or "file_json_digest," in checker_text
        ):
            errors.append(f"{rel} must use cube_digest_lib canonical digest helpers")


    time_hash_bound_examples = [
        "spec/examples/time.sync.snapshot.json",
        "spec/examples/time.sync.receipt.json",
        "spec/examples/time.event.json",
    ]
    for rel in time_hash_bound_examples:
        try:
            canonical_json_text(load_json_strict_text((ROOT / rel).read_text(encoding="utf-8")))
        except CanonicalJsonError as exc:
            errors.append(f"{rel} must be admissible to the restricted-JCS helper: {exc}")

    time_schema_text = "\n".join(
        (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for rel in (
            "spec/time.sync.snapshot.schema.json",
            "spec/time.sync.receipt.schema.json",
            "spec/time.event.schema.json",
        )
    )
    for field in ("offset_ms", "uncertainty_ms", "rtt_ms", "delta_ms", "step_ms", "last_step_ms"):
        if f'"{field}"' in time_schema_text and f'"description": "{field}' not in time_schema_text and "decimal string" not in time_schema_text:
            errors.append(f"time schema field {field} must document decimal-string canonicalization posture")
    if '"type": "number"' in time_schema_text:
        errors.append("hash-bound time evidence schemas must not use JSON number fields; use decimal strings")

    legacy_files = _legacy_helper_files()
    if len(legacy_files) > MAX_LEGACY_LOCAL_DIGEST_HELPERS:
        errors.append(
            f"legacy local digest helpers increased to {len(legacy_files)}; "
            f"ratchet allows at most {MAX_LEGACY_LOCAL_DIGEST_HELPERS}"
        )

    if errors:
        print("Canonical JSON digest contract FAILED")
        for error in errors:
            print("-", error)
        if legacy_files:
            print("Legacy local digest-helper files still to refactor:")
            for rel in legacy_files[:20]:
                print("-", rel)
            if len(legacy_files) > 20:
                print(f"- ... {len(legacy_files) - 20} more")
        return 1

    print(
        "Canonical JSON digest contract OK "
        f"({EXPECTED_PROFILE}; {len(legacy_files)} legacy local helper files remain under ratchet)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

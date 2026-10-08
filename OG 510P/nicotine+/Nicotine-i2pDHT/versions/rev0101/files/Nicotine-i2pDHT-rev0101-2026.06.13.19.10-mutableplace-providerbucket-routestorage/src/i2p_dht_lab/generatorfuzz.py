"""Generated deterministic fuzz corpus for parser/wire/shadow boundaries.

``fuzzwire.py`` pins hand-written malformed fixtures.  This module grows that
surface without pretending to be a production fuzzer: accepted seed cases are
systematically mutated into rejection cases, then the same tiny harness checks
that parser, wire, and shadow validators still reject them.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .fuzzwire import FuzzCase, FuzzExpectation, FuzzRunReport, FuzzSurfaceKind, run_fuzz_wire_cases
from .ids import DOMAIN, sha256

GENERATOR_FUZZ_DOMAIN = DOMAIN + b":generator-fuzz-v1:"


class GeneratedMutationKind(str, Enum):
    PARSE_TRAILING_DATA = "parse_trailing_data"
    PARSE_DUPLICATE_KEY = "parse_duplicate_key"
    PARSE_DEPTH_BOMB = "parse_depth_bomb"
    WIRE_PAYLOAD_APPEND = "wire_payload_append"
    WIRE_PAYLOAD_TRUNCATE = "wire_payload_truncate"
    SHADOW_EXPECTED_DIGEST_DRIFT = "shadow_expected_digest_drift"


@dataclass(frozen=True)
class GeneratedFuzzCase:
    mutation_kind: GeneratedMutationKind
    parent_case_digest: bytes
    case: FuzzCase

    @property
    def digest(self) -> bytes:
        return sha256(GENERATOR_FUZZ_DOMAIN + b":case:" + bencode({
            b"mutation": self.mutation_kind.value,
            b"parent": self.parent_case_digest,
            b"case": self.case.case_digest,
        }))


@dataclass(frozen=True)
class GeneratedFuzzCorpus:
    seed_count: int
    generated_cases: tuple[GeneratedFuzzCase, ...]
    corpus_digest: bytes

    @property
    def case_count(self) -> int:
        return len(self.generated_cases)

    @property
    def fuzz_cases(self) -> tuple[FuzzCase, ...]:
        return tuple(item.case for item in self.generated_cases)


@dataclass(frozen=True)
class GeneratedFuzzReport:
    corpus: GeneratedFuzzCorpus
    run: FuzzRunReport
    rejected_generated_cases: int
    report_digest: bytes

    @property
    def passed(self) -> bool:
        return self.run.passed and self.rejected_generated_cases == self.corpus.case_count


def _depth_bomb(depth: int = 20) -> bytes:
    payload = b"1:x"
    for _ in range(depth):
        payload = b"l" + payload
    return payload + (b"e" * depth)


def generate_rejection_corpus(seed_cases: Iterable[FuzzCase]) -> GeneratedFuzzCorpus:
    generated: list[GeneratedFuzzCase] = []
    seeds = tuple(seed_cases)
    for case in seeds:
        if case.expectation is not FuzzExpectation.ACCEPT:
            continue
        if case.surface is FuzzSurfaceKind.PARSE_GUARD:
            generated.append(GeneratedFuzzCase(
                GeneratedMutationKind.PARSE_TRAILING_DATA,
                case.case_digest,
                FuzzCase(f"{case.label}-generated-trailing", FuzzSurfaceKind.PARSE_GUARD, case.payload + b"junk", FuzzExpectation.REJECT, "trailing"),
            ))
            generated.append(GeneratedFuzzCase(
                GeneratedMutationKind.PARSE_DUPLICATE_KEY,
                case.case_digest,
                FuzzCase(f"{case.label}-generated-dupkey", FuzzSurfaceKind.PARSE_GUARD, b"d1:a1:x1:a1:ye", FuzzExpectation.REJECT, "duplicate"),
            ))
            generated.append(GeneratedFuzzCase(
                GeneratedMutationKind.PARSE_DEPTH_BOMB,
                case.case_digest,
                FuzzCase(f"{case.label}-generated-depth", FuzzSurfaceKind.PARSE_GUARD, _depth_bomb(), FuzzExpectation.REJECT, "depth"),
            ))
        elif case.surface is FuzzSurfaceKind.WIRE_FRAME:
            generated.append(GeneratedFuzzCase(
                GeneratedMutationKind.WIRE_PAYLOAD_APPEND,
                case.case_digest,
                FuzzCase(f"{case.label}-generated-append", FuzzSurfaceKind.WIRE_FRAME, case.payload + b"!", FuzzExpectation.REJECT, "payload", frame=case.frame, now=case.now),
            ))
            truncated = case.payload[:-1] if case.payload else b"x"
            generated.append(GeneratedFuzzCase(
                GeneratedMutationKind.WIRE_PAYLOAD_TRUNCATE,
                case.case_digest,
                FuzzCase(f"{case.label}-generated-truncate", FuzzSurfaceKind.WIRE_FRAME, truncated, FuzzExpectation.REJECT, "payload", frame=case.frame, now=case.now),
            ))
        elif case.surface is FuzzSurfaceKind.SHADOW_FRAME:
            generated.append(GeneratedFuzzCase(
                GeneratedMutationKind.SHADOW_EXPECTED_DIGEST_DRIFT,
                case.case_digest,
                FuzzCase(f"{case.label}-generated-drift", FuzzSurfaceKind.SHADOW_FRAME, case.payload, FuzzExpectation.REJECT, "digest", frame=case.frame, now=case.now, expected_report_digest=sha256(GENERATOR_FUZZ_DOMAIN + case.case_digest)),
            ))
    digest = sha256(GENERATOR_FUZZ_DOMAIN + b":corpus:" + bencode({
        b"seed_count": len(seeds),
        b"generated": [item.digest for item in generated],
    }))
    return GeneratedFuzzCorpus(len(seeds), tuple(generated), digest)


def run_generated_fuzz_corpus(corpus: GeneratedFuzzCorpus) -> GeneratedFuzzReport:
    run = run_fuzz_wire_cases(corpus.fuzz_cases)
    rejected = sum(1 for item in run.results if not item.observed_accept)
    digest = sha256(GENERATOR_FUZZ_DOMAIN + b":report:" + bencode({
        b"corpus": corpus.corpus_digest,
        b"run": run.report_digest,
        b"rejected": rejected,
        b"failed": run.failed_cases,
    }))
    return GeneratedFuzzReport(corpus, run, rejected, digest)

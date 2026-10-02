#!/usr/bin/env python3
"""Canonical construction and verification for IoTox Ratox R7 evidence.

The module intentionally uses only Python's standard library plus the same
libsodium runtime already required by IoTox. Durations are always derived from
same-clock timestamps. No controller timestamp is subtracted from a host
timestamp.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import hashlib
import io
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Iterator, Sequence, TextIO

EVIDENCE_SCHEMA = "iotox-ratox-r7-samples-v2"
SCHEDULE_SCHEMA = "iotox-ratox-r7-schedule-v1"
MEASUREMENTS_SCHEMA = "iotox-ratox-r7-measurements-v1"
ATTESTATION_DOMAIN = "iotox-ratox-r7-attestation-v1"
RANDOMIZATION_ALGORITHM = "sha256-counter-fisher-yates-run-bound-v2"
ATTESTATION_SCHEME = "ed25519-ephemeral-capture-v1"
SERVICE_PATH = "ratox-v1-complete-pty"
TOXCORE_VERSION = "0.2.23"
REQUIRED_ROUTES = ("direct-udp", "forced-tcp")
REQUIRED_BULK_STREAMS = (0, 1, 8, 16, 32, 64)
SCHEDULE_BLOCK_SIZE = len(REQUIRED_ROUTES) * len(REQUIRED_BULK_STREAMS)
MINIMUM_SAMPLES_PER_CELL = 1000
MAXIMUM_SAMPLES_PER_CELL = 10_000
MAXIMUM_LINE_BYTES = 4096
MAXIMUM_INPUT_BYTES = 64 * 1024 * 1024
MAXIMUM_METADATA_FIELDS = 64
MAXIMUM_INPUT_LINES = (
    SCHEDULE_BLOCK_SIZE * MAXIMUM_SAMPLES_PER_CELL
    + MAXIMUM_METADATA_FIELDS
    + 256
)
DIRECT_P95_LIMIT_US = 50_000
DIRECT_P99_LIMIT_US = 100_000
MISS_LIMIT_US = 250_000
OWNER_P99_STRICT_LIMIT_US = 2000
UINT64_MAX = (1 << 64) - 1
HEX_32 = re.compile(r"[0-9a-f]{32}\Z")
HEX_40 = re.compile(r"[0-9a-f]{40}\Z")
HEX_64 = re.compile(r"[0-9a-f]{64}\Z")
HEX_128 = re.compile(r"[0-9a-f]{128}\Z")
UUID_LOWER = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)
METADATA_KEY = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")

UNSIGNED_METADATA_KEYS = frozenset(
    {
        "attestation-scheme",
        "bulk-evidence-bytes",
        "bulk-evidence-sha256",
        "bulk-load-semantics",
        "capture-role-count",
        "controller-boot-id",
        "controller-capture-key",
        "controller-clock",
        "cross-host-clock-comparison",
        "distinct-kernel-boots",
        "host-boot-id",
        "host-capture-key",
        "host-clock",
        "physical-topology",
        "provenance-artifacts-bound",
        "randomization-algorithm",
        "randomized",
        "route-evidence-bytes",
        "route-evidence-sha256",
        "route-topology",
        "run-id",
        "samples-per-cell",
        "samples-sha256",
        "schedule-block-size",
        "schedule-seed",
        "schedule-sha256",
        "schema",
        "service-path",
        "source-commit",
        "toxcore-version",
    }
)
SIGNATURE_METADATA_KEYS = frozenset(
    {"controller-signature", "host-signature"}
)
FINAL_METADATA_KEYS = UNSIGNED_METADATA_KEYS | SIGNATURE_METADATA_KEYS

SCHEDULE_METADATA_KEYS = frozenset(
    {
        "randomization-algorithm",
        "run-id",
        "samples-per-cell",
        "schedule-block-size",
        "schedule-seed",
        "schema",
    }
)
MEASUREMENT_METADATA_KEYS = frozenset({"run-id", "schema"})

SAMPLE_FIELD_COUNT = 24
MEASUREMENT_FIELD_COUNT = 22
TRIAL_FIELD_COUNT = 5


class InputError(ValueError):
    """Input is malformed, incomplete, noncanonical, or unsafe to consume."""


@dataclass(frozen=True)
class Trial:
    ordinal: int
    route: str
    bulk_streams: int
    token: str

    def line(self) -> str:
        return (
            f"trial\t{self.ordinal}\t{self.route}\t{self.bulk_streams}\t"
            f"{self.token}\n"
        )


@dataclass(frozen=True)
class Measurement:
    ordinal: int
    token: str
    controller_input_us: int
    controller_output_us: int
    controller_render_us: int
    host_receive_us: int
    host_input_commit_us: int
    host_output_us: int
    owner_queue_wait_us: int
    input_commits: int
    render_copies: int
    complete: int
    session_id: str
    input_message_id: int
    input_sequence: int
    input_next_sequence: int
    output_sequence: int
    output_next_sequence: int
    host_stage_event_ordinal: int
    host_commit_event_ordinal: int
    host_output_event_ordinal: int


@dataclass(frozen=True)
class Sample:
    route: str
    bulk_streams: int
    ordinal: int
    token: str
    controller_input_us: int
    controller_output_us: int
    controller_render_us: int
    host_receive_us: int
    host_input_commit_us: int
    host_output_us: int
    owner_queue_wait_us: int
    input_commits: int
    render_copies: int
    complete: int
    session_id: str
    input_message_id: int
    input_sequence: int
    input_next_sequence: int
    output_sequence: int
    output_next_sequence: int
    host_stage_event_ordinal: int
    host_commit_event_ordinal: int
    host_output_event_ordinal: int

    @property
    def end_to_end_us(self) -> int:
        return self.controller_render_us - self.controller_input_us

    @property
    def host_receive_to_pty_us(self) -> int:
        return self.host_input_commit_us - self.host_receive_us

    @property
    def host_pty_to_output_us(self) -> int:
        return self.host_output_us - self.host_input_commit_us

    @property
    def controller_output_to_render_us(self) -> int:
        return self.controller_render_us - self.controller_output_us

    def line(self) -> str:
        fields = (
            "sample",
            self.route,
            str(self.bulk_streams),
            str(self.ordinal),
            self.token,
            str(self.controller_input_us),
            str(self.controller_output_us),
            str(self.controller_render_us),
            str(self.host_receive_us),
            str(self.host_input_commit_us),
            str(self.host_output_us),
            str(self.owner_queue_wait_us),
            str(self.input_commits),
            str(self.render_copies),
            str(self.complete),
            self.session_id,
            str(self.input_message_id),
            str(self.input_sequence),
            str(self.input_next_sequence),
            str(self.output_sequence),
            str(self.output_next_sequence),
            str(self.host_stage_event_ordinal),
            str(self.host_commit_event_ordinal),
            str(self.host_output_event_ordinal),
        )
        return "\t".join(fields) + "\n"


@dataclass(frozen=True)
class CellReport:
    route: str
    bulk_streams: int
    samples: int
    end_to_end_p50_us: int
    end_to_end_p95_us: int
    end_to_end_p99_us: int
    host_receive_to_pty_p50_us: int
    host_receive_to_pty_p95_us: int
    host_receive_to_pty_p99_us: int
    host_pty_to_output_p50_us: int
    host_pty_to_output_p95_us: int
    host_pty_to_output_p99_us: int
    controller_output_to_render_p50_us: int
    controller_output_to_render_p95_us: int
    controller_output_to_render_p99_us: int
    owner_queue_wait_p50_us: int
    owner_queue_wait_p95_us: int
    owner_queue_wait_p99_us: int
    misses_at_or_above_250000_us: int
    semantic_failures: int
    passed: bool
    failures: tuple[str, ...]


@dataclass(frozen=True)
class QualificationReport:
    passed: bool
    schema: str
    metadata: dict[str, str]
    thresholds: dict[str, int | str]
    total_samples: int
    cells: tuple[CellReport, ...]
    failures: tuple[str, ...]


@dataclass(frozen=True)
class _RegularFileObservation:
    payload: bytes
    device: int
    inode: int


@dataclass(frozen=True)
class _EvidenceArtifact:
    sha256: str
    size: int
    device: int
    inode: int


class _HashRandom:
    """Deterministic SHA-256 counter stream with unbiased randbelow()."""

    def __init__(self, seed_hex: str) -> None:
        self._seed = bytes.fromhex(seed_hex)
        self._counter = 0
        self._buffer = bytearray()

    def _fill(self, count: int) -> None:
        while len(self._buffer) < count:
            if self._counter > UINT64_MAX:
                raise InputError("schedule PRNG counter exhausted")
            block = hashlib.sha256(
                b"iotox-ratox-r7-schedule-prng-v1\0"
                + self._seed
                + self._counter.to_bytes(8, "big")
            ).digest()
            self._buffer.extend(block)
            self._counter += 1

    def randbelow(self, bound: int) -> int:
        if bound <= 0 or bound > UINT64_MAX:
            raise ValueError("randbelow bound is outside uint64")
        cutoff = (1 << 64) - ((1 << 64) % bound)
        while True:
            self._fill(8)
            candidate = int.from_bytes(self._buffer[:8], "big")
            del self._buffer[:8]
            if candidate < cutoff:
                return candidate % bound


def _canonical_uint(text: str, field: str, *, nonzero: bool = False) -> int:
    if not text or not text.isascii() or not text.isdecimal():
        raise InputError(f"{field} must be a canonical unsigned decimal")
    if len(text) > 1 and text[0] == "0":
        raise InputError(f"{field} must not contain leading zeroes")
    value = int(text, 10)
    if value > UINT64_MAX:
        raise InputError(f"{field} exceeds uint64")
    if nonzero and value == 0:
        raise InputError(f"{field} must be nonzero")
    return value


def _require_pattern(value: str, pattern: re.Pattern[str], field: str) -> str:
    if pattern.fullmatch(value) is None:
        raise InputError(f"{field} is not canonical")
    return value


def _check_ascii_printable(text: str, field: str) -> None:
    if not text.isascii():
        raise InputError(f"{field} must be ASCII")
    if any(ord(character) < 0x20 or ord(character) > 0x7E for character in text):
        raise InputError(f"{field} contains a non-printable byte")


def _iter_canonical_lines(stream: TextIO) -> Iterator[tuple[int, str]]:
    total_bytes = 0
    for line_number, raw_line in enumerate(stream, start=1):
        if line_number > MAXIMUM_INPUT_LINES:
            raise InputError("input exceeds the maximum line count")
        if "\r" in raw_line:
            raise InputError(f"line {line_number} contains a carriage return")
        if not raw_line.isascii():
            raise InputError(f"line {line_number} must be ASCII")
        total_bytes += len(raw_line)
        if total_bytes > MAXIMUM_INPUT_BYTES:
            raise InputError("input exceeds the maximum byte count")
        if len(raw_line) > MAXIMUM_LINE_BYTES:
            raise InputError(
                f"line {line_number} exceeds {MAXIMUM_LINE_BYTES} bytes"
            )
        if not raw_line.endswith("\n"):
            raise InputError(f"line {line_number} is missing its final newline")
        line = raw_line[:-1]
        if not line:
            raise InputError(f"line {line_number} is empty")
        yield line_number, line


def _parse_metadata_line(
    line_number: int,
    fields: list[str],
    metadata: dict[str, str],
    *,
    previous_key: str | None,
) -> str:
    if len(fields) != 2:
        raise InputError(
            f"line {line_number} metadata must contain exactly two fields"
        )
    key, value = fields
    if METADATA_KEY.fullmatch(key) is None:
        raise InputError(f"line {line_number} has a noncanonical metadata key")
    _check_ascii_printable(value, f"metadata {key}")
    if key in metadata:
        raise InputError(f"metadata key {key!r} is duplicated")
    if len(metadata) >= MAXIMUM_METADATA_FIELDS:
        raise InputError("metadata field count exceeds the configured bound")
    if previous_key is not None and key <= previous_key:
        raise InputError("metadata keys must be strictly sorted")
    metadata[key] = value
    return key


def trial_token(run_id: str, ordinal: int, route: str, bulk_streams: int) -> str:
    payload = (
        "iotox-ratox-r7-trial-v1\0"
        f"run-id={run_id}\n"
        f"ordinal={ordinal}\n"
        f"route={route}\n"
        f"bulk-streams={bulk_streams}\n"
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def generate_trials(
    run_id: str, schedule_seed: str, samples_per_cell: int
) -> list[Trial]:
    _require_pattern(run_id, HEX_32, "run-id")
    _require_pattern(schedule_seed, HEX_64, "schedule-seed")
    if not MINIMUM_SAMPLES_PER_CELL <= samples_per_cell <= MAXIMUM_SAMPLES_PER_CELL:
        raise InputError(
            f"samples-per-cell must be in {MINIMUM_SAMPLES_PER_CELL}.."
            f"{MAXIMUM_SAMPLES_PER_CELL}"
        )
    cells = [
        (route, bulk)
        for route in REQUIRED_ROUTES
        for bulk in REQUIRED_BULK_STREAMS
    ]
    # Bind the pseudorandom stream to both public inputs. Reusing a seed for a
    # different run cannot accidentally recreate the same matrix order.
    stream_key = hashlib.sha256(
        b"iotox-ratox-r7-schedule-stream-v2\0"
        + bytes.fromhex(run_id)
        + bytes.fromhex(schedule_seed)
    ).hexdigest()
    random = _HashRandom(stream_key)
    trials: list[Trial] = []
    ordinal = 1
    for _ in range(samples_per_cell):
        block = list(cells)
        for index in range(len(block) - 1, 0, -1):
            swap = random.randbelow(index + 1)
            block[index], block[swap] = block[swap], block[index]
        for route, bulk in block:
            trials.append(
                Trial(
                    ordinal=ordinal,
                    route=route,
                    bulk_streams=bulk,
                    token=trial_token(run_id, ordinal, route, bulk),
                )
            )
            ordinal += 1
    return trials


def schedule_metadata(
    run_id: str, schedule_seed: str, samples_per_cell: int
) -> dict[str, str]:
    return {
        "randomization-algorithm": RANDOMIZATION_ALGORITHM,
        "run-id": run_id,
        "samples-per-cell": str(samples_per_cell),
        "schedule-block-size": str(SCHEDULE_BLOCK_SIZE),
        "schedule-seed": schedule_seed,
        "schema": SCHEDULE_SCHEMA,
    }


def render_schedule(
    run_id: str, schedule_seed: str, samples_per_cell: int
) -> str:
    metadata = schedule_metadata(run_id, schedule_seed, samples_per_cell)
    trials = generate_trials(run_id, schedule_seed, samples_per_cell)
    return "".join(
        [*(f"{key}\t{value}\n" for key, value in sorted(metadata.items())),
         *(trial.line() for trial in trials)]
    )


def parse_schedule(stream: TextIO) -> tuple[dict[str, str], list[Trial]]:
    metadata: dict[str, str] = {}
    trials: list[Trial] = []
    previous_key: str | None = None
    saw_trials = False
    for line_number, line in _iter_canonical_lines(stream):
        fields = line.split("\t")
        if fields[0] != "trial":
            if saw_trials:
                raise InputError("schedule metadata may not follow trial rows")
            previous_key = _parse_metadata_line(
                line_number, fields, metadata, previous_key=previous_key
            )
            continue
        saw_trials = True
        if len(fields) != TRIAL_FIELD_COUNT:
            raise InputError(
                f"line {line_number} trial must contain exactly "
                f"{TRIAL_FIELD_COUNT} fields"
            )
        ordinal = _canonical_uint(fields[1], "trial ordinal", nonzero=True)
        route = fields[2]
        if route not in REQUIRED_ROUTES:
            raise InputError(f"line {line_number} has unsupported route {route!r}")
        bulk = _canonical_uint(fields[3], "trial bulk_streams")
        if bulk not in REQUIRED_BULK_STREAMS:
            raise InputError(
                f"line {line_number} has unsupported bulk_streams={bulk}"
            )
        token = _require_pattern(fields[4], HEX_64, "trial token")
        if ordinal != len(trials) + 1:
            raise InputError("trial ordinals must be ordered, contiguous, and start at 1")
        trials.append(Trial(ordinal, route, bulk, token))

    if set(metadata) != SCHEDULE_METADATA_KEYS:
        missing = sorted(SCHEDULE_METADATA_KEYS - set(metadata))
        extra = sorted(set(metadata) - SCHEDULE_METADATA_KEYS)
        raise InputError(
            f"schedule metadata keys are incomplete or unsupported; "
            f"missing={missing} extra={extra}"
        )
    if metadata["schema"] != SCHEDULE_SCHEMA:
        raise InputError(f"schedule schema must be {SCHEDULE_SCHEMA!r}")
    if metadata["randomization-algorithm"] != RANDOMIZATION_ALGORITHM:
        raise InputError("schedule randomization algorithm is unsupported")
    if metadata["schedule-block-size"] != str(SCHEDULE_BLOCK_SIZE):
        raise InputError("schedule block size is not canonical")
    run_id = _require_pattern(metadata["run-id"], HEX_32, "run-id")
    seed = _require_pattern(metadata["schedule-seed"], HEX_64, "schedule-seed")
    per_cell = _canonical_uint(
        metadata["samples-per-cell"], "samples-per-cell", nonzero=True
    )
    expected = generate_trials(run_id, seed, per_cell)
    if trials != expected:
        raise InputError("schedule trials do not match the deterministic balanced schedule")
    return metadata, trials


def parse_measurements(
    stream: TextIO,
) -> tuple[dict[str, str], list[Measurement]]:
    metadata: dict[str, str] = {}
    measurements: list[Measurement] = []
    previous_key: str | None = None
    saw_rows = False
    for line_number, line in _iter_canonical_lines(stream):
        fields = line.split("\t")
        if fields[0] != "measurement":
            if saw_rows:
                raise InputError("measurement metadata may not follow rows")
            previous_key = _parse_metadata_line(
                line_number, fields, metadata, previous_key=previous_key
            )
            continue
        saw_rows = True
        if len(fields) != MEASUREMENT_FIELD_COUNT:
            raise InputError(
                f"line {line_number} measurement must contain exactly "
                f"{MEASUREMENT_FIELD_COUNT} fields"
            )
        measurement = Measurement(
            ordinal=_canonical_uint(fields[1], "measurement ordinal", nonzero=True),
            token=_require_pattern(fields[2], HEX_64, "measurement token"),
            controller_input_us=_canonical_uint(
                fields[3], "controller_input_us", nonzero=True
            ),
            controller_output_us=_canonical_uint(
                fields[4], "controller_output_us", nonzero=True
            ),
            controller_render_us=_canonical_uint(
                fields[5], "controller_render_us", nonzero=True
            ),
            host_receive_us=_canonical_uint(fields[6], "host_receive_us", nonzero=True),
            host_input_commit_us=_canonical_uint(
                fields[7], "host_input_commit_us", nonzero=True
            ),
            host_output_us=_canonical_uint(fields[8], "host_output_us", nonzero=True),
            owner_queue_wait_us=_canonical_uint(fields[9], "owner_queue_wait_us"),
            input_commits=_canonical_uint(fields[10], "input_commits"),
            render_copies=_canonical_uint(fields[11], "render_copies"),
            complete=_canonical_uint(fields[12], "complete"),
            session_id=_require_pattern(fields[13], HEX_64, "session_id"),
            input_message_id=_canonical_uint(
                fields[14], "input_message_id", nonzero=True
            ),
            input_sequence=_canonical_uint(fields[15], "input_sequence", nonzero=True),
            input_next_sequence=_canonical_uint(
                fields[16], "input_next_sequence", nonzero=True
            ),
            output_sequence=_canonical_uint(fields[17], "output_sequence", nonzero=True),
            output_next_sequence=_canonical_uint(
                fields[18], "output_next_sequence", nonzero=True
            ),
            host_stage_event_ordinal=_canonical_uint(
                fields[19], "host_stage_event_ordinal", nonzero=True
            ),
            host_commit_event_ordinal=_canonical_uint(
                fields[20], "host_commit_event_ordinal", nonzero=True
            ),
            host_output_event_ordinal=_canonical_uint(
                fields[21], "host_output_event_ordinal", nonzero=True
            ),
        )
        if measurement.ordinal != len(measurements) + 1:
            raise InputError(
                "measurement ordinals must be ordered, contiguous, and start at 1"
            )
        measurements.append(measurement)

    if set(metadata) != MEASUREMENT_METADATA_KEYS:
        missing = sorted(MEASUREMENT_METADATA_KEYS - set(metadata))
        extra = sorted(set(metadata) - MEASUREMENT_METADATA_KEYS)
        raise InputError(
            f"measurement metadata keys are incomplete or unsupported; "
            f"missing={missing} extra={extra}"
        )
    if metadata["schema"] != MEASUREMENTS_SCHEMA:
        raise InputError(f"measurement schema must be {MEASUREMENTS_SCHEMA!r}")
    _require_pattern(metadata["run-id"], HEX_32, "run-id")
    if not measurements:
        raise InputError("measurement input contains no rows")
    return metadata, measurements


def _validate_sample_shape(samples: Sequence[Sample]) -> None:
    if not samples:
        raise InputError("evidence contains no samples")
    seen_message_ids: set[tuple[str, int]] = set()
    seen_input_spans: set[tuple[str, int, int]] = set()
    seen_output_spans: set[tuple[str, int, int]] = set()
    seen_host_events: set[int] = set()
    previous_controller_input = 0
    previous_controller_render = 0
    previous_host_receive = 0
    previous_host_output = 0
    previous_host_event = 0
    session_input_next: dict[str, int] = {}
    session_output_next: dict[str, int] = {}

    for expected_ordinal, sample in enumerate(samples, start=1):
        if sample.ordinal != expected_ordinal:
            raise InputError("sample ordinals must be ordered, contiguous, and start at 1")
        if sample.controller_input_us <= previous_controller_input:
            raise InputError("controller input timestamps must be strictly increasing")
        if sample.controller_render_us < previous_controller_render:
            raise InputError("controller render timestamps must not move backwards")
        if sample.controller_input_us < previous_controller_render:
            raise InputError("controller trials must not overlap")
        previous_controller_input = sample.controller_input_us
        previous_controller_render = sample.controller_render_us
        if sample.host_receive_us < previous_host_receive:
            raise InputError("host receive timestamps must not move backwards")
        if sample.host_output_us < previous_host_output:
            raise InputError("host output timestamps must not move backwards")
        if sample.host_receive_us < previous_host_output:
            raise InputError("host trials must not overlap")
        if sample.host_stage_event_ordinal <= previous_host_event:
            raise InputError("host event ordinals must be globally increasing")
        previous_host_receive = sample.host_receive_us
        previous_host_output = sample.host_output_us
        previous_host_event = sample.host_output_event_ordinal
        if not (
            sample.controller_input_us
            < sample.controller_output_us
            <= sample.controller_render_us
        ):
            raise InputError(
                f"sample ordinal {sample.ordinal} has invalid controller-local timestamp order"
            )
        if not (
            sample.host_receive_us
            <= sample.host_input_commit_us
            <= sample.host_output_us
        ):
            raise InputError(
                f"sample ordinal {sample.ordinal} has invalid host-local timestamp order"
            )
        if sample.input_next_sequence != sample.input_sequence + 1:
            raise InputError(
                f"sample ordinal {sample.ordinal} is not one exact keypress byte"
            )
        if sample.output_next_sequence <= sample.output_sequence:
            raise InputError(
                f"sample ordinal {sample.ordinal} has an empty output span"
            )
        if not (
            sample.host_stage_event_ordinal
            < sample.host_commit_event_ordinal
            < sample.host_output_event_ordinal
        ):
            raise InputError(
                f"sample ordinal {sample.ordinal} has invalid host event order"
            )
        for event_ordinal in (
            sample.host_stage_event_ordinal,
            sample.host_commit_event_ordinal,
            sample.host_output_event_ordinal,
        ):
            if event_ordinal in seen_host_events:
                raise InputError(f"host event ordinal {event_ordinal} is reused")
            seen_host_events.add(event_ordinal)

        message_key = (sample.session_id, sample.input_message_id)
        input_key = (
            sample.session_id,
            sample.input_sequence,
            sample.input_next_sequence,
        )
        output_key = (
            sample.session_id,
            sample.output_sequence,
            sample.output_next_sequence,
        )
        if message_key in seen_message_ids:
            raise InputError("an input message ID is reused within one session")
        if input_key in seen_input_spans:
            raise InputError("an input byte span is reused")
        if output_key in seen_output_spans:
            raise InputError("an output byte span is reused")
        seen_message_ids.add(message_key)
        seen_input_spans.add(input_key)
        seen_output_spans.add(output_key)

        prior_input = session_input_next.get(sample.session_id)
        if prior_input is not None and sample.input_sequence < prior_input:
            raise InputError("session input sequence moved backwards or overlapped")
        prior_output = session_output_next.get(sample.session_id)
        if prior_output is not None and sample.output_sequence < prior_output:
            raise InputError("session output sequence moved backwards or overlapped")
        session_input_next[sample.session_id] = sample.input_next_sequence
        session_output_next[sample.session_id] = sample.output_next_sequence

        # Deliberately do not add or compare durations from the controller and
        # host clocks. Each duration is derived only within one clock domain;
        # cross-host decomposition remains diagnostic rather than arithmetic.


def _samples_digest(samples: Sequence[Sample]) -> str:
    digest = hashlib.sha256()
    for sample in samples:
        digest.update(sample.line().encode("ascii"))
    return digest.hexdigest()


def _schedule_digest(run_id: str, seed: str, samples_per_cell: int) -> str:
    return hashlib.sha256(
        render_schedule(run_id, seed, samples_per_cell).encode("ascii")
    ).hexdigest()


def _required_metadata_values(metadata: dict[str, str]) -> None:
    fixed = {
        "attestation-scheme": ATTESTATION_SCHEME,
        "bulk-load-semantics": "external-review-required",
        "capture-role-count": "2",
        "controller-clock": "steady",
        "cross-host-clock-comparison": "0",
        "distinct-kernel-boots": "1",
        "host-clock": "steady",
        "physical-topology": "external-review-required",
        "provenance-artifacts-bound": "1",
        "randomization-algorithm": RANDOMIZATION_ALGORITHM,
        "randomized": "1",
        "route-topology": "external-review-required",
        "schedule-block-size": str(SCHEDULE_BLOCK_SIZE),
        "schema": EVIDENCE_SCHEMA,
        "service-path": SERVICE_PATH,
        "toxcore-version": TOXCORE_VERSION,
    }
    for key, required in fixed.items():
        actual = metadata.get(key)
        if actual != required:
            raise InputError(
                f"metadata {key!r} must be {required!r}, got {actual!r}"
            )
    _require_pattern(metadata["run-id"], HEX_32, "run-id")
    _require_pattern(metadata["schedule-seed"], HEX_64, "schedule-seed")
    _require_pattern(metadata["source-commit"], HEX_40, "source-commit")
    for key in (
        "samples-sha256",
        "schedule-sha256",
        "route-evidence-sha256",
        "bulk-evidence-sha256",
        "controller-capture-key",
        "host-capture-key",
    ):
        _require_pattern(metadata[key], HEX_64, key)
    for key in ("controller-boot-id", "host-boot-id"):
        _require_pattern(metadata[key], UUID_LOWER, key)
    if metadata["controller-boot-id"] == metadata["host-boot-id"]:
        raise InputError("controller and host boot IDs must be distinct")
    if metadata["controller-capture-key"] == metadata["host-capture-key"]:
        raise InputError("controller and host capture keys must be distinct")
    samples_per_cell = _canonical_uint(
        metadata["samples-per-cell"], "samples-per-cell", nonzero=True
    )
    if not MINIMUM_SAMPLES_PER_CELL <= samples_per_cell <= MAXIMUM_SAMPLES_PER_CELL:
        raise InputError(
            f"samples-per-cell must be in {MINIMUM_SAMPLES_PER_CELL}.."
            f"{MAXIMUM_SAMPLES_PER_CELL}"
        )
    for key in ("route-evidence-bytes", "bulk-evidence-bytes"):
        artifact_bytes = _canonical_uint(metadata[key], key, nonzero=True)
        if artifact_bytes > MAXIMUM_INPUT_BYTES:
            raise InputError(f"metadata {key!r} exceeds the evidence byte bound")
    if metadata["route-evidence-sha256"] == metadata["bulk-evidence-sha256"]:
        raise InputError("route and bulk evidence must bind distinct byte content")


def parse_evidence(
    stream: TextIO, *, require_signatures: bool = True
) -> tuple[dict[str, str], list[Sample]]:
    metadata: dict[str, str] = {}
    samples: list[Sample] = []
    previous_key: str | None = None
    saw_samples = False
    for line_number, line in _iter_canonical_lines(stream):
        fields = line.split("\t")
        if fields[0] != "sample":
            if saw_samples:
                raise InputError("evidence metadata may not follow sample rows")
            previous_key = _parse_metadata_line(
                line_number, fields, metadata, previous_key=previous_key
            )
            continue
        saw_samples = True
        if len(fields) != SAMPLE_FIELD_COUNT:
            raise InputError(
                f"line {line_number} sample must contain exactly "
                f"{SAMPLE_FIELD_COUNT} fields"
            )
        route = fields[1]
        if route not in REQUIRED_ROUTES:
            raise InputError(f"line {line_number} has unsupported route {route!r}")
        bulk = _canonical_uint(fields[2], "bulk_streams")
        if bulk not in REQUIRED_BULK_STREAMS:
            raise InputError(
                f"line {line_number} has unsupported bulk_streams={bulk}"
            )
        sample = Sample(
            route=route,
            bulk_streams=bulk,
            ordinal=_canonical_uint(fields[3], "ordinal", nonzero=True),
            token=_require_pattern(fields[4], HEX_64, "sample token"),
            controller_input_us=_canonical_uint(
                fields[5], "controller_input_us", nonzero=True
            ),
            controller_output_us=_canonical_uint(
                fields[6], "controller_output_us", nonzero=True
            ),
            controller_render_us=_canonical_uint(
                fields[7], "controller_render_us", nonzero=True
            ),
            host_receive_us=_canonical_uint(fields[8], "host_receive_us", nonzero=True),
            host_input_commit_us=_canonical_uint(
                fields[9], "host_input_commit_us", nonzero=True
            ),
            host_output_us=_canonical_uint(fields[10], "host_output_us", nonzero=True),
            owner_queue_wait_us=_canonical_uint(fields[11], "owner_queue_wait_us"),
            input_commits=_canonical_uint(fields[12], "input_commits"),
            render_copies=_canonical_uint(fields[13], "render_copies"),
            complete=_canonical_uint(fields[14], "complete"),
            session_id=_require_pattern(fields[15], HEX_64, "session_id"),
            input_message_id=_canonical_uint(
                fields[16], "input_message_id", nonzero=True
            ),
            input_sequence=_canonical_uint(fields[17], "input_sequence", nonzero=True),
            input_next_sequence=_canonical_uint(
                fields[18], "input_next_sequence", nonzero=True
            ),
            output_sequence=_canonical_uint(fields[19], "output_sequence", nonzero=True),
            output_next_sequence=_canonical_uint(
                fields[20], "output_next_sequence", nonzero=True
            ),
            host_stage_event_ordinal=_canonical_uint(
                fields[21], "host_stage_event_ordinal", nonzero=True
            ),
            host_commit_event_ordinal=_canonical_uint(
                fields[22], "host_commit_event_ordinal", nonzero=True
            ),
            host_output_event_ordinal=_canonical_uint(
                fields[23], "host_output_event_ordinal", nonzero=True
            ),
        )
        samples.append(sample)

    expected_keys = FINAL_METADATA_KEYS if require_signatures else UNSIGNED_METADATA_KEYS
    if set(metadata) != expected_keys:
        missing = sorted(expected_keys - set(metadata))
        extra = sorted(set(metadata) - expected_keys)
        raise InputError(
            f"evidence metadata keys are incomplete or unsupported; "
            f"missing={missing} extra={extra}"
        )
    _required_metadata_values(metadata)
    if require_signatures:
        _require_pattern(
            metadata["controller-signature"], HEX_128, "controller-signature"
        )
        _require_pattern(metadata["host-signature"], HEX_128, "host-signature")
    _validate_sample_shape(samples)

    samples_per_cell = int(metadata["samples-per-cell"])
    expected_count = SCHEDULE_BLOCK_SIZE * samples_per_cell
    if len(samples) != expected_count:
        raise InputError(
            f"evidence contains {len(samples)} samples; expected exactly {expected_count}"
        )
    expected_trials = generate_trials(
        metadata["run-id"], metadata["schedule-seed"], samples_per_cell
    )
    for sample, trial in zip(samples, expected_trials, strict=True):
        if (
            sample.ordinal != trial.ordinal
            or sample.route != trial.route
            or sample.bulk_streams != trial.bulk_streams
            or sample.token != trial.token
        ):
            raise InputError(
                f"sample ordinal {sample.ordinal} contradicts the deterministic schedule"
            )
    if metadata["schedule-sha256"] != _schedule_digest(
        metadata["run-id"], metadata["schedule-seed"], samples_per_cell
    ):
        raise InputError("schedule-sha256 does not match the reconstructed schedule")
    if metadata["samples-sha256"] != _samples_digest(samples):
        raise InputError("samples-sha256 does not match the canonical sample rows")
    return metadata, samples


def render_unsigned_evidence(metadata: dict[str, str], samples: Sequence[Sample]) -> str:
    if set(metadata) != UNSIGNED_METADATA_KEYS:
        raise InputError("unsigned evidence metadata is not exact")
    return "".join(
        [*(f"{key}\t{value}\n" for key, value in sorted(metadata.items())),
         *(sample.line() for sample in samples)]
    )


def render_final_evidence(metadata: dict[str, str], samples: Sequence[Sample]) -> str:
    if set(metadata) != FINAL_METADATA_KEYS:
        raise InputError("final evidence metadata is not exact")
    return "".join(
        [*(f"{key}\t{value}\n" for key, value in sorted(metadata.items())),
         *(sample.line() for sample in samples)]
    )


def attestation_payload(metadata: dict[str, str], role: str) -> bytes:
    if role not in ("controller", "host"):
        raise InputError("attestation role must be controller or host")
    unsigned = {key: metadata[key] for key in sorted(UNSIGNED_METADATA_KEYS)}
    lines = [ATTESTATION_DOMAIN, f"role\t{role}"]
    lines.extend(f"{key}\t{value}" for key, value in unsigned.items())
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_attestation_payload(payload: bytes) -> tuple[str, dict[str, str]]:
    try:
        text = payload.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise InputError("attestation payload is not ASCII") from error
    if not text.endswith("\n") or "\r" in text:
        raise InputError("attestation payload is not canonical newline-delimited ASCII")
    lines = text.splitlines()
    if len(lines) != len(UNSIGNED_METADATA_KEYS) + 2:
        raise InputError("attestation payload has an invalid line count")
    if lines[0] != ATTESTATION_DOMAIN:
        raise InputError("attestation payload domain is invalid")
    role_fields = lines[1].split("\t")
    if len(role_fields) != 2 or role_fields[0] != "role" or role_fields[1] not in (
        "controller",
        "host",
    ):
        raise InputError("attestation payload role is invalid")
    role = role_fields[1]
    metadata: dict[str, str] = {}
    previous_key: str | None = None
    for line_number, line in enumerate(lines[2:], start=3):
        previous_key = _parse_metadata_line(
            line_number,
            line.split("\t"),
            metadata,
            previous_key=previous_key,
        )
    if set(metadata) != UNSIGNED_METADATA_KEYS:
        raise InputError("attestation payload metadata is not exact")
    _required_metadata_values(metadata)
    if payload != attestation_payload(metadata, role):
        raise InputError("attestation payload is not canonically rendered")
    return role, metadata


class Sodium:
    PUBLIC_KEY_BYTES = 32
    SECRET_KEY_BYTES = 64
    SEED_BYTES = 32
    SIGNATURE_BYTES = 64

    def __init__(self) -> None:
        library_name = os.environ.get("IOTOX_SODIUM_LIBRARY") or ctypes.util.find_library(
            "sodium"
        )
        if not library_name:
            raise InputError("libsodium is unavailable")
        try:
            self.library = ctypes.CDLL(library_name)
        except OSError as error:
            raise InputError(f"unable to load libsodium: {error}") from error
        self.library.sodium_init.argtypes = []
        self.library.sodium_init.restype = ctypes.c_int
        self.library.crypto_sign_seed_keypair.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        self.library.crypto_sign_seed_keypair.restype = ctypes.c_int
        self.library.crypto_sign_detached.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.c_void_p,
            ctypes.c_ulonglong,
            ctypes.c_void_p,
        ]
        self.library.crypto_sign_detached.restype = ctypes.c_int
        self.library.crypto_sign_verify_detached.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_ulonglong,
            ctypes.c_void_p,
        ]
        self.library.crypto_sign_verify_detached.restype = ctypes.c_int
        self.library.sodium_memzero.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        self.library.sodium_memzero.restype = None
        if self.library.sodium_init() < 0:
            raise InputError("libsodium initialization failed")

    @staticmethod
    def _array(data: bytes | bytearray, size: int, field: str) -> ctypes.Array:
        if len(data) != size:
            raise InputError(f"{field} must contain exactly {size} bytes")
        array_type = ctypes.c_ubyte * size
        return array_type.from_buffer_copy(data)

    def keypair_from_seed(self, seed: bytes | bytearray) -> tuple[bytes, bytearray]:
        seed_array = self._array(seed, self.SEED_BYTES, "signing seed")
        public = (ctypes.c_ubyte * self.PUBLIC_KEY_BYTES)()
        secret = (ctypes.c_ubyte * self.SECRET_KEY_BYTES)()
        try:
            if self.library.crypto_sign_seed_keypair(public, secret, seed_array) != 0:
                raise InputError("libsodium keypair generation failed")
            return bytes(public), bytearray(secret)
        finally:
            self.library.sodium_memzero(seed_array, self.SEED_BYTES)

    def sign(self, payload: bytes, secret_key: bytes | bytearray) -> bytes:
        secret = self._array(secret_key, self.SECRET_KEY_BYTES, "secret key")
        signature = (ctypes.c_ubyte * self.SIGNATURE_BYTES)()
        signature_length = ctypes.c_ulonglong(0)
        payload_buffer = ctypes.create_string_buffer(payload, len(payload))
        try:
            if self.library.crypto_sign_detached(
                signature,
                ctypes.byref(signature_length),
                payload_buffer,
                len(payload),
                secret,
            ) != 0 or signature_length.value != self.SIGNATURE_BYTES:
                raise InputError("libsodium detached signing failed")
            return bytes(signature)
        finally:
            self.library.sodium_memzero(secret, self.SECRET_KEY_BYTES)

    def verify(self, signature: bytes, payload: bytes, public_key: bytes) -> bool:
        signature_array = self._array(
            signature, self.SIGNATURE_BYTES, "signature"
        )
        public = self._array(public_key, self.PUBLIC_KEY_BYTES, "public key")
        payload_buffer = ctypes.create_string_buffer(payload, len(payload))
        return self.library.crypto_sign_verify_detached(
            signature_array, payload_buffer, len(payload), public
        ) == 0

    def wipe(self, value: bytearray) -> None:
        if not value:
            return
        view = (ctypes.c_ubyte * len(value)).from_buffer(value)
        self.library.sodium_memzero(view, len(value))


def verify_attestations(metadata: dict[str, str]) -> None:
    sodium = Sodium()
    for role in ("controller", "host"):
        signature = bytes.fromhex(metadata[f"{role}-signature"])
        public_key = bytes.fromhex(metadata[f"{role}-capture-key"])
        if not sodium.verify(signature, attestation_payload(metadata, role), public_key):
            raise InputError(f"{role} evidence attestation signature is invalid")


def nearest_rank(values: Iterable[int], percentage: int) -> int:
    ordered = sorted(values)
    if not ordered:
        raise InputError("cannot compute a percentile over an empty cell")
    if not 1 <= percentage <= 100:
        raise ValueError("percentage must be in 1..100")
    rank = (len(ordered) * percentage + 99) // 100
    return ordered[rank - 1]


def qualify(metadata: dict[str, str], samples: Sequence[Sample]) -> QualificationReport:
    grouped: dict[tuple[str, int], list[Sample]] = {
        (route, bulk): []
        for route in REQUIRED_ROUTES
        for bulk in REQUIRED_BULK_STREAMS
    }
    for sample in samples:
        grouped[(sample.route, sample.bulk_streams)].append(sample)

    cell_reports: list[CellReport] = []
    failures: list[str] = []
    for route in REQUIRED_ROUTES:
        for bulk_streams in REQUIRED_BULK_STREAMS:
            cell = grouped[(route, bulk_streams)]
            e2e_p50 = nearest_rank((sample.end_to_end_us for sample in cell), 50)
            e2e_p95 = nearest_rank((sample.end_to_end_us for sample in cell), 95)
            e2e_p99 = nearest_rank((sample.end_to_end_us for sample in cell), 99)
            host_receive_to_pty_p50 = nearest_rank(
                (sample.host_receive_to_pty_us for sample in cell), 50
            )
            host_receive_to_pty_p95 = nearest_rank(
                (sample.host_receive_to_pty_us for sample in cell), 95
            )
            host_receive_to_pty_p99 = nearest_rank(
                (sample.host_receive_to_pty_us for sample in cell), 99
            )
            host_pty_to_output_p50 = nearest_rank(
                (sample.host_pty_to_output_us for sample in cell), 50
            )
            host_pty_to_output_p95 = nearest_rank(
                (sample.host_pty_to_output_us for sample in cell), 95
            )
            host_pty_to_output_p99 = nearest_rank(
                (sample.host_pty_to_output_us for sample in cell), 99
            )
            controller_output_to_render_p50 = nearest_rank(
                (sample.controller_output_to_render_us for sample in cell), 50
            )
            controller_output_to_render_p95 = nearest_rank(
                (sample.controller_output_to_render_us for sample in cell), 95
            )
            controller_output_to_render_p99 = nearest_rank(
                (sample.controller_output_to_render_us for sample in cell), 99
            )
            owner_p50 = nearest_rank(
                (sample.owner_queue_wait_us for sample in cell), 50
            )
            owner_p95 = nearest_rank(
                (sample.owner_queue_wait_us for sample in cell), 95
            )
            owner_p99 = nearest_rank(
                (sample.owner_queue_wait_us for sample in cell), 99
            )
            misses = sum(sample.end_to_end_us >= MISS_LIMIT_US for sample in cell)
            semantic_failures = sum(
                sample.input_commits != 1
                or sample.render_copies != 1
                or sample.complete != 1
                for sample in cell
            )
            cell_failures: list[str] = []
            if owner_p99 >= OWNER_P99_STRICT_LIMIT_US:
                cell_failures.append(
                    f"owner p99 {owner_p99} us is not strictly below "
                    f"{OWNER_P99_STRICT_LIMIT_US} us"
                )
            if semantic_failures:
                cell_failures.append(
                    f"{semantic_failures} samples violate one-commit/one-render/completeness"
                )
            if route == "direct-udp":
                if e2e_p95 > DIRECT_P95_LIMIT_US:
                    cell_failures.append(
                        f"direct UDP p95 {e2e_p95} us exceeds {DIRECT_P95_LIMIT_US} us"
                    )
                if e2e_p99 > DIRECT_P99_LIMIT_US:
                    cell_failures.append(
                        f"direct UDP p99 {e2e_p99} us exceeds {DIRECT_P99_LIMIT_US} us"
                    )
                if misses:
                    cell_failures.append(
                        f"direct UDP has {misses} samples at or above {MISS_LIMIT_US} us"
                    )
            label = f"route={route} bulk_streams={bulk_streams}"
            failures.extend(f"{label}: {failure}" for failure in cell_failures)
            cell_reports.append(
                CellReport(
                    route=route,
                    bulk_streams=bulk_streams,
                    samples=len(cell),
                    end_to_end_p50_us=e2e_p50,
                    end_to_end_p95_us=e2e_p95,
                    end_to_end_p99_us=e2e_p99,
                    host_receive_to_pty_p50_us=host_receive_to_pty_p50,
                    host_receive_to_pty_p95_us=host_receive_to_pty_p95,
                    host_receive_to_pty_p99_us=host_receive_to_pty_p99,
                    host_pty_to_output_p50_us=host_pty_to_output_p50,
                    host_pty_to_output_p95_us=host_pty_to_output_p95,
                    host_pty_to_output_p99_us=host_pty_to_output_p99,
                    controller_output_to_render_p50_us=(
                        controller_output_to_render_p50
                    ),
                    controller_output_to_render_p95_us=(
                        controller_output_to_render_p95
                    ),
                    controller_output_to_render_p99_us=(
                        controller_output_to_render_p99
                    ),
                    owner_queue_wait_p50_us=owner_p50,
                    owner_queue_wait_p95_us=owner_p95,
                    owner_queue_wait_p99_us=owner_p99,
                    misses_at_or_above_250000_us=misses,
                    semantic_failures=semantic_failures,
                    passed=not cell_failures,
                    failures=tuple(cell_failures),
                )
            )
    return QualificationReport(
        passed=not failures,
        schema=EVIDENCE_SCHEMA,
        metadata=dict(sorted(metadata.items())),
        thresholds={
            "minimum_samples_per_cell": MINIMUM_SAMPLES_PER_CELL,
            "maximum_samples_per_cell": MAXIMUM_SAMPLES_PER_CELL,
            "direct_p95_limit_us": DIRECT_P95_LIMIT_US,
            "direct_p99_limit_us": DIRECT_P99_LIMIT_US,
            "miss_limit_us": MISS_LIMIT_US,
            "owner_p99_relation": "strictly-less-than",
            "owner_p99_limit_us": OWNER_P99_STRICT_LIMIT_US,
        },
        total_samples=len(samples),
        cells=tuple(cell_reports),
        failures=tuple(failures),
    )


def analyze_stream(stream: TextIO) -> QualificationReport:
    metadata, samples = parse_evidence(stream, require_signatures=True)
    verify_attestations(metadata)
    return qualify(metadata, samples)


def _read_regular_file(
    path: Path, maximum_bytes: int = MAXIMUM_INPUT_BYTES
) -> _RegularFileObservation:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise InputError(f"{path} must name a regular file")
        if before.st_size > maximum_bytes:
            raise InputError(f"{path} exceeds the maximum byte count")
        chunks: list[bytes] = []
        remaining = before.st_size + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > maximum_bytes:
            raise InputError(f"{path} exceeds the maximum byte count")
        after = os.fstat(descriptor)
        identity_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        identity_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if identity_before != identity_after:
            raise InputError(f"{path} changed while it was being read")
        if len(payload) != before.st_size:
            raise InputError(f"{path} ended before its stable recorded size")
        return _RegularFileObservation(
            payload=payload,
            device=before.st_dev,
            inode=before.st_ino,
        )
    finally:
        os.close(descriptor)


def _read_regular_bytes(path: Path, maximum_bytes: int = MAXIMUM_INPUT_BYTES) -> bytes:
    return _read_regular_file(path, maximum_bytes).payload


def _read_small_dynamic_ascii(path: Path, maximum_bytes: int = 4096) -> str:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024, maximum_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum_bytes:
                raise InputError(f"{path} exceeds the maximum byte count")
        try:
            return b"".join(chunks).decode("ascii", errors="strict")
        except UnicodeDecodeError as error:
            raise InputError(f"{path} is not ASCII") from error
    finally:
        os.close(descriptor)


def local_boot_id() -> str:
    text = _read_small_dynamic_ascii(Path("/proc/sys/kernel/random/boot_id"), 128)
    if not text.endswith("\n") or text.count("\n") != 1:
        raise InputError("local kernel boot ID is not canonical")
    return _require_pattern(text[:-1], UUID_LOWER, "local kernel boot ID")


def _read_ascii(path: Path, maximum_bytes: int = MAXIMUM_INPUT_BYTES) -> str:
    payload = _read_regular_bytes(path, maximum_bytes)
    try:
        return payload.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise InputError(f"{path} is not ASCII") from error


def analyze_path(path: Path) -> QualificationReport:
    return analyze_stream(io.StringIO(_read_ascii(path)))


def _write_exclusive(path: Path, payload: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parent_flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        parent_flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        parent_flags |= os.O_NOFOLLOW
    parent_descriptor = os.open(path.parent, parent_flags)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = -1
    try:
        descriptor = os.open(path.name, flags, mode, dir_fd=parent_descriptor)
        os.fchmod(descriptor, mode)
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("exclusive output accepted zero bytes")
            offset += written
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.fsync(parent_descriptor)
    except Exception:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            os.unlink(path.name, dir_fd=parent_descriptor)
            try:
                os.fsync(parent_descriptor)
            except OSError:
                pass
        except FileNotFoundError:
            pass
        raise
    finally:
        os.close(parent_descriptor)


def _evidence_artifact(path: Path) -> _EvidenceArtifact:
    observation = _read_regular_file(path)
    if not observation.payload:
        raise InputError(f"{path} may not be empty evidence")
    return _EvidenceArtifact(
        sha256=hashlib.sha256(observation.payload).hexdigest(),
        size=len(observation.payload),
        device=observation.device,
        inode=observation.inode,
    )


def _validate_distinct_artifacts(
    route: _EvidenceArtifact, bulk: _EvidenceArtifact
) -> None:
    if (route.device, route.inode) == (bulk.device, bulk.inode):
        raise InputError("route and bulk evidence must be different regular files")
    if route.sha256 == bulk.sha256:
        raise InputError("route and bulk evidence must contain distinct bytes")


def analyze_bundle(
    evidence_path: Path, route_evidence_path: Path, bulk_evidence_path: Path
) -> QualificationReport:
    report = analyze_path(evidence_path)
    route = _evidence_artifact(route_evidence_path)
    bulk = _evidence_artifact(bulk_evidence_path)
    _validate_distinct_artifacts(route, bulk)
    if route.sha256 != report.metadata["route-evidence-sha256"]:
        raise InputError("route evidence digest does not match the sealed run")
    if str(route.size) != report.metadata["route-evidence-bytes"]:
        raise InputError("route evidence size does not match the sealed run")
    if bulk.sha256 != report.metadata["bulk-evidence-sha256"]:
        raise InputError("bulk evidence digest does not match the sealed run")
    if str(bulk.size) != report.metadata["bulk-evidence-bytes"]:
        raise InputError("bulk evidence size does not match the sealed run")
    return report


def prepare_evidence(
    schedule_text: str,
    measurements_text: str,
    *,
    source_commit: str,
    controller_boot_id: str,
    host_boot_id: str,
    controller_capture_key: str,
    host_capture_key: str,
    route_evidence_sha256: str,
    route_evidence_bytes: int,
    bulk_evidence_sha256: str,
    bulk_evidence_bytes: int,
) -> tuple[dict[str, str], list[Sample]]:
    schedule_meta, trials = parse_schedule(io.StringIO(schedule_text))
    measurement_meta, measurements = parse_measurements(
        io.StringIO(measurements_text)
    )
    if measurement_meta["run-id"] != schedule_meta["run-id"]:
        raise InputError("schedule and measurements use different run IDs")
    if len(measurements) != len(trials):
        raise InputError("schedule and measurement row counts differ")
    samples: list[Sample] = []
    for trial, measurement in zip(trials, measurements, strict=True):
        if measurement.ordinal != trial.ordinal or measurement.token != trial.token:
            raise InputError(
                f"measurement ordinal {measurement.ordinal} contradicts the schedule"
            )
        samples.append(
            Sample(
                route=trial.route,
                bulk_streams=trial.bulk_streams,
                ordinal=trial.ordinal,
                token=trial.token,
                controller_input_us=measurement.controller_input_us,
                controller_output_us=measurement.controller_output_us,
                controller_render_us=measurement.controller_render_us,
                host_receive_us=measurement.host_receive_us,
                host_input_commit_us=measurement.host_input_commit_us,
                host_output_us=measurement.host_output_us,
                owner_queue_wait_us=measurement.owner_queue_wait_us,
                input_commits=measurement.input_commits,
                render_copies=measurement.render_copies,
                complete=measurement.complete,
                session_id=measurement.session_id,
                input_message_id=measurement.input_message_id,
                input_sequence=measurement.input_sequence,
                input_next_sequence=measurement.input_next_sequence,
                output_sequence=measurement.output_sequence,
                output_next_sequence=measurement.output_next_sequence,
                host_stage_event_ordinal=measurement.host_stage_event_ordinal,
                host_commit_event_ordinal=measurement.host_commit_event_ordinal,
                host_output_event_ordinal=measurement.host_output_event_ordinal,
            )
        )
    _validate_sample_shape(samples)
    per_cell = int(schedule_meta["samples-per-cell"])
    metadata = {
        "attestation-scheme": ATTESTATION_SCHEME,
        "bulk-evidence-bytes": str(bulk_evidence_bytes),
        "bulk-evidence-sha256": _require_pattern(
            bulk_evidence_sha256, HEX_64, "bulk-evidence-sha256"
        ),
        "bulk-load-semantics": "external-review-required",
        "capture-role-count": "2",
        "controller-boot-id": _require_pattern(
            controller_boot_id, UUID_LOWER, "controller-boot-id"
        ),
        "controller-capture-key": _require_pattern(
            controller_capture_key, HEX_64, "controller-capture-key"
        ),
        "controller-clock": "steady",
        "cross-host-clock-comparison": "0",
        "distinct-kernel-boots": "1",
        "host-boot-id": _require_pattern(host_boot_id, UUID_LOWER, "host-boot-id"),
        "host-capture-key": _require_pattern(
            host_capture_key, HEX_64, "host-capture-key"
        ),
        "host-clock": "steady",
        "physical-topology": "external-review-required",
        "provenance-artifacts-bound": "1",
        "randomization-algorithm": RANDOMIZATION_ALGORITHM,
        "randomized": "1",
        "route-evidence-bytes": str(route_evidence_bytes),
        "route-evidence-sha256": _require_pattern(
            route_evidence_sha256, HEX_64, "route-evidence-sha256"
        ),
        "route-topology": "external-review-required",
        "run-id": schedule_meta["run-id"],
        "samples-per-cell": str(per_cell),
        "samples-sha256": _samples_digest(samples),
        "schedule-block-size": str(SCHEDULE_BLOCK_SIZE),
        "schedule-seed": schedule_meta["schedule-seed"],
        "schedule-sha256": hashlib.sha256(schedule_text.encode("ascii")).hexdigest(),
        "schema": EVIDENCE_SCHEMA,
        "service-path": SERVICE_PATH,
        "source-commit": _require_pattern(source_commit, HEX_40, "source-commit"),
        "toxcore-version": TOXCORE_VERSION,
    }
    if not isinstance(route_evidence_bytes, int) or isinstance(
        route_evidence_bytes, bool
    ):
        raise InputError("route-evidence-bytes must be an integer")
    if not isinstance(bulk_evidence_bytes, int) or isinstance(
        bulk_evidence_bytes, bool
    ):
        raise InputError("bulk-evidence-bytes must be an integer")
    _required_metadata_values(metadata)
    if metadata["schedule-sha256"] != _schedule_digest(
        metadata["run-id"], metadata["schedule-seed"], per_cell
    ):
        raise InputError("input schedule is not the canonical rendered schedule")
    return metadata, samples


def seal_evidence(
    unsigned_text: str, controller_signature: str, host_signature: str
) -> str:
    metadata, samples = parse_evidence(
        io.StringIO(unsigned_text), require_signatures=False
    )
    final = dict(metadata)
    final["controller-signature"] = _require_pattern(
        controller_signature, HEX_128, "controller-signature"
    )
    final["host-signature"] = _require_pattern(
        host_signature, HEX_128, "host-signature"
    )
    verify_attestations(final)
    rendered = render_final_evidence(final, samples)
    # Reparse the exact bytes that will be released.
    analyze_stream(io.StringIO(rendered))
    return rendered


def render_text(report: QualificationReport) -> str:
    output = [
        f"ratox-r7-qualification={'PASS' if report.passed else 'FAIL'}",
        f"schema={report.schema}",
        f"total-samples={report.total_samples}",
        f"cells={len(report.cells)}",
        f"run-id={report.metadata['run-id']}",
        f"source-commit={report.metadata['source-commit']}",
        f"samples-sha256={report.metadata['samples-sha256']}",
    ]
    for cell in report.cells:
        output.append(
            " ".join(
                (
                    f"route={cell.route}",
                    f"bulk-streams={cell.bulk_streams}",
                    f"samples={cell.samples}",
                    f"e2e-p50-us={cell.end_to_end_p50_us}",
                    f"e2e-p95-us={cell.end_to_end_p95_us}",
                    f"e2e-p99-us={cell.end_to_end_p99_us}",
                    f"host-receive-to-pty-p50-us={cell.host_receive_to_pty_p50_us}",
                    f"host-receive-to-pty-p95-us={cell.host_receive_to_pty_p95_us}",
                    f"host-receive-to-pty-p99-us={cell.host_receive_to_pty_p99_us}",
                    f"host-pty-to-output-p50-us={cell.host_pty_to_output_p50_us}",
                    f"host-pty-to-output-p95-us={cell.host_pty_to_output_p95_us}",
                    f"host-pty-to-output-p99-us={cell.host_pty_to_output_p99_us}",
                    "controller-output-to-render-p50-us="
                    f"{cell.controller_output_to_render_p50_us}",
                    "controller-output-to-render-p95-us="
                    f"{cell.controller_output_to_render_p95_us}",
                    "controller-output-to-render-p99-us="
                    f"{cell.controller_output_to_render_p99_us}",
                    f"owner-p50-us={cell.owner_queue_wait_p50_us}",
                    f"owner-p95-us={cell.owner_queue_wait_p95_us}",
                    f"owner-p99-us={cell.owner_queue_wait_p99_us}",
                    f"misses-ge-250000-us={cell.misses_at_or_above_250000_us}",
                    f"semantic-failures={cell.semantic_failures}",
                    f"qualified={1 if cell.passed else 0}",
                )
            )
        )
    output.extend(f"failure={failure}" for failure in report.failures)
    return "\n".join(output) + "\n"


def report_json(report: QualificationReport) -> str:
    return json.dumps(asdict(report), indent=2, sort_keys=True) + "\n"


def _signature_text(path: Path) -> str:
    text = _read_ascii(path, 1024)
    if not text.endswith("\n") or text.count("\n") != 1:
        raise InputError(f"{path} must contain one newline-terminated signature")
    return _require_pattern(text[:-1], HEX_128, "signature")


def _public_key_text(path: Path) -> str:
    text = _read_ascii(path, 1024)
    if not text.endswith("\n") or text.count("\n") != 1:
        raise InputError(f"{path} must contain one newline-terminated public key")
    return _require_pattern(text[:-1], HEX_64, "capture public key")


def _secret_key(path: Path) -> bytearray:
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    secret = bytearray()
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise InputError("secret key path must name a regular file")
        if before.st_uid != os.geteuid():
            raise InputError("secret key must be owned by the effective user")
        if before.st_nlink != 1:
            raise InputError("secret key must have exactly one hard link")
        if before.st_mode & 0o077:
            raise InputError("secret key permissions must deny group and other access")
        if before.st_size != Sodium.SECRET_KEY_BYTES:
            raise InputError("secret key file has an invalid size")
        secret = bytearray(Sodium.SECRET_KEY_BYTES)
        view = memoryview(secret)
        offset = 0
        while offset < len(secret):
            count = os.readv(descriptor, [view[offset:]])
            if count <= 0:
                raise InputError("secret key file ended early")
            offset += count
        if os.read(descriptor, 1):
            raise InputError("secret key file contains trailing bytes")
        after = os.fstat(descriptor)
        identity_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
            before.st_mode,
            before.st_uid,
            before.st_nlink,
        )
        identity_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
            after.st_mode,
            after.st_uid,
            after.st_nlink,
        )
        if identity_before != identity_after:
            raise InputError("secret key changed while it was being read")
        return secret
    except Exception:
        if secret:
            secret[:] = b"\x00" * len(secret)
        raise
    finally:
        os.close(descriptor)


def sign_attestation_payload(
    payload: bytes,
    secret_key_path: Path,
    *,
    boot_id_override: str | None = None,
) -> str:
    """Validate and sign one role payload with its exact ephemeral key.

    boot_id_override exists only so the deterministic self-test can exercise
    the complete signing path without pretending that one kernel is two hosts.
    The public CLI never supplies it.
    """

    sodium = Sodium()
    secret = _secret_key(secret_key_path)
    derived_secret = bytearray()
    try:
        role, metadata = parse_attestation_payload(payload)
        observed_boot_id = (
            local_boot_id()
            if boot_id_override is None
            else _require_pattern(
                boot_id_override, UUID_LOWER, "signing boot ID override"
            )
        )
        if metadata[f"{role}-boot-id"] != observed_boot_id:
            raise InputError(
                f"{role} attestation boot ID does not match this running kernel"
            )
        derived_seed = bytearray(secret[: Sodium.SEED_BYTES])
        try:
            public, derived_secret = sodium.keypair_from_seed(derived_seed)
        finally:
            sodium.wipe(derived_seed)
        if bytes(derived_secret) != bytes(secret):
            raise InputError("secret capture key is internally inconsistent")
        if public.hex() != metadata[f"{role}-capture-key"]:
            raise InputError(
                f"{role} secret key does not match the attested capture key"
            )
        return sodium.sign(payload, secret).hex()
    finally:
        sodium.wipe(secret)
        sodium.wipe(derived_secret)


def _fixture_measurements(trials: Sequence[Trial]) -> str:
    lines = [
        f"run-id\t{'11' * 16}\n",
        f"schema\t{MEASUREMENTS_SCHEMA}\n",
    ]
    controller = 1_000_000
    host = 5_000_000
    session_index = 1
    input_sequence = 1
    output_sequence = 1
    host_event = 1
    for trial in trials:
        if trial.ordinal % 500 == 1 and trial.ordinal != 1:
            session_index += 1
            input_sequence = 1
            output_sequence = 1
        e2e = 10_000 + (trial.ordinal % 100)
        controller_output = controller + e2e - 20
        controller_render = controller + e2e
        host_receive = host
        host_commit = host + 100
        host_output = host + 200
        session_id = f"{session_index:064x}"
        fields = (
            "measurement",
            str(trial.ordinal),
            trial.token,
            str(controller),
            str(controller_output),
            str(controller_render),
            str(host_receive),
            str(host_commit),
            str(host_output),
            "100",
            "1",
            "1",
            "1",
            session_id,
            str(trial.ordinal + 1000),
            str(input_sequence),
            str(input_sequence + 1),
            str(output_sequence),
            str(output_sequence + 1),
            str(host_event),
            str(host_event + 1),
            str(host_event + 2),
        )
        lines.append("\t".join(fields) + "\n")
        controller += 20_000
        host += 20_000
        input_sequence += 1
        output_sequence += 1
        host_event += 3
    return "".join(lines)


def self_test() -> None:
    run_id = "11" * 16
    seed = "22" * 32
    per_cell = MINIMUM_SAMPLES_PER_CELL
    schedule = render_schedule(run_id, seed, per_cell)
    schedule_meta, trials = parse_schedule(io.StringIO(schedule))
    assert schedule_meta["run-id"] == run_id
    assert len(trials) == SCHEDULE_BLOCK_SIZE * per_cell
    for offset in range(0, len(trials), SCHEDULE_BLOCK_SIZE):
        block = trials[offset : offset + SCHEDULE_BLOCK_SIZE]
        assert {(trial.route, trial.bulk_streams) for trial in block} == {
            (route, bulk)
            for route in REQUIRED_ROUTES
            for bulk in REQUIRED_BULK_STREAMS
        }
    other_run_trials = generate_trials("33" * 16, seed, per_cell)
    assert [
        (trial.route, trial.bulk_streams) for trial in trials[:SCHEDULE_BLOCK_SIZE]
    ] != [
        (trial.route, trial.bulk_streams)
        for trial in other_run_trials[:SCHEDULE_BLOCK_SIZE]
    ]

    sodium = Sodium()
    controller_public, controller_secret = sodium.keypair_from_seed(bytes([0x31]) * 32)
    host_public, host_secret = sodium.keypair_from_seed(bytes([0x42]) * 32)
    measurements = _fixture_measurements(trials)
    metadata, samples = prepare_evidence(
        schedule,
        measurements,
        source_commit="ab" * 20,
        controller_boot_id="11111111-1111-1111-8111-111111111111",
        host_boot_id="22222222-2222-2222-8222-222222222222",
        controller_capture_key=controller_public.hex(),
        host_capture_key=host_public.hex(),
        route_evidence_sha256=hashlib.sha256(b"route evidence\n").hexdigest(),
        route_evidence_bytes=len(b"route evidence\n"),
        bulk_evidence_sha256=hashlib.sha256(b"bulk evidence\n").hexdigest(),
        bulk_evidence_bytes=len(b"bulk evidence\n"),
    )
    unsigned = render_unsigned_evidence(metadata, samples)
    parsed_unsigned, parsed_samples = parse_evidence(
        io.StringIO(unsigned), require_signatures=False
    )
    assert parsed_samples == samples
    controller_payload = attestation_payload(parsed_unsigned, "controller")
    with tempfile.TemporaryDirectory(prefix="iotox-r7-signing-") as directory:
        controller_key = Path(directory) / "controller.key"
        controller_key.write_bytes(bytes(controller_secret))
        controller_key.chmod(0o600)
        controller_signature = sign_attestation_payload(
            controller_payload,
            controller_key,
            boot_id_override=metadata["controller-boot-id"],
        )
        try:
            sign_attestation_payload(
                controller_payload,
                controller_key,
                boot_id_override=metadata["host-boot-id"],
            )
        except InputError as error:
            assert "boot ID" in str(error)
        else:
            raise AssertionError("wrong-kernel capture signature was accepted")
    host_signature = sodium.sign(
        attestation_payload(parsed_unsigned, "host"), host_secret
    ).hex()
    sodium.wipe(controller_secret)
    sodium.wipe(host_secret)
    final = seal_evidence(unsigned, controller_signature, host_signature)
    first = analyze_stream(io.StringIO(final))
    second = analyze_stream(io.StringIO(final))
    assert first.passed
    assert first.total_samples == 12_000
    assert first.cells[0].host_receive_to_pty_p99_us == 100
    assert first.cells[0].host_pty_to_output_p99_us == 100
    assert first.cells[0].controller_output_to_render_p99_us == 20
    assert first.cells[0].owner_queue_wait_p95_us == 100
    assert report_json(first) == report_json(second)

    # Host-local durations may legitimately exceed a controller-local sample
    # duration when clocks differ in rate or instrumentation. Shape validation
    # must not recreate a cross-host arithmetic comparison.
    cross_clock_independent = replace(
        samples[0],
        host_input_commit_us=samples[0].host_receive_us + 20_000,
        host_output_us=samples[0].host_receive_us + 30_000,
    )
    _validate_sample_shape([cross_clock_independent])

    lines = final.splitlines(keepends=True)
    sample_index = next(index for index, line in enumerate(lines) if line.startswith("sample\t"))
    fields = lines[sample_index].rstrip("\n").split("\t")
    fields[7] = str(int(fields[7]) + 1)
    lines[sample_index] = "\t".join(fields) + "\n"
    try:
        analyze_stream(io.StringIO("".join(lines)))
    except InputError as error:
        assert "samples-sha256" in str(error)
    else:
        raise AssertionError("tampered sample was accepted")

    bad_signature = final.replace(
        f"controller-signature\t{controller_signature}\n",
        f"controller-signature\t{'00' * 64}\n",
        1,
    )
    try:
        analyze_stream(io.StringIO(bad_signature))
    except InputError as error:
        assert "signature" in str(error)
    else:
        raise AssertionError("invalid attestation was accepted")

    reused = list(samples)
    reused[1] = replace(
        reused[1], host_stage_event_ordinal=reused[0].host_stage_event_ordinal
    )
    try:
        _validate_sample_shape(reused)
    except InputError as error:
        assert "globally increasing" in str(error)
    else:
        raise AssertionError("out-of-order host event was accepted")

    with tempfile.TemporaryDirectory(prefix="iotox-r7-evidence-") as directory:
        root = Path(directory)
        evidence = root / "evidence.tsv"
        route_evidence = root / "route-evidence.txt"
        bulk_evidence = root / "bulk-evidence.txt"
        evidence.write_text(final, encoding="ascii", newline="")
        route_evidence.write_bytes(b"route evidence\n")
        bulk_evidence.write_bytes(b"bulk evidence\n")
        assert analyze_path(evidence) == first
        assert analyze_bundle(evidence, route_evidence, bulk_evidence) == first

        try:
            analyze_bundle(evidence, route_evidence, route_evidence)
        except InputError as error:
            assert "different regular files" in str(error)
        else:
            raise AssertionError("one file was accepted for both evidence roles")

        route_evidence.write_bytes(b"tampered route evidence\n")
        try:
            analyze_bundle(evidence, route_evidence, bulk_evidence)
        except InputError as error:
            assert "route evidence digest" in str(error)
        else:
            raise AssertionError("tampered route evidence was accepted")

        link = root / "evidence-link.tsv"
        link.symlink_to(evidence)
        try:
            analyze_path(link)
        except OSError:
            pass
        else:
            raise AssertionError("symlink evidence input was accepted")

    print("ratox-r7-analyzer self-test: PASS")


def analyzer_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed qualification gate for Ratox R7 v2 evidence"
    )
    parser.add_argument("input", nargs="?", type=Path, help="sealed R7 TSV evidence")
    parser.add_argument("--route-evidence", type=Path)
    parser.add_argument("--bulk-evidence", type=Path)
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.self_test:
        if (
            arguments.input is not None
            or arguments.json_report is not None
            or arguments.route_evidence is not None
            or arguments.bulk_evidence is not None
        ):
            parser.error(
                "--self-test does not accept input, evidence paths, or --json-report"
            )
        self_test()
        return 0
    if arguments.input is None:
        parser.error("input is required unless --self-test is used")
    if arguments.route_evidence is None or arguments.bulk_evidence is None:
        parser.error(
            "--route-evidence and --bulk-evidence are required for a qualification run"
        )
    try:
        report = analyze_bundle(
            arguments.input,
            arguments.route_evidence,
            arguments.bulk_evidence,
        )
        if arguments.json_report is not None:
            _write_exclusive(
                arguments.json_report, report_json(report).encode("ascii")
            )
        sys.stdout.write(render_text(report))
        return 0 if report.passed else 1
    except (InputError, OSError, UnicodeError) as error:
        print(f"ratox-r7-qualification=INVALID\nerror={error}", file=sys.stderr)
        return 2


def evidence_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    schedule_parser = subparsers.add_parser("schedule")
    schedule_parser.add_argument("--run-id", required=True)
    schedule_parser.add_argument("--seed", required=True)
    schedule_parser.add_argument(
        "--samples-per-cell", type=int, default=MINIMUM_SAMPLES_PER_CELL
    )
    schedule_parser.add_argument("--output", required=True, type=Path)

    keygen_parser = subparsers.add_parser("keygen")
    keygen_parser.add_argument("--secret-key", required=True, type=Path)
    keygen_parser.add_argument("--public-key", required=True, type=Path)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--schedule", required=True, type=Path)
    prepare_parser.add_argument("--measurements", required=True, type=Path)
    prepare_parser.add_argument("--source-commit", required=True)
    prepare_parser.add_argument("--controller-boot-id", required=True)
    prepare_parser.add_argument("--host-boot-id", required=True)
    prepare_parser.add_argument("--controller-public-key", required=True, type=Path)
    prepare_parser.add_argument("--host-public-key", required=True, type=Path)
    prepare_parser.add_argument("--route-evidence", required=True, type=Path)
    prepare_parser.add_argument("--bulk-evidence", required=True, type=Path)
    prepare_parser.add_argument("--output", required=True, type=Path)

    payload_parser = subparsers.add_parser("attestation-payload")
    payload_parser.add_argument("unsigned_evidence", type=Path)
    payload_parser.add_argument("--role", choices=("controller", "host"), required=True)
    payload_parser.add_argument("--output", required=True, type=Path)

    sign_parser = subparsers.add_parser("sign")
    sign_parser.add_argument("payload", type=Path)
    sign_parser.add_argument("--secret-key", required=True, type=Path)
    sign_parser.add_argument("--output", required=True, type=Path)

    seal_parser = subparsers.add_parser("seal")
    seal_parser.add_argument("unsigned_evidence", type=Path)
    seal_parser.add_argument("--controller-signature", required=True, type=Path)
    seal_parser.add_argument("--host-signature", required=True, type=Path)
    seal_parser.add_argument("--output", required=True, type=Path)

    subparsers.add_parser("self-test")
    arguments = parser.parse_args(argv)

    try:
        if arguments.command == "schedule":
            payload = render_schedule(
                arguments.run_id, arguments.seed, arguments.samples_per_cell
            ).encode("ascii")
            _write_exclusive(arguments.output, payload)
        elif arguments.command == "keygen":
            sodium = Sodium()
            seed = bytearray(os.urandom(Sodium.SEED_BYTES))
            secret = bytearray()
            try:
                public, secret = sodium.keypair_from_seed(seed)
                _write_exclusive(arguments.secret_key, bytes(secret), 0o600)
                try:
                    _write_exclusive(
                        arguments.public_key, (public.hex() + "\n").encode("ascii"), 0o600
                    )
                except Exception:
                    arguments.secret_key.unlink(missing_ok=True)
                    raise
            finally:
                sodium.wipe(seed)
                sodium.wipe(secret)
        elif arguments.command == "prepare":
            route_artifact = _evidence_artifact(arguments.route_evidence)
            bulk_artifact = _evidence_artifact(arguments.bulk_evidence)
            _validate_distinct_artifacts(route_artifact, bulk_artifact)
            metadata, samples = prepare_evidence(
                _read_ascii(arguments.schedule),
                _read_ascii(arguments.measurements),
                source_commit=arguments.source_commit,
                controller_boot_id=arguments.controller_boot_id,
                host_boot_id=arguments.host_boot_id,
                controller_capture_key=_public_key_text(
                    arguments.controller_public_key
                ),
                host_capture_key=_public_key_text(arguments.host_public_key),
                route_evidence_sha256=route_artifact.sha256,
                route_evidence_bytes=route_artifact.size,
                bulk_evidence_sha256=bulk_artifact.sha256,
                bulk_evidence_bytes=bulk_artifact.size,
            )
            _write_exclusive(
                arguments.output,
                render_unsigned_evidence(metadata, samples).encode("ascii"),
            )
        elif arguments.command == "attestation-payload":
            metadata, _ = parse_evidence(
                io.StringIO(_read_ascii(arguments.unsigned_evidence)),
                require_signatures=False,
            )
            _write_exclusive(
                arguments.output,
                attestation_payload(metadata, arguments.role),
            )
        elif arguments.command == "sign":
            signature = sign_attestation_payload(
                _read_regular_bytes(arguments.payload, 1024 * 1024),
                arguments.secret_key,
            )
            _write_exclusive(
                arguments.output, (signature + "\n").encode("ascii")
            )
        elif arguments.command == "seal":
            final = seal_evidence(
                _read_ascii(arguments.unsigned_evidence),
                _signature_text(arguments.controller_signature),
                _signature_text(arguments.host_signature),
            )
            _write_exclusive(arguments.output, final.encode("ascii"))
        elif arguments.command == "self-test":
            self_test()
        else:
            raise AssertionError("unhandled command")
        return 0
    except (InputError, OSError, UnicodeError) as error:
        print(f"ratox-r7-evidence: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(evidence_main())

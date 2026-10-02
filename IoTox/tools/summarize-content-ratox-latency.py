#!/usr/bin/env python3
"""Summarize Ratox latency samples that overlap content-v2 transfers."""

from __future__ import annotations

import argparse
import hashlib
import math
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path


SHA256 = re.compile(r"[0-9a-f]{64}")
CAPS = (1, 4, 8)
SLA_CAPS = (1, 2, 4, 8)
SAMPLES = 240
INTERVAL_MS = 100


class SummaryError(RuntimeError):
    pass


@dataclass(frozen=True)
class Phase:
    cap: int
    start_us: int
    end_us: int
    duration_ms: int
    content_bps: int
    active_lanes: int
    first_sample: int
    last_sample: int
    capture_sha256: str
    phase_ready_delay_ms: int


@dataclass(frozen=True)
class Sample:
    ordinal: int
    started_us: int
    returned_us: int
    rendered_us: int
    session: str
    queue_wait_us: int


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SummaryError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nearest_rank(values: list[int], percent: int) -> int:
    require(values and 1 <= percent <= 100, "invalid percentile input")
    ordered = sorted(values)
    return ordered[math.ceil(len(ordered) * percent / 100) - 1]


def parse_metadata(path: Path) -> tuple[tuple[int, ...], str, int, list[Phase]]:
    lines = path.read_text(encoding="ascii").splitlines()
    if lines[:2] == [
        "schema\tiotox-content-ratox-overlap-metadata-v1",
        "phase-order\t1,4,8",
    ]:
        caps = CAPS
        summary_schema = "iotox-content-ratox-latency-science-v1"
    elif lines[:2] == [
        "schema\tiotox-content-ratox-overlap-metadata-v2",
        "phase-order\t1,2,4,8",
    ]:
        caps = SLA_CAPS
        summary_schema = "iotox-content-ratox-latency-sla-v1"
    else:
        raise SummaryError("overlap metadata format is unsupported")
    total_samples = SAMPLES * len(caps)
    require(
        lines[2:6]
        == [
            f"samples-per-phase\t{SAMPLES}",
            f"samples-total\t{total_samples}",
            f"sample-interval-ms\t{INTERVAL_MS}",
            "columns\tcap\tcontent-start-us\tcontent-end-us\tcontent-duration-ms\tcontent-bps\tmax-active-lanes\tsample-first\tsample-last\tcapture-sha256\ttox-online-epoch\tphase-ready-delay-ms",
        ],
        "overlap metadata header is noncanonical",
    )
    require(
        len(lines) == 6 + len(caps),
        "overlap metadata phase count is invalid",
    )
    phases: list[Phase] = []
    epoch: int | None = None
    for phase_index, (expected_cap, line) in enumerate(
        zip(caps, lines[6:], strict=True)
    ):
        fields = line.split("\t")
        require(len(fields) == 12 and fields[0] == "phase", "metadata row shape is invalid")
        try:
            (
                cap,
                start,
                end,
                duration,
                bps,
                active,
                first_sample,
                last_sample,
                observed_epoch,
                phase_ready_delay_ms,
            ) = map(
                int, fields[1:9] + fields[10:12]
            )
        except ValueError as error:
            raise SummaryError("metadata row contains nondecimal values") from error
        digest = fields[9]
        expected_first = phase_index * SAMPLES + 1
        expected_last = expected_first + SAMPLES - 1
        require(
            cap == expected_cap
            and 0 < start < end
            and duration > 0
            and abs(duration - ((end - start) // 1000)) <= 2
            and bps == (8 * 1024 * 1024 * 1000) // duration
            and 1 <= active <= cap
            and first_sample == expected_first
            and last_sample == expected_last
            and SHA256.fullmatch(digest) is not None
            and observed_epoch > 0
            and 0 <= phase_ready_delay_ms <= 180_000,
            f"cap-{expected_cap} metadata is invalid",
        )
        if epoch is None:
            epoch = observed_epoch
        require(observed_epoch == epoch, "Tox online epoch changed between phases")
        phases.append(
            Phase(
                cap,
                start,
                end,
                duration,
                bps,
                active,
                first_sample,
                last_sample,
                digest,
                phase_ready_delay_ms,
            )
        )
    assert epoch is not None
    return caps, summary_schema, epoch, phases


def parse_capture(
    path: Path, expected_sha256: str, total_samples: int
) -> list[Sample]:
    require(sha256(path) == expected_sha256, f"capture digest mismatch: {path.name}")
    lines = path.read_text(encoding="ascii").splitlines()
    require(
        f"samples\t{total_samples}" in lines
        and f"sample-interval-ms\t{INTERVAL_MS}" in lines
        and "schema\tiotox-ratox-terminal-probe-v1" in lines,
        f"capture metadata is invalid: {path.name}",
    )
    rows = [line.split("\t") for line in lines if line.startswith("sample\t")]
    require(
        len(rows) == total_samples,
        f"capture sample count is invalid: {path.name}",
    )
    samples: list[Sample] = []
    previous_render = 0
    for ordinal, row in enumerate(rows, 1):
        require(len(row) == 11, f"capture row shape is invalid: {path.name}")
        try:
            numeric = [int(value) for value in row[1:5]]
            queue_wait = int(row[10])
            input_sequence = int(row[6])
            next_input = int(row[7])
            output_sequence = int(row[8])
            next_output = int(row[9])
        except ValueError as error:
            raise SummaryError(f"capture row is nondecimal: {path.name}") from error
        require(
            numeric[0] == ordinal
            and previous_render <= numeric[1] < numeric[2] <= numeric[3]
            and re.fullmatch(r"[0-9a-f]{32}", row[5]) is not None
            and next_input == input_sequence + 1
            and next_output == output_sequence + 1
            and queue_wait >= 0,
            f"capture row is inconsistent: {path.name}",
        )
        previous_render = numeric[3]
        samples.append(
            Sample(ordinal, numeric[1], numeric[2], numeric[3], row[5], queue_wait)
        )
    require(len({sample.session for sample in samples}) == 1, "Ratox session changed within a phase")
    return samples


def summarize(metadata: Path, capture: Path) -> str:
    caps, summary_schema, epoch, phases = parse_metadata(metadata)
    total_samples = SAMPLES * len(caps)
    capture_digests = {phase.capture_sha256 for phase in phases}
    require(len(capture_digests) == 1, "phases do not bind one persistent capture")
    samples = parse_capture(
        capture, next(iter(capture_digests)), total_samples
    )
    require(
        len({sample.session for sample in samples}) == 1,
        "Ratox session changed across phases",
    )
    output = [
        f"schema\t{summary_schema}",
        "phase-order\t" + ",".join(str(cap) for cap in caps),
        f"samples-per-phase\t{SAMPLES}",
        f"samples-total\t{total_samples}",
        f"sample-interval-ms\t{INTERVAL_MS}",
        f"tox-online-epoch\t{epoch}",
        "columns\tcap\tcontent-duration-ms\tcontent-bps\tmax-active-lanes\tphase-ready-delay-ms\toverlap-samples\trtt-p50-us\trtt-p95-us\trtt-p99-us\trtt-max-us\tqueue-p95-us\tqueue-max-us\tsession-sha256\tcapture-sha256",
    ]
    for phase in phases:
        segment = samples[phase.first_sample - 1 : phase.last_sample]
        require(
            len(segment) == SAMPLES
            and segment[0].returned_us < phase.start_us,
            f"cap-{phase.cap} probe lacks a pre-transfer sample",
        )
        overlap = [
            sample
            for sample in segment
            if phase.start_us <= sample.started_us <= phase.end_us
        ]
        require(len(overlap) >= 20, f"cap-{phase.cap} has too few overlapping samples")
        round_trips = [sample.returned_us - sample.started_us for sample in overlap]
        queue_waits = [sample.queue_wait_us for sample in overlap]
        session_sha256 = hashlib.sha256(bytes.fromhex(segment[0].session)).hexdigest()
        output.append(
            "\t".join(
                (
                    "phase",
                    str(phase.cap),
                    str(phase.duration_ms),
                    str(phase.content_bps),
                    str(phase.active_lanes),
                    str(phase.phase_ready_delay_ms),
                    str(len(overlap)),
                    str(nearest_rank(round_trips, 50)),
                    str(nearest_rank(round_trips, 95)),
                    str(nearest_rank(round_trips, 99)),
                    str(max(round_trips)),
                    str(nearest_rank(queue_waits, 95)),
                    str(max(queue_waits)),
                    session_sha256,
                    phase.capture_sha256,
                )
            )
        )
    return "\n".join(output) + "\n"


def self_test() -> None:
    require(nearest_rank([9, 1, 5, 3], 50) == 3, "nearest-rank p50 failed")
    require(nearest_rank([9, 1, 5, 3], 95) == 9, "nearest-rank p95 failed")
    try:
        nearest_rank([], 50)
    except SummaryError:
        pass
    else:
        raise SummaryError("empty percentile input was accepted")

    def exercise(caps: tuple[int, ...]) -> None:
        total_samples = SAMPLES * len(caps)
        metadata_schema = (
            "iotox-content-ratox-overlap-metadata-v1"
            if caps == CAPS
            else "iotox-content-ratox-overlap-metadata-v2"
        )
        summary_schema = (
            "iotox-content-ratox-latency-science-v1"
            if caps == CAPS
            else "iotox-content-ratox-latency-sla-v1"
        )
        root = tempfile.mkdtemp(prefix="iotox-content-ratox-summary.")
        directory = Path(root)
        session = "01" * 16
        capture_rows = [
            "peer-public-key-sha256\t" + "02" * 32,
            f"samples\t{total_samples}",
            f"sample-interval-ms\t{INTERVAL_MS}",
            "schema\tiotox-ratox-terminal-probe-v1",
        ]
        for ordinal in range(1, total_samples + 1):
            phase_index = (ordinal - 1) // SAMPLES
            cap = caps[phase_index]
            started = ordinal * 200_000
            returned = started + cap * 1_000
            rendered_at = returned + 10
            capture_rows.append(
                "\t".join(
                    (
                        "sample",
                        str(ordinal),
                        str(started),
                        str(returned),
                        str(rendered_at),
                        session,
                        str(ordinal),
                        str(ordinal + 1),
                        str(ordinal),
                        str(ordinal + 1),
                        str(ordinal),
                    )
                )
            )
        capture = directory / "content-ratox-timeline.tsv"
        capture.write_text("\n".join(capture_rows) + "\n", encoding="ascii")
        capture_digest = sha256(capture)
        metadata_rows = [
            f"schema\t{metadata_schema}",
            "phase-order\t" + ",".join(str(cap) for cap in caps),
            f"samples-per-phase\t{SAMPLES}",
            f"samples-total\t{total_samples}",
            f"sample-interval-ms\t{INTERVAL_MS}",
            "columns\tcap\tcontent-start-us\tcontent-end-us\tcontent-duration-ms\tcontent-bps\tmax-active-lanes\tsample-first\tsample-last\tcapture-sha256\ttox-online-epoch\tphase-ready-delay-ms",
        ]
        for index, cap in enumerate(caps):
            first = index * SAMPLES + 1
            last = first + SAMPLES - 1
            start = first * 200_000 + cap * 1_000 + 100
            end = start + 20_000_000
            duration = (end - start) // 1_000
            metadata_rows.append(
                "\t".join(
                    (
                        "phase",
                        str(cap),
                        str(start),
                        str(end),
                        str(duration),
                        str((8 * 1024 * 1024 * 1000) // duration),
                        str(cap),
                        str(first),
                        str(last),
                        capture_digest,
                        "7",
                        str((index + 1) * 100),
                    )
                )
            )
        metadata = directory / "metadata.tsv"
        metadata.write_text("\n".join(metadata_rows) + "\n", encoding="ascii")
        rendered = summarize(metadata, capture).splitlines()
        require(
            rendered[0] == f"schema\t{summary_schema}"
            and len(rendered) == 7 + len(caps),
            "complete summary row count or schema is invalid",
        )
        for index, (cap, row) in enumerate(
            zip(caps, rendered[7:], strict=True), 1
        ):
            fields = row.split("\t")
            require(
                fields[:7]
                == [
                    "phase",
                    str(cap),
                    "20000",
                    "419430",
                    str(cap),
                    str(index * 100),
                    "100",
                ]
                and fields[7:11]
                == [str(cap * 1_000)] * 4,
                f"cap-{cap} complete summary reconstruction failed",
            )
        for path in directory.iterdir():
            path.unlink()
        directory.rmdir()

    exercise(CAPS)
    exercise(SLA_CAPS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        print("summarize-content-ratox-latency self-test passed")
        return 0
    if not all((arguments.metadata, arguments.capture, arguments.output)):
        parser.error("--metadata, --capture, and --output are required")
    rendered = summarize(arguments.metadata, arguments.capture)
    temporary = arguments.output.with_name(arguments.output.name + ".tmp")
    temporary.write_text(rendered, encoding="ascii")
    temporary.chmod(0o600)
    temporary.replace(arguments.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SummaryError as error:
        print(f"error: {error}", file=__import__("sys").stderr)
        raise SystemExit(1) from error

"""Build the historical rev0368 submit-hardened Priority-0 responder bundle."""

import pathlib

from priority_zero_handoff_bundle_lib import build_responder_bundle

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = "handoffs/priority-zero-submit-hardened-external-replay-responder-bundle-2026-06-16.zip"
MEMBERS = [
    "assays/priority-zero-submit-hardened-external-replay-responder-only-2026-06-16.json",
    "assays/priority-zero-submit-hardened-external-replay-response-template-2026-06-16.json",
    "handoffs/priority-zero-submit-hardened-external-replay-responder-readme-2026-06-16.md",
]
FORBIDDEN = [
    "answer_key",
    "true_variant",
    "expected_score",
    "scorecard",
    "priority-zero-submit-hardened-external-replay-scorer-intake",
]


def build_bundle() -> str:
    return build_responder_bundle(
        root=ROOT,
        bundle_rel=BUNDLE,
        members=MEMBERS,
        date_time=(2026, 6, 16, 3, 18, 0),
        forbidden_tokens=FORBIDDEN,
    )


if __name__ == "__main__":
    build_bundle()
    print(BUNDLE)

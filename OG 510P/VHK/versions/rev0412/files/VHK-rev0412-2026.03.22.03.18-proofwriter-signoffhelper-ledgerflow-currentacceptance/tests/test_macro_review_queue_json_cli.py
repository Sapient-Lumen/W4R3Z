from __future__ import annotations

from pathlib import Path
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "queue"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "alpha.yaml").write_text(
        yaml.safe_dump({"name": "alpha", "steps": [{"type": "TypeText", "text": "alpha"}]})
    )
    (proj / "macros" / "beta.yaml").write_text(
        yaml.safe_dump({"name": "beta", "steps": [{"type": "TypeText", "text": "beta"}]})
    )
    (proj / "macros" / "gamma.yaml").write_text(
        yaml.safe_dump({"name": "gamma", "steps": [{"type": "TypeText", "text": "gamma"}]})
    )
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "queue",
                "macros": {
                    "alpha": "macros/alpha.yaml",
                    "beta": "macros/beta.yaml",
                    "gamma": "macros/gamma.yaml",
                },
            }
        )
    )
    return proj


def test_macro_review_queue_json_emits_macro_specific_review_and_repair_commands(tmp_path: Path):
    proj = _make_project(tmp_path)

    alpha_sidecar = proj / "macros" / "alpha.window-context.yaml"
    alpha_sidecar.write_text(
        yaml.safe_dump(
            {
                "segments": [
                    {"selector_kind": "exact", "transition_reason": "title"},
                ]
            },
            sort_keys=False,
        )
    )
    gamma_sidecar = proj / "macros" / "gamma.window-context.yaml"
    gamma_sidecar.write_text(
        yaml.safe_dump(
            {
                "segments": [
                    {"selector_kind": "stable", "transition_reason": "focus"},
                ]
            },
            sort_keys=False,
        )
    )

    os.utime(alpha_sidecar, (1000, 1000))
    os.utime(proj / "macros" / "alpha.yaml", (2000, 2000))
    os.utime(gamma_sidecar, (3000, 3000))
    os.utime(proj / "macros" / "gamma.yaml", (2000, 2000))

    res = runner.invoke(app, ["macro-review-queue-json", str(proj), "--stack-bin-prefix", "./bin/"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["stack_kind"] == "vhk.project.macro_review_queue"
    assert payload["counts"]["stale_recording_sidecars"] == 1
    assert payload["counts"]["missing_recording_sidecars"] == 1
    assert payload["counts"]["recording_newer_than_source"] == 1
    assert payload["counts"]["exact_segment_macros"] == 1
    assert payload["counts"]["title_segment_macros"] == 1

    taxonomy = payload["issue_taxonomy"]
    assert taxonomy["stale_recording_sidecar"]["action_lane"] == "recording_review"
    assert taxonomy["stale_recording_sidecar"]["scope_class"] == "recording_freshness"
    assert taxonomy["stale_recording_sidecar"]["truth_effect"] == "advisory_drift"
    assert taxonomy["exact_segments"]["status_label"] == "exact selector segments remain"
    assert payload["non_claims"][0].startswith("Review-queue warnings are advisory triage signals")

    stale = payload["queue"]["stale_recording_sidecars"][0]
    assert stale["name"] == "alpha"
    assert stale["issue_code"] == "stale_recording_sidecar"
    assert stale["severity"] == "warning"
    assert stale["status_label"] == "stale recorder evidence"
    assert stale["action_lane"] == "recording_review"
    assert stale["scope_class"] == "recording_freshness"
    assert stale["truth_effect"] == "advisory_drift"
    assert stale["non_claims"][0] == "Does not prove replay will fail."
    assert stale["review_command"] == "./bin/macro_recording_json.sh alpha"
    assert stale["cleanup_review_command"] == "./bin/optimize_macro.sh alpha"
    assert stale["cleanup_apply_command"] == "./bin/apply_optimize_macro.sh alpha"
    assert stale["retime_command"] == "./bin/retime_macro.sh alpha --speed 1.25 --in-place"
    assert "source=macros/alpha.yaml" in stale["evidence"]
    assert "recording_sidecar=macros/alpha.window-context.yaml" in stale["evidence"]
    assert "freshness=source_newer_than_recording" in stale["evidence"]
    assert "exact_segments=1" in stale["evidence"]
    assert "title_segments=1" in stale["evidence"]

    missing = payload["queue"]["missing_recording_sidecars"][0]
    assert missing["name"] == "beta"
    assert missing["action_lane"] == "record"
    assert missing["scope_class"] == "recording_presence"
    assert missing["truth_effect"] == "advisory_gap"
    assert missing["record_command"] == "./bin/record_macro.sh beta 5000"
    assert "recording_sidecar=<missing>" in missing["evidence"]

    newer = payload["queue"]["recording_newer_than_source"][0]
    assert newer["name"] == "gamma"
    assert newer["issue_code"] == "recording_newer_than_source"
    assert newer["truth_effect"] == "advisory_reconciliation"
    assert newer["review_command"] == "./bin/macro_recording_json.sh gamma"
    assert "freshness=recording_newer_than_source" in newer["evidence"]

    ordered_names = [item["name"] for item in payload["ordered"]]
    assert ordered_names[:3] == ["alpha", "alpha", "alpha"]
    assert ordered_names[-2:] == ["gamma", "beta"]

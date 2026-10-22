#!/usr/bin/env python3

import json
import os
import pathlib
import subprocess
import tempfile
import unittest


FINITE_SCRIPT = pathlib.Path("/home/overseer/scripts/finite_loop_registry.py")
GROUP_SCRIPT = pathlib.Path("/home/overseer/scripts/loop_group_registry.py")


class LoopGroupRegistryTests(unittest.TestCase):
    def run_group(self, *args: str, root: pathlib.Path, finite_root: pathlib.Path) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["OVERSEER_LOOP_GROUP_ROOT"] = str(root)
        env["OVERSEER_FINITE_LOOP_ROOT"] = str(finite_root)
        return subprocess.run(
            ["/run/current-system/sw/bin/python3", str(GROUP_SCRIPT), *args],
            check=False,
            text=True,
            capture_output=True,
            env=env,
        )

    def run_finite(self, *args: str, root: pathlib.Path) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["OVERSEER_FINITE_LOOP_ROOT"] = str(root)
        return subprocess.run(
            ["/run/current-system/sw/bin/python3", str(FINITE_SCRIPT), *args],
            check=False,
            text=True,
            capture_output=True,
            env=env,
        )

    def test_create_group_writes_status_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            result = self.run_group(
                "create",
                "--purpose",
                "Keep stable loop cohort for repo hygiene",
                "--stability-class",
                "stable",
                "--coordination-mode",
                "serial",
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(status["state"], "planned")
            self.assertEqual(status["member_count"], 0)
            latest = json.loads((group_root / "latest.json").read_text())
            self.assertEqual(latest["group_id"], status["group_id"])
            index = json.loads((group_root / "index.json").read_text())
            self.assertEqual(index["planned"][0]["group_id"], status["group_id"])
            self.assertEqual(index["active"], [])
            self.assertEqual(index["paused"], [])

    def test_attach_loop_updates_member_count(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            loop = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Test loop membership",
                    "--turn-budget",
                    "3",
                    root=finite_root,
                ).stdout
            )
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Experimental grouping",
                    "--stability-class",
                    "experimental",
                    "--coordination-mode",
                    "parallel",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            result = self.run_group(
                "attach-loop",
                "--group-id",
                group["group_id"],
                "--loop-id",
                loop["loop_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(status["state"], "active")
            self.assertEqual(status["member_count"], 1)
            self.assertEqual(status["member_loop_ids"], [loop["loop_id"]])
            index = json.loads((group_root / "index.json").read_text())
            self.assertEqual(index["active"][0]["group_id"], group["group_id"])

    def test_retire_group_writes_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Unstable retry cohort",
                    "--stability-class",
                    "unstable",
                    "--coordination-mode",
                    "rolling",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            result = self.run_group(
                "retire",
                "--group-id",
                group["group_id"],
                "--outcome",
                "retired",
                "--summary",
                "Superseded by a cleaner cohort",
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(status["state"], "retired")
            receipt = json.loads((group_root / "receipts" / f"{group['group_id']}.json").read_text())
            self.assertEqual(receipt["outcome"], "retired")
            index = json.loads((group_root / "index.json").read_text())
            self.assertEqual(index["terminal"][0]["group_id"], group["group_id"])

    def test_reconcile_pauses_group_when_all_members_are_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            loop = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Terminal loop",
                    "--turn-budget",
                    "1",
                    root=finite_root,
                ).stdout
            )
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Reconstruction cohort",
                    "--stability-class",
                    "unstable",
                    "--coordination-mode",
                    "serial",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            self.run_group(
                "attach-loop",
                "--group-id",
                group["group_id"],
                "--loop-id",
                loop["loop_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.run_finite(
                "complete",
                "--loop-id",
                loop["loop_id"],
                "--outcome",
                "completed",
                "--summary",
                "done",
                "--turns-consumed",
                "1",
                root=finite_root,
            )
            result = self.run_group(
                "reconcile",
                "--group-id",
                group["group_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(status["state"], "paused")
            self.assertEqual(status["member_state_counts"]["completed"], 1)
            self.assertIn("reconstruction_resume_hint", status)
            index = json.loads((group_root / "index.json").read_text())
            self.assertEqual(index["paused"][0]["group_id"], group["group_id"])

    def test_reconstruct_writes_group_recovery_packet(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            loop = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Recover grouped loop",
                    "--turn-budget",
                    "2",
                    root=finite_root,
                ).stdout
            )
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Recovery cohort",
                    "--stability-class",
                    "stable",
                    "--coordination-mode",
                    "serial",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            self.run_group(
                "attach-loop",
                "--group-id",
                group["group_id"],
                "--loop-id",
                loop["loop_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.run_finite(
                "checkpoint",
                "--loop-id",
                loop["loop_id"],
                "--phase",
                "delegated-turn",
                "--summary",
                "working",
                "--resume-hint",
                "resume",
                root=finite_root,
            )
            result = self.run_group(
                "reconstruct",
                "--group-id",
                group["group_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["group_id"], group["group_id"])
            self.assertEqual(packet["suggested_action"], "reopen-active-lineages")
            self.assertEqual(packet["member_reopen_order"][0]["loop_id"], loop["loop_id"])
            self.assertEqual(packet["lineage_count"], 1)
            self.assertEqual(packet["lineage_state_counts"]["active"], 1)
            self.assertEqual(packet["lineage_reopen_order"][0]["tip_loop_id"], loop["loop_id"])
            self.assertTrue((group_root / "recovery" / f"{group['group_id']}.json").exists())
            latest = json.loads((group_root / "recovery" / "latest.json").read_text())
            self.assertEqual(latest["group_id"], group["group_id"])

    def test_reconstruct_prefers_planned_lineage_tip(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            source = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Root grouped loop",
                    "--turn-budget",
                    "1",
                    root=finite_root,
                ).stdout
            )
            follow = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Grouped followup loop",
                    "--turn-budget",
                    "2",
                    "--followup-of",
                    source["loop_id"],
                    "--lineage-root",
                    source["loop_id"],
                    "--lineage-depth",
                    "1",
                    "--spawn-reason",
                    "followup",
                    root=finite_root,
                ).stdout
            )
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Lineage-aware reconstruction",
                    "--stability-class",
                    "stable",
                    "--coordination-mode",
                    "serial",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            self.run_group(
                "attach-loop",
                "--group-id",
                group["group_id"],
                "--loop-id",
                source["loop_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.run_finite(
                "complete",
                "--loop-id",
                source["loop_id"],
                "--outcome",
                "completed",
                "--summary",
                "root finished",
                "--turns-consumed",
                "1",
                root=finite_root,
            )
            turns_root = finite_root / "runs" / follow["loop_id"] / "turns"
            turns_root.mkdir(parents=True, exist_ok=True)
            (turns_root / "turn-0001.json").write_text(
                json.dumps(
                    {
                        "execution_mode": "fresh",
                        "execution_mode_reason": "requested_resume_demoted_by_cold_required",
                        "resume_demoted_reason": "auth_context_mismatch_requires_fresh_session",
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            result = self.run_group(
                "reconstruct",
                "--group-id",
                group["group_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["suggested_action"], "reopen-planned-lineages")
            self.assertEqual(packet["lineage_count"], 1)
            self.assertEqual(packet["lineage_state_counts"]["planned"], 1)
            self.assertEqual(packet["member_lineages"][0]["tip_loop_id"], follow["loop_id"])
            self.assertEqual(packet["member_lineages"][0]["attached_loop_ids"], [source["loop_id"]])
            self.assertEqual(packet["member_lineages"][0]["tip_continuity_status"], "cold-required")
            self.assertEqual(packet["member_lineages"][0]["tip_last_execution_mode"], "fresh")
            self.assertEqual(
                packet["member_lineages"][0]["tip_last_execution_mode_reason"],
                "requested_resume_demoted_by_cold_required",
            )
            self.assertEqual(
                packet["member_lineages"][0]["tip_last_resume_demoted_reason"],
                "auth_context_mismatch_requires_fresh_session",
            )
            self.assertEqual(packet["lineage_reopen_order"][0]["tip_loop_id"], follow["loop_id"])
            self.assertEqual(
                packet["lineage_reopen_order"][0]["tip_last_execution_mode_reason"],
                "requested_resume_demoted_by_cold_required",
            )
            self.assertIn(
                str(finite_root / "runs" / follow["loop_id"] / "status.json"),
                packet["reopen_order"],
            )

    def test_reconstruct_prefers_lineage_successor_from_terminal_tip(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            source = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Root terminal loop",
                    "--turn-budget",
                    "1",
                    root=finite_root,
                ).stdout
            )
            follow = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Terminal followup loop",
                    "--turn-budget",
                    "1",
                    "--followup-of",
                    source["loop_id"],
                    "--lineage-root",
                    source["loop_id"],
                    "--lineage-depth",
                    "1",
                    "--spawn-reason",
                    "followup",
                    root=finite_root,
                ).stdout
            )
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Terminal lineage successor",
                    "--stability-class",
                    "unstable",
                    "--coordination-mode",
                    "serial",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            self.run_group(
                "attach-loop",
                "--group-id",
                group["group_id"],
                "--loop-id",
                source["loop_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.run_finite(
                "complete",
                "--loop-id",
                source["loop_id"],
                "--outcome",
                "completed",
                "--summary",
                "source done",
                "--turns-consumed",
                "1",
                root=finite_root,
            )
            self.run_finite(
                "complete",
                "--loop-id",
                follow["loop_id"],
                "--outcome",
                "completed",
                "--summary",
                "follow done",
                "--turns-consumed",
                "1",
                root=finite_root,
            )
            follow_run_root = finite_root / "runs" / follow["loop_id"]
            status_path = follow_run_root / "status.json"
            status = json.loads(status_path.read_text())
            status.update(
                {
                    "last_turn_outcome": "completed",
                    "last_task_state": "needs successor",
                    "last_resume_hint": "Spawn the next bounded follow-up",
                }
            )
            status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            turns_root = follow_run_root / "turns"
            turns_root.mkdir(parents=True, exist_ok=True)
            (turns_root / "turn-0001.json").write_text(
                json.dumps(
                    {
                        "turn_response": {
                            "outcome": "continue",
                            "summary": "A successor loop should take the next bounded step",
                            "resume_hint": "Spawn the next bounded follow-up",
                            "next_turn_prompt": "Inspect the remaining tail work and write the next receipt.",
                            "task_state": "midstream",
                            "needs_human": False,
                            "confidence": "medium",
                            "evidence_paths": [],
                        }
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            self.run_finite(
                "reconstruct",
                "--loop-id",
                follow["loop_id"],
                root=finite_root,
            )
            result = self.run_group(
                "reconstruct",
                "--group-id",
                group["group_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["suggested_action"], "spawn-lineage-successor")
            self.assertEqual(packet["lineage_state_counts"]["paused"], 1)
            self.assertEqual(packet["member_lineages"][0]["tip_loop_id"], follow["loop_id"])
            self.assertEqual(packet["member_lineages"][0]["suggested_action"], "spawn-lineage-successor")

    def test_reconcile_keeps_capacity_deferred_lineage_planned(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            loop = json.loads(
                self.run_finite(
                    "create",
                    "--task-summary",
                    "Capacity deferred loop",
                    "--turn-budget",
                    "5",
                    root=finite_root,
                ).stdout
            )
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Capacity waiting cohort",
                    "--stability-class",
                    "experimental",
                    "--coordination-mode",
                    "serial",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            self.run_group(
                "attach-loop",
                "--group-id",
                group["group_id"],
                "--loop-id",
                loop["loop_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.run_finite(
                "checkpoint",
                "--loop-id",
                loop["loop_id"],
                "--state",
                "planned",
                "--phase",
                "waiting_for_capacity",
                "--summary",
                "loop turn deferred under interactive or queue pressure",
                "--resume-hint",
                "retry when capacity changes",
                root=finite_root,
            )
            self.run_finite(
                "hold",
                "--loop-id",
                loop["loop_id"],
                "--hold-reason",
                "capacity",
                "--requested-by",
                "finite-loop-executor",
                "--resume-authority",
                "interactive",
                "--resume-precondition",
                "interactive lease released",
                "--summary",
                "loop turn deferred under interactive or queue pressure",
                root=finite_root,
            )
            result = self.run_group(
                "reconcile",
                "--group-id",
                group["group_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(status["state"], "planned")
            self.assertEqual(status["lineage_state_counts"]["planned"], 1)
            self.assertIn("waiting for execution or capacity", status["reconstruction_summary"])
            self.assertIn("explicitly held", json.dumps(status["member_lineages"]))

    def test_reconstruct_terminal_group_marks_terminal_action(self) -> None:
        with tempfile.TemporaryDirectory() as group_tmpdir, tempfile.TemporaryDirectory() as finite_tmpdir:
            group_root = pathlib.Path(group_tmpdir)
            finite_root = pathlib.Path(finite_tmpdir)
            group = json.loads(
                self.run_group(
                    "create",
                    "--purpose",
                    "Terminal recovery cohort",
                    "--stability-class",
                    "experimental",
                    "--coordination-mode",
                    "serial",
                    root=group_root,
                    finite_root=finite_root,
                ).stdout
            )
            self.run_group(
                "retire",
                "--group-id",
                group["group_id"],
                "--outcome",
                "retired",
                "--summary",
                "finished cohort",
                root=group_root,
                finite_root=finite_root,
            )
            result = self.run_group(
                "reconstruct",
                "--group-id",
                group["group_id"],
                root=group_root,
                finite_root=finite_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["state"], "retired")
            self.assertEqual(packet["suggested_action"], "inspect-terminal-group")
            self.assertIn("terminal", packet["reconstruction_summary"])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


EXECUTOR_PATH = pathlib.Path("/home/overseer/scripts/finite_loop_executor.py")
SPEC = importlib.util.spec_from_file_location("finite_loop_executor", EXECUTOR_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FiniteLoopExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tempdir.name)
        self.finite_root = self.root / "finite"
        self.group_root = self.root / "groups"
        self.control_root = self.root / "loop-control"
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.run_root = self.finite_root / "runs" / "loop-1"
        self.run_root.mkdir(parents=True)
        self.runtime = {
            "runtime_root": str(self.finite_root / "runtime" / "loop-1"),
            "codex_home": str(self.finite_root / "runtime" / "loop-1" / "codex-home"),
            "active_auth_path": str(self.finite_root / "runtime" / "loop-1" / "codex-home" / "auth.json"),
            "workspace_mode": "git-worktree",
            "workspace_path": str(self.root / "worktrees" / "loop-1"),
            "source_workspace": str(self.workspace),
            "runtime_lock_scope": "profile",
            "runtime_lock_root": str(self.root / "runtime-locks"),
        }
        MODULE.FINITE_ROOT = self.finite_root
        MODULE.GROUP_ROOT = self.group_root
        MODULE.LOOP_CONTROL_ROOT = self.control_root

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_status(self, payload: dict) -> None:
        path = self.run_root / "status.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_continue_turn_updates_loop_checkpoint(self) -> None:
        self.write_status(
            {
                "loop_id": "loop-1",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-10T00:00:00Z",
                "state": "planned",
                "phase": "planned",
                "task_summary": "Inspect the repo and continue if more work remains",
                "turn_budget_total": 3,
                "turn_budget_remaining": 3,
                "turn_count": 0,
                "session_policy": "separate-session",
                "continuity_status": "cold-required",
                "consumer_id": "loop-1",
                "consumer_class": "daemon",
                "interactive_priority": True,
            }
        )

        def fake_finite_registry(args: list[str]) -> dict:
            if args[0] == "checkpoint":
                phase = args[args.index("--phase") + 1]
                if phase == "turn-1-starting":
                    payload = {
                        "loop_id": "loop-1",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-10T00:00:30Z",
                        "state": "running",
                        "phase": "turn-1-starting",
                        "task_summary": "Inspect the repo and continue if more work remains",
                        "turn_budget_total": 3,
                        "turn_budget_remaining": 3,
                        "turn_count": 0,
                        "session_policy": "separate-session",
                        "continuity_status": "cold-required",
                        "consumer_id": "loop-1",
                        "consumer_class": "daemon",
                        "interactive_priority": True,
                    }
                    self.write_status(payload)
                    return payload
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:01:00Z",
                    "state": "running",
                    "phase": "turn-1",
                    "task_summary": "Inspect the repo and continue if more work remains",
                    "turn_budget_total": 3,
                    "turn_budget_remaining": 2,
                    "turn_count": 1,
                    "session_policy": "separate-session",
                    "continuity_status": "warm-resume",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                }
                self.write_status(payload)
                return payload
            if args[0] == "hold":
                payload = json.loads((self.run_root / "status.json").read_text())
                payload["hold"] = {
                    "hold_status": "held",
                    "hold_reason": "capacity",
                    "hold_scope": "loop",
                    "requested_by": "finite-loop-executor",
                    "requested_at": "2026-03-10T00:00:21Z",
                    "resume_authority": "interactive",
                    "resume_preconditions": ["interactive lease released or daemon queue pressure reduced"],
                    "review_paths": [
                        "/home/overseer/state/codex-load-balancer/leases.json",
                        "/home/overseer/state/codex-load-balancer/queue.json",
                    ],
                    "summary": "loop turn deferred under interactive or queue pressure",
                    "expires_at": None,
                    "released_at": None,
                    "release_reason": None,
                }
                self.write_status(payload)
                return payload
            if args[0] == "hold":
                payload = json.loads((self.run_root / "status.json").read_text())
                payload["hold"] = {
                    "hold_status": "held",
                    "hold_reason": "capacity",
                    "hold_scope": "loop",
                    "requested_by": "finite-loop-executor",
                    "requested_at": "2026-03-10T00:00:21Z",
                    "resume_authority": "interactive",
                    "resume_preconditions": ["interactive lease released or daemon queue pressure reduced"],
                    "review_paths": [
                        "/home/overseer/state/codex-load-balancer/leases.json",
                        "/home/overseer/state/codex-load-balancer/queue.json",
                    ],
                    "summary": "loop turn deferred under interactive or queue pressure",
                    "expires_at": None,
                    "released_at": None,
                    "release_reason": None,
                }
                self.write_status(payload)
                return payload
            if args[0] == "hold":
                payload = json.loads((self.run_root / "status.json").read_text())
                payload["hold"] = {
                    "hold_status": "held",
                    "hold_reason": "capacity",
                    "hold_scope": "loop",
                    "requested_by": "finite-loop-executor",
                    "requested_at": "2026-03-10T00:00:21Z",
                    "resume_authority": "interactive",
                    "resume_preconditions": ["interactive lease released or daemon queue pressure reduced"],
                    "review_paths": [
                        "/home/overseer/state/codex-load-balancer/leases.json",
                        "/home/overseer/state/codex-load-balancer/queue.json",
                    ],
                    "summary": "loop turn deferred under interactive or queue pressure",
                    "expires_at": None,
                    "released_at": None,
                    "release_reason": None,
                }
                self.write_status(payload)
                return payload
            if args[0] == "hold":
                payload = json.loads((self.run_root / "status.json").read_text())
                payload["hold"] = {
                    "hold_status": "held",
                    "hold_reason": "capacity",
                    "hold_scope": "loop",
                    "requested_by": "finite-loop-executor",
                    "requested_at": "2026-03-10T00:00:21Z",
                    "resume_authority": "interactive",
                    "resume_preconditions": ["interactive lease released or daemon queue pressure reduced"],
                    "review_paths": [
                        "/home/overseer/state/codex-load-balancer/leases.json",
                        "/home/overseer/state/codex-load-balancer/queue.json",
                    ],
                    "summary": "loop turn deferred under interactive or queue pressure",
                    "expires_at": None,
                    "released_at": None,
                    "release_reason": None,
                }
                self.write_status(payload)
                return payload
            raise AssertionError(args)

        def fake_run_runner(**kwargs) -> int:
            live_status = json.loads((self.run_root / "status.json").read_text())
            self.assertEqual(live_status["state"], "running")
            self.assertEqual(live_status["phase"], "turn-1-starting")
            self.assertEqual(live_status["executor_state"], "running")
            message_path = kwargs["message_path"]
            meta_path = kwargs["meta_path"]
            MODULE.write_json(
                message_path,
                {
                    "outcome": "continue",
                    "summary": "Read the repo and found the next executor task",
                    "resume_hint": "Run the next bounded turn with the executor contract again",
                    "next_turn_prompt": "Continue the repo executor setup and leave receipts",
                    "task_state": "executor prep underway",
                    "needs_human": False,
                    "confidence": "medium",
                    "evidence_paths": ["/home/overseer/README.md"],
                },
            )
            MODULE.write_json(
                meta_path,
                {
                    "selected_profile": "A1",
                    "completed_session": "sess-1",
                    "execution_mode": "fresh",
                    "execution_mode_reason": "no_requested_session",
                    "run_receipt": "/tmp/run.json",
                    "latest_checkpoint": "/tmp/checkpoint.json",
                    "evidence_packet": "/tmp/evidence.json",
                    "selection": {"continuity_status": "warm-resume"},
                },
            )
            return 0

        with (
            mock.patch.object(MODULE, "finite_registry", side_effect=fake_finite_registry),
            mock.patch.object(MODULE, "group_registry"),
            mock.patch.object(MODULE, "prepare_runtime", return_value=self.runtime),
            mock.patch.object(MODULE, "run_runner", side_effect=fake_run_runner),
            mock.patch.object(sys, "argv", [str(EXECUTOR_PATH), "--loop-id", "loop-1", "--workspace", str(self.workspace)]),
        ):
            rc = MODULE.main()

        self.assertEqual(rc, 0)
        latest = json.loads((self.run_root / "executor-latest.json").read_text())
        self.assertEqual(latest["turns"][0]["turn_response"]["outcome"], "continue")
        self.assertEqual(latest["turns"][0]["execution_mode_reason"], "no_requested_session")
        status = json.loads((self.run_root / "status.json").read_text())
        self.assertEqual(status["last_session_id"], "sess-1")
        self.assertEqual(status["last_turn_outcome"], "continue")

    def test_run_runner_does_not_forward_search_flag_to_codex_exec(self) -> None:
        schema_path = self.run_root / "turns" / "turn-0001.schema.json"
        message_path = self.run_root / "turns" / "turn-0001.response.json"
        meta_path = self.run_root / "turns" / "turn-0001.meta.json"
        captured = {}

        def fake_subprocess_run(command, check=False):
            captured["command"] = command
            return mock.Mock(returncode=0)

        loop_status = {
            "consumer_id": "loop-1",
            "requested_profile": "A5",
            "last_session_id": None,
        }

        with mock.patch.object(MODULE.subprocess, "run", side_effect=fake_subprocess_run):
            rc = MODULE.run_runner(
                loop_status=loop_status,
                runtime=self.runtime,
                prompt="do the thing",
                schema_path=schema_path,
                message_path=message_path,
                meta_path=meta_path,
                requested_profile="A5",
                wait_seconds=60,
                enable_search=True,
            )

        self.assertEqual(rc, 0)
        self.assertIn("--", captured["command"])
        self.assertNotIn("--search", captured["command"])
        self.assertIn("--output-schema", captured["command"])
        self.assertIn(str(schema_path), captured["command"])
        self.assertIn(str(message_path), captured["command"])

    def test_terminal_turn_completes_loop(self) -> None:
        self.write_status(
            {
                "loop_id": "loop-1",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-10T00:00:00Z",
                "state": "running",
                "phase": "turn-1",
                "task_summary": "Finish the task",
                "turn_budget_total": 2,
                "turn_budget_remaining": 1,
                "turn_count": 1,
                "session_policy": "separate-session",
                "continuity_status": "warm-resume",
                "consumer_id": "loop-1",
                "consumer_class": "daemon",
                "interactive_priority": True,
                "last_session_id": "sess-1",
            }
        )

        def fake_finite_registry(args: list[str]) -> dict:
            if args[0] == "checkpoint":
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:01:30Z",
                    "state": "running",
                    "phase": "turn-2-starting",
                    "task_summary": "Finish the task",
                    "turn_budget_total": 2,
                    "turn_budget_remaining": 1,
                    "turn_count": 1,
                    "session_policy": "separate-session",
                    "continuity_status": "warm-resume",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                    "last_session_id": "sess-1",
                }
                self.write_status(payload)
                return payload
            if args[0] == "complete":
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:02:00Z",
                    "state": "completed",
                    "phase": "terminal",
                    "task_summary": "Finish the task",
                    "turn_budget_total": 2,
                    "turn_budget_remaining": 0,
                    "turn_count": 2,
                    "session_policy": "separate-session",
                    "continuity_status": "warm-resume",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                    "final_summary": "Task finished cleanly",
                }
                self.write_status(payload)
                return payload
            raise AssertionError(args)

        def fake_run_runner(**kwargs) -> int:
            MODULE.write_json(
                kwargs["message_path"],
                {
                    "outcome": "completed",
                    "summary": "Task finished cleanly",
                    "resume_hint": "No more turns needed",
                    "next_turn_prompt": "",
                    "task_state": "done",
                    "needs_human": False,
                    "confidence": "high",
                    "evidence_paths": [],
                },
            )
            MODULE.write_json(
                kwargs["meta_path"],
                {
                    "selected_profile": "A1",
                    "completed_session": "sess-1",
                    "execution_mode": "resume",
                    "run_receipt": "/tmp/run.json",
                    "latest_checkpoint": "/tmp/checkpoint.json",
                    "evidence_packet": "/tmp/evidence.json",
                    "selection": {"continuity_status": "warm-resume"},
                },
            )
            return 0

        with (
            mock.patch.object(MODULE, "finite_registry", side_effect=fake_finite_registry),
            mock.patch.object(MODULE, "group_registry"),
            mock.patch.object(MODULE, "prepare_runtime", return_value=self.runtime),
            mock.patch.object(MODULE, "run_runner", side_effect=fake_run_runner),
            mock.patch.object(sys, "argv", [str(EXECUTOR_PATH), "--loop-id", "loop-1", "--workspace", str(self.workspace)]),
        ):
            rc = MODULE.main()

        self.assertEqual(rc, 0)
        latest = json.loads((self.run_root / "executor-latest.json").read_text())
        self.assertEqual(latest["terminal_outcome"], "completed")
        status = json.loads((self.run_root / "status.json").read_text())
        self.assertEqual(status["executor_state"], "terminal")
        self.assertEqual(status["last_turn_outcome"], "completed")

    def test_group_attach_and_checkpoint_happen(self) -> None:
        self.write_status(
            {
                "loop_id": "loop-1",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-10T00:00:00Z",
                "state": "planned",
                "phase": "planned",
                "task_summary": "Group-aware turn",
                "turn_budget_total": 2,
                "turn_budget_remaining": 2,
                "turn_count": 0,
                "session_policy": "separate-session",
                "continuity_status": "cold-required",
                "consumer_id": "loop-1",
                "consumer_class": "daemon",
                "interactive_priority": True,
            }
        )
        group_calls: list[list[str]] = []

        def fake_group_registry(args: list[str]) -> dict:
            group_calls.append(args)
            if args[0] in {"attach-loop", "checkpoint"}:
                return {"status": "ok"}
            if args[0] == "reconcile":
                return {
                    "group_id": "group-1",
                    "state": "active",
                    "purpose": "Executor cohort",
                    "stability_class": "stable",
                    "coordination_mode": "serial",
                    "member_count": 1,
                }
            if args[0] == "status":
                return {
                    "group_id": "group-1",
                    "state": "active",
                    "purpose": "Executor cohort",
                    "stability_class": "stable",
                    "coordination_mode": "serial",
                    "member_count": 1,
                    "summary": "Group summary",
                    "resume_hint": "Resume group work",
                }
            raise AssertionError(args)

        def fake_finite_registry(args: list[str]) -> dict:
            if args[0] == "checkpoint":
                phase = args[args.index("--phase") + 1]
                if phase == "turn-1-starting":
                    payload = {
                        "loop_id": "loop-1",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-10T00:00:30Z",
                        "state": "running",
                        "phase": "turn-1-starting",
                        "task_summary": "Group-aware turn",
                        "turn_budget_total": 2,
                        "turn_budget_remaining": 2,
                        "turn_count": 0,
                        "session_policy": "separate-session",
                        "continuity_status": "cold-required",
                        "consumer_id": "loop-1",
                        "consumer_class": "daemon",
                        "interactive_priority": True,
                    }
                    self.write_status(payload)
                    return payload
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:01:00Z",
                    "state": "running",
                    "phase": "turn-1",
                    "task_summary": "Group-aware turn",
                    "turn_budget_total": 2,
                    "turn_budget_remaining": 1,
                    "turn_count": 1,
                    "session_policy": "separate-session",
                    "continuity_status": "warm-resume",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                }
                self.write_status(payload)
                return payload
            raise AssertionError(args)

        def fake_run_runner(**kwargs) -> int:
            MODULE.write_json(
                kwargs["message_path"],
                {
                    "outcome": "continue",
                    "summary": "Grouped turn made progress",
                    "resume_hint": "Continue grouped work",
                    "next_turn_prompt": "Advance the grouped loop again",
                    "task_state": "group task in progress",
                    "needs_human": False,
                    "confidence": "medium",
                    "evidence_paths": [],
                },
            )
            MODULE.write_json(
                kwargs["meta_path"],
                {
                    "selected_profile": "A2",
                    "completed_session": "sess-2",
                    "execution_mode": "fresh",
                    "execution_mode_reason": "requested_resume_demoted_by_cold_required",
                    "resume_demoted_reason": "auth_context_mismatch_requires_fresh_session",
                    "run_receipt": "/tmp/run.json",
                    "latest_checkpoint": "/tmp/checkpoint.json",
                    "evidence_packet": "/tmp/evidence.json",
                    "selection": {"continuity_status": "cold-required"},
                },
            )
            return 0

        with (
            mock.patch.object(MODULE, "finite_registry", side_effect=fake_finite_registry),
            mock.patch.object(MODULE, "group_registry", side_effect=fake_group_registry),
            mock.patch.object(MODULE, "prepare_runtime", return_value=self.runtime),
            mock.patch.object(MODULE, "run_runner", side_effect=fake_run_runner),
            mock.patch.object(sys, "argv", [str(EXECUTOR_PATH), "--loop-id", "loop-1", "--group-id", "group-1", "--workspace", str(self.workspace)]),
        ):
            rc = MODULE.main()

        self.assertEqual(rc, 0)
        self.assertTrue(any(call[0] == "attach-loop" for call in group_calls))
        self.assertTrue(any(call[0] == "checkpoint" for call in group_calls))
        latest = json.loads((self.run_root / "executor-latest.json").read_text())
        self.assertEqual(
            latest["turns"][0]["execution_mode_reason"],
            "requested_resume_demoted_by_cold_required",
        )
        self.assertEqual(
            latest["turns"][0]["resume_demoted_reason"],
            "auth_context_mismatch_requires_fresh_session",
        )

    def test_deferred_turn_stays_planned_and_pending_capacity(self) -> None:
        self.write_status(
            {
                "loop_id": "loop-1",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-10T00:00:00Z",
                "state": "planned",
                "phase": "planned",
                "task_summary": "Wait honestly under interactive pressure",
                "turn_budget_total": 5,
                "turn_budget_remaining": 5,
                "turn_count": 0,
                "session_policy": "separate-session",
                "continuity_status": "cold-required",
                "consumer_id": "loop-1",
                "consumer_class": "daemon",
                "interactive_priority": True,
            }
        )
        group_calls: list[list[str]] = []

        def fake_group_registry(args: list[str]) -> dict:
            group_calls.append(args)
            if args[0] in {"attach-loop", "checkpoint"}:
                return {"status": "ok"}
            if args[0] == "reconcile":
                return {
                    "group_id": "group-1",
                    "state": "planned",
                    "purpose": "Observed experiments",
                    "stability_class": "experimental",
                    "coordination_mode": "serial",
                    "member_count": 1,
                }
            if args[0] == "status":
                return {
                    "group_id": "group-1",
                    "state": "planned",
                    "purpose": "Observed experiments",
                    "stability_class": "experimental",
                    "coordination_mode": "serial",
                    "member_count": 1,
                }
            raise AssertionError(args)

        def fake_finite_registry(args: list[str]) -> dict:
            if args[0] == "checkpoint":
                phase = args[args.index("--phase") + 1]
                if phase == "turn-1-starting":
                    payload = {
                        "loop_id": "loop-1",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-10T00:00:10Z",
                        "state": "running",
                        "phase": "turn-1-starting",
                        "task_summary": "Wait honestly under interactive pressure",
                        "turn_budget_total": 5,
                        "turn_budget_remaining": 5,
                        "turn_count": 0,
                        "session_policy": "separate-session",
                        "continuity_status": "cold-required",
                        "consumer_id": "loop-1",
                        "consumer_class": "daemon",
                        "interactive_priority": True,
                    }
                    self.write_status(payload)
                    return payload
                self.assertIn("--state", args)
                self.assertEqual(args[args.index("--state") + 1], "planned")
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:00:20Z",
                    "state": "planned",
                    "phase": "waiting_for_capacity",
                    "task_summary": "Wait honestly under interactive pressure",
                    "turn_budget_total": 5,
                    "turn_budget_remaining": 5,
                    "turn_count": 0,
                    "session_policy": "separate-session",
                    "continuity_status": "cold-required",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                    "last_summary": "loop turn deferred under interactive or queue pressure",
                    "last_resume_hint": "retry through the shared load balancer when pressure changes",
                }
                self.write_status(payload)
                return payload
            if args[0] == "hold":
                payload = json.loads((self.run_root / "status.json").read_text())
                payload["hold"] = {
                    "hold_status": "held",
                    "hold_reason": "capacity",
                    "hold_scope": "loop",
                    "requested_by": "finite-loop-executor",
                    "requested_at": "2026-03-10T00:00:21Z",
                    "resume_authority": "interactive",
                    "resume_preconditions": ["interactive lease released or daemon queue pressure reduced"],
                    "review_paths": [
                        "/home/overseer/state/codex-load-balancer/leases.json",
                        "/home/overseer/state/codex-load-balancer/queue.json",
                    ],
                    "summary": "loop turn deferred under interactive or queue pressure",
                    "expires_at": None,
                    "released_at": None,
                    "release_reason": None,
                }
                self.write_status(payload)
                return payload
            raise AssertionError(args)

        def fake_run_runner(**kwargs) -> int:
            MODULE.write_json(kwargs["meta_path"], {"runner_exit_code": 30})
            return 30

        with (
            mock.patch.object(MODULE, "finite_registry", side_effect=fake_finite_registry),
            mock.patch.object(MODULE, "group_registry", side_effect=fake_group_registry),
            mock.patch.object(MODULE, "prepare_runtime", return_value=self.runtime),
            mock.patch.object(MODULE, "run_runner", side_effect=fake_run_runner),
            mock.patch.object(
                sys,
                "argv",
                [str(EXECUTOR_PATH), "--loop-id", "loop-1", "--group-id", "group-1", "--workspace", str(self.workspace)],
            ),
        ):
            rc = MODULE.main()

        self.assertEqual(rc, 30)
        latest = json.loads((self.run_root / "executor-latest.json").read_text())
        self.assertEqual(latest["terminal_outcome"], "deferred")
        status = json.loads((self.run_root / "status.json").read_text())
        self.assertEqual(status["state"], "planned")
        self.assertEqual(status["phase"], "waiting_for_capacity")
        self.assertEqual(status["turn_count"], 0)
        self.assertEqual(status["turn_budget_remaining"], 5)
        self.assertEqual(status["executor_state"], "waiting_for_capacity")
        self.assertEqual(status["hold"]["hold_status"], "held")
        self.assertEqual(status["hold"]["hold_reason"], "capacity")
        checkpoint_calls = [call for call in group_calls if call[0] == "checkpoint"]
        self.assertTrue(checkpoint_calls)
        self.assertIn("--state", checkpoint_calls[0])
        self.assertEqual(checkpoint_calls[0][checkpoint_calls[0].index("--state") + 1], "planned")

    def test_invalid_structured_output_fails_loop_truthfully(self) -> None:
        self.write_status(
            {
                "loop_id": "loop-1",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-10T00:00:00Z",
                "state": "planned",
                "phase": "planned",
                "task_summary": "Return invalid output",
                "turn_budget_total": 2,
                "turn_budget_remaining": 2,
                "turn_count": 0,
                "session_policy": "separate-session",
                "continuity_status": "cold-required",
                "consumer_id": "loop-1",
                "consumer_class": "daemon",
                "interactive_priority": True,
            }
        )

        def fake_finite_registry(args: list[str]) -> dict:
            if args[0] == "checkpoint":
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:00:30Z",
                    "state": "running",
                    "phase": "turn-1-starting",
                    "task_summary": "Return invalid output",
                    "turn_budget_total": 2,
                    "turn_budget_remaining": 2,
                    "turn_count": 0,
                    "session_policy": "separate-session",
                    "continuity_status": "cold-required",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                }
                self.write_status(payload)
                return payload
            if args[0] == "complete":
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:01:00Z",
                    "state": "failed",
                    "phase": "terminal",
                    "task_summary": "Return invalid output",
                    "turn_budget_total": 2,
                    "turn_budget_remaining": 1,
                    "turn_count": 1,
                    "session_policy": "separate-session",
                    "continuity_status": "cold-required",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                    "final_summary": "bad output",
                }
                self.write_status(payload)
                return payload
            raise AssertionError(args)

        def fake_run_runner(**kwargs) -> int:
            MODULE.write_json(kwargs["message_path"], {"oops": "wrong"})
            MODULE.write_json(
                kwargs["meta_path"],
                {
                    "selected_profile": "A1",
                    "completed_session": "sess-3",
                    "execution_mode": "fresh",
                    "run_receipt": "/tmp/run.json",
                    "latest_checkpoint": "/tmp/checkpoint.json",
                    "evidence_packet": "/tmp/evidence.json",
                    "selection": {"continuity_status": "cold-required"},
                },
            )
            return 0

        with (
            mock.patch.object(MODULE, "finite_registry", side_effect=fake_finite_registry),
            mock.patch.object(MODULE, "group_registry"),
            mock.patch.object(MODULE, "prepare_runtime", return_value=self.runtime),
            mock.patch.object(MODULE, "run_runner", side_effect=fake_run_runner),
            mock.patch.object(sys, "argv", [str(EXECUTOR_PATH), "--loop-id", "loop-1", "--workspace", str(self.workspace)]),
        ):
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = MODULE.main()

        self.assertEqual(rc, 41)
        self.assertIn("turn response missing keys", stderr.getvalue())
        latest = json.loads((self.run_root / "executor-latest.json").read_text())
        self.assertEqual(latest["terminal_outcome"], "failed")
        status = json.loads((self.run_root / "status.json").read_text())
        self.assertEqual(status["executor_state"], "failed")

    def test_cancel_before_turn_control_note_short_circuits_runner(self) -> None:
        control_root = self.root / "loop-control" / "notes"
        control_root.mkdir(parents=True, exist_ok=True)
        (control_root / "loop-1.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "loop_id": "loop-1",
                    "action": "cancel-before-turn",
                    "summary": "Cancel before the next turn begins.",
                    "updated_at": "2026-03-12T00:10:00Z",
                }
            ),
            encoding="utf-8",
        )
        self.write_status(
            {
                "loop_id": "loop-1",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-10T00:00:00Z",
                "state": "planned",
                "phase": "planned",
                "task_summary": "Cancelled by control note",
                "turn_budget_total": 2,
                "turn_budget_remaining": 2,
                "turn_count": 0,
                "session_policy": "separate-session",
                "continuity_status": "cold-required",
                "consumer_id": "loop-1",
                "consumer_class": "daemon",
                "interactive_priority": True,
            }
        )

        def fake_finite_registry(args: list[str]) -> dict:
            if args[0] == "complete":
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:02:00Z",
                    "state": "cancelled",
                    "phase": "terminal",
                    "task_summary": "Cancelled by control note",
                    "turn_budget_total": 2,
                    "turn_budget_remaining": 2,
                    "turn_count": 0,
                    "session_policy": "separate-session",
                    "continuity_status": "cold-required",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                    "final_summary": "loop cancelled before turn by control note",
                }
                self.write_status(payload)
                return payload
            raise AssertionError(args)

        with (
            mock.patch.object(MODULE, "finite_registry", side_effect=fake_finite_registry),
            mock.patch.object(MODULE, "group_registry"),
            mock.patch.object(MODULE, "prepare_runtime", return_value=self.runtime),
            mock.patch.object(MODULE, "run_runner", side_effect=AssertionError("runner should not be called")),
            mock.patch.object(sys, "argv", [str(EXECUTOR_PATH), "--loop-id", "loop-1", "--workspace", str(self.workspace)]),
        ):
            rc = MODULE.main()

        self.assertEqual(rc, 0)
        status = json.loads((self.run_root / "status.json").read_text())
        self.assertEqual(status["state"], "cancelled")
        control_payload = json.loads((control_root / "loop-1.json").read_text())
        self.assertEqual(control_payload["status"], "consumed")
        self.assertEqual(control_payload["consumed_reason"], "cancel-before-turn")

    def test_hold_after_turn_control_note_holds_loop(self) -> None:
        control_root = self.root / "loop-control" / "notes"
        control_root.mkdir(parents=True, exist_ok=True)
        (control_root / "loop-1.json").write_text(
            json.dumps(
                {
                    "status": "active",
                    "loop_id": "loop-1",
                    "action": "hold-after-turn",
                    "summary": "Hold after the current turn.",
                    "requested_by": "interactive",
                    "updated_at": "2026-03-12T00:10:00Z",
                }
            ),
            encoding="utf-8",
        )
        self.write_status(
            {
                "loop_id": "loop-1",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-10T00:00:00Z",
                "state": "planned",
                "phase": "planned",
                "task_summary": "Hold after a useful turn",
                "turn_budget_total": 3,
                "turn_budget_remaining": 3,
                "turn_count": 0,
                "session_policy": "separate-session",
                "continuity_status": "cold-required",
                "consumer_id": "loop-1",
                "consumer_class": "daemon",
                "interactive_priority": True,
            }
        )

        def fake_finite_registry(args: list[str]) -> dict:
            if args[0] == "checkpoint":
                phase = args[args.index("--phase") + 1]
                if phase == "turn-1-starting":
                    payload = {
                        "loop_id": "loop-1",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-10T00:00:20Z",
                        "state": "running",
                        "phase": "turn-1-starting",
                        "task_summary": "Hold after a useful turn",
                        "turn_budget_total": 3,
                        "turn_budget_remaining": 3,
                        "turn_count": 0,
                        "session_policy": "separate-session",
                        "continuity_status": "cold-required",
                        "consumer_id": "loop-1",
                        "consumer_class": "daemon",
                        "interactive_priority": True,
                    }
                    self.write_status(payload)
                    return payload
                payload = {
                    "loop_id": "loop-1",
                    "created_at": "2026-03-10T00:00:00Z",
                    "updated_at": "2026-03-10T00:01:00Z",
                    "state": "planned",
                    "phase": "held_by_control_note",
                    "task_summary": "Hold after a useful turn",
                    "turn_budget_total": 3,
                    "turn_budget_remaining": 2,
                    "turn_count": 1,
                    "session_policy": "separate-session",
                    "continuity_status": "warm-resume",
                    "consumer_id": "loop-1",
                    "consumer_class": "daemon",
                    "interactive_priority": True,
                    "last_summary": "useful progress",
                    "last_resume_hint": "resume later",
                }
                self.write_status(payload)
                return payload
            if args[0] == "hold":
                payload = json.loads((self.run_root / "status.json").read_text())
                payload["hold"] = {
                    "hold_status": "held",
                    "hold_reason": "operator",
                    "hold_scope": "loop",
                    "requested_by": "interactive",
                    "requested_at": "2026-03-10T00:01:01Z",
                    "resume_authority": "interactive",
                    "resume_preconditions": ["review the loop control note before resuming bounded work"],
                    "review_paths": [str(control_root / "loop-1.json")],
                    "summary": "Hold after the current turn.",
                    "expires_at": None,
                    "released_at": None,
                    "release_reason": None,
                }
                self.write_status(payload)
                return payload
            raise AssertionError(args)

        def fake_run_runner(**kwargs) -> int:
            MODULE.write_json(
                kwargs["message_path"],
                {
                    "outcome": "continue",
                    "summary": "useful progress",
                    "resume_hint": "resume later",
                    "next_turn_prompt": "continue the bounded work later",
                    "task_state": "work partially complete",
                    "needs_human": False,
                    "confidence": "medium",
                    "evidence_paths": [],
                },
            )
            MODULE.write_json(
                kwargs["meta_path"],
                {
                    "selected_profile": "A5",
                    "completed_session": "sess-5",
                    "execution_mode": "fresh",
                    "run_receipt": "/tmp/run.json",
                    "latest_checkpoint": "/tmp/checkpoint.json",
                    "evidence_packet": "/tmp/evidence.json",
                    "selection": {"continuity_status": "warm-resume"},
                },
            )
            return 0

        with (
            mock.patch.object(MODULE, "finite_registry", side_effect=fake_finite_registry),
            mock.patch.object(MODULE, "group_registry"),
            mock.patch.object(MODULE, "prepare_runtime", return_value=self.runtime),
            mock.patch.object(MODULE, "run_runner", side_effect=fake_run_runner),
            mock.patch.object(sys, "argv", [str(EXECUTOR_PATH), "--loop-id", "loop-1", "--workspace", str(self.workspace)]),
        ):
            rc = MODULE.main()

        self.assertEqual(rc, 0)
        latest = json.loads((self.run_root / "executor-latest.json").read_text())
        self.assertEqual(latest["terminal_outcome"], "held")
        status = json.loads((self.run_root / "status.json").read_text())
        self.assertEqual(status["state"], "planned")
        self.assertEqual(status["phase"], "held_by_control_note")
        self.assertEqual(status["hold"]["hold_status"], "held")
        self.assertEqual(status["hold"]["hold_reason"], "operator")
        control_payload = json.loads((control_root / "loop-1.json").read_text())
        self.assertEqual(control_payload["status"], "consumed")
        self.assertEqual(control_payload["consumed_reason"], "hold-after-turn")


if __name__ == "__main__":
    unittest.main()

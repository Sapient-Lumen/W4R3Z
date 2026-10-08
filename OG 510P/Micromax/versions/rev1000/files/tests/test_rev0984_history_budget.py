from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from micromax_editor.buffer import BufferSplice, Cursor
from micromax_editor.editor import Editor, MacroReplaySnapshot
from micromax_editor.option_policy import script_option_policy, script_option_read_policy
from micromax_editor.undo import (
    Edit,
    RetainedTextCharge,
    UndoManager,
    logical_text_bytes,
)

ROOT = Path(__file__).resolve().parents[1]


def _edit(
    name: str,
    *charges: tuple[object, str, int],
    events: list[str] | None = None,
) -> Edit:
    sink = events if events is not None else []
    return Edit(
        undo=lambda: sink.append(f"undo:{name}"),
        redo=lambda: sink.append(f"redo:{name}"),
        description=name,
        retained_text=tuple(
            RetainedTextCharge(owner=owner, label=label, byte_count=size)
            for owner, label, size in charges
        ),
    )


def _closure_snapshot(callback: Callable[[], None]) -> MacroReplaySnapshot:
    snapshots = [
        cell.cell_contents
        for cell in (callback.__closure__ or ())
        if isinstance(cell.cell_contents, MacroReplaySnapshot)
    ]
    assert len(snapshots) == 1
    return snapshots[0]


def test_logical_text_bytes_is_utf8_exact_without_changing_surrogate_policy() -> None:
    text = "ascii-é-🙂-\ud800"
    assert logical_text_bytes(text) == len(text.encode("utf-8", errors="surrogatepass"))
    assert logical_text_bytes("x" * 200_000) == 200_000


def test_undo_manager_accounts_across_undo_and_redo_by_owner_identity() -> None:
    undo = UndoManager()
    owner_a = object()
    owner_b = object()
    undo.record(_edit("one", (owner_a, "a", 3), (owner_b, "b", 7)))
    undo.record(_edit("two", (owner_a, "a", 5)))

    assert undo.retained_text_bytes() == 15
    assert undo.retained_text_bytes(owner_a) == 8
    assert undo.retained_text_bytes(owner_b) == 7
    assert undo.retained_text_bytes(owner_a, include_redo=False) == 8

    assert undo.undo() is True
    assert undo.retained_text_bytes(owner_a) == 8
    assert undo.retained_text_bytes(owner_a, include_redo=False) == 3
    assert undo.redo() is True
    assert undo.retained_text_bytes(owner_a, include_redo=False) == 8


class _CountingCharge:
    def __init__(self, owner: object, byte_count: int, reads: list[int]) -> None:
        self.owner = owner
        self.label = "counted"
        self._byte_count = int(byte_count)
        self._reads = reads

    @property
    def byte_count(self) -> int:
        self._reads[0] += 1
        return self._byte_count


def test_history_accounting_queries_and_noop_budget_checks_do_not_rescan_rows() -> None:
    undo = UndoManager()
    owner = object()
    reads = [0]
    for index in range(1_000):
        charge = _CountingCharge(owner, 1, reads)
        undo.record(
            Edit(
                undo=lambda: None,
                redo=lambda: None,
                description=f"row {index}",
                retained_text=(charge,),  # type: ignore[arg-type]
            )
        )

    # Recording reads each new charge once.  Status and a budget check that
    # removes nothing must consult cached owner totals, not revisit 1,000 rows.
    assert reads[0] == 1_000
    reads[0] = 0
    assert undo.retained_text_bytes(owner) == 1_000
    assert undo.retained_text_bytes() == 1_000
    report = undo.trim_undo_to_budgets(((owner, "main", 1_000),))
    assert report.dropped_edits == 0
    assert reads[0] == 0

    # Crossing the budget reads only the one retired row's charge.  The oldest
    # stack operation is deque-backed, so retirement does not shift all rows.
    report = undo.trim_undo_to_budgets(((owner, "main", 999),))
    assert report.dropped_edits == 1
    assert report.dropped_retained_text_bytes == 1
    assert reads[0] == 1
    assert undo.retained_text_bytes(owner) == 999


def test_restoring_stack_membership_rebuilds_cached_retained_text_totals() -> None:
    undo = UndoManager()
    owner_a = object()
    owner_b = object()
    undo.record(_edit("one", (owner_a, "a", 3)))
    undo.record(_edit("two", (owner_a, "a", 5), (owner_b, "b", 7)))
    snapshot = undo.snapshot()

    assert undo.undo() is True
    undo.record(_edit("branch", (owner_b, "b", 11)))
    assert undo.retained_text_bytes(owner_a) == 3
    assert undo.retained_text_bytes(owner_b) == 11

    undo.restore(snapshot)
    assert undo.depth() == 2
    assert undo.redo_depth() == 0
    assert undo.retained_text_bytes(owner_a) == 8
    assert undo.retained_text_bytes(owner_b) == 7
    assert undo.retained_text_bytes() == 15


def test_cached_accounting_matches_stack_scan_across_seeded_history_transitions() -> None:
    rng = random.Random(984)
    owners = [object() for _ in range(5)]
    undo = UndoManager()
    saved = []

    def expected(owner: object | None = None, *, include_redo: bool = True) -> int:
        snapshot = undo.snapshot()
        rows = list(snapshot.undo)
        if include_redo:
            rows.extend(snapshot.redo)
        return sum(
            charge.byte_count
            for edit in rows
            for charge in edit.retained_text
            if owner is None or charge.owner is owner
        )

    def check() -> None:
        assert undo.retained_text_bytes() == expected()
        assert undo.retained_text_bytes(include_redo=False) == expected(
            include_redo=False,
        )
        for owner in owners:
            assert undo.retained_text_bytes(owner) == expected(owner)
            assert undo.retained_text_bytes(
                owner,
                include_redo=False,
            ) == expected(owner, include_redo=False)

    for index in range(2_000):
        operation = rng.randrange(8)
        if operation in {0, 1, 2}:
            charges = tuple(
                (owner, "owner", rng.randrange(0, 32))
                for owner in rng.sample(owners, rng.randrange(0, 4))
            )
            undo.record(_edit(f"row {index}", *charges))
        elif operation == 3 and undo.can_undo():
            assert undo.undo() is True
        elif operation == 4 and undo.can_redo():
            assert undo.redo() is True
        elif operation == 5:
            saved.append(undo.snapshot())
            del saved[:-12]
        elif operation == 6 and saved:
            undo.restore(rng.choice(saved))
        else:
            touched = rng.sample(owners, rng.randrange(0, 4))
            before = expected(include_redo=False)
            report = undo.trim_undo_to_budgets(
                (owner, "owner", rng.randrange(-2, 80))
                for owner in touched
            )
            assert report.dropped_retained_text_bytes == (
                before - expected(include_redo=False)
            )
        check()


def test_budget_trimming_removes_only_complete_oldest_linear_rows() -> None:
    undo = UndoManager()
    owner_a = object()
    owner_b = object()
    events: list[str] = []
    undo.record(_edit("compound", (owner_a, "a", 5), (owner_b, "b", 7), events=events))
    undo.record(_edit("latest", (owner_a, "a", 5), events=events))

    report = undo.trim_undo_to_budgets(((owner_a, "a", 6),))

    assert report.dropped_edits == 1
    assert report.dropped_retained_text_bytes == 12
    assert report.over_budget == ()
    assert undo.depth() == 1
    assert undo.retained_text_bytes(owner_a) == 5
    assert undo.retained_text_bytes(owner_b) == 0
    assert undo.undo() is True
    assert events == ["undo:latest"]


def test_budget_preserves_the_newest_indivisible_row_and_reports_soft_overage() -> None:
    undo = UndoManager()
    owner = object()
    undo.record(_edit("large paste", (owner, "main", 11)))

    report = undo.trim_undo_to_budgets(((owner, "main", 4),))

    assert report.dropped_edits == 0
    assert undo.depth() == 1
    assert len(report.over_budget) == 1
    assert report.over_budget[0].label == "main"
    assert report.over_budget[0].retained_text_bytes == 11
    assert report.over_budget[0].budget_bytes == 4


def test_new_edit_releases_abandoned_redo_text_before_budget_trimming() -> None:
    undo = UndoManager()
    owner = object()
    undo.record(_edit("old", (owner, "main", 4)))
    undo.record(_edit("undone", (owner, "main", 4)))
    assert undo.undo() is True
    assert undo.retained_text_bytes(owner) == 8
    assert undo.retained_text_bytes(owner, include_redo=False) == 4

    undo.record(_edit("branch", (owner, "main", 4)))
    report = undo.trim_undo_to_budgets(((owner, "main", 4),))

    assert undo.redo_depth() == 0
    assert report.dropped_edits == 1
    assert report.dropped_retained_text_bytes == 4
    assert undo.depth() == 1
    assert undo.retained_text_bytes(owner) == 4
    assert undo.peek_undo() is not None
    assert undo.peek_undo().description == "branch"


def test_editor_local_undobytes_trims_old_splices_but_keeps_exact_recent_undo() -> None:
    ed = Editor()
    ed.new_buffer("main", "")
    eb = ed.cur()
    assert ed.set_option_value("undobytes", "3", local=True) == 3
    now = [0.0]
    ed._now_fn = lambda: now[0]

    for char in "abcde":
        ed.input["text"] = char
        assert ed.run_action("InsertText") is True
        now[0] += 1.0

    assert eb.buf.get_text() == "abcde"
    assert ed.undo.depth() == 3
    assert ed.undo.retained_text_bytes(eb) == 3
    trim_messages = [message for message in ed.messages if "undo: trimmed" in message]
    assert trim_messages == [
        "undo: trimmed 2 oldest changes (2 retained text bytes)"
    ]

    assert ed.undo_feedback() is True
    assert ed.undo_feedback() is True
    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == "ab"
    assert ed.undo_feedback() is False

    assert ed.redo_feedback() is True
    assert ed.redo_feedback() is True
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "abcde"


def test_trim_notice_coalescing_preserves_message_authority_boundaries() -> None:
    ed = Editor()
    ed.new_buffer("main", "")
    ed.set_option_value("undobytes", "1", local=True)
    now = [0.0]
    ed._now_fn = lambda: now[0]

    for char in "ab":
        ed.input["text"] = char
        assert ed.run_action("InsertText") is True
        now[0] += 1.0

    with ed.script_context("trim-probe"):
        for char in "cd":
            ed.input["text"] = char
            assert ed.run_action("InsertText") is True
            now[0] += 1.0

    trim_messages = [message for message in ed.messages if "undo: trimmed" in message]
    assert trim_messages == [
        "undo: trimmed 1 oldest change (1 retained text bytes)",
        "undo: trimmed 2 oldest changes (2 retained text bytes)",
    ]
    trim_authority = [
        authority
        for message, authority in zip(ed.messages, ed.message_authority, strict=True)
        if "undo: trimmed" in message
    ]
    assert trim_authority[0].script_context is False
    assert trim_authority[1].script_context is True
    assert trim_authority[1].script_origin_id == "trim-probe"


def test_editor_keeps_one_oversized_recent_change_visible_and_recoverable() -> None:
    ed = Editor()
    ed.new_buffer("main", "")
    eb = ed.cur()
    assert ed.set_option_value("undobytes", "2", local=True) == 2

    ed.input["text"] = "payload"
    assert ed.run_action("InsertText") is True

    assert ed.undo.depth() == 1
    assert ed.undo.retained_text_bytes(eb) == len("payload")
    assert any(
        "undo: newest change kept whole for main: 7 > undobytes 2" in message
        for message in ed.messages
    )
    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == ""


def test_repeated_oversized_rows_keep_one_bounded_feedback_cluster() -> None:
    ed = Editor()
    ed.new_buffer("main", "")
    eb = ed.cur()
    assert ed.set_option_value("undobytes", "1", local=True) == 1

    for _ in range(10):
        ed.input["text"] = "xx"
        assert ed.run_action("InsertText") is True

    budget_messages = [
        message
        for message in ed.messages
        if message.startswith("undo: trimmed")
        or message.startswith("undo: newest change kept whole")
    ]
    assert budget_messages == [
        "undo: trimmed 9 oldest changes (18 retained text bytes)",
        "undo: newest change kept whole for main: 2 > undobytes 1",
    ]
    assert ed.undo.depth() == 1
    assert ed.undo.retained_text_bytes(eb) == 2
    assert ed.undo_feedback() is True
    assert eb.buf.get_text() == "xx" * 9


def test_oversized_feedback_cluster_preserves_lower_authority_boundary() -> None:
    ed = Editor()
    ed.new_buffer("main", "")
    ed.set_option_value("undobytes", "1", local=True)

    for _ in range(2):
        ed.input["text"] = "xx"
        assert ed.run_action("InsertText") is True
    with ed.script_context("overage-probe"):
        for _ in range(2):
            ed.input["text"] = "xx"
            assert ed.run_action("InsertText") is True

    rows = [
        (message, authority)
        for message, authority in zip(
            ed.messages,
            ed.message_authority,
            strict=True,
        )
        if message.startswith("undo: trimmed")
        or message.startswith("undo: newest change kept whole")
    ]
    assert [message for message, _authority in rows] == [
        "undo: trimmed 1 oldest change (2 retained text bytes)",
        "undo: newest change kept whole for main: 2 > undobytes 1",
        "undo: trimmed 2 oldest changes (4 retained text bytes)",
        "undo: newest change kept whole for main: 2 > undobytes 1",
    ]
    assert [authority.script_context for _message, authority in rows] == [
        False,
        False,
        True,
        True,
    ]
    assert rows[-1][1].script_origin_id == "overage-probe"


def test_undostatus_exposes_current_buffer_and_total_retained_text_accounting() -> None:
    ed = Editor()
    ed.new_buffer("main", "")
    ed.set_option_value("undobytes", "100", local=True)
    ed.input["text"] = "payload"
    assert ed.run_action("InsertText") is True

    assert ed.exec_command_line("undostatus") is True
    assert ed.messages[-1] == (
        "undo: 1 undo, 0 redo; main 7/100 retained text bytes; 7 total"
    )


def test_equal_text_splice_drops_callback_dead_large_witness_strings() -> None:
    ed = Editor()
    ed.new_buffer("main", "seed")
    eb = ed.cur()
    huge = "x" * 1_000_000
    sidecars = ed._snapshot_buffer_sidecars(eb)
    witness = BufferSplice(
        start=Cursor(0, 0),
        old_end=Cursor(0, 0),
        new_end=Cursor(0, 0),
        old_text=huge,
        new_text=huge,
        changed=False,
    )

    ed._record_undo_splice(eb, witness, sidecars, sidecars, "sidecar only")
    row = ed.undo.peek_undo()
    assert row is not None
    assert row.retained_text[0].byte_count == 0

    closure_strings: list[str] = []
    for callback in (row.undo, row.redo):
        for cell in callback.__closure__ or ():
            if isinstance(cell.cell_contents, str):
                closure_strings.append(cell.cell_contents)
    assert max((len(value) for value in closure_strings), default=0) == 0
    assert ed.undo_feedback() is True
    assert ed.redo_feedback() is True
    assert eb.buf.get_text() == "seed"


def test_aggregate_transaction_retains_full_state_only_for_changed_buffers() -> None:
    source = ("a" * 79 + "\n") * 2_500
    ed = Editor()
    ed.new_buffer("a", source)
    ed.new_buffer("b", source.replace("a", "b"))
    ed.new_buffer("c", source.replace("a", "c"))
    a, b, c = ed.buffers["a"], ed.buffers["b"], ed.buffers["c"]
    assert ed.exec_command_line("buffer a") is True
    a_ref, b_ref, c_ref = a, b, c
    b_text = b.buf.get_text()
    c_text = c.buf.get_text()

    before = ed._buffer_transaction_snapshot()
    with ed.undo.suppress_recording():
        ed.input["text"] = "X"
        assert ed.run_action("InsertText") is True
    after = ed._buffer_transaction_snapshot(reuse_unchanged_text_from=before)
    ed._record_buffer_transaction_snapshot(before, after, "tiny aggregate")

    row = ed.undo.peek_undo()
    assert row is not None
    assert len(row.retained_text) == 1
    assert row.retained_text[0].owner is a
    assert row.retained_text[0].byte_count == logical_text_bytes(source) + logical_text_bytes("X" + source)

    for callback in (row.undo, row.redo):
        retained = _closure_snapshot(callback)
        by_name = {snap.name: snap for snap in retained.buffers}
        assert by_name["a"].text in {source, "X" + source}
        assert by_name["b"].text == ""
        assert by_name["c"].text == ""
        assert by_name["b"].local_options == {}
        assert by_name["c"].jump_list == ()

    assert ed.undo_feedback() is True
    assert ed.buffers["a"] is a_ref
    assert ed.buffers["b"] is b_ref
    assert ed.buffers["c"] is c_ref
    assert a.buf.get_text() == source
    assert b.buf.get_text() == b_text
    assert c.buf.get_text() == c_text

    assert ed.redo_feedback() is True
    assert a.buf.get_text() == "X" + source
    assert b.buf.get_text() == b_text
    assert c.buf.get_text() == c_text


def test_multibuffer_budget_trims_only_whole_aggregate_transactions() -> None:
    ed = Editor()
    ed.new_buffer("a", "")
    ed.new_buffer("b", "")
    a, b = ed.buffers["a"], ed.buffers["b"]
    ed.options.set("undobytes", "12", local=a.local_options)
    ed.options.set("undobytes", "12", local=b.local_options)

    def record_pair(a_text: str, b_text: str, description: str) -> None:
        before = ed._buffer_transaction_snapshot()
        with ed.undo.suppress_recording():
            a.buf.set_text(a_text)
            b.buf.set_text(b_text)
        after = ed._buffer_transaction_snapshot(reuse_unchanged_text_from=before)
        ed._record_buffer_transaction_snapshot(before, after, description)

    record_pair("aaa", "bbb", "first pair")
    assert ed.undo.depth() == 1
    record_pair("aaaaaaaa", "bbbbbbbb", "second pair")

    # Each owner retained 3 bytes in the old row and 3+8 in the new row.
    # Satisfying either 12-byte limit must retire the complete two-buffer row.
    assert ed.undo.depth() == 1
    assert ed.undo.retained_text_bytes(a) == 11
    assert ed.undo.retained_text_bytes(b) == 11
    assert any("undo: trimmed 1 oldest change (6 retained text bytes)" in row for row in ed.messages)

    assert ed.undo_feedback() is True
    assert a.buf.get_text() == "aaa"
    assert b.buf.get_text() == "bbb"
    assert ed.undo_feedback() is False
    assert ed.redo_feedback() is True
    assert a.buf.get_text() == "aaaaaaaa"
    assert b.buf.get_text() == "bbbbbbbb"


def test_after_snapshot_reuses_unchanged_multiline_text_and_skips_eager_hash_fallback() -> None:
    ed = Editor()
    ed.new_buffer("a", "alpha\nbeta\ngamma")
    ed.new_buffer("b", "one\ntwo\nthree")
    before = ed._buffer_transaction_snapshot()
    before_by_name = {snap.name: snap for snap in before.buffers}

    def fail_signature(_text: str) -> tuple[int, str]:
        raise AssertionError("saved signature fallback should not run")

    ed.buffers["a"].buf._text_signature = fail_signature  # type: ignore[method-assign]
    ed.buffers["b"].buf._text_signature = fail_signature  # type: ignore[method-assign]
    after = ed._buffer_transaction_snapshot(reuse_unchanged_text_from=before)
    after_by_name = {snap.name: snap for snap in after.buffers}

    assert after_by_name["a"].text is before_by_name["a"].text
    assert after_by_name["b"].text is before_by_name["b"].text


def test_sidecar_only_aggregate_counts_one_shared_text_payload_not_two() -> None:
    source = ("line payload\n" * 1_000).rstrip("\n")
    ed = Editor()
    ed.new_buffer("main", source)
    eb = ed.cur()
    before = ed._buffer_transaction_snapshot()
    eb.cursors[:] = [Cursor(100, 3)]
    after = ed._buffer_transaction_snapshot(reuse_unchanged_text_from=before)

    assert before.buffers[0].text is after.buffers[0].text
    ed._record_buffer_transaction_snapshot(before, after, "cursor transaction")
    row = ed.undo.peek_undo()
    assert row is not None
    assert len(row.retained_text) == 1
    assert row.retained_text[0].byte_count == logical_text_bytes(source)

    assert ed.undo_feedback() is True
    assert eb.cursors == [Cursor(0, 0)]
    assert eb.buf.get_text() == source
    assert ed.redo_feedback() is True
    assert eb.cursors == [Cursor(100, 3)]
    assert eb.buf.get_text() == source


def test_undobytes_is_write_protected_from_scripts_but_safe_to_read() -> None:
    assert script_option_policy("undobytes").allowed is False
    assert script_option_policy("undobytes").reason == "protected option"
    assert script_option_read_policy("undobytes").allowed is True


def test_history_retention_witness_measures_transaction_compaction_and_budget() -> None:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + existing if existing else "")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "measure_history_retention.py"),
            "--chars",
            "400000",
            "--buffers",
            "3",
            "--samples",
            "1",
            "--budget-bytes",
            "1024",
            "--budget-edits",
            "20",
            "--chunk-chars",
            "128",
            "--accounting-rows",
            "2000",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["schema"] == "micromax.history-retention-witness.v1"
    current = payload["changed_buffers_only"]
    reference = payload["broad_snapshot_reference"]
    budget = payload["budget_journey"]
    accounting = payload["accounting_hotpath"]

    assert current["full_text_buffer_snapshot_rows"] == 2
    assert reference["full_text_buffer_snapshot_rows"] == 6
    assert current["accounted_retained_text_bytes"] == current["retained_snapshot_text_bytes"]
    assert reference["traced_current_bytes_median"] > current["traced_current_bytes_median"]
    assert payload["comparison"]["traced_current_reduction_percent"] > 50
    assert payload["comparison"]["traced_peak_reduction_percent"] > 0
    assert payload["comparison"]["retained_snapshot_text_reduction_percent"] > 60
    assert current["undo_exact"] is True and current["redo_exact"] is True
    assert reference["undo_exact"] is True and reference["redo_exact"] is True
    assert budget["retained_text_bytes"] == 1024
    assert budget["retained_undo_rows"] == 8
    assert budget["trimmed_undo_rows"] == 12
    assert budget["trim_messages"] == 1
    assert budget["trim_notices"] == [
        "undo: trimmed 12 oldest changes (1536 retained text bytes)"
    ]
    assert budget["undo_exact"] is True and budget["redo_exact"] is True
    assert accounting["history_rows"] == 2_000
    assert accounting["charge_reads_while_recording"] == 2_000
    assert accounting["charge_reads_for_two_queries_and_noop_budget_check"] == 0
    assert accounting["linear_rescan_reference_reads_for_same_operations"] == 6_000
    assert accounting["charge_reads_to_retire_one_oldest_row"] == 1
    assert accounting["single_budget_dropped_rows"] == 1
    assert accounting["retained_rows_after_trim"] == 1_999

from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
import copy
from typing import Any, Mapping, Sequence, Tuple

from .cpp_transition import (
    TransitionMicroRecord,
    cpp_transition_signatures,
    cpp_transition_tool_status,
    is_supported_transition,
    state_signature,
    transition_record_from_state_action,
    with_jace_ultimate_shuffle_transport,
)
from .decision import apply_decision_index, build_decision_frame
from .replay import deck_from_json, state_fingerprint
from .engine import start_game
from .mulligan_ranker import make_mulligan_agent


@dataclass(frozen=True)
class CppTraceStepRow:
    trace_id: str
    step: int
    player: int
    frame: str
    main_phase: str
    pending_choice_kind: str
    stack_depth: int
    action_kind: str
    action: str
    supported_by_cpp: bool
    skipped_reason: str
    python_pre_fingerprint_ok: bool
    python_post_fingerprint_ok: bool
    cpp_match: bool | None
    case_id: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PreparedCppTraceBatch:
    """Replay-derived transition records before the C++ executable is called."""

    revision: str
    trace_count: int
    records: Tuple[TransitionMicroRecord, ...]
    expected_signatures: Tuple[str, ...]
    record_row_indices: Tuple[int, ...]
    rows: Tuple[CppTraceStepRow, ...]
    python_errors: Tuple[str, ...]

    @property
    def events(self) -> int:
        return len(self.rows)

    @property
    def supported_events(self) -> int:
        return len(self.records)

    def as_dict(self) -> dict[str, object]:
        return {
            "revision": self.revision,
            "trace_count": self.trace_count,
            "events": self.events,
            "supported_events": self.supported_events,
            "python_errors": list(self.python_errors),
        }


@dataclass(frozen=True)
class CppTraceBatchSummary:
    revision: str
    traces: int
    events: int
    supported_events: int
    skipped_events: int
    mismatches: int
    python_replay_errors: int
    support_rate: float
    cpp_match_rate_on_supported: float
    tool_status: dict[str, object]
    unsupported_examples: Tuple[dict[str, object], ...]
    mismatch_examples: Tuple[dict[str, object], ...]
    python_error_examples: Tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _trace_id(trace: Mapping[str, Any], fallback: int) -> str:
    cfg = trace.get("config", {}) if isinstance(trace.get("config", {}), Mapping) else {}
    return str(trace.get("trace_id") or f"trace{fallback}_seed{cfg.get('seed', 'na')}_p{cfg.get('starting_player', 'na')}_life{cfg.get('starting_life', 'na')}")


def _pending_kind(state) -> str:
    return "none" if state.pending_choice is None else str(state.pending_choice.kind)


def prepare_public_traces_for_cpp(transaces: Sequence[Mapping[str, Any]], *, revision: str = "rev0021") -> PreparedCppTraceBatch:
    """Replay public traces and prepare C++ one-action transition records.

    This is the refactored rev0021 seam.  It separates expensive/semantic Python
    replay and record projection from the C++ batch executable call.  That lets
    benchmarks measure the C++ part directly and lets future rollout pipelines
    reuse the preparation result without duplicating trace-checking code.
    """

    records: list[TransitionMicroRecord] = []
    expected_signatures: list[str] = []
    record_row_indices: list[int] = []
    rows: list[CppTraceStepRow] = []
    python_errors: list[str] = []

    for trace_index, trace in enumerate(transaces):
        tid = _trace_id(trace, trace_index)
        try:
            cfg = trace["config"]
            deck0 = deck_from_json(cfg["deck0"])
            deck1 = deck_from_json(cfg["deck1"])
            state_rng = Random(int(cfg.get("transition_seed", cfg["seed"])))
            mulligan_policies_payload = cfg.get("mulligan_policies")
            mulligan_policies = tuple(mulligan_policies_payload) if mulligan_policies_payload is not None else None
            mulligan_agents_payload = cfg.get("mulligan_agents")
            mulligan_agents = tuple(make_mulligan_agent(a) for a in mulligan_agents_payload) if mulligan_agents_payload is not None else None
            state = start_game(
                deck0,
                deck1,
                seed=int(cfg["seed"]),
                starting_player=int(cfg["starting_player"]),
                starting_life=int(cfg["starting_life"]),
                mulligan_policy=cfg.get("mulligan_policy"),
                mulligan_policies=mulligan_policies,  # type: ignore[arg-type]
                mulligan_agents=mulligan_agents,  # type: ignore[arg-type]
                record_log=False,
            )
            for event in list(trace.get("events", [])):
                step = int(event.get("step", len(rows) + 1))
                frame = build_decision_frame(state)
                pre_ok = state_fingerprint(state) == event.get("pre_fingerprint")
                legal_ok = list(frame.legal_action_strings) == list(event.get("legal_actions", []))
                action_index = int(event.get("action_index", -1))
                if not pre_ok or not legal_ok or action_index < 0 or action_index >= frame.action_count:
                    python_errors.append(f"{tid} step {step}: pre/legal/action-index mismatch pre_ok={pre_ok} legal_ok={legal_ok} idx={action_index} count={frame.action_count}")
                    rows.append(
                        CppTraceStepRow(
                            trace_id=tid,
                            step=step,
                            player=int(frame.player),
                            frame=str(state.frame),
                            main_phase=str(state.main_phase),
                            pending_choice_kind=_pending_kind(state),
                            stack_depth=len(state.stack),
                            action_kind="INVALID_REPLAY_STEP",
                            action="INVALID_REPLAY_STEP",
                            supported_by_cpp=False,
                            skipped_reason="python_replay_precheck_failed",
                            python_pre_fingerprint_ok=bool(pre_ok),
                            python_post_fingerprint_ok=False,
                            cpp_match=None,
                            case_id=f"{tid}_step{step}",
                        )
                    )
                    break
                action = frame.legal_actions[action_index]
                compact = action.compact()
                action_payload = event.get("action", {})
                event_compact = action_payload.get("compact") if isinstance(action_payload, Mapping) else None
                if compact != event_compact:
                    python_errors.append(f"{tid} step {step}: action compact mismatch got={compact!r} expected={event_compact!r}")
                    break

                pre_frame = str(state.frame)
                pre_main_phase = str(state.main_phase)
                pre_pending_kind = _pending_kind(state)
                pre_stack_depth = len(state.stack)
                case_id = f"{tid}_step{step}_{pre_frame}_{pre_pending_kind}_{action.kind}"
                pre_state_for_cpp = copy.deepcopy(state)
                apply_decision_index(state, frame, action_index, state_rng)
                post_sig = state_signature(state)
                post_ok = state_fingerprint(state) == event.get("post_fingerprint")
                transported_action = with_jace_ultimate_shuffle_transport(pre_state_for_cpp, action, state)
                supported = is_supported_transition(pre_state_for_cpp, transported_action)
                row_index = len(rows)
                skipped_reason = "" if supported else "unsupported_by_cpp_transition_microkernel"
                if supported:
                    records.append(transition_record_from_state_action(pre_state_for_cpp, transported_action, case_id))
                    record_row_indices.append(row_index)
                    expected_signatures.append(post_sig)
                if not post_ok:
                    python_errors.append(f"{tid} step {step}: post_fingerprint mismatch")
                rows.append(
                    CppTraceStepRow(
                        trace_id=tid,
                        step=step,
                        player=int(frame.player),
                        frame=pre_frame,
                        main_phase=pre_main_phase,
                        pending_choice_kind=pre_pending_kind,
                        stack_depth=pre_stack_depth,
                        action_kind=action.kind,
                        action=compact,
                        supported_by_cpp=bool(supported),
                        skipped_reason=skipped_reason,
                        python_pre_fingerprint_ok=bool(pre_ok),
                        python_post_fingerprint_ok=bool(post_ok),
                        cpp_match=None,
                        case_id=case_id,
                    )
                )
            final_payload = trace.get("final", {})
            if isinstance(final_payload, Mapping):
                if final_payload.get("truncated") and state.winner is None:
                    state.frame = "GAME_OVER"
                    state.loss_reason = "max_decisions_reached"
                expected_final = final_payload.get("fingerprint")
                if expected_final and state_fingerprint(state) != expected_final:
                    python_errors.append(f"{tid}: final fingerprint mismatch")
        except Exception as exc:  # pragma: no cover - diagnostics path
            python_errors.append(f"{tid}: exception {type(exc).__name__}: {exc}")

    return PreparedCppTraceBatch(
        revision=revision,
        trace_count=len(transaces),
        records=tuple(records),
        expected_signatures=tuple(expected_signatures),
        record_row_indices=tuple(record_row_indices),
        rows=tuple(rows),
        python_errors=tuple(python_errors),
    )


def finalize_cpp_trace_batch(prepared: PreparedCppTraceBatch) -> tuple[CppTraceBatchSummary, list[CppTraceStepRow]]:
    """Run C++ over a prepared trace batch and attach match labels."""

    rows: list[CppTraceStepRow] = list(prepared.rows)
    mismatch_examples: list[dict[str, object]] = []
    mismatches = 0
    if prepared.records:
        actual = cpp_transition_signatures(prepared.records)
        for record_idx, (got, want) in enumerate(zip(actual, prepared.expected_signatures)):
            row_index = prepared.record_row_indices[record_idx]
            old = rows[row_index]
            ok = got == want
            if not ok:
                mismatches += 1
                if len(mismatch_examples) < 10:
                    mismatch_examples.append(
                        {
                            "case_id": old.case_id,
                            "trace_id": old.trace_id,
                            "step": old.step,
                            "action": old.action,
                            "expected": want,
                            "actual": got,
                        }
                    )
            rows[row_index] = CppTraceStepRow(
                trace_id=old.trace_id,
                step=old.step,
                player=old.player,
                frame=old.frame,
                main_phase=old.main_phase,
                pending_choice_kind=old.pending_choice_kind,
                stack_depth=old.stack_depth,
                action_kind=old.action_kind,
                action=old.action,
                supported_by_cpp=old.supported_by_cpp,
                skipped_reason=old.skipped_reason,
                python_pre_fingerprint_ok=old.python_pre_fingerprint_ok,
                python_post_fingerprint_ok=old.python_post_fingerprint_ok,
                cpp_match=ok,
                case_id=old.case_id,
            )

    events = len(rows)
    supported = sum(1 for r in rows if r.supported_by_cpp)
    skipped = events - supported
    unsupported_examples = tuple(r.as_dict() for r in rows if not r.supported_by_cpp)[:10]
    match_rate = 1.0 if supported == 0 else (supported - mismatches) / supported
    summary = CppTraceBatchSummary(
        revision=prepared.revision,
        traces=prepared.trace_count,
        events=events,
        supported_events=supported,
        skipped_events=skipped,
        mismatches=mismatches,
        python_replay_errors=len(prepared.python_errors),
        support_rate=0.0 if events == 0 else supported / events,
        cpp_match_rate_on_supported=match_rate,
        tool_status=cpp_transition_tool_status().as_dict(),
        unsupported_examples=unsupported_examples,
        mismatch_examples=tuple(mismatch_examples),
        python_error_examples=tuple(prepared.python_errors[:10]),
    )
    return summary, rows


def check_public_traces_with_cpp(transaces: Sequence[Mapping[str, Any]], *, revision: str = "rev0019") -> tuple[CppTraceBatchSummary, list[CppTraceStepRow]]:
    """Replay public traces in Python and check every supported step in C++."""

    prepared = prepare_public_traces_for_cpp(transaces, revision=revision)
    return finalize_cpp_trace_batch(prepared)

from __future__ import annotations

from pathlib import Path

import pytest

from glassttyd.conversation import (
    BrokerClient,
    BrokerUnavailable,
    ConversationEngine,
    EngineConfig,
)
from glassttyd.mock_tab import MockChatGPTTab, MockReply


def fast_config(**overrides) -> EngineConfig:
    base = dict(poll_interval=0.01, start_grace=0.5, max_wait=5.0, settle_polls=2, request_timeout=5.0)
    base.update(overrides)
    return EngineConfig(**base)


def engine_for(socket_path: Path, **overrides) -> ConversationEngine:
    return ConversationEngine(BrokerClient(socket_path, default_timeout=5.0), config=fast_config(**overrides))


def test_send_returns_settled_answer(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        result = engine_for(sock).send('hello there')

    assert result.ok
    assert result.submitted
    assert result.text is not None
    assert 'hello there' in result.text
    assert result.settle_reason == 'generation-settled'
    assert result.detection == 'generation'
    assert result.readback_ok is True
    assert result.final_generation == 'settled-or-idle'


def test_send_auto_continues_a_gated_answer(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        result = engine_for(sock).send('give me the long one [[continue]]')

    assert result.ok
    assert result.continues == 1
    assert 'part 1' in (result.text or '')
    assert 'part 2' in (result.text or '')


def test_no_continue_flag_stops_at_the_gate(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        result = engine_for(sock, auto_continue=False).send('long one [[continue]]')

    assert result.ok
    assert result.continues == 0
    assert result.settle_reason == 'needs-continue-not-followed'
    assert 'part 2' not in (result.text or '')


def test_falls_back_to_text_stability_without_generation_signal(tmp_path: Path) -> None:
    """Older extension builds expose no generation lifecycle; the engine must still work."""
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock, emit_generation=False):
        result = engine_for(sock).send('hello fallback')

    assert result.ok
    assert result.detection == 'text-stability'
    assert result.settle_reason == 'output-stable'
    assert 'hello fallback' in (result.text or '')


def test_stalled_generation_is_reported_not_silently_ok(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        result = engine_for(sock).send('this will [[stall]]')

    assert not result.ok
    assert result.submitted
    assert result.settle_reason == 'no-generation-detected'
    assert result.error


def test_refused_submit_is_reported(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        result = engine_for(sock).send('nope [[error]]')

    assert not result.ok
    assert result.submitted is False
    assert 'blocked' in (result.error or '')


def test_staged_prompt_is_not_submitted(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock) as tab:
        result = engine_for(sock).send('staged only', submit=False)

    assert result.ok
    assert result.submitted is False
    assert result.settle_reason == 'staged-not-submitted'
    assert tab.composer == 'staged only'  # still sitting in the composer


def test_second_turn_does_not_return_the_first_answer(tmp_path: Path) -> None:
    """Baseline tracking must prevent a stale previous answer from being reported."""
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        engine = engine_for(sock)
        first = engine.send('first question')
        second = engine.send('second question')

    assert 'first question' in (first.text or '')
    assert 'second question' in (second.text or '')
    assert first.text != second.text


def test_missing_socket_raises_broker_unavailable(tmp_path: Path) -> None:
    client = BrokerClient(tmp_path / 'nope.sock')
    with pytest.raises(BrokerUnavailable):
        client.ensure_available()


def test_stale_socket_file_is_reported_as_unavailable(tmp_path: Path) -> None:
    """A socket inode left behind by a crashed broker must not leak a raw traceback."""
    stale = tmp_path / 'daemon.sock'
    stale.touch()
    engine = engine_for(stale)
    result = engine.send('hello')

    assert not result.ok
    assert 'nothing is listening' in (result.error or '')


def test_custom_responder_drives_the_engine(tmp_path: Path) -> None:
    def responder(prompt: str, turn_index: int) -> MockReply:
        return MockReply(parts=[f'scripted:{prompt.upper()}'])

    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock, responder=responder):
        result = engine_for(sock).send('abc')

    assert result.ok
    assert result.text == 'scripted:ABC'


def test_mock_matches_the_real_content_script_reply_shapes(tmp_path: Path) -> None:
    """The mock is only a valid test double if it replies in the page's exact shape.

    extension/src/content/main.ts answers `transcript.latest` under `text` and
    `state.snapshot` under `latest_output`. A mock that invents its own shape
    would let a broken engine pass CI and still fail against a real tab.
    """
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        engine = engine_for(sock)
        engine.send('hello')

        latest = engine.read_latest()
        assert 'text' in latest and latest['text']

        snapshot = engine.snapshot()
        assert 'latest_output' in snapshot
        assert 'prompt' in snapshot and 'selection' in snapshot
        assert isinstance(snapshot.get('generation'), dict)
        assert snapshot['generation']['state'] == 'settled-or-idle'


def test_read_prompt_reflects_the_composer(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        engine = engine_for(sock)
        engine.send('staged text', submit=False)
        assert engine.read_prompt() == 'staged text'


def test_timeout_is_surfaced_when_generation_never_ends(tmp_path: Path) -> None:
    def never_ends(prompt: str, turn_index: int) -> MockReply:
        return MockReply(parts=[f'part-{i}' for i in range(500)])

    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock, responder=never_ends):
        result = engine_for(sock, max_wait=0.25, auto_continue=True, max_continues=1).send('forever')

    # Either it hits the wall clock or it stops at the un-followed continue gate;
    # both are honest terminal states, never a silent success with partial text.
    assert result.settle_reason in {'timeout', 'needs-continue-not-followed'}

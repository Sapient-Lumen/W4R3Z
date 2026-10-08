from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from glassttyd.conversation import BrokerClient, ConversationEngine, EngineConfig
from glassttyd.cli import _diagnose_failure
from glassttyd.mock_tab import DRIFT_SCENARIOS, MockChatGPTTab, build_mock_probe
from glassttyd.surface import (
    CONFIDENT_THRESHOLD,
    SurfaceStore,
    build_snapshot,
    diff_snapshots,
    propose_repairs,
    triage,
)

URL = 'https://chatgpt.com/c/mock'


def snap(drift: str = 'none', composer_text: str = 'a staged draft'):
    """Probe with a draft staged, by default.

    This is not test convenience, it is how the real page works. ChatGPT does not
    render a send button until the composer has text — the live 2026-07-11 capture
    shows #composer-submit-button matching zero nodes on a perfectly healthy page.
    So any probe that intends to say something about `send` must stage text first
    (`glassttyd surface-triage --probe-with-draft`). Probing empty and concluding
    "send is gone" is the false positive that rev0355 exists to kill; see
    tests/test_attachments_and_live_surface.py for the empty-composer cases.
    """
    return build_snapshot(build_mock_probe(drift, url=URL, composer_text=composer_text))


def engine_for(sock: Path) -> ConversationEngine:
    cfg = EngineConfig(poll_interval=0.01, start_grace=0.5, max_wait=5.0, settle_polls=2, request_timeout=5.0)
    return ConversationEngine(BrokerClient(sock, default_timeout=5.0), config=cfg)


# --------------------------------------------------------------------------- #
# Snapshot + fingerprint
# --------------------------------------------------------------------------- #
def test_healthy_surface_is_ok_and_has_all_capabilities() -> None:
    report = triage(snap('none'))

    assert report['verdict'] == 'surface-ok'
    assert report['findings'] == []
    assert report['repairs'] == []


def test_fingerprint_is_stable_for_the_same_surface_and_changes_on_drift() -> None:
    assert snap('none')['fingerprint'] == snap('none')['fingerprint']
    assert snap('none')['fingerprint'] != snap('send-renamed')['fingerprint']


def test_transient_anchors_never_produce_repairs() -> None:
    """A missing 'stop generating' button means nothing is generating — not drift.

    Proposing a repair for it would be crying wolf, and a drift detector that
    cries wolf gets ignored on the day it is right.
    """
    healthy = snap('none')
    assert healthy['anchors']['generation_stop']['found'] is False
    assert [r['anchor'] for r in propose_repairs(healthy)] == []


# --------------------------------------------------------------------------- #
# Diff
# --------------------------------------------------------------------------- #
def test_diff_detects_capability_loss_and_new_controls() -> None:
    delta = diff_snapshots(snap('none'), snap('new-composer-control'))

    assert delta['identical'] is False
    assert any(c['key'] == 'testid:composer-mode-picker' for c in delta['controls_added'])


def test_diff_of_identical_surfaces_is_identical() -> None:
    assert diff_snapshots(snap('none'), snap('none'))['identical'] is True


def test_diff_reports_submit_capability_regression() -> None:
    delta = diff_snapshots(snap('none'), snap('send-renamed'))
    regressions = [c for c in delta['capability_changes'] if c['capability'] == 'submit_prompt']

    assert regressions and regressions[0]['before'] is True and regressions[0]['after'] is False


def test_diff_reports_authentication_posture_change() -> None:
    before = snap('none')
    after = snap('none')
    after['authentication']['posture'] = 'anonymous'
    after['fingerprint'] = build_snapshot({
        **build_mock_probe('none', url=URL, composer_text='a staged draft'),
        'authentication': after['authentication'],
    })['fingerprint']

    delta = diff_snapshots(before, after)

    assert delta['authentication_change'] == {'before': 'authenticated', 'after': 'anonymous'}
    assert delta['counts']['authentication_changes'] == 1


def test_transient_capability_loss_is_not_a_regression() -> None:
    before = snap('none')
    after = snap('none')
    after['capabilities']['continue_generation'] = False

    report = triage(after, baseline=before)

    assert not any(
        finding.get('kind') == 'regression'
        and finding.get('capability') == 'continue_generation'
        for finding in report['findings']
    )


# --------------------------------------------------------------------------- #
# Triage — every drift scenario must produce the right diagnosis
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    'drift,expected_verdict',
    [
        ('none', 'surface-ok'),
        ('send-renamed', 'surface-drift-blocking'),
        ('send-removed', 'surface-drift-blocking'),
        ('composer-removed', 'surface-drift-blocking'),
        ('decoy-send', 'surface-drift-blocking'),
        ('new-composer-control', 'surface-drift-cosmetic'),
    ],
)
def test_triage_verdicts_per_scenario(drift: str, expected_verdict: str) -> None:
    assert triage(snap(drift))['verdict'] == expected_verdict


def test_triage_names_the_commands_a_drift_breaks() -> None:
    report = triage(snap('composer-removed'))
    lost = [f for f in report['findings'] if f.get('capability') == 'write_prompt']

    assert lost
    assert set(lost[0]['breaks_commands']) == {'ask', 'chat', 'run'}


def test_triage_flags_a_silent_anchor_substitution() -> None:
    """The dangerous case: the command still 'works', it just clicks the wrong node."""
    report = triage(snap('send-renamed'))

    assert any(f['kind'] == 'anchor-substituted' and f['severity'] == 'critical' for f in report['findings'])


def test_triage_detects_regression_against_a_baseline() -> None:
    report = triage(snap('send-renamed'), baseline=snap('none'))

    assert any(f['kind'] == 'regression' for f in report['findings'])


# --------------------------------------------------------------------------- #
# Failure correlation — the sentence the operator actually wants
# --------------------------------------------------------------------------- #
def test_failure_correlation_explains_a_refused_submit() -> None:
    failure = {'settle_reason': 'error', 'submitted': False, 'error': 'submit was blocked'}
    report = triage(snap('send-renamed'), baseline=snap('none'), failure=failure)

    assert 'send control' in report['likely_cause']


def test_failure_correlation_blames_a_modal_dialog() -> None:
    failure = {'settle_reason': 'no-generation-detected', 'submitted': True}
    report = triage(snap('nag-dialog'), failure=failure)

    assert 'dialog' in report['likely_cause']


def test_failure_correlation_blames_a_rate_limit_banner() -> None:
    failure = {'settle_reason': 'no-generation-detected', 'submitted': True}
    report = triage(snap('rate-limit-banner'), failure=failure)

    assert 'rate limit' in report['likely_cause']


# --------------------------------------------------------------------------- #
# Repair proposals
# --------------------------------------------------------------------------- #
def test_repair_proposes_the_renamed_send_button() -> None:
    proposals = propose_repairs(snap('send-renamed'))
    send = next(p for p in proposals if p['anchor'] == 'send')

    assert send['confident'] is True
    assert send['suggested_selector'] == '[data-testid="composer-send-v2"]'


# --- SAFETY REGRESSION GUARDS --------------------------------------------- #
# An earlier version of the scorer confidently proposed `send -> #prompt-textarea`
# (the text editor itself) simply because it was an unknown, visible thing in the
# composer. A repair engine that can tell the adapter to click the text box is
# worse than no repair engine. These two tests exist so that never returns.

def test_repair_never_proposes_a_non_control_as_send() -> None:
    for drift in DRIFT_SCENARIOS:
        for proposal in propose_repairs(snap(drift)):
            if proposal['anchor'] != 'send':
                continue
            for candidate in proposal['candidates']:
                assert candidate['id'] != 'prompt-textarea', f'{drift}: proposed the composer as send'
                assert candidate['classification'] != 'unknown' or not proposal['confident']


def test_repair_refuses_the_add_files_decoy() -> None:
    """The real send is gone and an 'Add files' control sits in its place.

    GlassTTY must stay broken rather than click the wrong thing.
    """
    proposals = propose_repairs(snap('decoy-send'))
    send = next(p for p in proposals if p['anchor'] == 'send')

    assert send['confident'] is False
    assert send['suggested_selector'] is None
    assert send['candidates'] == []


def test_confidence_requires_positive_identification() -> None:
    """Outscoring a bad field is not the same as being right."""
    for drift in DRIFT_SCENARIOS:
        for proposal in propose_repairs(snap(drift)):
            if proposal['confident']:
                best = proposal['candidates'][0]
                assert best['classification'] != 'unknown'
                assert best['confidence'] >= CONFIDENT_THRESHOLD


# --------------------------------------------------------------------------- #
# History store
# --------------------------------------------------------------------------- #
def test_store_promotes_a_baseline_and_collapses_a_timeline(tmp_path: Path) -> None:
    store = SurfaceStore(tmp_path / 'surface')
    healthy = snap('none')
    store.save(healthy)
    store.promote(healthy)
    store.save(snap('none'))          # unchanged
    store.save(snap('send-renamed'))  # changed

    assert store.baseline()['fingerprint'] == healthy['fingerprint']
    timeline = store.timeline()
    assert [row['changed'] for row in timeline] == [True, False, True]


# --------------------------------------------------------------------------- #
# The whole loop, end to end: break -> diagnose -> repair -> heal
# --------------------------------------------------------------------------- #
def test_drifted_tab_is_diagnosed_repaired_and_healed(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='send-renamed') as tab:
        engine = engine_for(sock)

        # 1. it is broken
        broken = engine.send('hello')
        assert not broken.ok
        assert broken.composer_cleanup and broken.composer_cleanup['ok']

        # 2. Diagnosis temporarily stages its own unsent draft so ChatGPT's
        # transient send control is observable, then restores the empty composer.
        store_root = tmp_path / 'surface'
        SurfaceStore(store_root).promote(snap('none'))
        report = _diagnose_failure(
            engine,
            broken,
            Namespace(store=str(store_root), tab_id=None, request_timeout=5.0),
        )
        assert report is not None
        assert tab.composer == ''
        assert report['verdict'] == 'surface-drift-blocking'
        send_repair = next(r for r in report['repairs'] if r['anchor'] == 'send')
        assert send_repair['confident']

        # 3. apply the repair as a runtime override — no rebuild
        engine.client.request('surface.overrides.set', {'overrides': {'send': send_repair['suggested_selector']}})
        assert tab.overrides == {'send': '[data-testid="composer-send-v2"]'}

        # 4. it works again
        healed = engine.send('hello')
        assert healed.ok
        assert 'hello' in (healed.text or '')


def test_a_wrong_override_cannot_make_a_broken_tab_pretend_to_work(tmp_path: Path) -> None:
    """An override is a hint, not a bypass. Pointing it at the wrong node must not
    manufacture a success."""
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='send-renamed'):
        engine = engine_for(sock)
        engine.client.request('surface.overrides.set', {'overrides': {'send': '#composer-plus-btn'}})
        result = engine.send('hello')

    assert not result.ok

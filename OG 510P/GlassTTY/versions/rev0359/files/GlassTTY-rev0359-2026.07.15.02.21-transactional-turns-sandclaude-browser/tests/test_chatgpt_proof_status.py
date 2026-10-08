from __future__ import annotations

from pathlib import Path

from chatgpt_proof_status import build_next_action, build_status, pack_status


def test_status_reports_resumable_next_action_for_current_tree(tmp_path: Path) -> None:
    report = build_status(summary_path=tmp_path / 'state.json', require_live=False)

    assert report['tool'] == 'glasstty-chatgpt-proof-status'
    assert report['verdict'] in {'live-proof-pipeline-incomplete', 'live-proof-pipeline-complete'}
    assert report['next_action']['stage']
    assert 'command' in report['next_action']
    assert (tmp_path / 'state.json').exists()


def test_pack_status_treats_readme_only_pack_as_missing(tmp_path: Path) -> None:
    pack = tmp_path / 'pack'
    pack.mkdir()
    (pack / 'README.md').write_text('operator docs only\n', encoding='utf-8')

    status = pack_status(pack, require_live=True, require_privacy_pass=True)

    assert status['has_files'] is False
    assert status['verdict'] == 'evidence-pack-missing'
    assert any('missing or empty' in blocker for blocker in status['blockers'])


def test_next_action_moves_from_privacy_to_publish_when_pack_is_ready() -> None:
    contract = {'exists': True}
    preflight = {'verdict': 'ready-for-live-operator-attempt-not-a-live-proof'}
    capture = {'exists': True, 'ok': True, 'verdict': 'proof-ingest-ok'}
    live_pack = {
        'has_files': True,
        'verdict': 'live-evidence-pack-review-ready',
        'privacy_review': {'verdict': 'privacy-review-pass'},
    }
    publish_bundle = {'exists': False, 'verdict': 'publish-bundle-missing'}

    action = build_next_action(
        contract=contract,
        preflight=preflight,
        capture=capture,
        live_pack=live_pack,
        publish_bundle=publish_bundle,
        require_live=True,
    )

    assert action['stage'] == 'publish-and-verify'
    assert 'proof-publish-bundle' in action['command']


def test_status_capture_stage_mentions_recovery_vault() -> None:
    from chatgpt_proof_status import build_next_action

    action = build_next_action(
        contract={'exists': True},
        preflight={'verdict': 'ready-for-live-operator-attempt-not-a-live-proof'},
        capture={'exists': False},
        live_pack={},
        publish_bundle={},
        require_live=True,
    )

    assert action['stage'] == 'capture-live-proof'
    assert 'Restore recovery vault' in action['command']
    assert 'Download recovery JSON' in action['command']

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_surface_oracle_userscript_is_local_privacy_first() -> None:
    source = (ROOT / 'tools' / 'chatgpt-surface-oracle.user.js').read_text(
        encoding='utf-8',
    )

    assert '// @match        https://chatgpt.com/*' in source
    assert '// @grant        GM_registerMenuCommand' in source
    assert '// @grant        GM_setClipboard' in source
    assert '// @grant        GM_download' in source
    assert 'local_only: true' in source
    assert 'no_cookie_read: true' in source
    assert 'no_local_storage_read: true' in source
    assert 'no_auto_submit: true' in source
    assert 'window.confirm' in source
    assert 'GLASSTTY_USER_SURFACE_CAPSULE_JSON=' in source
    assert 'GLASSTTY_USER_SURFACE_REPORT_JSON=' in source
    assert 'GLASSTTY_USER_SURFACE_DRILL_JSON=' in source
    assert 'runSendDrill' in source
    assert 'auto_copy_results: true' in source
    assert '#composer-submit-button' in source
    assert 'rememberAndCopy(prefix, result)' in source
    assert 'armedCheckpointProof' in source
    assert 'EXPECTED_SURFACE_CONTRACT' in source
    assert 'surface_contract_drift' in source
    assert 'GLASSTTY_USER_SURFACE_DRIFT_JSON=' in source
    assert 'GlassTTY: copy drift verdict' in source
    assert 'eval(' not in source
    assert 'new Function' not in source
    assert "createElement('script'" not in source
    assert 'createElement("script"' not in source
    assert '\u2028' not in source
    assert '\u2029' not in source
    assert max(len(line) for line in source.splitlines()) <= 100


def test_pageworld_restprobe_is_passive_and_paste_safe() -> None:
    source = (ROOT / 'tools' / 'chatgpt-pageworld-restprobe.js').read_text(
        encoding='utf-8',
    )

    assert 'GLASSTTY_PAGEWORLD_REST_JSON=' in source
    assert 'no_network_writes: true' in source
    assert 'no_storage_reads: true' in source
    assert 'no_prompt_submission: true' in source
    assert 'selected_window_keys' in source
    assert 'react_hook' in source
    assert 'editing_capabilities' in source
    assert 'eval(' not in source
    assert 'new Function' not in source
    assert "createElement('script'" not in source
    assert 'createElement("script"' not in source
    assert '\u2028' not in source
    assert '\u2029' not in source
    assert max(len(line) for line in source.splitlines()) <= 100

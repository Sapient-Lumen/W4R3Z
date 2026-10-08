from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from glassttyd.conversation import (
    ATTACH_CHUNK_BYTES,
    BrokerClient,
    BrokerTimeout,
    ConversationEngine,
    EngineConfig,
)
from glassttyd.mock_tab import MockChatGPTTab, build_mock_probe
from glassttyd.surface import (
    build_snapshot,
    is_stable_selector,
    is_volatile_id,
    propose_repairs,
    triage,
)

URL = 'https://chatgpt.com/c/mock'


def engine_for(sock: Path, **overrides) -> ConversationEngine:
    base = dict(poll_interval=0.01, start_grace=0.5, max_wait=5.0, settle_polls=2,
                request_timeout=5.0, attach_timeout=10.0, chip_wait=1.0)
    base.update(overrides)
    return ConversationEngine(BrokerClient(sock, default_timeout=10.0), config=EngineConfig(**base))


def snap(drift: str = 'none', **kwargs):
    return build_snapshot(build_mock_probe(drift, url=URL, **kwargs))


# --------------------------------------------------------------------------- #
# Attachment transfer
# --------------------------------------------------------------------------- #
def test_attach_streams_a_file_and_renders_a_chip(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        result = engine_for(sock).attach(package)

    assert result.ok
    assert result.bytes == package.stat().st_size
    assert result.sha256 == hashlib.sha256(package.read_bytes()).hexdigest()
    assert result.chip_present
    assert tab.attached and tab.attached[0]['name'] == 'package.zip'


def test_attach_chunks_a_file_larger_than_the_native_messaging_limit(tmp_path: Path) -> None:
    """Chrome caps host->extension messages at 1 MB. A real package is bigger than
    that, which is precisely why the userscript queuer needed an HTTP file server.
    GlassTTY chunks instead — and the bytes must survive the round trip intact."""
    payload = bytes(range(256)) * 12_000          # ~3 MB, well past the 1 MB ceiling
    package = tmp_path / 'big.bin'
    package.write_bytes(payload)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        result = engine_for(sock).attach(package)

    assert result.ok
    assert result.chunks > 1
    assert result.chunks == -(-len(payload) // ATTACH_CHUNK_BYTES)
    assert result.bytes == len(payload)
    assert tab.attached[0]['bytes'] == len(payload)   # reassembled byte-exact


def test_attach_streams_from_disk_without_reading_the_whole_file(tmp_path: Path, monkeypatch) -> None:
    payload = bytes(range(256)) * 8_000
    package = tmp_path / 'streamed.bin'
    package.write_bytes(payload)
    expected_digest = hashlib.sha256(payload).hexdigest()
    sock = tmp_path / 'daemon.sock'

    def whole_file_read_is_a_regression(_path):
        raise AssertionError('attach must not use Path.read_bytes()')

    monkeypatch.setattr(Path, 'read_bytes', whole_file_read_is_a_regression)
    with MockChatGPTTab(sock):
        result = engine_for(sock).attach(package)

    assert result.ok
    assert result.sha256 == expected_digest


def test_attach_rejects_a_directory_without_crashing(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        result = engine_for(sock).attach(tmp_path)

    assert not result.ok
    assert 'not a regular file' in (result.error or '')


def test_attachment_transfer_can_be_aborted_without_leaking_browser_state(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    client = BrokerClient(sock, default_timeout=2.0)
    transfer_id = 'aborted-transfer'

    with MockChatGPTTab(sock) as tab:
        begin = client.request('attach.begin', {
            'transfer_id': transfer_id,
            'name': 'partial.bin',
            'mime': 'application/octet-stream',
            'size': 4,
            'chunks': 1,
        })
        aborted = client.request('attach.abort', {'transfer_id': transfer_id})

    assert begin.payload['ok'] is True
    assert aborted.payload['ok'] is True
    assert aborted.payload['aborted'] is True
    assert tab.transfers == {}


def test_attachment_protocol_rejects_unbounded_envelopes_and_chunk_indices(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    client = BrokerClient(sock, default_timeout=2.0)

    with MockChatGPTTab(sock) as tab:
        oversized = client.request('attach.begin', {
            'transfer_id': 'oversized', 'name': 'huge.bin', 'mime': 'application/octet-stream',
            'size': 513 * 1024 * 1024, 'chunks': 1,
        })
        inconsistent = client.request('attach.begin', {
            'transfer_id': 'inconsistent', 'name': 'small.bin', 'mime': 'application/octet-stream',
            'size': 4, 'chunks': 2,
        })
        begin = client.request('attach.begin', {
            'transfer_id': 'bounded', 'name': 'small.bin', 'mime': 'application/octet-stream',
            'size': 4, 'chunks': 1,
        })
        bad_index = client.request('attach.chunk', {
            'transfer_id': 'bounded', 'index': 99, 'data': 'YWJjZA==',
        })
        invalid_begin = client.request('attach.begin', {
            'transfer_id': 'invalid-base64', 'name': 'small.bin', 'mime': 'application/octet-stream',
            'size': 4, 'chunks': 1,
        })
        client.request('attach.chunk', {
            'transfer_id': 'invalid-base64', 'index': 0, 'data': '%%%%',
        })
        invalid_commit = client.request('attach.commit', {'transfer_id': 'invalid-base64'})

    assert oversized.payload['ok'] is False
    assert inconsistent.payload['ok'] is False
    assert begin.payload['ok'] is True
    assert bad_index.payload['ok'] is False
    assert invalid_begin.payload['ok'] is True
    assert invalid_commit.payload['ok'] is False
    assert 'decode failed' in invalid_commit.payload['error']
    assert tab.transfers['bounded']['chunks'] == [None]


def test_attach_refuses_a_zero_byte_file(tmp_path: Path) -> None:
    """An empty archive is truthy and attaches happily. It then poisons everything
    downstream while looking like a model failure. Refuse it at the door."""
    empty = tmp_path / 'empty.zip'
    empty.write_bytes(b'')
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        result = engine_for(sock).attach(empty)

    assert not result.ok
    assert 'zero-byte' in (result.error or '')
    assert tab.attached == []


def test_attach_warns_on_a_suspiciously_small_file(tmp_path: Path) -> None:
    tiny = tmp_path / 'tiny.zip'
    tiny.write_bytes(b'PK')
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock):
        result = engine_for(sock).attach(tiny)

    assert result.ok
    assert any('bytes' in warning for warning in result.warnings)


def test_missing_file_is_reported(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        result = engine_for(sock).attach(tmp_path / 'nope.zip')
    assert not result.ok
    assert 'not found' in (result.error or '')


# --- THE fileless-prompt guard -------------------------------------------- #
def test_send_refuses_to_submit_when_the_attachment_cannot_be_witnessed(tmp_path: Path) -> None:
    """The input accepts the bytes; the page never renders a chip.

    Submitting here sends a prompt that *says* a file is attached and isn't. That
    failure does not look like a failure — it looks like ChatGPT ignoring you, and
    you debug the wrong thing for a day. So: do not submit.
    """
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='silent-upload-failure') as tab:
        result = engine_for(sock).send('review the attached package', attach=[package])

    assert not result.ok
    assert result.submitted is False
    assert 'fileless' in (result.error or '')
    assert result.attachment_cleanup and result.attachment_cleanup['ok']
    assert result.composer_cleanup and result.composer_cleanup['ok']
    assert tab.composer == ''
    assert tab.attached == []


def test_failed_second_attachment_rolls_back_the_first(tmp_path: Path) -> None:
    first = tmp_path / 'first.txt'
    first.write_text('first attachment\n', encoding='utf-8')
    missing = tmp_path / 'missing.txt'
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        result = engine_for(sock).send('review both', attach=[first, missing])

    assert not result.ok
    assert result.submission_outcome == 'not-attempted'
    assert result.attachment_cleanup and result.attachment_cleanup['ok']
    assert result.composer_cleanup and result.composer_cleanup['ok']
    assert tab.composer == ''
    assert tab.attached == []


def test_failed_attachment_rollback_reports_an_unsafe_composer(tmp_path: Path) -> None:
    first = tmp_path / 'first.txt'
    first.write_text('first attachment\n', encoding='utf-8')
    missing = tmp_path / 'missing.txt'
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='sticky-attachment-chip') as tab:
        result = engine_for(sock, chip_wait=0.01).send('review both', attach=[first, missing])

    assert not result.ok
    assert result.attachment_cleanup and not result.attachment_cleanup['ok']
    assert 'inspect and clear the composer' in (result.error or '')
    assert [item['name'] for item in tab.attached] == ['first.txt']


def test_send_refuses_to_mix_preexisting_operator_attachments(tmp_path: Path) -> None:
    operator_file = tmp_path / 'operator.txt'
    requested_file = tmp_path / 'requested.txt'
    operator_file.write_text('operator attachment\n', encoding='utf-8')
    requested_file.write_text('command attachment\n', encoding='utf-8')
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        engine = engine_for(sock)
        assert engine.attach(operator_file).ok
        result = engine.send('review this', attach=[requested_file])

    assert not result.ok
    assert '1 input file(s)' in (result.error or '')
    assert result.attachment_cleanup is None
    assert [item['name'] for item in tab.attached] == ['operator.txt']


def test_send_detects_a_preexisting_chip_after_the_page_consumes_input_files(tmp_path: Path) -> None:
    operator_file = tmp_path / 'operator.txt'
    requested_file = tmp_path / 'requested.txt'
    operator_file.write_text('operator attachment\n', encoding='utf-8')
    requested_file.write_text('command attachment\n', encoding='utf-8')
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='consumed-file-input') as tab:
        engine = engine_for(sock)
        staged = engine.attach(operator_file)
        assert staged.ok and staged.input_files == 0 and staged.chip_present
        result = engine.send('review this', attach=[requested_file])

    assert not result.ok
    assert '1 known chip(s)' in (result.error or '')
    assert result.attachment_cleanup is None
    assert [item['name'] for item in tab.attached] == ['operator.txt']


def test_blocked_submit_rolls_back_staged_attachments(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='send-removed') as tab:
        result = engine_for(sock).send('review this', attach=[package])

    assert not result.ok
    assert result.submission_outcome == 'not-attempted'
    assert result.attachment_cleanup and result.attachment_cleanup['ok']
    assert result.composer_cleanup and result.composer_cleanup['ok']
    assert tab.composer == ''
    assert tab.attached == []


def test_send_preserves_a_preexisting_operator_draft(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        engine = engine_for(sock)
        assert engine.write_prompt('operator draft') == (True, True)
        result = engine.send('automation prompt')

    assert not result.ok
    assert result.submission_outcome == 'not-attempted'
    assert 'operator draft' in (result.error or '')
    assert result.composer_cleanup is None
    assert tab.composer == 'operator draft'
    assert tab.transcript == []


def test_unknown_submit_outcome_is_recorded_and_attachments_are_cleared(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    class UnknownSubmitClient:
        def __init__(self) -> None:
            self.delegate = BrokerClient(sock, default_timeout=10.0)

        def request(self, message_type, payload=None, **kwargs):
            if message_type == 'prompt.submit':
                raise BrokerTimeout('simulated lost submit reply')
            return self.delegate.request(message_type, payload, **kwargs)

    with MockChatGPTTab(sock) as tab:
        engine = ConversationEngine(
            UnknownSubmitClient(),
            config=EngineConfig(request_timeout=5.0, attach_timeout=10.0, chip_wait=1.0),
        )
        result = engine.send('review this', attach=[package])

    assert not result.ok
    assert result.submitted is False
    assert result.submission_outcome == 'unknown'
    assert 'outcome is unknown' in (result.error or '')
    assert result.attachment_cleanup and result.attachment_cleanup['ok']
    assert result.composer_cleanup and result.composer_cleanup['ok']
    assert tab.composer == ''
    assert tab.attached == []


def test_no_require_attachment_allows_the_override(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='silent-upload-failure'):
        result = engine_for(sock, require_attachment=False).send('review this', attach=[package])

    assert result.ok
    assert result.submitted


def test_missing_file_input_is_a_degraded_capability(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 100)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='no-file-input'):
        result = engine_for(sock).attach(package)

    assert not result.ok
    report = triage(snap('no-file-input'))
    lost = [f for f in report['findings'] if f.get('capability') == 'attach_files']
    assert lost and lost[0]['severity'] == 'degraded'


def test_attached_file_travels_with_the_submitted_turn(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        result = engine_for(sock).send('review this', attach=[package])

    assert result.ok
    assert result.attachments and result.attachments[0]['chip_present']
    user_turn = next(t for t in tab.transcript if t['role'] == 'user')
    assert user_turn['attachments'][0]['name'] == 'package.zip'


def test_repeated_identical_chip_controls_still_witness_multiple_attachments(tmp_path: Path) -> None:
    first = tmp_path / 'first.txt'
    second = tmp_path / 'second.txt'
    first.write_text('first attachment\n', encoding='utf-8')
    second.write_text('second attachment\n', encoding='utf-8')
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        engine = engine_for(sock)
        first_result = engine.attach(first)
        second_result = engine.attach(second)

    assert first_result.chip_present
    assert second_result.chip_present
    assert second_result.added_keys == ['testid:attachment-chip']
    assert [item['name'] for item in tab.attached] == ['first.txt', 'second.txt']


def test_filename_already_in_prompt_is_not_treated_as_new_chip_evidence(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 100)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock):
        engine = engine_for(sock)
        engine.write_prompt('Review package.zip carefully')
        result = engine.attach(package)

    assert result.expected_name_visible_before is True
    assert result.expected_name_visible is True
    assert result.expected_name_newly_visible is False
    assert result.chip_present is True  # the independently known chip role proves it


def test_attachment_clear_proves_the_composer_returned_to_baseline(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock) as tab:
        engine = engine_for(sock, chip_wait=0.1)
        attached = engine.attach(package)
        cleared = engine.clear_attachments(attached.composer_keys_before, expected_name=attached.name)

    assert attached.chip_present
    assert cleared.ok
    assert cleared.input_files == 0
    assert cleared.added_keys == []
    assert tab.attached == []


def test_attachment_clear_fails_when_the_chip_remains(tmp_path: Path) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 5000)
    sock = tmp_path / 'daemon.sock'

    with MockChatGPTTab(sock, drift='sticky-attachment-chip'):
        engine = engine_for(sock, chip_wait=0.01)
        attached = engine.attach(package)
        cleared = engine.clear_attachments(attached.composer_keys_before, expected_name=attached.name)

    assert attached.chip_present
    assert not cleared.ok
    assert cleared.input_files == 1
    assert cleared.added_keys
    assert 'remained' in (cleared.error or '')


def test_attachment_clear_refuses_an_old_extension_without_a_witness() -> None:
    class OldExtensionClient:
        def request(self, *_args, **_kwargs):
            return SimpleNamespace(payload={'ok': True, 'adapter': 'chatgpt'})

    engine = ConversationEngine(OldExtensionClient())
    cleared = engine.clear_attachments(['id:prompt-textarea'])

    assert not cleared.ok
    assert 'did not return a cleanup witness' in (cleared.error or '')


# --------------------------------------------------------------------------- #
# Regressions found in the live 2026-07-11 surface report
# --------------------------------------------------------------------------- #
def test_volatile_framework_ids_are_never_offered_as_selectors() -> None:
    """The live report contains 65 [id^="radix-"] nodes — including the composer's
    own effort pill, #radix-_r_ds_. Those ids are regenerated on every page load.
    An override written against one works exactly once, then fails silently."""
    assert is_volatile_id('radix-_r_ds_')
    assert is_volatile_id('radix-_R_ajalpakoac97l35_')
    assert is_volatile_id(':r7:')
    assert not is_volatile_id('composer-submit-button')

    assert not is_stable_selector('#radix-_r_ds_')
    assert not is_stable_selector('div:nth-of-type(1) > button:nth-of-type(2)')
    assert is_stable_selector('#composer-submit-button')
    assert is_stable_selector('[data-testid="send-button"]')


def test_no_repair_is_confident_without_a_durable_selector() -> None:
    for drift in ('none', 'send-renamed', 'send-removed', 'decoy-send', 'volatile-ids'):
        for proposal in propose_repairs(snap(drift, composer_text='hello')):
            if proposal['confident']:
                assert is_stable_selector(proposal['suggested_selector']), drift


def test_empty_composer_does_not_report_a_healthy_page_as_broken() -> None:
    """Straight from the live capture: on a perfectly healthy page with an empty
    composer, #composer-submit-button matched ZERO nodes and the old contract
    declared `surface-drift-blocker`. Send is *hidden until you type*, not gone."""
    report = triage(snap('none', composer_text=''))

    assert report['verdict'] != 'surface-drift-blocking'
    assert not any(f['severity'] == 'critical' for f in report['findings'])
    assert any(f['kind'] == 'capability-unknown' for f in report['findings'])
    assert report['repairs'] == []          # nothing is broken, so nothing to fix


def test_send_is_verifiable_once_the_composer_has_text() -> None:
    report = triage(snap('none', composer_text='a draft'))

    assert report['verdict'] == 'surface-ok'
    assert report['findings'] == []


def test_a_genuinely_missing_send_is_still_caught_when_the_composer_has_text() -> None:
    """The fix must not blind the detector: with text staged, a missing send is real."""
    report = triage(snap('send-removed', composer_text='a draft'))

    assert report['verdict'] == 'surface-drift-blocking'
    assert any(f.get('capability') == 'submit_prompt' for f in report['findings'])


def test_unknown_capability_is_not_a_regression_against_a_baseline() -> None:
    baseline = snap('none', composer_text='drafted')   # send was visible
    idle = snap('none', composer_text='')              # send now unknowable
    report = triage(idle, baseline=baseline)

    assert not any(f['kind'] == 'regression' for f in report['findings'])


def test_effort_pill_is_classified_not_reported_as_an_oddity() -> None:
    """The composer pill (live: __composer-pill, text 'Pro') is a known control."""
    probe = build_mock_probe('none', url=URL)
    pill = next(c for c in probe['controls'] if c['text'] == 'Pro')
    assert pill['classification'] == 'effort-pill'


def test_live_root_composer_controls_have_narrow_role_matchers() -> None:
    """The 2026-07-14 root surface added upload inputs and footer links.

    The links use exact text matching deliberately: a broad ``learn more`` term
    would hide an unrelated future composer action from the oddity hunter.
    """
    source = (
        Path(__file__).resolve().parents[1]
        / 'extension' / 'src' / 'adapters' / 'surface-probe.ts'
    ).read_text(encoding='utf-8')

    assert "ids: ['composer-plus-btn', 'upload-files', 'upload-photos', 'upload-camera']" in source
    assert "testIds: ['composer-plus-btn', 'upload-photos-input']" in source
    assert "exactTexts: ['terms', 'privacy policy', 'learn more']" in source
    assert 'candidate === text' in source


def test_live_authentication_posture_gates_attachment_capability() -> None:
    root = Path(__file__).resolve().parents[1]
    probe = (root / 'extension' / 'src' / 'adapters' / 'surface-probe.ts').read_text(encoding='utf-8')
    adapter = (root / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')

    assert '[data-testid="login-button"]' in probe
    assert '[data-testid="signup-button"]' in probe
    assert "authentication.posture === 'authenticated'" in probe
    assert "authentication.posture !== 'authenticated'" in adapter
    assert 'file attachment requires an authenticated browser session' in adapter


def test_extension_attachment_protocol_is_bounded_and_abortable() -> None:
    root = Path(__file__).resolve().parents[1]
    content = (root / 'extension' / 'src' / 'content' / 'main.ts').read_text(encoding='utf-8')
    adapter = (root / 'extension' / 'src' / 'adapters' / 'chatgpt.ts').read_text(encoding='utf-8')

    assert 'MAX_ACTIVE_ATTACH_TRANSFERS' in content
    assert 'MAX_ATTACHMENT_BYTES' in content
    assert 'payload.index >= transfer.chunks.length' in content
    assert "case 'attach.abort'" in content
    assert 'decodeAttachmentChunks(transfer.chunks, transfer.size)' in content
    assert 'input_files_before' in content
    assert 'composer attachments changed during transfer' in content
    assert 'clearAttachments(document: Document)' in adapter
    assert "new Event('input', { bubbles: true })" in adapter


def test_surface_snapshot_fingerprint_tracks_authentication_posture() -> None:
    authenticated = snap()
    anonymous_probe = build_mock_probe('none', url=URL)
    anonymous_probe['authentication'] = {
        'posture': 'anonymous',
        'login_control_present': True,
        'signup_control_present': True,
        'account_control_present': False,
    }
    anonymous = build_snapshot(anonymous_probe)

    assert authenticated['authentication']['posture'] == 'authenticated'
    assert anonymous['fingerprint'] != authenticated['fingerprint']


def test_surface_triage_explains_anonymous_attachment_loss() -> None:
    probe = build_mock_probe('none', url=URL)
    probe['authentication'] = {
        'posture': 'anonymous',
        'login_control_present': True,
        'signup_control_present': True,
        'account_control_present': False,
    }
    probe['capabilities']['attach_files'] = False

    report = triage(build_snapshot(probe), baseline=snap('none'))
    finding = next(item for item in report['findings'] if item.get('capability') == 'attach_files')
    regression = next(
        item for item in report['findings']
        if item.get('kind') == 'regression' and item.get('capability') == 'attach_files'
    )

    assert report['verdict'] == 'surface-drift-degraded'
    assert report['authentication']['posture'] == 'anonymous'
    assert finding['cause'] == 'authentication-required'
    assert 'logged out' in finding['why']
    assert regression['severity'] == 'degraded'
    assert any('log in to ChatGPT' in action for action in report['next_actions'])


# --------------------------------------------------------------------------- #
# stop / new-chat
# --------------------------------------------------------------------------- #
def test_stop_aborts_a_running_generation(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock) as tab:
        engine = engine_for(sock)
        engine.write_prompt('a long one [[continue]]')
        engine.submit()
        assert engine.stop() is True
        assert tab.generation is None


def test_stop_reports_false_when_nothing_is_generating(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock):
        assert engine_for(sock).stop() is False


def test_new_chat_clears_the_conversation(tmp_path: Path) -> None:
    sock = tmp_path / 'daemon.sock'
    with MockChatGPTTab(sock) as tab:
        engine = engine_for(sock)
        engine.send('first')
        assert tab.transcript

        assert engine.new_chat() is True
        assert tab.transcript == []
        assert tab.latest_output == ''


def test_mock_classifies_the_composer_and_chip_like_the_adapter_does() -> None:
    """The mock has quietly disagreed with the real content script three times now
    (transcript key, witness shape, control classification) and the suite passed
    anyway each time. A mock that is not field-for-field faithful is theatre."""
    probe = build_mock_probe('none', url=URL, attached_files=1)
    by_role = {c['classification'] for c in probe['controls']}

    assert 'composer' in by_role          # the prompt editor is not an "oddity"
    assert 'attachment-chip' in by_role   # the chip is classified, not unknown
    assert 'effort-pill' in by_role
    # A healthy composer must contain nothing the atlas cannot name.
    unknown = [c for c in probe['controls']
               if c['classification'] == 'unknown' and c['region'] == 'composer' and c['visible']]
    assert unknown == [], f"unclassified composer controls: {unknown}"

from __future__ import annotations

import json
from pathlib import Path

import pytest

from glassttyd.cli import _parse_queue_file, _slugify, _substitute_vars, build_parser, cmd_attach, cmd_run
from glassttyd.mock_tab import MockChatGPTTab


def test_parser_registers_conversation_commands() -> None:
    parser = build_parser()
    for command in ('ask', 'chat', 'run', 'mock-tab'):
        args = parser.parse_args([command] if command != 'run' else ['run', 'queue.txt'])
        assert args.func is not None


def test_ask_accepts_engine_flags() -> None:
    args = build_parser().parse_args(['ask', 'hello', '--no-continue', '--max-wait', '30', '--json'])
    assert args.prompt == 'hello'
    assert args.no_continue is True
    assert args.max_wait == 30
    assert args.json is True


def test_attach_command_fails_when_no_chip_can_be_witnessed(tmp_path: Path, capsys) -> None:
    package = tmp_path / 'package.zip'
    package.write_bytes(b'PK\x03\x04' + b'x' * 100)
    sock = tmp_path / 'daemon.sock'
    args = build_parser().parse_args([
        'attach', '--attach', str(package), '--socket', str(sock),
        '--chip-wait', '0.01',
    ])

    with MockChatGPTTab(sock, drift='silent-upload-failure'):
        status = cmd_attach(args)

    capsys.readouterr()
    assert status == 1


def test_parse_blocks_queue_with_names(tmp_path: Path) -> None:
    queue = tmp_path / 'q.txt'
    queue.write_text('--- audit\nAudit the repo.\n\n--- plan\nPlan the next rev.\n', encoding='utf-8')

    items = _parse_queue_file(queue, 'auto')

    assert [item['name'] for item in items] == ['audit', 'plan']
    assert items[0]['prompt'] == 'Audit the repo.'
    assert items[1]['prompt'] == 'Plan the next rev.'


def test_parse_blocks_queue_without_names(tmp_path: Path) -> None:
    queue = tmp_path / 'q.txt'
    queue.write_text('first prompt\n---\nsecond prompt\n', encoding='utf-8')

    items = _parse_queue_file(queue, 'blocks')

    assert [item['prompt'] for item in items] == ['first prompt', 'second prompt']


def test_parse_jsonl_queue_strings_and_objects(tmp_path: Path) -> None:
    queue = tmp_path / 'q.jsonl'
    queue.write_text(
        json.dumps('bare string prompt') + '\n'
        + json.dumps({'prompt': 'object prompt', 'name': 'named', 'vars': {'x': '1'}}) + '\n',
        encoding='utf-8',
    )

    items = _parse_queue_file(queue, 'auto')

    assert items[0]['prompt'] == 'bare string prompt'
    assert items[1]['name'] == 'named'
    assert items[1]['vars'] == {'x': '1'}


def test_parse_jsonl_rejects_malformed_record(tmp_path: Path) -> None:
    queue = tmp_path / 'q.jsonl'
    queue.write_text(json.dumps({'no_prompt_field': True}) + '\n', encoding='utf-8')

    with pytest.raises(SystemExit):
        _parse_queue_file(queue, 'jsonl')


def test_substitute_vars_replaces_and_reports_missing() -> None:
    text, missing = _substitute_vars('Audit {{project}} for {{thing}}', {'project': 'GlassTTY'})

    assert text == 'Audit GlassTTY for {{thing}}'
    assert missing == ['thing']


def test_substitute_vars_clean_when_all_present() -> None:
    text, missing = _substitute_vars('Hello {{name}}', {'name': 'world'})

    assert text == 'Hello world'
    assert missing == []


def test_slugify_produces_safe_filenames() -> None:
    assert _slugify('Audit the repo!! (v2)') == 'audit-the-repo-v2'
    assert _slugify('') == 'prompt'
    assert len(_slugify('x' * 200)) <= 40


def test_run_accepts_pacing_and_resume_flags() -> None:
    args = build_parser().parse_args(
        ['run', 'q.txt', '--resume', '--min-delay', '2', '--max-delay', '5', '--var', 'project=GlassTTY']
    )
    assert args.resume is True
    assert args.min_delay == 2
    assert args.max_delay == 5
    assert args.var == ['project=GlassTTY']


# --- end-to-end queue runs against the mock tab ---------------------------- #
def _run_queue(tmp_path: Path, queue_text: str, out_dir: Path, extra: list[str] | None = None) -> int:
    sock = tmp_path / 'daemon.sock'
    queue = tmp_path / 'queue.txt'
    queue.write_text(queue_text, encoding='utf-8')
    argv = [
        'run', str(queue),
        '--out-dir', str(out_dir),
        '--socket', str(sock),
        '--poll-interval', '0.01',
        '--start-grace', '0.5',
        '--max-wait', '5',
        '--quiet',
    ] + (extra or [])
    args = build_parser().parse_args(argv)
    with MockChatGPTTab(sock):
        return cmd_run(args)


def test_run_executes_queue_and_captures_responses(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'
    code = _run_queue(
        tmp_path,
        '--- audit\nAudit {{project}}.\n\n--- plan\nPlan {{project}}.\n',
        out_dir,
        ['--var', 'project=GlassTTY'],
    )

    assert code == 0
    assert (out_dir / '001-audit.md').read_text().strip().endswith('Audit GlassTTY.')
    assert (out_dir / '002-plan.md').exists()

    records = [json.loads(line) for line in (out_dir / 'transcript.jsonl').read_text().splitlines()]
    assert [r['name'] for r in records] == ['audit', 'plan']
    assert all(r['ok'] for r in records)
    assert not (out_dir / '.glasstty-inflight.json').exists()


def test_run_resume_retries_only_a_definitely_unsubmitted_failure(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'

    first = _run_queue(tmp_path, 'good one\n---\nbad one [[error]]\n---\nthird one\n', out_dir)
    assert first == 1  # a turn did not settle

    # A refused submit definitely did not land, so that item may be fixed and retried.
    second = _run_queue(tmp_path, 'good one\n---\nfixed now\n---\nthird one\n', out_dir, ['--resume'])
    assert second == 0

    records = [json.loads(line) for line in (out_dir / 'transcript.jsonl').read_text().splitlines()]
    final = {r['index']: r for r in records}  # later records overwrite earlier
    assert set(final) == {1, 2, 3}
    assert all(r['ok'] for r in final.values())
    # turn 2 was attempted twice (once failing, once settling); 1 and 3 only once
    assert sum(1 for r in records if r['index'] == 2) == 2
    assert sum(1 for r in records if r['index'] == 1) == 1


def test_run_resume_refuses_a_submitted_unsettled_turn(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'
    queue = 'this may have landed [[stall]]\n'

    assert _run_queue(tmp_path, queue, out_dir) == 1
    with pytest.raises(SystemExit, match='avoid a duplicate prompt'):
        _run_queue(tmp_path, queue, out_dir, ['--resume'])

    records = (out_dir / 'transcript.jsonl').read_text().splitlines()
    assert len(records) == 1
    assert json.loads(records[0])['submission_outcome'] == 'submitted'


def test_run_resume_refuses_changed_successful_prompt(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'
    assert _run_queue(tmp_path, 'original prompt\n', out_dir) == 0

    with pytest.raises(SystemExit, match='prompt, name, template values, or attachment content changed'):
        _run_queue(tmp_path, 'changed prompt\n', out_dir, ['--resume'])


def test_run_resume_refuses_changed_attachment_content(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'
    package = tmp_path / 'package.txt'
    package.write_text('first content\n', encoding='utf-8')
    queue = 'review the attachment\n'

    assert _run_queue(tmp_path, queue, out_dir, ['--attach', str(package)]) == 0
    package.write_text('second content\n', encoding='utf-8')

    with pytest.raises(SystemExit, match='attachment content changed'):
        _run_queue(tmp_path, queue, out_dir, ['--resume', '--attach', str(package)])


def test_run_resume_refuses_legacy_index_only_success(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'
    out_dir.mkdir()
    (out_dir / 'transcript.jsonl').write_text(
        json.dumps({'index': 1, 'ok': True, 'submitted': True}) + '\n',
        encoding='utf-8',
    )

    with pytest.raises(SystemExit, match='predates content-addressed queue inputs'):
        _run_queue(tmp_path, 'same-looking prompt\n', out_dir, ['--resume'])


def test_run_resume_refuses_an_unresolved_inflight_turn(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'
    out_dir.mkdir()
    (out_dir / '.glasstty-inflight.json').write_text(json.dumps({
        'schema': 'glasstty.queue-inflight/v1',
        'attempt_id': 'lost-after-submit',
        'index': 1,
        'name': 'prompt-001',
    }) + '\n', encoding='utf-8')

    with pytest.raises(SystemExit, match='submission may have landed'):
        _run_queue(tmp_path, 'possibly submitted\n', out_dir, ['--resume'])


def test_run_resume_recreates_a_missing_response_from_the_transcript(tmp_path: Path) -> None:
    out_dir = tmp_path / 'out'
    queue = 'recover my response\n'
    assert _run_queue(tmp_path, queue, out_dir) == 0
    response = out_dir / '001-recover-my-response.md'
    expected = response.read_text(encoding='utf-8')
    response.unlink()

    assert _run_queue(tmp_path, queue, out_dir, ['--resume']) == 0
    assert response.read_text(encoding='utf-8') == expected

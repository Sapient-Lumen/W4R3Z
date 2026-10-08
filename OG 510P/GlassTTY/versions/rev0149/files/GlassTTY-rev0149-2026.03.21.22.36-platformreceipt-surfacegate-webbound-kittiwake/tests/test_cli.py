from __future__ import annotations

import json

from glassttyd.cli import (
    build_overflow_prune_report,
    build_overflow_report,
    build_parser,
    cmd_overflow_prune,
    cmd_overflow_report,
    describe_matching_receivers,
    describe_receiver_resolution,
    extract_receivers_from_browser_event,
    extract_supported_tabs_from_browser_event,
    extract_target_tab_from_browser_event,
    extract_text_from_browser_event,
    make_envelope,
    receiver_key,
    receiver_is_active_outermost,
    receiver_is_outermost,
    receiver_label,
    receiver_matches,
    select_matching_receivers,
)


def test_make_envelope_keeps_tab_id() -> None:
    envelope = make_envelope('prompt.read', {}, tab_id=77)
    assert envelope['type'] == 'prompt.read'
    assert envelope['tab_id'] == 77


def test_submit_prompt_parser_accepts_tab_id() -> None:
    parser = build_parser()
    args = parser.parse_args(['submit-prompt', '--wait', '--tab-id', '9'])
    assert args.command == 'submit-prompt'
    assert args.wait is True
    assert args.tab_id == 9


def test_select_tab_parser_accepts_wait() -> None:
    parser = build_parser()
    args = parser.parse_args(['select-tab', '42', '--wait'])
    assert args.command == 'select-tab'
    assert args.tab_id == 42
    assert args.wait is True




def test_list_receivers_parser_accepts_tab_id() -> None:
    parser = build_parser()
    args = parser.parse_args(['list-receivers', '--tab-id', '12'])
    assert args.command == 'list-receivers'
    assert args.tab_id == 12


def test_select_receiver_parser_accepts_wait() -> None:
    parser = build_parser()
    args = parser.parse_args(['select-receiver', '42', 'doc:child-7', '--wait'])
    assert args.command == 'select-receiver'
    assert args.tab_id == 42
    assert args.receiver_key == 'doc:child-7'
    assert args.wait is True


def test_clear_receiver_override_parser_accepts_wait() -> None:
    parser = build_parser()
    args = parser.parse_args(['clear-receiver-override', '42', '--wait'])
    assert args.command == 'clear-receiver-override'
    assert args.tab_id == 42
    assert args.wait is True

def test_read_latest_parser_accepts_text_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(['read-latest', '--wait', '--text'])
    assert args.command == 'read-latest'
    assert args.wait is True
    assert args.text is True


def test_trace_parser_accepts_limit_and_wait() -> None:
    parser = build_parser()
    args = parser.parse_args(['trace', '--wait', '--limit', '25'])
    assert args.command == 'trace'
    assert args.wait is True
    assert args.limit == 25


def test_probe_parser_accepts_health_limit_and_offscreen() -> None:
    parser = build_parser()
    args = parser.parse_args(['probe', '--wait', '--limit', '33', '--await-health-ms', '2200', '--ensure-offscreen'])
    assert args.command == 'probe'
    assert args.wait is True
    assert args.limit == 33
    assert args.await_health_ms == 2200
    assert args.ensure_offscreen is True



def test_compare_coverage_experiments_parser_accepts_paths_and_override() -> None:
    parser = build_parser()
    args = parser.parse_args(['compare-coverage-experiments', 'before.json', 'after.json', '--experiment-id', 'manifest_match_about_blank', '--pretty'])
    assert args.command == 'compare-coverage-experiments'
    assert args.baseline == 'before.json'
    assert args.candidate == 'after.json'
    assert args.experiment_id == 'manifest_match_about_blank'
    assert args.pretty is True


def test_content_script_experiment_parser_accepts_tab_id() -> None:
    parser = build_parser()
    args = parser.parse_args(['content-script-experiment', '--tab-id', '11'])
    assert args.command == 'content-script-experiment'
    assert args.tab_id == 11


def test_set_content_script_experiment_parser_accepts_wait() -> None:
    parser = build_parser()
    args = parser.parse_args(['set-content-script-experiment', 'manifest_match_about_blank', '--wait', '--tab-id', '8'])
    assert args.command == 'set-content-script-experiment'
    assert args.experiment_id == 'manifest_match_about_blank'
    assert args.wait is True
    assert args.tab_id == 8


def test_clear_content_script_experiment_parser_accepts_wait() -> None:
    parser = build_parser()
    args = parser.parse_args(['clear-content-script-experiment', '--wait'])
    assert args.command == 'clear-content-script-experiment'
    assert args.wait is True


def test_offscreen_dom_parser_accepts_selectors_and_stdin() -> None:
    parser = build_parser()
    args = parser.parse_args(['offscreen-dom', '-', '--selector', 'textarea', '--selector', '[contenteditable=true]', '--max-candidates', '5'])
    assert args.command == 'offscreen-dom'
    assert args.html_file == '-'
    assert args.selector == ['textarea', '[contenteditable=true]']
    assert args.max_candidates == 5

def test_offscreen_fixture_parser_accepts_base_url() -> None:
    parser = build_parser()
    args = parser.parse_args(['offscreen-fixture', 'sample.html', '--base-url', 'https://claude.ai/chat/example', '--selector', 'main', '--max-candidates', '6'])
    assert args.command == 'offscreen-fixture'
    assert args.html_file == 'sample.html'
    assert args.base_url == 'https://claude.ai/chat/example'
    assert args.selector == ['main']
    assert args.max_candidates == 6


def test_plan_fixture_parser_accepts_pretty_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(['plan-fixture', 'sample.json', '--pretty'])
    assert args.command == 'plan-fixture'
    assert args.fixture == 'sample.json'
    assert args.pretty is True


def test_extract_text_from_browser_event() -> None:
    message = {'stream': 'browser_event', 'message': {'payload': {'text': 'hello'}}}
    assert extract_text_from_browser_event(message) == 'hello'


def test_extract_supported_tabs_from_browser_event() -> None:
    message = {
        'stream': 'browser_event',
        'message': {
            'payload': {
                'supportedTabs': [
                    {'tabId': 7, 'url': 'https://claude.ai/chat/abc'},
                    {'tabId': 8, 'url': 'https://claude.ai/chat/def'},
                ]
            }
        },
    }
    tabs = extract_supported_tabs_from_browser_event(message)
    assert [tab['tabId'] for tab in tabs] == [7, 8]




def test_extract_target_tab_from_browser_event_prefers_selected_id() -> None:
    message = {
        'stream': 'browser_event',
        'message': {
            'payload': {
                'selectedTargetTabId': 8,
                'supportedTabs': [
                    {'tabId': 7, 'url': 'https://claude.ai/chat/abc'},
                    {'tabId': 8, 'url': 'https://claude.ai/chat/def', 'title': 'Chosen'},
                ]
            }
        },
    }
    target = extract_target_tab_from_browser_event(message)
    assert target is not None
    assert target['tabId'] == 8


def test_extract_receivers_from_browser_event_filters_by_tab() -> None:
    message = {
        'stream': 'browser_event',
        'message': {
            'payload': {
                'supportedTabs': [
                    {
                        'tabId': 7,
                        'selectedReceiverKey': 'doc:doc-top',
                        'receivers': [
                            {'documentId': 'doc-top', 'frameId': 0, 'receiverReady': True, 'lastSeenAt': '2026-03-08T22:20:00Z'},
                            {'documentId': 'doc-child', 'frameId': 2, 'receiverReady': False, 'lastSeenAt': '2026-03-08T22:20:01Z'},
                        ],
                    },
                    {
                        'tabId': 8,
                        'receivers': [
                            {'frameId': 5, 'receiverReady': True, 'lastSeenAt': '2026-03-08T22:20:02Z'},
                        ],
                    },
                ]
            }
        },
    }
    rows = extract_receivers_from_browser_event(message, 7)
    assert [row['tabId'] for row in rows] == [7, 7]
    assert [receiver_key(row) for row in rows] == ['doc:doc-top', 'doc:doc-child']
    all_rows = extract_receivers_from_browser_event(message)
    assert len(all_rows) == 3

def test_native_message_budget_parser_accepts_multiple_paths_and_pretty_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(['native-message-budget', 'fixtures', 'sample.json', '--pretty'])
    assert args.command == 'native-message-budget'
    assert args.path == ['fixtures', 'sample.json']
    assert args.pretty is True


def test_overflow_report_parser_accepts_artifact_and_include_message() -> None:
    parser = build_parser()
    args = parser.parse_args(['overflow-report', '--artifact', '/tmp/overflow.json', '--include-message'])
    assert args.command == 'overflow-report'
    assert args.artifact == '/tmp/overflow.json'
    assert args.include_message is True


def test_overflow_prune_parser_accepts_retention_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(['overflow-prune', '--keep', '3', '--max-age-days', '7', '--max-disk-bytes', '4096', '--apply'])
    assert args.command == 'overflow-prune'
    assert args.keep == 3
    assert args.max_age_days == 7
    assert args.max_disk_bytes == 4096
    assert args.apply is True


def test_build_overflow_report_uses_latest_summary_without_dumping_full_message(monkeypatch, tmp_path, capsys) -> None:
    home = tmp_path / 'glasstty-home'
    artifact = home / 'state' / 'fixtures' / 'oversized-host-outbound-sample.json'
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T10:00:00Z',
        'budget': {'size_bytes': 1049000, 'limit_bytes': 1048576, 'fits': False},
        'message': {
            'type': 'bridge.offscreen_fixture',
            'request_id': 'req-overflow',
            'payload': {'blob': 'x' * 5000, 'note': 'big'},
        },
    }), encoding='utf-8')
    latest = home / 'state' / 'latest' / 'oversized-host-outbound.json'
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'artifact_path': str(artifact),
        'original_type': 'bridge.offscreen_fixture',
        'size_bytes': 1049000,
        'limit_bytes': 1048576,
        'captured_at': '2026-03-17T10:00:00Z',
    }), encoding='utf-8')
    monkeypatch.setenv('GLASSTTY_HOME', str(home))

    report = build_overflow_report()
    assert report['artifact_exists'] is True
    assert report['inventory']['artifact_count'] == 1
    assert report['artifact_summary']['message_type'] == 'bridge.offscreen_fixture'
    assert report['artifact_summary']['payload_keys'] == ['blob', 'note']
    assert 'artifact_message' not in report
    assert report['artifact_summary']['message_excerpt'].endswith('...')

    rc = cmd_overflow_report(type('Args', (), {'artifact': None, 'include_message': False})())
    captured = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert captured['artifact_summary']['message_type'] == 'bridge.offscreen_fixture'
    assert 'artifact_message' not in captured


def test_cmd_overflow_report_returns_missing_status_for_dangling_artifact(monkeypatch, tmp_path, capsys) -> None:
    home = tmp_path / 'glasstty-home'
    latest = home / 'state' / 'latest' / 'oversized-host-outbound.json'
    latest.parent.mkdir(parents=True, exist_ok=True)
    missing = home / 'state' / 'fixtures' / 'missing.json'
    latest.write_text(json.dumps({'artifact_path': str(missing), 'original_type': 'bridge.offscreen_fixture'}), encoding='utf-8')
    monkeypatch.setenv('GLASSTTY_HOME', str(home))
    rc = cmd_overflow_report(type('Args', (), {'artifact': None, 'include_message': False})())
    captured = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert captured['artifact_exists'] is False


def test_build_overflow_prune_report_plans_and_applies_retention(monkeypatch, tmp_path, capsys) -> None:
    home = tmp_path / 'glasstty-home'
    fixtures = home / 'state' / 'fixtures'
    fixtures.mkdir(parents=True, exist_ok=True)
    newest = fixtures / 'oversized-host-outbound-newest.json'
    newest.write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T10:02:00Z',
        'budget': {'size_bytes': 400, 'limit_bytes': 1048576, 'fits': False},
        'message': {'type': 'bridge.offscreen_fixture', 'request_id': 'req-newest', 'payload': {'blob': 'n'}},
    }), encoding='utf-8')
    middle = fixtures / 'oversized-host-outbound-middle.json'
    middle.write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T10:01:00Z',
        'budget': {'size_bytes': 300, 'limit_bytes': 1048576, 'fits': False},
        'message': {'type': 'bridge.offscreen_fixture', 'request_id': 'req-middle', 'payload': {'blob': 'm'}},
    }), encoding='utf-8')
    oldest = fixtures / 'oversized-host-outbound-oldest.json'
    oldest.write_text(json.dumps({
        'kind': 'oversized-host-outbound',
        'captured_at': '2026-03-17T10:00:00Z',
        'budget': {'size_bytes': 200, 'limit_bytes': 1048576, 'fits': False},
        'message': {'type': 'bridge.offscreen_fixture', 'request_id': 'req-oldest', 'payload': {'blob': 'o'}},
    }), encoding='utf-8')
    latest = home / 'state' / 'latest' / 'oversized-host-outbound.json'
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps({'artifact_path': str(newest), 'original_type': 'bridge.offscreen_fixture'}), encoding='utf-8')
    monkeypatch.setenv('GLASSTTY_HOME', str(home))

    report = build_overflow_prune_report(keep=1)
    assert report['plan']['delete_count'] == 2
    assert newest.exists() is True
    assert report['plan']['inventory']['artifact_count'] == 3

    rc = cmd_overflow_prune(type('Args', (), {'keep': 1, 'max_age_days': None, 'max_disk_bytes': None, 'apply': True})())
    captured = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert captured['applied']['deleted_count'] == 2
    assert newest.exists() is True
    assert middle.exists() is False
    assert oldest.exists() is False
    assert captured['post_inventory']['artifact_count'] == 1


def test_resolve_receiver_parser_accepts_filters() -> None:
    parser = build_parser()
    args = parser.parse_args(['resolve-receiver', '42', '--url-contains', 'frame', '--frame-path-contains', 'claude.ai', '--frame-depth', '1', '--document-lifecycle', 'active', '--active-outermost', '--ready-only', '--explain', '--set-override', '--wait'])
    assert args.command == 'resolve-receiver'
    assert args.tab_id == 42
    assert args.url_contains == 'frame'
    assert args.frame_path_contains == 'claude.ai'
    assert args.frame_depth == 1
    assert args.document_lifecycle == 'active'
    assert args.active_outermost is True
    assert args.ready_only is True
    assert args.explain is True
    assert args.set_override is True
    assert args.wait is True



def test_receiver_matches_uses_frame_metadata_filters() -> None:
    receiver = {
        'documentId': 'doc-child',
        'frameId': 2,
        'frameType': 'sub_frame',
        'frameUrl': 'https://claude.ai/artifacts/frame',
        'frameDepth': 1,
        'framePathHosts': ['claude.ai', 'claude.ai'],
        'framePathUrls': ['https://claude.ai/chat/top', 'https://claude.ai/artifacts/frame'],
        'framePathLabel': 'claude.ai → claude.ai',
        'receiverReady': True,
    }
    assert receiver_matches(receiver, receiver_key_filter='doc:doc-child') is True
    assert receiver_matches(receiver, frame_id=2, frame_type='sub_frame', url_contains='artifacts', frame_host_contains='claude.ai', frame_path_contains='claude.ai →', frame_depth=1, ready_only=True) is True
    assert receiver_matches(receiver, top_frame=True) is False
    assert receiver_matches(receiver, active_outermost=True) is False
    assert receiver_matches(receiver, document_lifecycle='active') is False
    assert receiver_matches(receiver, url_contains='settings') is False
    assert receiver_matches(receiver, frame_depth=2) is False



def test_select_matching_receivers_filters_rows() -> None:
    rows = [
        {'tabId': 7, 'documentId': 'doc-top', 'frameId': 0, 'receiverReady': True, 'frameUrl': 'https://claude.ai/chat/top', 'frameDepth': 0, 'framePathHosts': ['claude.ai']},
        {'tabId': 7, 'documentId': 'doc-child', 'frameId': 2, 'receiverReady': True, 'frameType': 'sub_frame', 'frameUrl': 'https://claude.ai/chat/frame', 'frameDepth': 1, 'framePathHosts': ['claude.ai', 'claude.ai'], 'framePathLabel': 'claude.ai → claude.ai'},
        {'tabId': 7, 'frameId': 9, 'receiverReady': False, 'frameType': 'sub_frame', 'frameUrl': 'https://claude.ai/chat/stale', 'frameDepth': 2, 'framePathHosts': ['claude.ai', 'claude.ai', 'claude.ai'], 'framePathLabel': 'claude.ai → claude.ai → claude.ai'},
    ]
    ready_child = select_matching_receivers(rows, ready_only=True, frame_type='sub_frame', url_contains='frame', frame_depth=1)
    assert [receiver_key(row) for row in ready_child] == ['doc:doc-child']
    depth_two = select_matching_receivers(rows, frame_path_contains='→ claude.ai →', frame_depth=2)
    assert [receiver_key(row) for row in depth_two] == ['frame:9']


def test_receiver_label_prefers_frame_path_context() -> None:
    receiver = {
        'documentId': 'doc-child',
        'frameId': 4,
        'frameUrl': 'https://docs.example.test/embed/pane',
        'frameDepth': 2,
        'framePathHosts': ['app.example.test', 'docs.example.test', 'docs.example.test'],
        'framePathLabel': 'app.example.test → docs.example.test → docs.example.test',
        'receiverReady': True,
    }
    assert 'depth:2' in receiver_label(receiver)
    assert 'app.example.test → docs.example.test → docs.example.test' in receiver_label(receiver)


def test_receiver_outermost_helpers_use_frame_type_and_lifecycle() -> None:
    prerender_outermost = {
        'documentId': 'doc-prerender',
        'frameId': 41,
        'frameType': 'outermost_frame',
        'documentLifecycle': 'prerender',
        'frameUrl': 'https://claude.ai/chat/prerender',
        'receiverReady': True,
    }
    active_outermost = {
        'documentId': 'doc-active',
        'frameId': 0,
        'frameType': 'outermost_frame',
        'documentLifecycle': 'active',
        'frameUrl': 'https://claude.ai/chat/live',
        'receiverReady': True,
    }
    assert receiver_is_outermost(prerender_outermost) is True
    assert receiver_is_active_outermost(prerender_outermost) is False
    assert receiver_matches(prerender_outermost, top_frame=True) is True
    assert receiver_matches(prerender_outermost, active_outermost=True) is False
    assert receiver_matches(prerender_outermost, document_lifecycle='prerender') is True
    assert receiver_is_active_outermost(active_outermost) is True
    assert receiver_matches(active_outermost, top_frame=True, active_outermost=True, document_lifecycle='active') is True


def test_select_matching_receivers_can_target_active_outermost() -> None:
    rows = [
        {
            'tabId': 7,
            'documentId': 'doc-prerender-top',
            'frameId': 41,
            'frameType': 'outermost_frame',
            'documentLifecycle': 'prerender',
            'receiverReady': True,
            'frameUrl': 'https://claude.ai/chat/prerender',
        },
        {
            'tabId': 7,
            'documentId': 'doc-active-top',
            'frameId': 0,
            'frameType': 'outermost_frame',
            'documentLifecycle': 'active',
            'receiverReady': True,
            'frameUrl': 'https://claude.ai/chat/live',
        },
        {
            'tabId': 7,
            'documentId': 'doc-child',
            'frameId': 2,
            'frameType': 'sub_frame',
            'documentLifecycle': 'active',
            'receiverReady': True,
            'frameUrl': 'https://claude.ai/chat/frame',
            'frameDepth': 1,
            'framePathHosts': ['claude.ai', 'claude.ai'],
            'framePathLabel': 'claude.ai → claude.ai',
        },
    ]
    outermost = select_matching_receivers(rows, top_frame=True)
    assert [receiver_key(row) for row in outermost] == ['doc:doc-active-top', 'doc:doc-prerender-top']
    active_outermost = select_matching_receivers(rows, active_outermost=True, ready_only=True)
    assert [receiver_key(row) for row in active_outermost] == ['doc:doc-active-top']


def test_receiver_label_treats_nonzero_outermost_as_top_frame() -> None:
    receiver = {
        'documentId': 'doc-prerender',
        'frameId': 41,
        'frameType': 'outermost_frame',
        'documentLifecycle': 'prerender',
        'frameUrl': 'https://claude.ai/chat/prerender',
        'receiverReady': True,
    }
    label = receiver_label(receiver)
    assert label.startswith('top-frame · doc:doc-prer')
    assert 'claude.ai' in label
    assert 'prerender' in label


def test_select_matching_receivers_sorts_by_resolution_policy() -> None:
    rows = [
        {
            'tabId': 7,
            'documentId': 'doc-prerender-top',
            'frameId': 41,
            'frameType': 'outermost_frame',
            'documentLifecycle': 'prerender',
            'receiverReady': True,
            'frameUrl': 'https://claude.ai/chat/prerender',
            'lastSeenAt': '2026-03-09T09:30:01Z',
        },
        {
            'tabId': 7,
            'documentId': 'doc-child-fresh',
            'frameId': 2,
            'frameType': 'sub_frame',
            'documentLifecycle': 'active',
            'receiverReady': True,
            'frameDepth': 1,
            'frameUrl': 'https://claude.ai/chat/frame',
            'lastSeenAt': '2026-03-09T09:30:03Z',
        },
        {
            'tabId': 7,
            'documentId': 'doc-active-top',
            'frameId': 0,
            'frameType': 'outermost_frame',
            'documentLifecycle': 'active',
            'receiverReady': True,
            'frameUrl': 'https://claude.ai/chat/live',
            'lastSeenAt': '2026-03-09T09:30:02Z',
        },
    ]
    matches = select_matching_receivers(rows, ready_only=True)
    assert [receiver_key(row) for row in matches] == ['doc:doc-active-top', 'doc:doc-child-fresh', 'doc:doc-prerender-top']


def test_describe_receiver_resolution_explains_rank_inputs() -> None:
    receiver = {
        'documentId': 'doc-active-top',
        'frameId': 0,
        'frameType': 'outermost_frame',
        'documentLifecycle': 'active',
        'receiverReady': True,
        'frameDepth': 0,
        'frameUrl': 'https://claude.ai/chat/live',
        'lastSeenAt': '2026-03-09T09:30:02Z',
    }
    summary = describe_receiver_resolution(receiver, rank=1)
    assert summary['rank'] == 1
    assert summary['receiverKey'] == 'doc:doc-active-top'
    assert summary['outermost'] is True
    assert summary['activeOutermost'] is True
    assert summary['ready'] is True
    assert summary['rankingVector']['frameDepth'] == 0
    assert 'lifecycle=active_or_unknown' in summary['reasons']
    assert 'frame=outermost' in summary['reasons']
    assert 'receiver=ready' in summary['reasons']


def test_describe_matching_receivers_returns_ranked_summaries() -> None:
    rows = [
        {
            'documentId': 'doc-prerender-top',
            'frameId': 41,
            'frameType': 'outermost_frame',
            'documentLifecycle': 'prerender',
            'receiverReady': True,
            'frameUrl': 'https://claude.ai/chat/prerender',
            'lastSeenAt': '2026-03-09T09:30:01Z',
        },
        {
            'documentId': 'doc-active-top',
            'frameId': 0,
            'frameType': 'outermost_frame',
            'documentLifecycle': 'active',
            'receiverReady': True,
            'frameUrl': 'https://claude.ai/chat/live',
            'lastSeenAt': '2026-03-09T09:30:02Z',
        },
    ]
    ranked = describe_matching_receivers(rows)
    assert [item['receiverKey'] for item in ranked] == ['doc:doc-active-top', 'doc:doc-prerender-top']
    assert [item['rank'] for item in ranked] == [1, 2]

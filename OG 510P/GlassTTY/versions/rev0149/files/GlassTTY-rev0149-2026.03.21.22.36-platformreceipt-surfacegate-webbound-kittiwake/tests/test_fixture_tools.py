from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_seed_fixture_corpus_and_index(tmp_path: Path) -> None:
    corpus = tmp_path / 'corpus'
    subprocess.check_call([sys.executable, str(ROOT / 'scripts' / 'seed-fixture-corpus.py'), str(corpus), '--force'])
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'index-fixtures.py'), str(corpus)], text=True)
    data = json.loads(output)
    assert data['count'] == 11
    assert data['by_adapter']['fixturelab'] == 8
    assert data['by_adapter']['offscreen-html'] == 2
    assert data['by_adapter']['claude'] == 1
    sample = next(item for item in data['fixtures'] if item['adapter'] == 'claude')
    live_dialog = next(item for item in data['fixtures'] if item['path'].endswith('fixturelab-dialog-live.json'))
    assert live_dialog['top_dialog_name'] == 'Profile settings'
    assert live_dialog['top_submit_label'] == 'Save'
    assert sample['top_input_locator_strategy'] in {'role', 'label', 'placeholder', 'css', None}
    assert sample['top_input_locator_root_strategy'] in {'page', 'form_name', 'fieldset_legend', 'dialog_name', 'frame_path_selectors', 'frame_selector', 'frame_name', 'frame_title', 'frame_path_selectors+form_name', 'frame_selector+form_name', 'frame_selector+fieldset_legend', 'frame_name+form_name', 'frame_name+fieldset_legend', None}


def test_compare_fixtures_reports_changed_output_hint(tmp_path: Path) -> None:
    left = tmp_path / 'left.json'
    right = tmp_path / 'right.json'
    left.write_text(json.dumps({'message': {'payload': {'adapter': 'claude', 'title': 'Thread', 'url': 'https://claude.ai/chat/a', 'prompt': 'hello', 'latest_output': 'world', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea', 'label_text': 'Message', 'description_text': 'Type your request', 'fieldset_legend': 'Composer'}], 'outputs': [{'selector_hint': 'article'}]}, 'metadata': {'top_submit_label': 'Send', 'top_submit_action': 'https://claude.ai/submit', 'semantic_outline': {'form_actions': ['https://claude.ai/submit'], 'prompt_descriptions': ['Type your request'], 'fieldset_legends': ['Composer'], 'control_kinds': ['textbox'], 'link_hosts': ['claude.ai']}}}}}), encoding='utf-8')
    right.write_text(json.dumps({'message': {'payload': {'adapter': 'claude', 'title': 'Thread', 'url': 'https://claude.ai/chat/a', 'prompt': 'hello there', 'latest_output': 'world expanded', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea', 'label_text': 'Reply', 'description_text': 'Reply to Claude', 'fieldset_legend': 'Reply box'}], 'outputs': [{'selector_hint': '.assistant'}]}, 'metadata': {'top_submit_label': 'Continue', 'top_submit_action': 'https://claude.ai/respond', 'semantic_outline': {'form_actions': ['https://claude.ai/respond'], 'prompt_descriptions': ['Reply to Claude'], 'fieldset_legends': ['Reply box'], 'control_kinds': ['textbox'], 'link_hosts': ['claude.ai']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'compare-fixtures.py'), str(left), str(right)], text=True)
    data = json.loads(output)
    assert data['delta']['same_adapter'] is True
    assert data['delta']['output_hint_changed'] is True
    assert data['delta']['input_label_changed'] is True
    assert data['delta']['input_description_changed'] is True
    assert data['delta']['fieldset_legend_changed'] is True
    assert data['delta']['submit_label_changed'] is True
    assert data['delta']['submit_action_changed'] is True
    assert data['delta']['submit_action_kind_changed'] is False
    assert data['delta']['input_locator_strategy_changed'] in {True, False}
    assert data['delta']['input_locator_root_strategy_changed'] in {True, False}
    assert data['delta']['input_locator_hint_changed'] is True
    assert data['delta']['submit_locator_strategy_changed'] in {True, False}
    assert data['delta']['submit_locator_root_strategy_changed'] in {True, False}
    assert data['delta']['submit_locator_hint_changed'] is True
    assert data['delta']['form_action_changed'] is True
    assert data['delta']['prompt_length_delta'] > 0


def test_cli_index_and_compare_commands(tmp_path: Path) -> None:
    corpus = tmp_path / 'corpus'
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT / 'daemon' / 'src') + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    subprocess.check_call([sys.executable, '-m', 'glassttyd.cli', 'seed-fixture-corpus', str(corpus), '--force'], env=env)
    indexed = subprocess.check_output([sys.executable, '-m', 'glassttyd.cli', 'index-fixtures', str(corpus)], text=True, env=env)
    data = json.loads(indexed)
    assert data['count'] == 11
    compared = subprocess.check_output([sys.executable, '-m', 'glassttyd.cli', 'compare-fixtures', str(corpus / 'fixturelab-home.json'), str(corpus / 'fixturelab-thread.json')], text=True, env=env)
    compare = json.loads(compared)
    assert compare['delta']['same_adapter'] is True
    assert compare['delta']['latest_output_length_delta'] != 0
    assert 'input_description_changed' in compare['delta']
    assert 'submit_action_changed' in compare['delta']


def test_compare_fixtures_reports_accessibility_and_choice_drift(tmp_path: Path) -> None:
    left = tmp_path / 'left-select.json'
    right = tmp_path / 'right-select.json'
    left.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Profile', 'url': 'https://example.test/profile', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'select#visibility', 'label_text': 'Visibility', 'accessible_name': 'Profile visibility', 'description_text': 'Choose who can see this', 'form_name': 'Profile settings', 'option_count': 2, 'option_labels': ['Public', 'Private'], 'selected_options': ['Public'], 'control_kind': 'combobox'}], 'outputs': []}, 'metadata': {'top_submit_label': 'Save', 'top_submit_action': 'https://example.test/profile/save', 'semantic_outline': {'accessible_names': ['Profile visibility'], 'prompt_descriptions': ['Choose who can see this'], 'form_names': ['Profile settings'], 'option_labels': ['Public', 'Private'], 'form_actions': ['https://example.test/profile/save'], 'control_kinds': ['combobox'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    right.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Profile', 'url': 'https://example.test/profile', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'select#visibility', 'label_text': 'Visibility', 'accessible_name': 'Audience', 'description_text': 'Choose your audience', 'form_name': 'Audience settings', 'option_count': 3, 'option_labels': ['Public', 'Team', 'Private'], 'selected_options': ['Team'], 'control_kind': 'combobox'}], 'outputs': []}, 'metadata': {'top_submit_label': 'Apply', 'top_submit_action': 'https://example.test/profile/apply', 'semantic_outline': {'accessible_names': ['Audience'], 'prompt_descriptions': ['Choose your audience'], 'form_names': ['Audience settings'], 'option_labels': ['Public', 'Team', 'Private'], 'form_actions': ['https://example.test/profile/apply'], 'control_kinds': ['combobox'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'compare-fixtures.py'), str(left), str(right)], text=True)
    data = json.loads(output)
    assert data['delta']['input_accessible_name_changed'] is True
    assert data['delta']['form_name_changed'] is True
    assert data['delta']['option_count_changed'] is True
    assert data['delta']['selected_option_changed'] is True
    assert data['delta']['option_labels_changed'] is True
    assert data['delta']['form_names_changed'] is True



def test_compare_fixtures_reports_control_state_and_constraint_drift(tmp_path: Path) -> None:
    left = tmp_path / 'left-state.json'
    right = tmp_path / 'right-state.json'
    left.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Signup', 'url': 'https://example.test/signup', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'input[type="email"]', 'label_text': 'Email', 'choice_group': 'account', 'autocomplete': 'email', 'input_mode': 'email', 'constraint_hints': ['pattern:.+@example\\.com'], 'constraint_flags': ['typeMismatch'], 'checked_state': 'unchecked', 'disabled': False, 'readonly': False, 'multiple': False, 'selected_count': 0, 'control_kind': 'input:email'}], 'outputs': []}, 'metadata': {'top_submit_label': 'Create', 'top_submit_action': 'https://example.test/signup/create', 'semantic_outline': {'choice_groups': ['account'], 'autocomplete_tokens': ['email'], 'state_flags': ['checked:unchecked'], 'constraint_hints': ['pattern:.+@example\\.com'], 'control_kinds': ['input:email'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    right.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Signup', 'url': 'https://example.test/signup', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'input[type="email"]', 'label_text': 'Email', 'choice_group': 'team', 'autocomplete': 'section-user1 email', 'input_mode': 'text', 'constraint_hints': ['maxlength:80'], 'constraint_flags': ['tooLong'], 'checked_state': 'checked', 'disabled': True, 'readonly': True, 'multiple': True, 'selected_count': 2, 'control_kind': 'input:email'}], 'outputs': []}, 'metadata': {'top_submit_label': 'Create', 'top_submit_action': 'https://example.test/signup/create', 'semantic_outline': {'choice_groups': ['team'], 'autocomplete_tokens': ['section-user1 email'], 'state_flags': ['disabled', 'readonly', 'multiple', 'checked:checked'], 'constraint_hints': ['maxlength:80'], 'control_kinds': ['input:email'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'compare-fixtures.py'), str(left), str(right)], text=True)
    data = json.loads(output)
    assert data['delta']['checked_state_changed'] is True
    assert data['delta']['disabled_changed'] is True
    assert data['delta']['readonly_changed'] is True
    assert data['delta']['multiple_changed'] is True
    assert data['delta']['selected_count_changed'] is True
    assert data['delta']['autocomplete_changed'] is True
    assert data['delta']['input_mode_changed'] is True
    assert data['delta']['choice_group_changed'] is True
    assert data['delta']['constraint_hints_changed'] is True
    assert data['delta']['constraint_flags_changed'] is True
    assert data['delta']['choice_groups_changed'] is True
    assert data['delta']['autocomplete_tokens_changed'] is True
    assert data['delta']['state_flags_changed'] is True
    assert data['delta']['constraint_outline_changed'] is True


def test_plan_fixture_generates_locator_hints_and_actions(tmp_path: Path) -> None:
    fixture = tmp_path / 'planner.json'
    fixture.write_text(json.dumps({
        'message': {'payload': {
            'adapter': 'offscreen-html',
            'title': 'Signup',
            'url': 'https://example.test/signup',
            'prompt': 'person@example.com',
            'latest_output': 'Account created successfully',
            'selection': '',
            'candidates': {
                'inputs': [{
                    'selector_hint': 'input[type="email"][name="email"]',
                    'label_text': 'Email address',
                    'accessible_name': 'Work email',
                    'placeholder': 'name@example.com',
                    'description_text': 'Use your company address',
                    'control_kind': 'input:email',
                    'autocomplete': 'email',
                    'required': True,
                    'invalid': True,
                    'constraint_flags': ['typeMismatch'],
                }],
                'outputs': [{
                    'selector_hint': 'article[data-testid*=assistant]',
                    'label_text': 'Assistant reply',
                }],
            },
            'metadata': {
                'submit_candidates': [{
                    'selector_hint': 'button[type="submit"]',
                    'accessible_name': 'Create account',
                    'text_sample': 'Create account',
                    'control_kind': 'button',
                    'submit_action': 'https://example.test/signup/create',
                }],
            },
        }},
    }), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'plan-fixture.py'), str(fixture)], text=True)
    data = json.loads(output)
    assert data['write_target']['action'] == 'fill'
    assert data['write_target']['preferred_locator'] == 'page.getByRole("textbox", { name: "Work email" })'
    assert data['write_target']['preferred_locator_root'] == 'page'
    assert data['write_target']['preferred_locator_strategy'] == 'role'
    assert data['write_target']['preferred_locator_root_strategy'] == 'page'
    assert data['write_target']['value_kind'] == 'text'
    assert 'page.getByLabel("Email address")' in data['write_target']['locator_hints']
    assert 'page.getByPlaceholder("name@example.com")' in data['write_target']['locator_hints']
    assert data['write_target']['locator_candidates'][0]['strategy'] == 'role'
    assert 'await expect(page.getByRole("textbox", { name: "Work email" })).toBeVisible()' in data['write_target']['assertion_hints']
    assert 'await expect(page.getByRole("textbox", { name: "Work email" })).toHaveValue("person@example.com")' in data['write_target']['assertion_hints']
    assert data['write_target']['observed_value_sample'] == 'person@example.com'
    assert data['submit_target']['action'] == 'click'
    assert data['submit_target']['preferred_locator'] == 'page.getByRole("button", { name: "Create account" })'
    assert data['submit_target']['preferred_locator_root'] == 'page'
    assert data['submit_target']['preferred_locator_strategy'] == 'role'
    assert [step['id'] for step in data['steps']] == ['write', 'submit', 'read']
    assert data['steps'][0]['kind'] == 'write'
    assert data['steps'][0]['locator_strategy'] == 'role'
    assert data['steps'][0]['locator_root_strategy'] == 'page'
    assert data['steps'][0]['value_kind'] == 'text'
    assert data['steps'][1]['depends_on'] == ['write']
    assert data['steps'][2]['depends_on'] == ['submit']
    assert 'await expect(page.getByRole("text", { name: "Assistant reply" })).toContainText("Account created successfully")' not in data['read_target']['assertion_hints']
    assert 'toContainText("Account created successfully")' in ' '.join(data['read_target']['assertion_hints'])
    assert 'await writeTarget.fill(INPUT_TEXT)' in data['playwright_playbook'][0]
    assert 'constraint_flags=typeMismatch' in data.get('warnings', [])


def test_plan_fixture_generates_scoped_frame_locators_and_playbook_roots(tmp_path: Path) -> None:
    fixture = tmp_path / 'planner-frame.json'
    fixture.write_text(json.dumps({
        'message': {'payload': {
            'adapter': 'offscreen-html',
            'title': 'Billing',
            'url': 'https://example.test/settings',
            'prompt': '4242424242424242',
            'latest_output': 'Card saved',
            'selection': '',
            'candidates': {
                'inputs': [{
                    'selector_hint': 'input[name="cardNumber"]',
                    'label_text': 'Card number',
                    'accessible_name': 'Card number',
                    'control_kind': 'input:text',
                    'form_name': 'Billing details',
                    'fieldset_legend': 'Primary card',
                    'frame_selector': '#billing-frame',
                }],
                'outputs': [{
                    'selector_hint': '.status',
                    'label_text': 'Billing status',
                    'frame_selector': '#billing-frame',
                }],
            },
            'metadata': {
                'submit_candidates': [{
                    'selector_hint': 'button[type="submit"]',
                    'accessible_name': 'Save card',
                    'form_name': 'Billing details',
                    'frame_selector': '#billing-frame',
                    'submit_action': 'https://example.test/settings/save-card',
                }],
            },
        }},
    }), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'plan-fixture.py'), str(fixture)], text=True)
    data = json.loads(output)
    expected_root = 'page.frameLocator("#billing-frame").getByRole("form", { name: "Billing details" })'
    assert data['write_target']['preferred_locator_root'] == expected_root
    assert data['write_target']['preferred_locator_root_strategy'] == 'frame_selector+form_name'
    assert data['write_target']['preferred_locator'] == expected_root + '.getByRole("textbox", { name: "Card number" })'
    assert data['submit_target']['preferred_locator_root'] == expected_root
    assert data['submit_target']['preferred_locator_root_strategy'] == 'frame_selector+form_name'
    assert data['steps'][0]['preferred_locator_root'] == expected_root
    assert data['steps'][0]['locator_root_strategy'] == 'frame_selector+form_name'
    assert 'frame_selector=#billing-frame' in data.get('warnings', [])
    assert 'form_name=Billing details' in data.get('warnings', [])
    assert 'const writeRoot = page.frameLocator("#billing-frame").getByRole("form", { name: "Billing details" })' in data['playwright_playbook'][0]
    assert 'const writeTarget = writeRoot.getByRole("textbox", { name: "Card number" })' in data['playwright_playbook'][0]



def test_plan_fixture_generates_nested_frame_locators_and_playbook_roots(tmp_path: Path) -> None:
    fixture = tmp_path / 'planner-nested-frame.json'
    fixture.write_text(json.dumps({
        'message': {'payload': {
            'adapter': 'fixturelab',
            'title': 'Nested billing',
            'url': 'https://example.test/settings/nested',
            'prompt': '5555444433331111',
            'latest_output': 'Nested saved 1111',
            'selection': '',
            'candidates': {
                'inputs': [{
                    'selector_hint': 'input[name="cardNumber"]',
                    'label_text': 'Card number',
                    'accessible_name': 'Card number',
                    'control_kind': 'input:text',
                    'form_name': 'Nested billing details',
                    'fieldset_legend': 'Nested card editor',
                    'frame_selector': '#card-frame',
                    'frame_path': '#settings-frame >> #card-frame',
                    'frame_path_selectors': ['#settings-frame', '#card-frame'],
                }],
                'outputs': [{
                    'selector_hint': '.status',
                    'label_text': 'Billing status',
                    'frame_selector': '#card-frame',
                    'frame_path_selectors': ['#settings-frame', '#card-frame'],
                }],
            },
            'metadata': {
                'submit_candidates': [{
                    'selector_hint': 'button[type="submit"]',
                    'accessible_name': 'Save nested card',
                    'form_name': 'Nested billing details',
                    'frame_selector': '#card-frame',
                    'frame_path_selectors': ['#settings-frame', '#card-frame'],
                    'submit_action': 'https://example.test/settings/save-nested-card',
                }],
            },
        }},
    }), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'plan-fixture.py'), str(fixture)], text=True)
    data = json.loads(output)
    expected_root = 'page.frameLocator("#settings-frame").frameLocator("#card-frame").getByRole("form", { name: "Nested billing details" })'
    assert data['write_target']['preferred_locator_root'] == expected_root
    assert data['write_target']['preferred_locator_root_strategy'] == 'frame_path_selectors+form_name'
    assert data['submit_target']['preferred_locator_root'] == expected_root
    assert data['submit_target']['preferred_locator_root_strategy'] == 'frame_path_selectors+form_name'
    assert data['steps'][0]['locator_root_strategy'] == 'frame_path_selectors+form_name'
    assert 'frame_path_selectors=#settings-frame >> #card-frame' in data.get('warnings', [])
    assert 'const writeRoot = page.frameLocator("#settings-frame").frameLocator("#card-frame").getByRole("form", { name: "Nested billing details" })' in data['playwright_playbook'][0]


def test_compare_fixtures_reports_locator_root_drift(tmp_path: Path) -> None:
    left = tmp_path / 'left-root.json'
    right = tmp_path / 'right-root.json'
    left.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Billing', 'url': 'https://example.test/settings', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'input[name="cardNumber"]', 'label_text': 'Card number', 'accessible_name': 'Card number', 'control_kind': 'input:text', 'form_name': 'Billing details', 'frame_selector': '#billing-frame'}], 'outputs': []}, 'metadata': {'submit_candidates': [{'selector_hint': 'button[type="submit"]', 'accessible_name': 'Save card', 'form_name': 'Billing details', 'frame_selector': '#billing-frame'}]}}}}), encoding='utf-8')
    right.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Billing', 'url': 'https://example.test/settings', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'input[name="cardNumber"]', 'label_text': 'Card number', 'accessible_name': 'Card number', 'control_kind': 'input:text', 'form_name': 'Billing details'}], 'outputs': []}, 'metadata': {'submit_candidates': [{'selector_hint': 'button[type="submit"]', 'accessible_name': 'Save card', 'form_name': 'Billing details'}]}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'compare-fixtures.py'), str(left), str(right)], text=True)
    data = json.loads(output)
    assert data['left']['top_input_locator_root_strategy'] == 'frame_selector+form_name'
    assert data['right']['top_input_locator_root_strategy'] == 'form_name'
    assert data['delta']['input_locator_root_changed'] is True
    assert data['delta']['input_locator_root_strategy_changed'] is True
    assert data['delta']['submit_locator_root_changed'] is True
    assert data['delta']['submit_locator_root_strategy_changed'] is True


def test_cli_plan_fixture_command_runs_with_pythonpath(tmp_path: Path) -> None:
    fixture = tmp_path / 'planner-select.json'
    fixture.write_text(json.dumps({
        'message': {'payload': {
            'adapter': 'offscreen-html',
            'title': 'Preferences',
            'url': 'https://example.test/preferences',
            'prompt': '',
            'latest_output': '',
            'selection': '',
            'candidates': {
                'inputs': [{
                    'selector_hint': 'select#tone',
                    'label_text': 'Tone',
                    'accessible_name': 'Preferred tone',
                    'control_kind': 'combobox',
                    'option_labels': ['Friendly', 'Neutral', 'Formal'],
                    'selected_options': ['Neutral'],
                }],
                'outputs': [],
            },
            'metadata': {
                'submit_candidates': [{
                    'selector_hint': 'button[type="submit"]',
                    'accessible_name': 'Save settings',
                    'submit_action': 'https://example.test/preferences/save',
                }],
            },
        }},
    }), encoding='utf-8')
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT / 'daemon' / 'src') + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    output = subprocess.check_output([sys.executable, '-m', 'glassttyd.cli', 'plan-fixture', str(fixture)], text=True, env=env)
    data = json.loads(output)
    assert data['write_target']['action'] == 'select_option'
    assert data['write_target']['preferred_locator'] == 'page.getByRole("combobox", { name: "Preferred tone" })'
    assert data['write_target']['value_kind'] == 'choice'
    assert data['steps'][0]['value_kind'] == 'choice'
    assert data['submit_target']['preferred_locator'] == 'page.getByRole("button", { name: "Save settings" })'


def test_plan_fixture_generates_dialog_scoped_locators_and_playbook_roots(tmp_path: Path) -> None:
    fixture = tmp_path / 'planner-dialog.json'
    fixture.write_text(json.dumps({
        'message': {'payload': {
            'adapter': 'offscreen-html',
            'title': 'Profile settings',
            'url': 'https://example.test/dialog',
            'prompt': 'Draft inside dialog',
            'latest_output': 'Dialog saved state',
            'selection': '',
            'candidates': {
                'inputs': [{
                    'selector_hint': 'textarea#dialog-prompt',
                    'label_text': 'Message',
                    'accessible_name': 'Message',
                    'control_kind': 'textbox',
                    'dialog_name': 'Profile settings',
                    'form_name': 'Profile settings',
                }],
                'outputs': [{
                    'selector_hint': 'article.status',
                    'label_text': 'Dialog status',
                    'dialog_name': 'Profile settings',
                }],
            },
            'metadata': {
                'submit_candidates': [{
                    'selector_hint': 'button[type="button"]',
                    'accessible_name': 'Save',
                    'dialog_name': 'Profile settings',
                    'form_name': 'Profile settings',
                }],
            },
        }},
    }), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'plan-fixture.py'), str(fixture)], text=True)
    data = json.loads(output)
    expected_root = 'page.getByRole("dialog", { name: "Profile settings" })'
    assert data['write_target']['preferred_locator_root'] == expected_root
    assert data['write_target']['preferred_locator_root_strategy'] == 'dialog_name'
    assert data['write_target']['preferred_locator'] == expected_root + '.getByRole("textbox", { name: "Message" })'
    assert data['submit_target']['preferred_locator_root'] == expected_root
    assert data['submit_target']['preferred_locator_root_strategy'] == 'dialog_name'
    assert data['steps'][0]['locator_root_strategy'] == 'dialog_name'
    assert 'dialog_name=Profile settings' in data.get('warnings', [])
    assert 'const writeRoot = page.getByRole("dialog", { name: "Profile settings" })' in data['playwright_playbook'][0]



def test_plan_fixture_warns_when_read_scope_differs_from_write_scope(tmp_path: Path) -> None:
    fixture = tmp_path / 'iframe-split.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Split scope', 'url': 'https://example.test/split', 'prompt': 'Need billing follow-up', 'latest_output': 'Top-level billing summary is current', 'selection': '', 'candidates': {'inputs': [{'selector_hint': '[data-glasstty-role="prompt"]', 'label_text': 'Draft note', 'accessible_name': 'Draft note', 'control_kind': 'textarea', 'form_name': 'Embedded split composer', 'frame_selector': 'iframe#billing-split-frame', 'frame_name': 'billing-split-frame', 'frame_title': 'Billing draft frame', 'frame_path': 'iframe#billing-split-frame', 'frame_depth': 1, 'frame_path_selectors': ['iframe#billing-split-frame']}], 'outputs': [{'selector_hint': '[data-glasstty-role="latest-output"]', 'text_sample': 'Top-level billing summary is current', 'control_kind': 'article'}]}, 'metadata': {'top_submit_label': 'Queue follow-up', 'top_submit_action': 'https://example.test/split/save', 'top_submit_frame_path': 'iframe#billing-split-frame', 'submit_candidates': [{'selector_hint': '[data-glasstty-role="submit"]', 'accessible_name': 'Queue follow-up', 'form_name': 'Embedded split composer', 'submit_action': 'https://example.test/split/save', 'frame_selector': 'iframe#billing-split-frame', 'frame_path': 'iframe#billing-split-frame', 'frame_path_selectors': ['iframe#billing-split-frame']}], 'split_scope_detected': True}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'plan-fixture.py'), str(fixture)], text=True)
    data = json.loads(output)
    assert str(data['write_target']['preferred_locator_root_strategy']).startswith('frame_path_selectors')
    assert data['read_target']['preferred_locator_root_strategy'] == 'page'
    assert any('read scope differs from write scope' in item for item in data['warnings'])
    assert any('do not reuse the write locator root' in item for item in data['warnings'])



def test_plan_fixture_warns_when_frame_capture_is_partial(tmp_path: Path) -> None:
    fixture = tmp_path / 'iframe-partial.json'
    fixture.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Partial frame capture', 'url': 'https://example.test/partial', 'prompt': 'Accessible draft note', 'latest_output': 'Saved accessible draft', 'selection': '', 'candidates': {'inputs': [{'selector_hint': '[data-glasstty-role="prompt"]', 'label_text': 'Billing note', 'accessible_name': 'Billing note', 'control_kind': 'textarea', 'frame_selector': 'iframe#accessible-frame', 'frame_name': 'accessible-frame', 'frame_title': 'Accessible billing frame', 'frame_path': 'iframe#accessible-frame', 'frame_path_selectors': ['iframe#accessible-frame']}], 'outputs': [{'selector_hint': '[data-glasstty-role="latest-output"]', 'text_sample': 'Saved accessible draft', 'control_kind': 'article', 'frame_selector': 'iframe#accessible-frame', 'frame_name': 'accessible-frame', 'frame_title': 'Accessible billing frame', 'frame_path': 'iframe#accessible-frame', 'frame_path_selectors': ['iframe#accessible-frame']}]}, 'metadata': {'accessible_iframe_count': 1, 'blocked_iframe_count': 1, 'blocked_iframe_names': ['partner-frame'], 'blocked_iframe_titles': ['Partner billing widget'], 'blocked_frame_paths': ['iframe#partner-frame'], 'total_iframe_count': 2, 'frame_capture_ratio': 0.5, 'frame_capture_status': 'partial', 'frame_capture_warning': 'frame capture is partial: 1/2 iframes were accessible and 1 were blocked'}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'plan-fixture.py'), str(fixture)], text=True)
    data = json.loads(output)
    assert any('frame capture is partial' in item for item in data['warnings'])
    assert any('Partner billing widget' in item for item in data['warnings'])
    assert any('iframe#partner-frame' in item for item in data['warnings'])


def test_compare_fixtures_reports_dialog_scope_drift(tmp_path: Path) -> None:
    left = tmp_path / 'left-dialog.json'
    right = tmp_path / 'right-dialog.json'
    left.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Profile settings', 'url': 'https://example.test/dialog', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea#dialog-prompt', 'label_text': 'Message', 'accessible_name': 'Message', 'control_kind': 'textbox', 'dialog_name': 'Profile settings'}], 'outputs': []}, 'metadata': {'semantic_outline': {'dialog_names': ['Profile settings']}, 'submit_candidates': [{'selector_hint': 'button', 'accessible_name': 'Save', 'dialog_name': 'Profile settings'}]}}}}), encoding='utf-8')
    right.write_text(json.dumps({'message': {'payload': {'adapter': 'offscreen-html', 'title': 'Profile settings', 'url': 'https://example.test/dialog', 'prompt': '', 'latest_output': '', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea#dialog-prompt', 'label_text': 'Message', 'accessible_name': 'Message', 'control_kind': 'textbox'}], 'outputs': []}, 'metadata': {'semantic_outline': {'dialog_names': []}, 'submit_candidates': [{'selector_hint': 'button', 'accessible_name': 'Save'}]}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'compare-fixtures.py'), str(left), str(right)], text=True)
    data = json.loads(output)
    assert data['left']['top_dialog_name'] == 'Profile settings'
    assert data['right']['top_dialog_name'] is None
    assert data['delta']['dialog_name_changed'] is True
    assert data['delta']['dialog_names_changed'] is True



def test_compare_fixtures_reports_frame_capture_coverage_drift(tmp_path: Path) -> None:
    left = tmp_path / 'left-partial.json'
    right = tmp_path / 'right-full.json'
    left.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Partial frame capture', 'url': 'https://example.test/partial', 'prompt': 'Accessible draft note', 'latest_output': 'Saved accessible draft', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea', 'label_text': 'Billing note', 'accessible_name': 'Billing note', 'frame_path': 'iframe#accessible-frame', 'frame_path_selectors': ['iframe#accessible-frame'], 'control_kind': 'textarea'}], 'outputs': []}, 'metadata': {'accessible_iframe_count': 1, 'blocked_iframe_count': 1, 'blocked_iframe_names': ['partner-frame'], 'blocked_iframe_titles': ['Partner billing widget'], 'blocked_frame_paths': ['iframe#partner-frame'], 'traversed_document_count': 2, 'total_iframe_count': 2, 'frame_capture_ratio': 0.5, 'frame_capture_status': 'partial', 'frame_capture_warning': 'frame capture is partial: 1/2 iframes were accessible and 1 were blocked', 'semantic_outline': {'iframe_names': ['accessible-frame', 'partner-frame'], 'iframe_titles': ['Accessible billing frame', 'Partner billing widget'], 'frame_paths': ['iframe#accessible-frame'], 'control_kinds': ['textarea'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    right.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Full frame capture', 'url': 'https://example.test/partial', 'prompt': 'Accessible draft note', 'latest_output': 'Saved accessible draft', 'selection': '', 'candidates': {'inputs': [{'selector_hint': 'textarea', 'label_text': 'Billing note', 'accessible_name': 'Billing note', 'frame_path': 'iframe#accessible-frame', 'frame_path_selectors': ['iframe#accessible-frame'], 'control_kind': 'textarea'}], 'outputs': []}, 'metadata': {'accessible_iframe_count': 2, 'blocked_iframe_count': 0, 'blocked_iframe_names': [], 'blocked_iframe_titles': [], 'blocked_frame_paths': [], 'traversed_document_count': 3, 'total_iframe_count': 2, 'frame_capture_ratio': 1.0, 'frame_capture_status': 'full', 'semantic_outline': {'iframe_names': ['accessible-frame', 'partner-frame'], 'iframe_titles': ['Accessible billing frame', 'Partner billing widget'], 'frame_paths': ['iframe#accessible-frame', 'iframe#partner-frame'], 'control_kinds': ['textarea'], 'link_hosts': ['example.test']}}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'compare-fixtures.py'), str(left), str(right)], text=True)
    data = json.loads(output)
    assert data['left']['frame_capture_status'] == 'partial'
    assert data['right']['frame_capture_status'] == 'full'
    assert data['delta']['blocked_iframe_titles_changed'] is True
    assert data['delta']['frame_capture_ratio_changed'] is True
    assert data['delta']['frame_capture_status_changed'] is True
    assert data['delta']['frame_capture_warning_changed'] is True


def test_compare_fixtures_reports_output_scope_drift(tmp_path: Path) -> None:
    left = tmp_path / 'left-output-scope.json'
    right = tmp_path / 'right-output-scope.json'
    left.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Split scope', 'url': 'https://example.test/split', 'prompt': 'Need billing follow-up', 'latest_output': 'Top-level billing summary is current', 'selection': '', 'candidates': {'inputs': [{'selector_hint': '[data-glasstty-role="prompt"]', 'label_text': 'Draft note', 'accessible_name': 'Draft note', 'control_kind': 'textarea', 'frame_selector': 'iframe#billing-split-frame', 'frame_path': 'iframe#billing-split-frame', 'frame_path_selectors': ['iframe#billing-split-frame']}], 'outputs': [{'selector_hint': '[data-glasstty-role="latest-output"]', 'text_sample': 'Top-level billing summary is current', 'control_kind': 'article'}]}, 'metadata': {'split_scope_detected': True}}}}), encoding='utf-8')
    right.write_text(json.dumps({'message': {'payload': {'adapter': 'fixturelab', 'title': 'Frame-local scope', 'url': 'https://example.test/split', 'prompt': 'Need billing follow-up', 'latest_output': 'Frame status current', 'selection': '', 'candidates': {'inputs': [{'selector_hint': '[data-glasstty-role="prompt"]', 'label_text': 'Draft note', 'accessible_name': 'Draft note', 'control_kind': 'textarea', 'frame_selector': 'iframe#billing-split-frame', 'frame_path': 'iframe#billing-split-frame', 'frame_path_selectors': ['iframe#billing-split-frame']}], 'outputs': [{'selector_hint': '[data-glasstty-role="latest-output"]', 'text_sample': 'Frame status current', 'control_kind': 'article', 'frame_selector': 'iframe#billing-split-frame', 'frame_path': 'iframe#billing-split-frame', 'frame_path_selectors': ['iframe#billing-split-frame']}]}, 'metadata': {'top_output_frame_path': 'iframe#billing-split-frame', 'top_output_frame_depth': 1, 'split_scope_detected': False}}}}), encoding='utf-8')
    output = subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'compare-fixtures.py'), str(left), str(right)], text=True)
    data = json.loads(output)
    assert data['left']['top_output_locator_root_strategy'] == 'page'
    assert str(data['right']['top_output_locator_root_strategy']).startswith('frame_path_selectors')
    assert data['delta']['output_locator_root_strategy_changed'] is True
    assert data['delta']['output_frame_path_changed'] is True
    assert data['delta']['split_scope_changed'] is True


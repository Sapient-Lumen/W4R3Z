from __future__ import annotations

import json
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


def load_fixture(path: Path) -> JsonDict:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'fixture at {path} is not a JSON object')
    message = data.get('message')
    if isinstance(message, dict):
        payload = message.get('payload')
        if isinstance(payload, dict):
            return payload
    if isinstance(data.get('adapter'), str):
        return data
    raise ValueError(f'fixture at {path} does not look like a GlassTTY fixture payload')


def metadata(payload: JsonDict) -> JsonDict:
    meta = payload.get('metadata')
    return meta if isinstance(meta, dict) else {}


def candidates(payload: JsonDict, bucket: str) -> list[JsonDict]:
    root = payload.get('candidates')
    if not isinstance(root, dict):
        return []
    items = root.get(bucket)
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def submit_candidates(payload: JsonDict) -> list[JsonDict]:
    meta = metadata(payload)
    items = meta.get('submit_candidates')
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _compact_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _normalized_text_sample(value: str | None, *, limit: int = 120) -> str | None:
    if not isinstance(value, str):
        return None
    compact = ' '.join(value.split())
    if not compact:
        return None
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 1)].rstrip() + '…'


def candidate_name(candidate: JsonDict) -> str | None:
    for key in ('accessible_name', 'label_text', 'text_sample', 'placeholder', 'name', 'selector_hint'):
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    selected = _compact_list(candidate.get('selected_options'))
    if selected:
        return selected[0]
    return None


def candidate_role(candidate: JsonDict, *, purpose: str) -> str | None:
    explicit_role = candidate.get('role')
    if isinstance(explicit_role, str) and explicit_role.strip():
        return explicit_role.strip()
    control_kind = str(candidate.get('control_kind') or '').strip().lower()
    selector_hint = str(candidate.get('selector_hint') or '').lower()
    if purpose == 'submit':
        return 'button'
    mapping = {
        'searchbox': 'searchbox',
        'textbox': 'textbox',
        'combobox': 'combobox',
        'listbox': 'listbox',
        'checkbox': 'checkbox',
        'radio': 'radio',
        'switch': 'switch',
        'contenteditable': 'textbox',
        'input:text': 'textbox',
        'input:email': 'textbox',
        'input:url': 'textbox',
        'input:tel': 'textbox',
        'input:password': 'textbox',
        'input:search': 'searchbox',
        'input:number': 'spinbutton',
        'input:range': 'slider',
        'input:checkbox': 'checkbox',
        'input:radio': 'radio',
    }
    if control_kind in mapping:
        return mapping[control_kind]
    if selector_hint.startswith('select'):
        return 'combobox'
    if selector_hint.startswith('textarea'):
        return 'textbox'
    if selector_hint.startswith('button') or '[type="submit"]' in selector_hint:
        return 'button'
    return None


def candidate_action(candidate: JsonDict, *, purpose: str) -> str:
    role = candidate_role(candidate, purpose=purpose)
    control_kind = str(candidate.get('control_kind') or '').strip().lower()
    selector_hint = str(candidate.get('selector_hint') or '').lower()
    if purpose == 'read':
        return 'extract_text'
    if purpose == 'submit' or role == 'button' or selector_hint.startswith('button'):
        return 'click'
    if role in {'checkbox', 'radio', 'switch'}:
        return 'set_checked'
    if role in {'combobox', 'listbox'}:
        return 'select_option'
    if control_kind == 'input:file':
        return 'set_input_files'
    return 'fill'


def candidate_context_candidates(candidate: JsonDict, *, purpose: str) -> list[JsonDict]:
    items: list[JsonDict] = []
    seen: set[str] = set()

    def add(kind: str, strategy: str, code: str | None, rationale: str, *, semantic: bool, priority: int) -> None:
        if not code or code in seen:
            return
        seen.add(code)
        items.append({
            'kind': kind,
            'strategy': strategy,
            'code': code,
            'priority': priority,
            'semantic': semantic,
            'rationale': rationale,
        })

    frame_candidates: list[JsonDict] = []
    frame_selector = str(candidate.get('frame_selector') or '').strip()
    frame_name = str(candidate.get('frame_name') or '').strip()
    frame_title = str(candidate.get('frame_title') or '').strip()
    frame_path_selectors = [item.strip() for item in _compact_list(candidate.get('frame_path_selectors')) if item.strip()]
    if frame_path_selectors:
        chain = 'page'
        for selector in frame_path_selectors:
            chain += f'.frameLocator({_q(selector)})'
        frame_candidates.append({
            'kind': 'frame',
            'strategy': 'frame_path_selectors',
            'code': chain,
            'priority': 6,
            'semantic': False,
            'rationale': 'saved nested iframe selector chain from fixture evidence',
        })
    if frame_selector:
        frame_candidates.append({
            'kind': 'frame',
            'strategy': 'frame_selector',
            'code': f'page.frameLocator({_q(frame_selector)})',
            'priority': 10,
            'semantic': False,
            'rationale': 'saved iframe selector from fixture evidence',
        })
    if frame_name:
        frame_css = f'iframe[name={json.dumps(frame_name)}]'
        frame_candidates.append({
            'kind': 'frame',
            'strategy': 'frame_name',
            'code': f'page.frameLocator({_q(frame_css)})',
            'priority': 12,
            'semantic': True,
            'rationale': 'iframe name captured in the saved fixture',
        })
    if frame_title:
        frame_css = f'iframe[title={json.dumps(frame_title)}]'
        frame_candidates.append({
            'kind': 'frame',
            'strategy': 'frame_title',
            'code': f'page.frameLocator({_q(frame_css)})',
            'priority': 14,
            'semantic': True,
            'rationale': 'iframe title captured in the saved fixture',
        })

    scope_specs: list[JsonDict] = []
    form_name = str(candidate.get('form_name') or '').strip()
    fieldset_legend = str(candidate.get('fieldset_legend') or '').strip()
    dialog_name = str(candidate.get('dialog_name') or '').strip()
    if dialog_name:
        scope_specs.append({
            'kind': 'dialog',
            'strategy': 'dialog_name',
            'relative_code': f'.getByRole({_q("dialog")}, {{ name: {_q(dialog_name)} }})',
            'priority': 20,
            'semantic': True,
            'rationale': 'named dialog scope captured in the saved fixture',
        })
    if form_name:
        scope_specs.append({
            'kind': 'form',
            'strategy': 'form_name',
            'relative_code': f'.getByRole({_q("form")}, {{ name: {_q(form_name)} }})',
            'priority': 24,
            'semantic': True,
            'rationale': 'named form scope captured in the saved fixture',
        })
    if fieldset_legend:
        scope_specs.append({
            'kind': 'group',
            'strategy': 'fieldset_legend',
            'relative_code': f'.getByRole({_q("group")}, {{ name: {_q(fieldset_legend)} }})',
            'priority': 28,
            'semantic': True,
            'rationale': 'fieldset legend scope captured in the saved fixture',
        })

    if frame_candidates:
        if scope_specs:
            for frame in frame_candidates:
                for scope in scope_specs:
                    add(
                        f'{frame["kind"]}_{scope["kind"]}',
                        f'{frame["strategy"]}+{scope["strategy"]}',
                        f'{frame["code"]}{scope["relative_code"]}',
                        f'{frame["rationale"]}; {scope["rationale"]}',
                        semantic=bool(frame.get('semantic')) and bool(scope.get('semantic')),
                        priority=int(frame['priority']) + int(scope['priority']),
                    )
        for frame in frame_candidates:
            add(
                str(frame['kind']),
                str(frame['strategy']),
                str(frame['code']),
                str(frame['rationale']),
                semantic=bool(frame['semantic']),
                priority=int(frame['priority']) + 40,
            )
        return items

    if scope_specs:
        for scope in scope_specs:
            add(
                str(scope['kind']),
                str(scope['strategy']),
                f'page{scope["relative_code"]}',
                str(scope['rationale']),
                semantic=bool(scope['semantic']),
                priority=int(scope['priority']),
            )

    add('page', 'page', 'page', 'page-wide fallback when no narrower scope is available', semantic=True, priority=90)
    return items


def candidate_locator_candidates(candidate: JsonDict, *, purpose: str) -> list[JsonDict]:
    items: list[JsonDict] = []
    seen: set[str] = set()

    def add(strategy: str, root: JsonDict, relative_code: str | None, rationale: str, *, semantic: bool, priority: int) -> None:
        root_code = root.get('code')
        if not isinstance(root_code, str) or not root_code:
            return
        if not relative_code:
            return
        code = f'{root_code}{relative_code}' if relative_code.startswith('.') else relative_code
        if not code or code in seen:
            return
        seen.add(code)
        items.append({
            'strategy': strategy,
            'code': code,
            'relative_code': relative_code,
            'root_code': root_code,
            'root_kind': root.get('kind'),
            'root_strategy': root.get('strategy'),
            'priority': priority,
            'semantic': semantic,
            'rationale': rationale,
        })

    role = candidate_role(candidate, purpose=purpose)
    name = candidate_name(candidate)
    label = candidate.get('label_text')
    placeholder = candidate.get('placeholder')
    selector_hint = candidate.get('selector_hint')
    field_name = candidate.get('name')
    text_sample = candidate.get('text_sample')
    roots = candidate_context_candidates(candidate, purpose=purpose)

    for root in roots:
        base_priority = int(root.get('priority') or 0)
        root_rationale = str(root.get('rationale') or '').strip()
        if isinstance(role, str) and isinstance(name, str):
            add(
                'role',
                root,
                f'.getByRole({_q(role)}, {{ name: {_q(name)} }})',
                'preferred user-facing role plus accessible name' + (f'; {root_rationale}' if root_rationale else ''),
                semantic=True,
                priority=base_priority + 1,
            )
        if purpose == 'input' and isinstance(label, str) and label.strip():
            add(
                'label',
                root,
                f'.getByLabel({_q(label.strip())})',
                'associated form label' + (f'; {root_rationale}' if root_rationale else ''),
                semantic=True,
                priority=base_priority + 2,
            )
        if purpose == 'input' and isinstance(placeholder, str) and placeholder.strip():
            add(
                'placeholder',
                root,
                f'.getByPlaceholder({_q(placeholder.strip())})',
                'placeholder fallback when label semantics are weak' + (f'; {root_rationale}' if root_rationale else ''),
                semantic=True,
                priority=base_priority + 3,
            )
        if isinstance(text_sample, str) and text_sample.strip():
            add(
                'text',
                root,
                f'.getByText({_q(text_sample.strip())})',
                'visible text fallback for buttons or output-like regions' + (f'; {root_rationale}' if root_rationale else ''),
                semantic=True,
                priority=base_priority + (4 if purpose == 'submit' else 5),
            )
        if isinstance(field_name, str) and field_name.strip():
            add(
                'name_attribute',
                root,
                f'.locator(`[name={json.dumps(field_name.strip())}]`)',
                'explicit form contract when semantic locators are insufficient' + (f'; {root_rationale}' if root_rationale else ''),
                semantic=False,
                priority=base_priority + 6,
            )
        if isinstance(selector_hint, str) and selector_hint.strip():
            add(
                'css',
                root,
                f'.locator({_q(selector_hint.strip())})',
                'last-resort structural fallback from saved fixture evidence' + (f'; {root_rationale}' if root_rationale else ''),
                semantic=False,
                priority=base_priority + 7,
            )
    items.sort(key=lambda item: (int(item.get('priority') or 0), str(item.get('strategy') or ''), str(item.get('code') or '')))
    return items


def candidate_locator_hints(candidate: JsonDict, *, purpose: str) -> list[str]:
    return [item['code'] for item in candidate_locator_candidates(candidate, purpose=purpose)]


def candidate_locator_strategy(candidate: JsonDict, *, purpose: str) -> str | None:
    items = candidate_locator_candidates(candidate, purpose=purpose)
    if not items:
        return None
    strategy = items[0].get('strategy')
    return strategy if isinstance(strategy, str) else None


def candidate_locator_root(candidate: JsonDict, *, purpose: str) -> str | None:
    items = candidate_locator_candidates(candidate, purpose=purpose)
    if not items:
        return None
    root_code = items[0].get('root_code')
    return root_code if isinstance(root_code, str) else None


def candidate_locator_root_strategy(candidate: JsonDict, *, purpose: str) -> str | None:
    items = candidate_locator_candidates(candidate, purpose=purpose)
    if not items:
        return None
    strategy = items[0].get('root_strategy')
    return strategy if isinstance(strategy, str) else None


def candidate_value_kind(candidate: JsonDict, *, purpose: str) -> str | None:
    if purpose in {'read', 'submit'}:
        return None
    action = candidate_action(candidate, purpose=purpose)
    role = candidate_role(candidate, purpose=purpose)
    control_kind = str(candidate.get('control_kind') or '').strip().lower()
    if action == 'set_checked' or role in {'checkbox', 'radio', 'switch'}:
        return 'boolean'
    if action == 'select_option' or role in {'combobox', 'listbox'}:
        return 'choice'
    if action == 'set_input_files' or control_kind == 'input:file':
        return 'files'
    if control_kind == 'input:number':
        return 'number'
    return 'text'


def candidate_assertion_hints(candidate: JsonDict, *, purpose: str, observed_value: str | None = None) -> list[str]:
    locator = (candidate_locator_hints(candidate, purpose=purpose) or ['locator'])[0]
    hints: list[str] = [f'await expect({locator}).toBeVisible()']
    action = candidate_action(candidate, purpose=purpose)
    role = candidate_role(candidate, purpose=purpose)
    observed_sample = _normalized_text_sample(observed_value)

    if purpose == 'submit':
        if candidate.get('disabled') is True:
            hints.append(f'await expect({locator}).toBeDisabled()')
        else:
            hints.append(f'await expect({locator}).toBeEnabled()')
        return hints

    if purpose == 'read':
        if observed_sample:
            hints.append(f'await expect({locator}).toContainText({_q(observed_sample)})')
        return hints

    if candidate.get('disabled') is True:
        hints.append(f'await expect({locator}).toBeDisabled()')
        return hints

    if action == 'set_checked' or role in {'checkbox', 'radio', 'switch'}:
        checked_state = candidate.get('checked_state')
        if checked_state == 'checked':
            hints.append(f'await expect({locator}).toBeChecked()')
        elif checked_state == 'unchecked':
            hints.append(f'await expect({locator}).not.toBeChecked()')
        return hints

    if candidate.get('readonly') is not True and action in {'fill', 'select_option'}:
        hints.append(f'await expect({locator}).toBeEditable()')

    if action == 'fill' and observed_sample:
        control_kind = str(candidate.get('control_kind') or '').strip().lower()
        selector_hint = str(candidate.get('selector_hint') or '').strip().lower()
        if control_kind.startswith('input:') or control_kind == 'textarea' or selector_hint.startswith('input') or selector_hint.startswith('textarea'):
            hints.append(f'await expect({locator}).toHaveValue({_q(observed_sample)})')
        else:
            hints.append(f'await expect({locator}).toContainText({_q(observed_sample)})')

    if candidate.get('required') is True:
        hints.append('// field looked required in the saved DOM; expect validation or completion before submit')
    if candidate.get('invalid') is True:
        hints.append('// saved DOM reported this control as invalid; confirm validation clears before submit')

    selected_options = _compact_list(candidate.get('selected_options'))
    if action == 'select_option' and selected_options:
        hints.append(f'// after selecting, verify the chosen option label(s): {", ".join(selected_options[:3])}')

    constraint_flags = _compact_list(candidate.get('constraint_flags'))
    if constraint_flags:
        hints.append(f'// saved DOM reported constraint flags: {", ".join(constraint_flags[:4])}')
    return hints


def candidate_notes(candidate: JsonDict, *, purpose: str) -> list[str]:
    notes: list[str] = []
    frame_selector = str(candidate.get('frame_selector') or '').strip()
    frame_name = str(candidate.get('frame_name') or '').strip()
    frame_title = str(candidate.get('frame_title') or '').strip()
    frame_path_selectors = [item.strip() for item in _compact_list(candidate.get('frame_path_selectors')) if item.strip()]
    frame_path = str(candidate.get('frame_path') or '').strip()
    form_name = str(candidate.get('form_name') or '').strip()
    fieldset_legend = str(candidate.get('fieldset_legend') or '').strip()
    dialog_name = str(candidate.get('dialog_name') or '').strip()
    if frame_path_selectors:
        notes.append(f'frame_path_selectors={" >> ".join(frame_path_selectors)}')
    elif frame_path:
        notes.append(f'frame_path={frame_path}')
    elif frame_selector:
        notes.append(f'frame_selector={frame_selector}')
    elif frame_name:
        notes.append(f'frame_name={frame_name}')
    elif frame_title:
        notes.append(f'frame_title={frame_title}')
    if dialog_name:
        notes.append(f'dialog_name={dialog_name}')
    if form_name:
        notes.append(f'form_name={form_name}')
    if fieldset_legend:
        notes.append(f'fieldset_legend={fieldset_legend}')
    if candidate.get('disabled') is True:
        notes.append('control is disabled in the saved DOM')
    if candidate.get('readonly') is True:
        notes.append('control is readonly in the saved DOM')
    if candidate.get('invalid') is True:
        notes.append('control is currently invalid under native or ARIA validation')
    if candidate.get('required') is True:
        notes.append('control is marked required')
    if candidate.get('multiple') is True:
        notes.append('control accepts multiple values or selections')
    checked_state = candidate.get('checked_state')
    if isinstance(checked_state, str) and checked_state:
        notes.append(f'checked_state={checked_state}')
    selected_options = _compact_list(candidate.get('selected_options'))
    if selected_options:
        notes.append(f'selected_options={", ".join(selected_options[:3])}')
    constraint_flags = _compact_list(candidate.get('constraint_flags'))
    if constraint_flags:
        notes.append(f'constraint_flags={", ".join(constraint_flags[:4])}')
    constraint_hints = _compact_list(candidate.get('constraint_hints'))
    if constraint_hints:
        notes.append(f'constraint_hints={", ".join(constraint_hints[:4])}')
    choice_group = candidate.get('choice_group')
    if isinstance(choice_group, str) and choice_group.strip():
        notes.append(f'choice_group={choice_group.strip()}')
    if purpose == 'submit':
        submit_action = candidate.get('submit_action') or candidate.get('form_action')
        if isinstance(submit_action, str) and submit_action.strip():
            notes.append(f'submit_action={submit_action.strip()}')
    return notes


def candidate_protocol_step(
    candidate: JsonDict,
    *,
    purpose: str,
    target_key: str,
    step_id: str,
    depends_on: list[str] | None = None,
    observed_value: str | None = None,
) -> JsonDict:
    locator_candidates = candidate_locator_candidates(candidate, purpose=purpose)
    context_candidates = candidate_context_candidates(candidate, purpose=purpose)
    step: JsonDict = {
        'id': step_id,
        'target_key': target_key,
        'kind': {'input': 'write', 'read': 'read', 'submit': 'submit'}[purpose],
        'action': candidate_action(candidate, purpose=purpose),
        'preferred_locator': (locator_candidates[0]['code'] if locator_candidates else None),
        'preferred_locator_root': (locator_candidates[0]['root_code'] if locator_candidates else (context_candidates[0]['code'] if context_candidates else None)),
        'preferred_locator_relative': (locator_candidates[0]['relative_code'] if locator_candidates else None),
        'locator_strategy': (locator_candidates[0]['strategy'] if locator_candidates else None),
        'locator_root_strategy': (locator_candidates[0]['root_strategy'] if locator_candidates else (context_candidates[0]['strategy'] if context_candidates else None)),
        'locator_root_candidates': context_candidates,
        'locator_candidates': locator_candidates,
        'assertion_hints': candidate_assertion_hints(candidate, purpose=purpose, observed_value=observed_value),
    }
    if depends_on:
        step['depends_on'] = depends_on
    value_kind = candidate_value_kind(candidate, purpose=purpose)
    if isinstance(value_kind, str):
        step['value_kind'] = value_kind
    if observed_value is not None:
        step['observed_value_length'] = len(observed_value)
        step['observed_value_sample'] = _normalized_text_sample(observed_value, limit=160)
    if purpose == 'input':
        step['value_source'] = 'user_input'
    elif purpose == 'read':
        step['value_destination'] = 'captured_output'
    return step


def candidate_summary(candidate: JsonDict, *, purpose: str, observed_value: str | None = None) -> JsonDict:
    locator_candidates = candidate_locator_candidates(candidate, purpose=purpose)
    context_candidates = candidate_context_candidates(candidate, purpose=purpose)
    summary: JsonDict = {
        'selector_hint': candidate.get('selector_hint'),
        'action': candidate_action(candidate, purpose=purpose),
        'locator_hints': [item['code'] for item in locator_candidates],
        'locator_root_candidates': context_candidates,
        'locator_candidates': locator_candidates,
        'preferred_locator': (locator_candidates or [{'code': None}])[0]['code'],
        'preferred_locator_root': (locator_candidates or [{'root_code': None}])[0]['root_code'],
        'preferred_locator_relative': (locator_candidates or [{'relative_code': None}])[0]['relative_code'],
        'preferred_locator_strategy': (locator_candidates or [{'strategy': None}])[0]['strategy'],
        'preferred_locator_root_strategy': (locator_candidates or [{'root_strategy': None}])[0]['root_strategy'],
        'control_kind': candidate.get('control_kind'),
        'accessible_name': candidate.get('accessible_name'),
        'label_text': candidate.get('label_text'),
        'description_text': candidate.get('description_text'),
        'placeholder': candidate.get('placeholder'),
        'form_name': candidate.get('form_name'),
        'fieldset_legend': candidate.get('fieldset_legend'),
        'dialog_name': candidate.get('dialog_name'),
        'frame_selector': candidate.get('frame_selector'),
        'frame_name': candidate.get('frame_name'),
        'frame_title': candidate.get('frame_title'),
        'choice_group': candidate.get('choice_group'),
        'option_labels': _compact_list(candidate.get('option_labels')),
        'selected_options': _compact_list(candidate.get('selected_options')),
        'value_kind': candidate_value_kind(candidate, purpose=purpose),
        'assertion_hints': candidate_assertion_hints(candidate, purpose=purpose, observed_value=observed_value),
        'notes': candidate_notes(candidate, purpose=purpose),
    }
    if observed_value is not None:
        summary['observed_value_length'] = len(observed_value)
        summary['observed_value_sample'] = _normalized_text_sample(observed_value, limit=160)
    for key in ('submit_action', 'submit_method', 'submit_target', 'autocomplete', 'input_mode', 'checked_state'):
        value = candidate.get(key)
        if isinstance(value, str) and value:
            summary[key] = value
    for key in ('disabled', 'readonly', 'required', 'invalid', 'multiple'):
        value = candidate.get(key)
        if isinstance(value, bool):
            summary[key] = value
    for key in ('option_count', 'selected_count'):
        value = candidate.get(key)
        if isinstance(value, int):
            summary[key] = value
    return summary


def interaction_plan(payload: JsonDict, *, path: str | None = None) -> JsonDict:
    meta = metadata(payload)
    inputs = candidates(payload, 'inputs')
    outputs = candidates(payload, 'outputs')
    submits = submit_candidates(payload)
    prompt_value = payload.get('prompt') if isinstance(payload.get('prompt'), str) else None
    latest_output = payload.get('latest_output') if isinstance(payload.get('latest_output'), str) else None

    plan: JsonDict = {
        'adapter': payload.get('adapter'),
        'title': payload.get('title'),
        'url': payload.get('url'),
    }
    if path:
        plan['path'] = path
    if inputs:
        plan['write_target'] = candidate_summary(inputs[0], purpose='input', observed_value=prompt_value)
    if outputs:
        plan['read_target'] = candidate_summary(outputs[0], purpose='read', observed_value=latest_output)
    if submits:
        plan['submit_target'] = candidate_summary(submits[0], purpose='submit')

    steps: list[JsonDict] = []
    if inputs:
        steps.append(candidate_protocol_step(inputs[0], purpose='input', target_key='write_target', step_id='write', observed_value=prompt_value))
    if submits:
        depends = ['write'] if inputs else None
        steps.append(candidate_protocol_step(submits[0], purpose='submit', target_key='submit_target', step_id='submit', depends_on=depends))
    if outputs:
        depends: list[str] | None = None
        if submits:
            depends = ['submit']
        elif inputs:
            depends = ['write']
        steps.append(candidate_protocol_step(outputs[0], purpose='read', target_key='read_target', step_id='read', depends_on=depends, observed_value=latest_output))

    if steps:
        plan['steps'] = steps
        plan['playwright_playbook'] = []
        for step in steps:
            locator = step.get('preferred_locator') or 'locator'
            var_name = f"{step['id']}Target"
            locator_root = step.get('preferred_locator_root')
            locator_relative = step.get('preferred_locator_relative')
            snippet_lines = [f"// {step['kind']} via {step.get('locator_strategy') or 'locator'}"]
            if isinstance(locator_root, str) and locator_root and locator_root != 'page' and isinstance(locator_relative, str) and locator_relative:
                root_var_name = f"{step['id']}Root"
                snippet_lines.append(f'const {root_var_name} = {locator_root}')
                snippet_lines.append(f'const {var_name} = {root_var_name}{locator_relative}')
            else:
                snippet_lines.append(f'const {var_name} = {locator}')
            for hint in step.get('assertion_hints', []):
                if isinstance(hint, str):
                    snippet_lines.append(hint.replace(locator, var_name))
            action = step.get('action')
            if action == 'fill':
                snippet_lines.append(f'await {var_name}.fill(INPUT_TEXT)')
            elif action == 'select_option':
                snippet_lines.append(f'await {var_name}.selectOption(OPTION_VALUE)')
            elif action == 'set_checked':
                snippet_lines.append(f'await {var_name}.check()')
            elif action == 'set_input_files':
                snippet_lines.append(f'await {var_name}.setInputFiles(FILE_PATHS)')
            elif action == 'click':
                snippet_lines.append(f'await {var_name}.click()')
            elif action == 'extract_text':
                snippet_lines.append(f'const {step["id"]}Text = await {var_name}.innerText()')
            plan['playwright_playbook'].append('\n'.join(snippet_lines))

    warnings: list[str] = []
    for key in ('write_target', 'submit_target', 'read_target'):
        target = plan.get(key)
        if isinstance(target, dict):
            warnings.extend(note for note in target.get('notes', []) if isinstance(note, str))

    frame_capture_status = str(meta.get('frame_capture_status') or '').strip()
    frame_capture_warning = str(meta.get('frame_capture_warning') or '').strip()
    blocked_iframe_titles = [item for item in _compact_list(meta.get('blocked_iframe_titles')) if item]
    blocked_frame_paths = [item for item in _compact_list(meta.get('blocked_frame_paths')) if item]
    blocked_iframe_names = [item for item in _compact_list(meta.get('blocked_iframe_names')) if item]
    if frame_capture_status in {'partial', 'blocked_only'}:
        if frame_capture_warning:
            warnings.append(frame_capture_warning)
        else:
            accessible_count = meta.get('accessible_iframe_count')
            total_iframe_count = meta.get('total_iframe_count')
            blocked_count = meta.get('blocked_iframe_count')
            warnings.append(
                f'frame capture is incomplete: accessible={accessible_count}, total={total_iframe_count}, blocked={blocked_count}'
            )
        labels: list[str] = []
        if blocked_iframe_titles:
            labels.append('blocked iframe titles=' + ', '.join(str(item) for item in blocked_iframe_titles))
        if blocked_iframe_names:
            labels.append('blocked iframe names=' + ', '.join(str(item) for item in blocked_iframe_names))
        if blocked_frame_paths:
            labels.append('blocked frame paths=' + ', '.join(str(item) for item in blocked_frame_paths))
        warnings.extend(labels)

    write_target = plan.get('write_target')
    read_target = plan.get('read_target')
    if isinstance(write_target, dict) and isinstance(read_target, dict):
        write_root = write_target.get('preferred_locator_root') or 'page'
        read_root = read_target.get('preferred_locator_root') or 'page'
        if isinstance(write_root, str) and isinstance(read_root, str) and write_root != read_root:
            warnings.append(f'read scope differs from write scope: write uses {write_root}, read uses {read_root}')
        write_frame = write_target.get('frame_selector') or write_target.get('frame_name') or write_target.get('frame_title')
        read_frame = read_target.get('frame_selector') or read_target.get('frame_name') or read_target.get('frame_title')
        if write_frame and not read_frame:
            warnings.append('input appears inside a frame but output reads from the page; do not reuse the write locator root for read assertions')
        elif read_frame and not write_frame:
            warnings.append('output appears inside a frame while input writes from the page; use a dedicated read locator root')
    if warnings:
        deduped: list[str] = []
        seen: set[str] = set()
        for warning in warnings:
            if warning in seen:
                continue
            seen.add(warning)
            deduped.append(warning)
        plan['warnings'] = deduped
    return plan

function safeTrim(value: string | null | undefined): string | null {
  if (typeof value !== 'string') return null;
  const compact = value.replace(/\s+/g, ' ').trim();
  return compact || null;
}

export function compactText(value: string | null | undefined, limit = 20_000): string {
  if (typeof value !== 'string') return '';
  const compact = value.replace(/\s+/g, ' ').trim();
  if (!compact) return '';
  return compact.length <= limit ? compact : compact.slice(0, limit);
}

export function isVisible(el: Element | null): boolean {
  if (!el) return false;
  const rect = (el as HTMLElement).getBoundingClientRect();
  const style = window.getComputedStyle(el as HTMLElement);
  return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
}

export function textFrom(el: Element | null): string | null {
  if (!el) return null;
  if (el instanceof HTMLTextAreaElement) return safeTrim(el.value);
  if (el instanceof HTMLInputElement) return safeTrim(el.value);
  return safeTrim(el.textContent);
}

function selectorIdentity(node: Element): string | null {
  const id = safeTrim(node.getAttribute('id'));
  if (id) return `#${id}`;
  const name = safeTrim(node.getAttribute('name'));
  if (name) return `[name=${JSON.stringify(name)}]`;
  return null;
}

export function selectorHint(node: Element, fallback: string): string {
  const parts = [node.tagName.toLowerCase()];
  const identity = selectorIdentity(node);
  const role = safeTrim(node.getAttribute('role'));
  const placeholder = safeTrim(node.getAttribute('placeholder'));
  const aria = safeTrim(node.getAttribute('aria-label'));
  if (identity) parts.push(identity);
  if (role) parts.push(`[role=${JSON.stringify(role)}]`);
  if (placeholder) parts.push(`[placeholder*=${JSON.stringify(placeholder.slice(0, 24))}]`);
  if (aria) parts.push(`[aria-label*=${JSON.stringify(aria.slice(0, 24))}]`);
  return parts.join(' ') || fallback;
}

function uniqueStrings(values: Array<string | null | undefined>): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  for (const value of values) {
    const trimmed = safeTrim(value);
    if (!trimmed || seen.has(trimmed)) continue;
    seen.add(trimmed);
    out.push(trimmed);
  }
  return out;
}

function labelTexts(node: Element): string[] {
  if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement || node instanceof HTMLOutputElement || node instanceof HTMLProgressElement || node instanceof HTMLMeterElement) {
    return uniqueStrings(Array.from(node.labels || []).map((label) => label.textContent));
  }
  const labelledBy = safeTrim(node.getAttribute('aria-labelledby'));
  if (!labelledBy) return [];
  return uniqueStrings(labelledBy.split(/\s+/).map((id) => node.ownerDocument.getElementById(id)?.textContent ?? null));
}

function descriptionTexts(node: Element): string[] {
  const describedBy = safeTrim(node.getAttribute('aria-describedby'));
  if (!describedBy) return [];
  return uniqueStrings(describedBy.split(/\s+/).map((id) => node.ownerDocument.getElementById(id)?.textContent ?? null));
}

function nearestLegend(node: Element): string | null {
  const fieldset = node.closest('fieldset');
  return safeTrim(fieldset?.querySelector('legend')?.textContent ?? null);
}

function nearestDialog(node: Element): { name?: string; role?: string; modal?: boolean; open?: boolean } {
  const dialog = node.closest('dialog, [role="dialog"], [role="alertdialog"]');
  if (!(dialog instanceof Element)) return {};
  const role = safeTrim(dialog.getAttribute('role')) || (dialog.tagName === 'DIALOG' ? 'dialog' : null) || undefined;
  const labelledBy = safeTrim(dialog.getAttribute('aria-labelledby'));
  const labelFromRef = labelledBy
    ? uniqueStrings(labelledBy.split(/\s+/).map((id) => dialog.ownerDocument.getElementById(id)?.textContent ?? null))[0]
    : null;
  const name = labelFromRef || safeTrim(dialog.getAttribute('aria-label')) || safeTrim(dialog.querySelector('h1, h2, h3, [data-dialog-title], legend')?.textContent ?? null) || undefined;
  let modal: boolean | undefined;
  if (dialog instanceof HTMLDialogElement) {
    try {
      modal = dialog.matches(':modal');
    } catch {
      modal = dialog.hasAttribute('open');
    }
  } else {
    modal = dialog.getAttribute('aria-modal') === 'true';
  }
  const open = dialog instanceof HTMLDialogElement ? dialog.open : dialog.hasAttribute('open') || dialog.getAttribute('aria-hidden') === 'false';
  return { ...(name ? { name } : {}), ...(role ? { role } : {}), ...(typeof modal === 'boolean' ? { modal } : {}), open };
}

function formContext(node: Element): { name?: string; action?: string; method?: string } {
  const form = node.closest('form');
  if (!(form instanceof HTMLFormElement)) return {};
  const labelledBy = safeTrim(form.getAttribute('aria-labelledby'));
  const labelFromRef = labelledBy
    ? uniqueStrings(labelledBy.split(/\s+/).map((id) => form.ownerDocument.getElementById(id)?.textContent ?? null))[0]
    : null;
  const name = labelFromRef || safeTrim(form.getAttribute('aria-label')) || safeTrim(form.querySelector('legend, h1, h2, h3, h4, h5, h6')?.textContent ?? null) || undefined;
  const action = safeTrim(form.getAttribute('action')) || safeTrim(form.action) || undefined;
  const method = safeTrim(form.getAttribute('method')) || safeTrim(form.method) || undefined;
  return { ...(name ? { name } : {}), ...(action ? { action } : {}), ...(method ? { method } : {}) };
}

interface FrameChainEntry {
  selector: string;
  name?: string;
  title?: string;
}

function frameChainForWindow(win: Window): FrameChainEntry[] {
  const chain: FrameChainEntry[] = [];
  let current: Window | null = win;
  while (current && current.top !== current) {
    try {
      const frame = current.frameElement;
      if (!(frame instanceof HTMLIFrameElement)) break;
      chain.unshift({
        selector: selectorHint(frame, 'iframe'),
        ...(safeTrim(frame.name) ? { name: safeTrim(frame.name) as string } : {}),
        ...(safeTrim(frame.title) ? { title: safeTrim(frame.title) as string } : {}),
      });
      current = current.parent;
    } catch {
      break;
    }
  }
  return chain;
}

function frameContext(win: Window): { selector?: string; name?: string; title?: string; path?: string; depth?: number; pathSelectors?: string[]; pathNames?: string[]; pathTitles?: string[] } {
  const chain = frameChainForWindow(win);
  if (!chain.length) return {};
  const leaf = chain[chain.length - 1];
  const pathSelectors = chain.map((entry) => entry.selector);
  const pathNames = uniqueStrings(chain.map((entry) => entry.name ?? null));
  const pathTitles = uniqueStrings(chain.map((entry) => entry.title ?? null));
  return {
    selector: leaf.selector,
    ...(leaf.name ? { name: leaf.name } : {}),
    ...(leaf.title ? { title: leaf.title } : {}),
    ...(pathSelectors.length ? { path: pathSelectors.join(' >> '), pathSelectors } : {}),
    ...(pathNames.length ? { pathNames } : {}),
    ...(pathTitles.length ? { pathTitles } : {}),
    depth: chain.length,
  };
}

function controlKind(node: Element): string | null {
  const role = safeTrim(node.getAttribute('role'));
  if (role) return role;
  if (node instanceof HTMLTextAreaElement) return 'textarea';
  if (node instanceof HTMLSelectElement) return node.multiple ? 'listbox' : 'combobox';
  if (node instanceof HTMLInputElement) return `input:${(node.type || 'text').toLowerCase()}`;
  if (node instanceof HTMLButtonElement) return 'button';
  if (node.getAttribute('contenteditable') === '' || node.getAttribute('contenteditable') === 'true') return 'contenteditable';
  return node.tagName.toLowerCase();
}

function selectedOptions(node: Element): string[] {
  if (!(node instanceof HTMLSelectElement)) return [];
  return uniqueStrings(Array.from(node.selectedOptions).map((option) => option.label || option.textContent));
}

function optionLabels(node: Element): string[] {
  if (!(node instanceof HTMLSelectElement)) return [];
  return uniqueStrings(Array.from(node.options).map((option) => option.label || option.textContent));
}

function autocompleteValue(node: Element): string | null {
  if (!(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement)) return null;
  return safeTrim(node.autocomplete || node.getAttribute('autocomplete'));
}

function inputModeValue(node: Element): string | null {
  const attr = safeTrim(node.getAttribute('inputmode'));
  if (attr) return attr;
  if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement) {
    return safeTrim(node.inputMode);
  }
  return null;
}

function choiceGroup(node: Element): string | null {
  if (node instanceof HTMLInputElement && ['checkbox', 'radio'].includes((node.type || '').toLowerCase())) {
    return safeTrim(node.name) || nearestLegend(node);
  }
  return null;
}

function constraintHints(node: Element): string[] {
  const hints: string[] = [];
  if (node instanceof HTMLInputElement) {
    if (safeTrim(node.pattern)) hints.push(`pattern:${node.pattern}`);
    if (node.maxLength > -1) hints.push(`maxlength:${node.maxLength}`);
    if (node.minLength > -1) hints.push(`minlength:${node.minLength}`);
    if (safeTrim(node.min)) hints.push(`min:${node.min}`);
    if (safeTrim(node.max)) hints.push(`max:${node.max}`);
    if (safeTrim(node.step)) hints.push(`step:${node.step}`);
  } else if (node instanceof HTMLTextAreaElement) {
    if (node.maxLength > -1) hints.push(`maxlength:${node.maxLength}`);
    if (node.minLength > -1) hints.push(`minlength:${node.minLength}`);
  }
  return uniqueStrings(hints);
}

function constraintFlags(node: Element): string[] {
  if (!(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement)) return [];
  const validity = node.validity;
  const flags: string[] = [];
  const known: Array<Exclude<keyof ValidityState, 'valid'>> = ['badInput', 'customError', 'patternMismatch', 'rangeOverflow', 'rangeUnderflow', 'stepMismatch', 'tooLong', 'tooShort', 'typeMismatch', 'valueMissing'];
  for (const key of known) {
    if (validity[key]) flags.push(key);
  }
  return flags;
}

export interface LiveCandidateInfo {
  selector_hint: string;
  score: number;
  text_length: number;
  visible: boolean;
  label_text?: string;
  labels?: string[];
  accessible_name?: string;
  accessible_names?: string[];
  description_text?: string;
  descriptions?: string[];
  fieldset_legend?: string;
  fieldset_legends?: string[];
  dialog_name?: string;
  dialog_role?: string;
  dialog_modal?: boolean;
  dialog_open?: boolean;
  control_kind?: string;
  form_name?: string;
  form_action?: string;
  form_method?: string;
  frame_selector?: string;
  frame_name?: string;
  frame_title?: string;
  frame_path?: string;
  frame_depth?: number;
  frame_path_selectors?: string[];
  frame_path_names?: string[];
  frame_path_titles?: string[];
  option_count?: number;
  option_labels?: string[];
  selected_options?: string[];
  required?: boolean;
  invalid?: boolean;
  checked_state?: string;
  disabled?: boolean;
  readonly?: boolean;
  multiple?: boolean;
  selected_count?: number;
  autocomplete?: string;
  input_mode?: string;
  constraint_hints?: string[];
  constraint_flags?: string[];
  choice_group?: string;
  placeholder?: string;
  name?: string;
  role?: string;
  text_sample?: string;
  submit_action?: string;
  submit_method?: string;
  submit_target?: string;
}

export interface LiveSemanticOutline {
  heading_outline: string[];
  prompt_labels: string[];
  accessible_names: string[];
  prompt_descriptions: string[];
  submit_labels: string[];
  form_names: string[];
  form_actions: string[];
  fieldset_legends: string[];
  dialog_names: string[];
  iframe_names: string[];
  iframe_titles: string[];
  frame_paths: string[];
  control_kinds: string[];
  option_labels: string[];
  choice_groups: string[];
  autocomplete_tokens: string[];
  state_flags: string[];
  constraint_hints: string[];
  link_hosts: string[];
}

export interface LiveDocumentContext {
  document: Document;
  window: Window;
  depth: number;
  frame_selector?: string;
  frame_name?: string;
  frame_title?: string;
  frame_path?: string;
  frame_path_selectors: string[];
  frame_path_names: string[];
  frame_path_titles: string[];
}

export interface LiveFrameInventory {
  contexts: LiveDocumentContext[];
  iframe_samples: Array<Record<string, unknown>>;
  accessible_iframe_count: number;
  blocked_iframe_count: number;
  blocked_iframe_samples: Array<Record<string, unknown>>;
  blocked_iframe_names: string[];
  blocked_iframe_titles: string[];
  blocked_frame_paths: string[];
  traversed_document_count: number;
  total_iframe_count: number;
  frame_capture_ratio: number;
  frame_capture_status: string;
  max_frame_depth: number;
  frame_paths: string[];
}

export function candidateInfo(node: Element, score: number, fallback: string, win: Window = window): LiveCandidateInfo {
  const labels = labelTexts(node);
  const descriptions = descriptionTexts(node);
  const fieldsetLegend = nearestLegend(node);
  const dialog = nearestDialog(node);
  const form = formContext(node);
  const frame = frameContext(win);
  const selected = selectedOptions(node);
  const options = optionLabels(node);
  const placeholder = safeTrim(node.getAttribute('placeholder')) || undefined;
  const name = safeTrim(node.getAttribute('name')) || undefined;
  const explicitRole = safeTrim(node.getAttribute('role')) || undefined;
  const accessibleNames = uniqueStrings([
    safeTrim(node.getAttribute('aria-label')),
    ...labels,
    placeholder,
    name,
  ]);
  const textSample = safeTrim(node.textContent)?.slice(0, 120) || undefined;
  const control = controlKind(node) || undefined;
  const checkedState = node instanceof HTMLInputElement && ['checkbox', 'radio'].includes((node.type || '').toLowerCase())
    ? (node.checked ? 'checked' : 'unchecked')
    : undefined;
  const readonly = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement ? node.readOnly : undefined;
  const disabled = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement || node instanceof HTMLButtonElement
    ? node.disabled
    : undefined;
  const multiple = node instanceof HTMLInputElement || node instanceof HTMLSelectElement ? Boolean(node.multiple) : undefined;
  const required = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement ? node.required : undefined;
  const invalid = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement ? node.matches(':invalid') : undefined;
  const autoComplete = autocompleteValue(node) || undefined;
  const inputMode = inputModeValue(node) || undefined;
  const hintList = constraintHints(node);
  const flagList = constraintFlags(node);
  const choice = choiceGroup(node) || undefined;
  const submitAction = node instanceof HTMLButtonElement || (node instanceof HTMLInputElement && ['submit', 'button'].includes((node.type || '').toLowerCase()))
    ? form.action || undefined
    : undefined;
  const submitMethod = node instanceof HTMLButtonElement || (node instanceof HTMLInputElement && ['submit', 'button'].includes((node.type || '').toLowerCase()))
    ? form.method || undefined
    : undefined;
  const submitTarget = node instanceof HTMLButtonElement || node instanceof HTMLInputElement
    ? safeTrim(node.getAttribute('formtarget')) || undefined
    : undefined;
  return {
    selector_hint: selectorHint(node, fallback),
    score: Number(score.toFixed(3)),
    text_length: (textFrom(node) || '').length,
    visible: isVisible(node),
    ...(labels[0] ? { label_text: labels[0] } : {}),
    ...(labels.length ? { labels } : {}),
    ...(accessibleNames[0] ? { accessible_name: accessibleNames[0] } : {}),
    ...(accessibleNames.length ? { accessible_names: accessibleNames } : {}),
    ...(descriptions[0] ? { description_text: descriptions[0] } : {}),
    ...(descriptions.length ? { descriptions } : {}),
    ...(fieldsetLegend ? { fieldset_legend: fieldsetLegend, fieldset_legends: [fieldsetLegend] } : {}),
    ...(dialog.name ? { dialog_name: dialog.name } : {}),
    ...(dialog.role ? { dialog_role: dialog.role } : {}),
    ...(typeof dialog.modal === 'boolean' ? { dialog_modal: dialog.modal } : {}),
    ...(typeof dialog.open === 'boolean' ? { dialog_open: dialog.open } : {}),
    ...(control ? { control_kind: control } : {}),
    ...(form.name ? { form_name: form.name } : {}),
    ...(form.action ? { form_action: form.action } : {}),
    ...(form.method ? { form_method: form.method } : {}),
    ...(frame.selector ? { frame_selector: frame.selector } : {}),
    ...(frame.name ? { frame_name: frame.name } : {}),
    ...(frame.title ? { frame_title: frame.title } : {}),
    ...(frame.path ? { frame_path: frame.path } : {}),
    ...(typeof frame.depth === 'number' ? { frame_depth: frame.depth } : {}),
    ...(frame.pathSelectors?.length ? { frame_path_selectors: frame.pathSelectors } : {}),
    ...(frame.pathNames?.length ? { frame_path_names: frame.pathNames } : {}),
    ...(frame.pathTitles?.length ? { frame_path_titles: frame.pathTitles } : {}),
    ...(options.length ? { option_count: options.length, option_labels: options } : {}),
    ...(selected.length ? { selected_options: selected, selected_count: selected.length } : {}),
    ...(typeof required === 'boolean' ? { required } : {}),
    ...(typeof invalid === 'boolean' ? { invalid } : {}),
    ...(checkedState ? { checked_state: checkedState } : {}),
    ...(typeof disabled === 'boolean' ? { disabled } : {}),
    ...(typeof readonly === 'boolean' ? { readonly } : {}),
    ...(typeof multiple === 'boolean' ? { multiple } : {}),
    ...(autoComplete ? { autocomplete: autoComplete } : {}),
    ...(inputMode ? { input_mode: inputMode } : {}),
    ...(hintList.length ? { constraint_hints: hintList } : {}),
    ...(flagList.length ? { constraint_flags: flagList } : {}),
    ...(choice ? { choice_group: choice } : {}),
    ...(placeholder ? { placeholder } : {}),
    ...(name ? { name } : {}),
    ...(explicitRole ? { role: explicitRole } : {}),
    ...(textSample ? { text_sample: textSample } : {}),
    ...(submitAction ? { submit_action: submitAction } : {}),
    ...(submitMethod ? { submit_method: submitMethod } : {}),
    ...(submitTarget ? { submit_target: submitTarget } : {}),
  };
}

function iframeSampleFromElement(iframe: HTMLIFrameElement, ownerDocument: Document, depth: number, extra: Record<string, unknown> = {}): Record<string, unknown> {
  const src = safeTrim(iframe.getAttribute('src')) || undefined;
  let resolvedSrc: string | undefined;
  if (src) {
    try {
      resolvedSrc = new URL(src, ownerDocument.baseURI).href;
    } catch {
      resolvedSrc = undefined;
    }
  }
  const name = safeTrim(iframe.getAttribute('name')) || undefined;
  const title = safeTrim(iframe.getAttribute('title')) || undefined;
  return {
    selectorHint: selectorHint(iframe, 'iframe'),
    depth,
    ...(src ? { src } : {}),
    ...(resolvedSrc ? { resolvedSrc } : {}),
    ...(name ? { name } : {}),
    ...(title ? { title } : {}),
    ...extra,
  };
}

function accessibleFrameContext(parent: LiveDocumentContext, iframe: HTMLIFrameElement): LiveDocumentContext | null {
  try {
    const frameWindow = iframe.contentWindow;
    const frameDocument = iframe.contentDocument || frameWindow?.document || null;
    if (!frameWindow || !frameDocument || !frameDocument.documentElement) return null;
    const selector = selectorHint(iframe, 'iframe');
    const name = safeTrim(iframe.getAttribute('name')) || undefined;
    const title = safeTrim(iframe.getAttribute('title')) || undefined;
    const pathSelectors = [...parent.frame_path_selectors, selector];
    const pathNames = uniqueStrings([...parent.frame_path_names, name]);
    const pathTitles = uniqueStrings([...parent.frame_path_titles, title]);
    return {
      document: frameDocument,
      window: frameWindow,
      depth: parent.depth + 1,
      frame_selector: selector,
      ...(name ? { frame_name: name } : {}),
      ...(title ? { frame_title: title } : {}),
      ...(pathSelectors.length ? { frame_path: pathSelectors.join(' >> ') } : {}),
      frame_path_selectors: pathSelectors,
      frame_path_names: pathNames,
      frame_path_titles: pathTitles,
    };
  } catch {
    return null;
  }
}

export function collectLiveFrameInventory(rootDocument: Document = document, rootWindow: Window = window, maxDepth = 4): LiveFrameInventory {
  const rootContext: LiveDocumentContext = {
    document: rootDocument,
    window: rootWindow,
    depth: 0,
    frame_path_selectors: [],
    frame_path_names: [],
    frame_path_titles: [],
  };
  const contexts: LiveDocumentContext[] = [rootContext];
  const queue: LiveDocumentContext[] = [rootContext];
  const iframeSamples: Array<Record<string, unknown>> = [];
  const blockedIframeSamples: Array<Record<string, unknown>> = [];
  const visitedDocuments = new Set<Document>([rootDocument]);
  let accessibleIframeCount = 0;
  let blockedIframeCount = 0;
  let maxFrameDepth = 0;

  while (queue.length) {
    const context = queue.shift() as LiveDocumentContext;
    maxFrameDepth = Math.max(maxFrameDepth, context.depth);
    if (context.depth >= maxDepth) continue;
    const iframes = Array.from(context.document.querySelectorAll('iframe'));
    for (const iframe of iframes) {
      if (!(iframe instanceof HTMLIFrameElement)) continue;
      const nextContext = accessibleFrameContext(context, iframe);
      const pathSelectors = [...context.frame_path_selectors, selectorHint(iframe, 'iframe')];
      const path = pathSelectors.join(' >> ');
      if (nextContext && !visitedDocuments.has(nextContext.document)) {
        accessibleIframeCount += 1;
        visitedDocuments.add(nextContext.document);
        contexts.push(nextContext);
        queue.push(nextContext);
        iframeSamples.push(iframeSampleFromElement(iframe, context.document, context.depth + 1, {
          accessible: true,
          ...(path ? { framePath: path, framePathSelectors: pathSelectors } : {}),
        }));
        continue;
      }
      if (nextContext) {
        iframeSamples.push(iframeSampleFromElement(iframe, context.document, context.depth + 1, {
          accessible: true,
          ...(path ? { framePath: path, framePathSelectors: pathSelectors } : {}),
        }));
        continue;
      }
      blockedIframeCount += 1;
      const blocked = iframeSampleFromElement(iframe, context.document, context.depth + 1, {
        accessible: false,
        reason: 'cross-origin-or-inaccessible',
        ...(path ? { framePath: path, framePathSelectors: pathSelectors } : {}),
      });
      iframeSamples.push(blocked);
      blockedIframeSamples.push(blocked);
    }
  }

  const totalIframeCount = iframeSamples.length;
  const frameCaptureStatus = totalIframeCount === 0
    ? 'no_iframes'
    : accessibleIframeCount === 0 && blockedIframeCount > 0
      ? 'blocked_only'
      : blockedIframeCount > 0
        ? 'partial'
        : 'full';
  const frameCaptureRatio = totalIframeCount > 0 ? Number((accessibleIframeCount / totalIframeCount).toFixed(3)) : 1;

  return {
    contexts,
    iframe_samples: iframeSamples.slice(0, 16),
    accessible_iframe_count: accessibleIframeCount,
    blocked_iframe_count: blockedIframeCount,
    blocked_iframe_samples: blockedIframeSamples.slice(0, 8),
    blocked_iframe_names: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.name === 'string' ? sample.name : null)),
    blocked_iframe_titles: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.title === 'string' ? sample.title : null)),
    blocked_frame_paths: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.framePath === 'string' ? sample.framePath : null)),
    traversed_document_count: contexts.length,
    total_iframe_count: totalIframeCount,
    frame_capture_ratio: frameCaptureRatio,
    frame_capture_status: frameCaptureStatus,
    max_frame_depth: maxFrameDepth,
    frame_paths: uniqueStrings(contexts.slice(1).map((context) => context.frame_path ?? null)),
  };
}

function semanticOutlineFromInventory(inventory: LiveFrameInventory, inputs: LiveCandidateInfo[], submits: LiveCandidateInfo[] = []): LiveSemanticOutline {
  const headings = uniqueStrings(inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map((heading) => heading.textContent)));
  const forms = inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('form')));
  const dialogs = inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]')));
  const iframes = inventory.iframe_samples;
  const allCandidates = [...inputs, ...submits];
  const stateFlags = uniqueStrings(allCandidates.flatMap((item) => {
    const flags: Array<string | null> = [];
    if (item.required) flags.push('required');
    if (item.invalid) flags.push('invalid');
    if (item.disabled) flags.push('disabled');
    if (item.readonly) flags.push('readonly');
    if (item.multiple) flags.push('multiple');
    if (item.checked_state) flags.push(`checked:${item.checked_state}`);
    return flags;
  }));
  const linkHosts = uniqueStrings(inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('a[href]')).map((link) => {
    try {
      return new URL((link as HTMLAnchorElement).href, context.document.baseURI).host;
    } catch {
      return null;
    }
  })));
  return {
    heading_outline: headings,
    prompt_labels: uniqueStrings(inputs.flatMap((item) => [item.label_text, ...(item.labels || [])])),
    accessible_names: uniqueStrings(inputs.flatMap((item) => [item.accessible_name, ...(item.accessible_names || [])])),
    prompt_descriptions: uniqueStrings(inputs.flatMap((item) => [item.description_text, ...(item.descriptions || [])])),
    submit_labels: uniqueStrings(submits.flatMap((item) => [item.accessible_name, item.label_text, item.text_sample])),
    form_names: uniqueStrings([
      ...inputs.map((item) => item.form_name || null),
      ...forms.map((form) => safeTrim(form.getAttribute('aria-label')) || safeTrim(form.querySelector('legend, h1, h2, h3, h4, h5, h6')?.textContent ?? null)),
    ]),
    form_actions: uniqueStrings([
      ...inputs.map((item) => item.form_action || null),
      ...submits.map((item) => item.submit_action || item.form_action || null),
      ...forms.map((form) => form instanceof HTMLFormElement ? safeTrim(form.action) : null),
    ]),
    fieldset_legends: uniqueStrings(inputs.flatMap((item) => [item.fieldset_legend, ...(item.fieldset_legends || [])])),
    dialog_names: uniqueStrings([
      ...inputs.map((item) => item.dialog_name || null),
      ...dialogs.map((dialog) => safeTrim(dialog.getAttribute('aria-label')) || safeTrim(dialog.querySelector('h1, h2, h3, legend')?.textContent ?? null)),
    ]),
    iframe_names: uniqueStrings([
      ...inputs.flatMap((item) => [item.frame_name, ...(item.frame_path_names || [])]),
      ...iframes.map((frame) => typeof frame.name === 'string' ? frame.name : null),
    ]),
    iframe_titles: uniqueStrings([
      ...inputs.flatMap((item) => [item.frame_title, ...(item.frame_path_titles || [])]),
      ...iframes.map((frame) => typeof frame.title === 'string' ? frame.title : null),
    ]),
    frame_paths: uniqueStrings([
      ...inputs.map((item) => item.frame_path || null),
      ...inventory.frame_paths,
      ...iframes.map((frame) => typeof frame.framePath === 'string' ? frame.framePath : null),
    ]),
    control_kinds: uniqueStrings(inputs.map((item) => item.control_kind || null)),
    option_labels: uniqueStrings(inputs.flatMap((item) => item.option_labels || [])),
    choice_groups: uniqueStrings(inputs.map((item) => item.choice_group || null)),
    autocomplete_tokens: uniqueStrings(inputs.map((item) => item.autocomplete || null)),
    state_flags: stateFlags,
    constraint_hints: uniqueStrings(inputs.flatMap((item) => item.constraint_hints || [])),
    link_hosts: linkHosts,
  };
}

export function semanticOutline(document: Document, inputs: LiveCandidateInfo[], submits: LiveCandidateInfo[] = []): LiveSemanticOutline {
  return semanticOutlineFromInventory(collectLiveFrameInventory(document, window), inputs, submits);
}

function dialogSamplesFromInventory(inventory: LiveFrameInventory): Array<Record<string, unknown>> {
  return inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]')).slice(0, 8).map((dialog) => {
    const ctx = nearestDialog(dialog);
    return {
      selectorHint: selectorHint(dialog, 'dialog'),
      ...(ctx.name ? { name: ctx.name } : {}),
      ...(ctx.role ? { role: ctx.role } : {}),
      ...(typeof ctx.modal === 'boolean' ? { modal: ctx.modal } : {}),
      ...(typeof ctx.open === 'boolean' ? { open: ctx.open } : {}),
      ...(context.frame_path ? { framePath: context.frame_path, framePathSelectors: context.frame_path_selectors } : {}),
    };
  })).slice(0, 16);
}

export function dialogSamples(document: Document): Array<Record<string, unknown>> {
  return dialogSamplesFromInventory(collectLiveFrameInventory(document, window));
}

function iframeSamplesFromInventory(inventory: LiveFrameInventory): Array<Record<string, unknown>> {
  return inventory.iframe_samples.slice(0, 16);
}

export function iframeSamples(document: Document): Array<Record<string, unknown>> {
  return iframeSamplesFromInventory(collectLiveFrameInventory(document, window));
}

export interface LiveFixtureMetadataOptions {
  inventory?: LiveFrameInventory | null;
  inputCandidates?: LiveCandidateInfo[] | null;
  outputCandidates?: LiveCandidateInfo[] | null;
  submitCandidates?: LiveCandidateInfo[] | null;
}

function countAcrossContexts(inventory: LiveFrameInventory, selector: string): number {
  return inventory.contexts.reduce((total, context) => total + context.document.querySelectorAll(selector).length, 0);
}

export function buildLiveFixtureMetadata(document: Document, inputNode: Element | null, submitNode: Element | null = null, inputInfo?: LiveCandidateInfo | null, submitInfo?: LiveCandidateInfo | null, options: LiveFixtureMetadataOptions = {}): Record<string, unknown> {
  const inventory = options.inventory || collectLiveFrameInventory(document, window);
  const computedInput = inputNode ? (inputInfo || candidateInfo(inputNode, 1, selectorHint(inputNode, 'input'))) : null;
  const computedSubmit = submitNode ? (submitInfo || candidateInfo(submitNode, 1, selectorHint(submitNode, 'button'))) : null;
  const inputs = options.inputCandidates?.length ? options.inputCandidates : (computedInput ? [computedInput] : []);
  const outputs = options.outputCandidates?.length ? options.outputCandidates : [];
  const submits = options.submitCandidates?.length ? options.submitCandidates : (computedSubmit ? [computedSubmit] : []);
  const primaryInput = computedInput || inputs[0] || null;
  const primaryOutput = outputs[0] || null;
  const primarySubmit = computedSubmit || submits[0] || null;
  const outline = semanticOutlineFromInventory(inventory, inputs, submits);
  const dialogs = dialogSamplesFromInventory(inventory);
  const iframes = iframeSamplesFromInventory(inventory);
  const frameCaptureWarning = inventory.frame_capture_status === 'partial'
    ? `frame capture is partial: ${inventory.accessible_iframe_count}/${inventory.total_iframe_count} iframes were accessible and ${inventory.blocked_iframe_count} were blocked`
    : inventory.frame_capture_status === 'blocked_only'
      ? `frame capture could not descend into any iframe: ${inventory.blocked_iframe_count} blocked iframe${inventory.blocked_iframe_count === 1 ? '' : 's'} observed`
      : null;

  return {
    link_count: countAcrossContexts(inventory, 'a[href]'),
    form_count: countAcrossContexts(inventory, 'form'),
    dialog_count: countAcrossContexts(inventory, 'dialog, [role="dialog"], [role="alertdialog"]'),
    iframe_count: countAcrossContexts(inventory, 'iframe'),
    heading_count: countAcrossContexts(inventory, 'h1, h2, h3, h4, h5, h6'),
    accessible_iframe_count: inventory.accessible_iframe_count,
    blocked_iframe_count: inventory.blocked_iframe_count,
    blocked_iframe_names: inventory.blocked_iframe_names,
    blocked_iframe_titles: inventory.blocked_iframe_titles,
    blocked_frame_paths: inventory.blocked_frame_paths,
    traversed_document_count: inventory.traversed_document_count,
    total_iframe_count: inventory.total_iframe_count,
    frame_capture_ratio: inventory.frame_capture_ratio,
    frame_capture_status: inventory.frame_capture_status,
    ...(frameCaptureWarning ? { frame_capture_warning: frameCaptureWarning } : {}),
    max_frame_depth: inventory.max_frame_depth,
    frame_paths: outline.frame_paths,
    blocked_iframe_samples: inventory.blocked_iframe_samples,
    split_scope_detected: (primaryInput?.frame_path ?? null) !== (primaryOutput?.frame_path ?? null),
    top_input_label: primaryInput?.label_text ?? null,
    top_input_accessible_name: primaryInput?.accessible_name ?? primaryInput?.label_text ?? null,
    top_input_description: primaryInput?.description_text ?? null,
    top_output_label: primaryOutput?.accessible_name ?? primaryOutput?.label_text ?? primaryOutput?.text_sample ?? null,
    top_output_frame_path: primaryOutput?.frame_path ?? null,
    top_output_frame_depth: primaryOutput?.frame_depth ?? null,
    top_fieldset_legend: primaryInput?.fieldset_legend ?? null,
    top_dialog_name: primaryInput?.dialog_name ?? null,
    top_form_name: primaryInput?.form_name ?? null,
    top_input_frame_path: primaryInput?.frame_path ?? null,
    top_input_frame_depth: primaryInput?.frame_depth ?? null,
    top_option_count: primaryInput?.option_count ?? null,
    top_selected_option: primaryInput?.selected_options?.[0] ?? null,
    top_checked_state: primaryInput?.checked_state ?? null,
    top_disabled: primaryInput?.disabled ?? false,
    top_readonly: primaryInput?.readonly ?? false,
    top_multiple: primaryInput?.multiple ?? false,
    top_selected_count: primaryInput?.selected_count ?? null,
    top_autocomplete: primaryInput?.autocomplete ?? null,
    top_input_mode: primaryInput?.input_mode ?? null,
    top_choice_group: primaryInput?.choice_group ?? null,
    top_constraint_hints: primaryInput?.constraint_hints ?? [],
    top_constraint_flags: primaryInput?.constraint_flags ?? [],
    top_submit_label: primarySubmit?.accessible_name ?? primarySubmit?.label_text ?? primarySubmit?.text_sample ?? null,
    top_submit_action: primarySubmit?.submit_action ?? primarySubmit?.form_action ?? null,
    top_submit_frame_path: primarySubmit?.frame_path ?? null,
    submit_candidates: submits,
    semantic_outline: outline,
    dialog_samples: dialogs,
    iframe_samples: iframes,
    form_actions: outline.form_actions,
  };
}

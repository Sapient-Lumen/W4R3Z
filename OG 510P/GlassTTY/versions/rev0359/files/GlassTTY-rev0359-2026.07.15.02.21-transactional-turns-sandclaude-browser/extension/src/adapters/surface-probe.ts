/**
 * Surface probe — the eyes of GlassTTY's drift-hunting wing.
 *
 * The existing surface contract answers "are the things I already know about
 * still there?". That is necessary but it is blind by construction: it can never
 * see a control that did not exist when the contract was written. Every ChatGPT
 * UI change that has ever broken this project arrived as *something new*.
 *
 * So this probe inverts the question. It inventories **every interactive control
 * on the page**, classifies each one against a known-role atlas, and reports what
 * it could not classify. Unknown controls in load-bearing regions (the composer,
 * a modal, a banner) are the raw material of drift: the new model picker, the
 * new "Add files and more" button that once masqueraded as send, the nag dialog,
 * the rate-limit banner.
 *
 * Nothing here clicks anything. The probe is read-only by construction.
 */

import { isVisible, selectorHint, textFrom } from '../content/generic';

export const SURFACE_PROBE_VERSION = 'rev0359';

export type ControlRole =
  | 'send'
  | 'stop'
  | 'continue'
  | 'attach'
  | 'dictate'
  | 'model-picker'
  | 'tools'
  | 'search'
  | 'copy'
  | 'edit'
  | 'regenerate'
  | 'feedback'
  | 'scroll'
  | 'new-chat'
  | 'sidebar'
  | 'account'
  | 'share'
  | 'close'
  | 'nav'
  | 'effort-pill'
  | 'conversation-options'
  | 'citation'
  | 'composer'
  | 'attachment-chip'
  | 'unknown';

export type SurfaceRegion = 'composer' | 'transcript' | 'dialog' | 'banner' | 'header' | 'sidebar' | 'page';

/**
 * Framework-generated ids that are regenerated on every page load.
 *
 * The live 2026-07-11 surface report contains 65 nodes matching [id^="radix-"]
 * — including the composer's model pill (#radix-_r_ds_). These ids look
 * beautifully specific and are completely worthless as selectors: they change
 * the moment you reload. Anything that treats them as durable will write an
 * override that silently stops matching tomorrow.
 */
export const VOLATILE_ID_PATTERNS = [/^radix-/i, /^:r[0-9a-z]+:$/i, /^headlessui-/i, /^mui-/i, /^react-aria-/i];

export function isVolatileId(id: string | null | undefined): boolean {
  if (!id) return true;
  return VOLATILE_ID_PATTERNS.some((pattern) => pattern.test(id));
}

export interface ProbedControl {
  selector_hint: string;
  tag: string;
  id: string | null;
  test_id: string | null;
  aria_label: string | null;
  title: string | null;
  text: string | null;
  role_attr: string | null;
  type_attr: string | null;
  disabled: boolean;
  visible: boolean;
  class_tokens: string[];
  region: SurfaceRegion;
  classification: ControlRole;
  /** How the classifier decided. Empty when unknown. */
  evidence: string[];
  /** Stable-ish identity for diffing across snapshots. */
  key: string;
  /** False when `id` is framework-generated and must never be used as a selector. */
  id_stable: boolean;
}

export interface ProbedAnchor {
  name: string;
  found: boolean;
  selector_hint: string | null;
  /** The selector GlassTTY's adapter expects to find this anchor by. */
  expected_selector: string | null;
  /** True when the found node actually matches the expected selector. */
  matches_expectation: boolean;
  detail: Record<string, unknown>;
}

export interface SurfaceOddity {
  kind: 'unknown-control' | 'dialog' | 'banner' | 'unexpected-anchor-selector' | 'missing-anchor' | 'send-hidden-empty-composer';
  severity: 'info' | 'warn' | 'critical';
  region: SurfaceRegion;
  summary: string;
  control?: ProbedControl;
  anchor?: string;
}

export interface ComposerState {
  present: boolean;
  empty: boolean;
  text_length: number;
  /** The hidden <input type=file> the attach path writes into. */
  file_input_present: boolean;
  file_input_selector: string | null;
  file_input_multiple: boolean;
  attachment_chip_count: number;
  attached_file_count: number;
}

export interface AuthenticationState {
  posture: 'authenticated' | 'anonymous' | 'unknown';
  login_control_present: boolean;
  signup_control_present: boolean;
  account_control_present: boolean;
}

export interface SurfaceProbeReport {
  probe_version: string;
  captured_at: string;
  url: string;
  route: { pathname: string; posture: string };
  authentication: AuthenticationState;
  composer: ComposerState;
  /**
   * `true` = works, `false` = broken, `null` = UNKNOWABLE right now.
   *
   * The null case is not pedantry, it is the difference between a working tool
   * and one you stop trusting. ChatGPT does not render a send button until the
   * composer has text: on the live 2026-07-11 surface report, `#composer-submit-button`
   * matched ZERO nodes on a perfectly healthy page, and the drift contract duly
   * screamed `surface-drift-blocker`. Absent-because-empty is not damage.
   */
  capabilities: Record<string, boolean | null>;
  anchors: ProbedAnchor[];
  controls: ProbedControl[];
  oddities: SurfaceOddity[];
  counts: Record<string, number>;
}

// --------------------------------------------------------------------------- //
// Role atlas. Each role is a list of matchers over a control's combined signal
// text. Order matters: the first hit wins, so put the most specific first.
// --------------------------------------------------------------------------- //
interface RoleMatcher {
  role: ControlRole;
  ids?: string[];
  testIds?: string[];
  terms?: string[];
  exactTexts?: string[];
  classes?: string[];
}

// Grounded in the live surface report of 2026-07-11. Every testid below was
// observed on a real ChatGPT page; guessing here is how you get an atlas that
// classifies nothing and reports the whole UI as an oddity.
const ROLE_ATLAS: RoleMatcher[] = [
  // The prompt editor itself. It is picked up by the interactive-node sweep
  // (role=textbox), and leaving it 'unknown' would make every healthy composer
  // report an oddity — the classic detector that nobody reads.
  { role: 'composer', ids: ['prompt-textarea'], testIds: ['prompt-textarea'], terms: ['chat with chatgpt', 'ask chatgpt'] },
  { role: 'send', ids: ['composer-submit-button'], testIds: ['send-button'], terms: ['send prompt', 'send message'] },
  { role: 'stop', testIds: ['stop-button'], terms: ['stop generating', 'stop streaming', 'stop responding', 'stop response'] },
  { role: 'continue', terms: ['continue generating', 'continue response'] },
  {
    role: 'attach',
    ids: ['composer-plus-btn', 'upload-files', 'upload-photos', 'upload-camera'],
    testIds: ['composer-plus-btn', 'upload-photos-input'],
    terms: ['add files and more', 'add files', 'add photos', 'attach', 'upload file'],
  },
  { role: 'dictate', terms: ['dictate', 'microphone', 'voice mode', 'start dictation', 'start voice'] },
  { role: 'model-picker', testIds: ['model-switcher-dropdown-button'], terms: ['model selector', 'switch model', 'choose model'] },
  // The composer pill. Live report shows it as a __composer-pill button whose
  // text is the current effort tier ("Pro"). Its id is volatile (radix-*), so it
  // is matched by class/text, never by id.
  { role: 'effort-pill', classes: ['__composer-pill'], terms: ['instant', 'medium', 'high', 'extra high', 'pro'] },
  { role: 'tools', terms: ['tools', 'deep research', 'create image', 'canvas'] },
  { role: 'search', terms: ['search chats', 'search'] },
  { role: 'copy', testIds: ['copy-turn-action-button'], terms: ['copy', 'copy code', 'copy response'] },
  { role: 'edit', terms: ['edit message', 'edit in canvas'] },
  { role: 'regenerate', terms: ['regenerate', 'try again', 'retry'] },
  { role: 'feedback', testIds: ['good-response-turn-action-button', 'bad-response-turn-action-button'], terms: ['good response', 'bad response', 'thumbs'] },
  { role: 'scroll', terms: ['scroll to bottom'] },
  { role: 'new-chat', testIds: ['create-new-chat-button'], terms: ['new chat'] },
  { role: 'conversation-options', testIds: ['conversation-options-button'], terms: ['conversation options', 'open conversation options', 'pin '] },
  { role: 'citation', testIds: ['webpage-citation-pill'], terms: ['sources'] },
  { role: 'sidebar', testIds: ['close-sidebar-button'], terms: ['sidebar', 'open sidebar', 'close sidebar'] },
  { role: 'account', testIds: ['accounts-profile-button'], terms: ['account', 'profile', 'settings', 'upgrade', 'log in', 'sign up', 'download apps'] },
  { role: 'share', terms: ['share'] },
  { role: 'close', terms: ['close', 'dismiss'] },
  // The signed-in root page renders these legal/help links inside the composer
  // form. Match exact link text so a future action button containing the same
  // words remains visible to the oddity hunter.
  { role: 'nav', exactTexts: ['terms', 'privacy policy', 'learn more'] },
];

function lower(value: string | null | undefined): string {
  return (value || '').trim().toLowerCase();
}

function classify(control: Omit<ProbedControl, 'classification' | 'evidence' | 'key' | 'id_stable'>): { role: ControlRole; evidence: string[] } {
  const id = lower(control.id);
  const testId = lower(control.test_id);
  const text = lower(control.text);
  const combined = [control.aria_label, control.title, control.text, control.test_id]
    .map(lower)
    .filter(Boolean)
    .join(' | ');

  for (const matcher of ROLE_ATLAS) {
    const evidence: string[] = [];
    if (matcher.ids?.some((candidate) => candidate === id)) evidence.push(`id=${id}`);
    if (matcher.testIds?.some((candidate) => candidate === testId)) evidence.push(`data-testid=${testId}`);
    if (matcher.classes?.some((candidate) => control.class_tokens?.includes(candidate))) {
      evidence.push(`class=${matcher.classes.find((candidate) => control.class_tokens?.includes(candidate))}`);
    }
    if (matcher.terms?.some((term) => combined.includes(term))) {
      const hit = matcher.terms.find((term) => combined.includes(term));
      evidence.push(`term=${hit}`);
    }
    if (matcher.exactTexts?.some((candidate) => candidate === text)) evidence.push(`text=${text}`);
    if (evidence.length) return { role: matcher.role, evidence };
  }
  return { role: 'unknown', evidence: [] };
}

function regionOf(node: Element): SurfaceRegion {
  if (node.closest('[role="dialog"], dialog, [aria-modal="true"]')) return 'dialog';
  if (node.closest('[role="alert"], [role="status"], [aria-live]')) return 'banner';
  if (node.closest('form, #composer-background, [data-testid="composer"], [class*="composer"]')) return 'composer';
  if (node.closest('nav, aside, [role="navigation"], [role="complementary"]')) return 'sidebar';
  if (node.closest('header, [role="banner"]')) return 'header';
  if (node.closest('main, [role="main"], article')) return 'transcript';
  return 'page';
}

/** A diff-stable identity: prefer id, then testid, then aria, then a selector hint. */
function controlKey(control: Omit<ProbedControl, 'key' | 'id_stable'>): string {
  // A volatile id is not an identity: keying on it would make every reload look
  // like "every control was removed and 65 new ones appeared".
  if (control.id && !isVolatileId(control.id)) return `id:${control.id}`;
  if (control.test_id) return `testid:${control.test_id}`;
  if (control.aria_label) return `aria:${lower(control.aria_label)}`;
  if (control.text) return `text:${lower(control.text).slice(0, 40)}`;
  return `sel:${control.selector_hint}`;
}

const INTERACTIVE_SELECTOR = [
  'button',
  '[role="button"]',
  '[role="menuitem"]',
  '[role="tab"]',
  '[role="switch"]',
  'a[href]',
  'input:not([type="hidden"])',
  'select',
  'textarea',
].join(', ');

function probeControls(document: Document): ProbedControl[] {
  const controls: ProbedControl[] = [];
  const seen = new Set<Element>();

  for (const node of Array.from(document.querySelectorAll(INTERACTIVE_SELECTOR))) {
    if (seen.has(node)) continue;
    seen.add(node);

    const el = node as HTMLElement;
    const text = textFrom(node);
    const partial = {
      selector_hint: selectorHint(node, 'control'),
      tag: node.tagName.toLowerCase(),
      id: node.getAttribute('id') || null,
      test_id: node.getAttribute('data-testid') || null,
      aria_label: node.getAttribute('aria-label') || null,
      title: node.getAttribute('title') || null,
      text: text ? text.slice(0, 120) : null,
      role_attr: node.getAttribute('role') || null,
      type_attr: node.getAttribute('type') || null,
      disabled: (el as HTMLButtonElement).disabled === true || node.getAttribute('aria-disabled') === 'true',
      visible: isVisible(node),
      class_tokens: Array.from(node.classList),
      region: regionOf(node),
    };
    const { role, evidence } = classify(partial);
    const withRole = { ...partial, classification: role, evidence };
    controls.push({ ...withRole, key: controlKey(withRole), id_stable: Boolean(partial.id) && !isVolatileId(partial.id) });
  }
  return controls;
}

/**
 * Anchors are the specific nodes GlassTTY's actions depend on. Unlike the
 * control inventory (which is exploratory), an anchor is a contract: if it moves
 * or vanishes, a command breaks. We record both what we found *and* whether it
 * still matches the selector the adapter expects, so a silent substitution
 * (a different node quietly winning the scorer) is visible.
 */
function probeAnchors(
  document: Document,
  found: {
    composer: HTMLElement | null;
    send: HTMLElement | null;
    stop: HTMLElement | null;
    continue: HTMLElement | null;
    latestAssistant: HTMLElement | null;
    latestUser: HTMLElement | null;
  },
  expected: { composer: string; send: string },
): ProbedAnchor[] {
  const anchor = (
    name: string,
    node: HTMLElement | null,
    expectedSelector: string | null,
    detail: Record<string, unknown> = {},
  ): ProbedAnchor => ({
    name,
    found: Boolean(node),
    selector_hint: node ? selectorHint(node, name) : null,
    expected_selector: expectedSelector,
    matches_expectation: Boolean(node && expectedSelector && node.matches(expectedSelector)),
    detail,
  });

  return [
    anchor('composer', found.composer, expected.composer, { editable: found.composer?.isContentEditable ?? null }),
    anchor('send', found.send, expected.send, {
      test_id: found.send?.getAttribute('data-testid') ?? null,
      aria_label: found.send?.getAttribute('aria-label') ?? null,
      disabled: found.send ? (found.send as HTMLButtonElement).disabled : null,
    }),
    anchor('generation_stop', found.stop, null, {}),
    anchor('generation_continue', found.continue, null, {}),
    anchor('latest_assistant_turn', found.latestAssistant, null, {}),
    anchor('latest_user_turn', found.latestUser, null, {}),
  ];
}

function collectOddities(controls: ProbedControl[], anchors: ProbedAnchor[], composer: ComposerState): SurfaceOddity[] {
  const oddities: SurfaceOddity[] = [];

  for (const control of controls) {
    if (!control.visible) continue;

    // An unclassified control sitting in the composer is the highest-value
    // signal this probe produces: it is exactly how a new send-adjacent button
    // (a new picker, a new mode toggle) first shows up.
    if (control.classification === 'unknown' && control.region === 'composer') {
      oddities.push({
        kind: 'unknown-control',
        severity: 'warn',
        region: 'composer',
        summary: `unclassified control in the composer: ${control.selector_hint}`,
        control,
      });
    } else if (control.classification === 'unknown' && control.region === 'dialog') {
      oddities.push({
        kind: 'dialog',
        severity: 'warn',
        region: 'dialog',
        summary: `unclassified control inside a modal dialog: ${control.selector_hint}`,
        control,
      });
    }
  }

  const dialogControls = controls.filter((control) => control.region === 'dialog' && control.visible);
  if (dialogControls.length) {
    oddities.push({
      kind: 'dialog',
      severity: 'warn',
      region: 'dialog',
      summary: `a modal dialog is open (${dialogControls.length} control(s)); it may be intercepting clicks`,
    });
  }

  const bannerControls = controls.filter((control) => control.region === 'banner' && control.visible);
  if (bannerControls.length) {
    oddities.push({
      kind: 'banner',
      severity: 'info',
      region: 'banner',
      summary: `a live/alert region is present (${bannerControls.length} control(s)); possible nag, error, or rate-limit notice`,
    });
  }

  for (const item of anchors) {
    if (!item.found) {
      // A missing send button with an EMPTY composer is ChatGPT working normally.
      if (item.name === 'send' && composer.present && composer.empty) {
        oddities.push({
          kind: 'send-hidden-empty-composer',
          severity: 'info',
          region: 'composer',
          summary: 'no send control, but the composer is empty — ChatGPT only renders send once you type. Probe with a draft for a definitive reading.',
          anchor: 'send',
        });
        continue;
      }
      const critical = item.name === 'composer' || item.name === 'send';
      oddities.push({
        kind: 'missing-anchor',
        severity: critical ? 'critical' : 'info',
        region: 'page',
        summary: `anchor not found: ${item.name}`,
        anchor: item.name,
      });
    } else if (item.expected_selector && !item.matches_expectation) {
      oddities.push({
        kind: 'unexpected-anchor-selector',
        severity: 'critical',
        region: 'page',
        summary: `anchor '${item.name}' resolved to ${item.selector_hint}, which does not match the expected selector ${item.expected_selector}`,
        anchor: item.name,
      });
    }
  }

  return oddities;
}

const FILE_INPUT_SELECTORS = [
  'form input[type="file"]',
  '[class*="composer"] input[type="file"]',
  'input[type="file"]',
];

export function findFileInputs(document: Document): HTMLInputElement[] {
  const inputs: HTMLInputElement[] = [];
  const seen = new Set<HTMLInputElement>();
  for (const selector of FILE_INPUT_SELECTORS) {
    for (const node of Array.from(document.querySelectorAll(selector))) {
      if (node instanceof HTMLInputElement && node.type === 'file' && !node.disabled && !seen.has(node)) {
        seen.add(node);
        inputs.push(node);
      }
    }
  }
  return inputs;
}

export function findFileInput(document: Document): HTMLInputElement | null {
  return findFileInputs(document)[0] ?? null;
}

export function authenticationState(document: Document): AuthenticationState {
  const visible = (selector: string): boolean => Array.from(document.querySelectorAll(selector)).some(isVisible);
  const loginControlPresent = visible('[data-testid="login-button"]');
  const signupControlPresent = visible('[data-testid="signup-button"]');
  const accountControlPresent = visible('[data-testid="accounts-profile-button"]');
  const anonymous = loginControlPresent || signupControlPresent;

  return {
    posture: anonymous ? 'anonymous' : (accountControlPresent ? 'authenticated' : 'unknown'),
    login_control_present: loginControlPresent,
    signup_control_present: signupControlPresent,
    account_control_present: accountControlPresent,
  };
}

function composerState(
  document: Document,
  composer: HTMLElement | null,
  controls: ProbedControl[],
): ComposerState {
  const fileInputs = findFileInputs(document);
  const fileInput = fileInputs[0] ?? null;
  const text = composer ? (composer.textContent || '').trim() : '';
  const inputFiles = fileInputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
  const attachmentChips = controls.filter((control) => (
    control.region === 'composer'
    && control.visible
    && control.classification === 'attachment-chip'
  )).length;
  return {
    present: Boolean(composer),
    empty: text.length === 0,
    text_length: text.length,
    file_input_present: Boolean(fileInput),
    file_input_selector: fileInput ? selectorHint(fileInput, 'file-input') : null,
    file_input_multiple: Boolean(fileInput?.multiple),
    attachment_chip_count: attachmentChips,
    attached_file_count: Math.max(inputFiles, attachmentChips),
  };
}

export interface ProbeInputs {
  url: string;
  route: { pathname: string; posture: string };
  composer: HTMLElement | null;
  send: HTMLElement | null;
  stop: HTMLElement | null;
  continueControl: HTMLElement | null;
  latestAssistant: HTMLElement | null;
  latestUser: HTMLElement | null;
  expectedComposerSelector: string;
  expectedSendSelector: string;
  generationState: string;
}

/** Visible composer controls, as diff-stable keys. Attachment witnessing combines
 * this diff with filename visibility or a known chip role; a new control alone is
 * not evidence that an upload succeeded. */
export function composerControlKeys(document: Document): string[] {
  return probeControls(document)
    .filter((control) => control.region === 'composer' && control.visible)
    .map((control) => control.key);
}

export function composerControlDelta(
  document: Document,
  keysBefore: string[],
): { added_keys: string[]; added_controls: ProbedControl[] } {
  const remaining = new Map<string, number>();
  for (const key of keysBefore) remaining.set(key, (remaining.get(key) || 0) + 1);

  const addedControls: ProbedControl[] = [];
  for (const control of probeControls(document)) {
    if (control.region !== 'composer' || !control.visible) continue;
    const prior = remaining.get(control.key) || 0;
    if (prior > 0) {
      remaining.set(control.key, prior - 1);
    } else {
      addedControls.push(control);
    }
  }
  return {
    added_keys: addedControls.map((control) => control.key),
    added_controls: addedControls,
  };
}

export function buildSurfaceProbe(document: Document, inputs: ProbeInputs): SurfaceProbeReport {
  const controls = probeControls(document);
  const composer = composerState(document, inputs.composer, controls);
  const authentication = authenticationState(document);
  const anchors = probeAnchors(
    document,
    {
      composer: inputs.composer,
      send: inputs.send,
      stop: inputs.stop,
      continue: inputs.continueControl,
      latestAssistant: inputs.latestAssistant,
      latestUser: inputs.latestUser,
    },
    { composer: inputs.expectedComposerSelector, send: inputs.expectedSendSelector },
  );
  const oddities = collectOddities(controls, anchors, composer);

  const byRole: Record<string, number> = {};
  for (const control of controls) {
    byRole[control.classification] = (byRole[control.classification] || 0) + 1;
  }

  return {
    probe_version: SURFACE_PROBE_VERSION,
    captured_at: new Date().toISOString(),
    url: inputs.url,
    route: inputs.route,
    authentication,
    composer,
    capabilities: {
      // Each of these maps 1:1 onto a GlassTTY command that breaks if it is false.
      write_prompt: Boolean(inputs.composer),
      // null when the composer is empty: ChatGPT hides send until you type, so a
      // missing send button here proves nothing either way. Claiming `false`
      // would flag a healthy page as broken (see the note on `capabilities`).
      submit_prompt: inputs.send ? true : (composer.present && composer.empty ? null : false),
      detect_generation: inputs.generationState !== 'unknown',
      read_latest_output: Boolean(inputs.latestAssistant),
      read_user_turn: Boolean(inputs.latestUser),
      continue_generation: Boolean(inputs.continueControl),
      attach_files: composer.file_input_present && authentication.posture === 'authenticated',
    },
    anchors,
    controls,
    oddities,
    counts: {
      controls: controls.length,
      visible_controls: controls.filter((control) => control.visible).length,
      unknown_controls: controls.filter((control) => control.classification === 'unknown').length,
      oddities: oddities.length,
      critical_oddities: oddities.filter((oddity) => oddity.severity === 'critical').length,
      ...byRole,
    },
  };
}

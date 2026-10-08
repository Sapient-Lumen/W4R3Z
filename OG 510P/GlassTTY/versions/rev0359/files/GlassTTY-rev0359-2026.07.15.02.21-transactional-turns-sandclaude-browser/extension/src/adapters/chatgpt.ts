import type { CandidateInfo, CandidateReport, FixtureCapture, GenerationSnapshot, LatestOutputWitness, PageAdapter, UserTurnWitness } from './base';
import { buildLiveFixtureMetadata, candidateInfo, collectLiveFrameInventory, isVisible, selectorHint, textFrom, type LiveDocumentContext } from '../content/generic';
import { authenticationState, buildSurfaceProbe, composerControlDelta, composerControlKeys, findFileInput, findFileInputs, type SurfaceProbeReport } from './surface-probe';

interface RankedNode {
  node: Element;
  context: LiveDocumentContext;
  index: number;
  score: number;
}

export type RoutePosture = 'plain-chat' | 'project-or-gpt' | 'canvas-or-artifact' | 'agent-or-tool' | 'login-or-marketing' | 'unknown';

interface RouteClassification {
  posture: RoutePosture;
  pathname: string;
  prompt_present: boolean;
  evidence: string[];
}

const PROMPT_SELECTORS = [
  '#prompt-textarea',
  '[data-testid="prompt-textarea"]',
  'textarea[placeholder*="Message" i]',
  'textarea[placeholder*="Ask" i]',
  'textarea',
  '[contenteditable="true"][role="textbox"]',
  '[contenteditable="plaintext-only"][role="textbox"]',
  '[role="textbox"]',
  'main [data-placeholder*="Message" i]',
  'main [data-placeholder*="Ask" i]',
  'main .ProseMirror[contenteditable]',
  'main [contenteditable="true"]',
  'main [contenteditable="plaintext-only"]',
  '[contenteditable="true"]',
  '[contenteditable="plaintext-only"]',
];

const OUTPUT_SELECTORS = [
  '[data-message-author-role="assistant"]',
  '[data-testid*="conversation-turn"]',
  'article',
  'main article',
  'main [class*="markdown"]',
  '.markdown',
  '[class*="assistant"]',
  '[class*="message"]',
  'main',
  '[role="main"]',
];

const USER_TURN_SELECTORS = [
  '[data-message-author-role="user"]',
  '[data-testid*="conversation-turn"]',
  'article',
  'main article',
  '[class*="user"]',
  '[class*="message"]',
];

const OBSERVED_LIVE_PROMPT_SELECTOR = '#prompt-textarea';
const OBSERVED_LIVE_SEND_SELECTOR = '#composer-submit-button';
const OBSERVED_LIVE_SEND_TESTID = 'send-button';
const OBSERVED_LIVE_SEND_ARIA_LABEL = 'Send prompt';

const SEND_BUTTON_SELECTORS = [
  '#composer-submit-button',
  'button#composer-submit-button',
  'button[data-testid="send-button"]',
  'button[aria-label*="Send" i]',
  'button[title*="Send" i]',
  'form button[type="submit"]',
  'button',
];

const SEND_BUTTON_MIN_SCORE = 0.45;

const GENERATION_STOP_TERMS = [
  'stop generating',
  'stop streaming',
  'stop response',
  'stop responding',
  'stop',
];

const GENERATION_CONTINUE_TERMS = [
  'continue generating',
  'continue response',
  'continue',
];

const NON_SEND_CONTROL_TERMS = [
  'add files',
  'add file',
  'add photos',
  'add photo',
  'add files and more',
  'composer-plus',
  'plus',
  'attach',
  'attachment',
  'upload',
  'file',
  'files',
  'voice',
  'dictate',
  'microphone',
  'audio',
  'stop',
  'cancel',
  'search',
  'tools',
  'tool',
  'deep research',
  'model',
  'picker',
  'reasoning',
  'library',
  'canvas',
  'email',
  'recipient',
  'image',
  'create image',
  'start dictation',
  'copy response',
  'copy message',
  'edit message',
  'good response',
  'bad response',
  'download apps',
  'sources',
  'extra high',
  'prompt 1',
  'prompt 2',
  'prompt 3',
  'prompt 4',
  'prompt 5',
  'prompt 6',
  'prompt 7',
  'prompt 8',
];

interface SendControlSignal {
  intent: boolean;
  explicit: boolean;
  submit: boolean;
  disqualified: boolean;
  combined: string;
}


/**
 * Runtime surface overrides.
 *
 * ChatGPT's UI moves. When it does, the honest options used to be (a) ship a new
 * extension build, or (b) be broken until you do. Neither is acceptable for a
 * tool you rely on daily.
 *
 * So the adapter consults a *runtime patch* before its compiled selectors. When
 * `surface-triage` identifies a confident repair, `surface-repair --apply` writes
 * it here and the very next `ask` works — no rebuild, no reload, no waiting on me.
 *
 * The override is a hint, not a bypass: an overridden node still has to be
 * visible and still has to pass the same send-intent scoring that rejects the
 * "Add files" decoy. A bad override degrades to the normal search; it can never
 * make GlassTTY click something it would otherwise refuse to click.
 */
export interface SurfaceOverrides {
  composer?: string;
  send?: string;
}

let surfaceOverrides: SurfaceOverrides = {};

export function setSurfaceOverrides(next: SurfaceOverrides | null | undefined): void {
  surfaceOverrides = next && typeof next === 'object' ? next : {};
}

export function getSurfaceOverrides(): SurfaceOverrides {
  return surfaceOverrides;
}

function topContext(document: Document, win: Window): LiveDocumentContext {
  return inventoryContexts(document, win)[0];
}

function overrideNode(selector: string | undefined, document: Document): HTMLElement | null {
  if (!selector) return null;
  let node: Element | null = null;
  try {
    node = document.querySelector(selector);
  } catch {
    return null; // a malformed override must never throw inside an action
  }
  if (!node || !(node instanceof HTMLElement)) return null;
  return isVisible(node) ? node : null;
}

function lower(value: string | null | undefined): string {
  return (value || '').trim().toLowerCase();
}

function includesAny(value: string, terms: string[]): boolean {
  return terms.some((term) => value.includes(term));
}

function authorRoleElement(node: Element | null): Element | null {
  return node?.closest('[data-message-author-role]') ?? null;
}

function authorRole(node: Element | null): string | null {
  return lower(authorRoleElement(node)?.getAttribute('data-message-author-role')) || null;
}

function authorRoleSource(node: Element | null): string | null {
  const roleElement = authorRoleElement(node);
  if (!roleElement) return null;
  return roleElement === node ? 'self' : 'ancestor';
}

function contentEditableMode(node: Element): string | null {
  const raw = node.getAttribute('contenteditable');
  if (raw === null) return null;
  const value = lower(raw);
  if (value === 'false') return null;
  return value || 'true';
}

function isEditableCandidate(node: Element): boolean {
  if (node instanceof HTMLTextAreaElement) return !node.disabled && !node.readOnly;
  if (node instanceof HTMLInputElement) return !node.disabled && !node.readOnly;
  return Boolean(contentEditableMode(node)) || node.getAttribute('role') === 'textbox';
}

function promptScore(node: Element): number {
  let score = isVisible(node) ? 0.45 : 0.03;
  const id = lower(node.getAttribute('id'));
  const testId = lower(node.getAttribute('data-testid'));
  const placeholder = lower(node.getAttribute('placeholder'));
  const dataPlaceholder = lower(node.getAttribute('data-placeholder'));
  const aria = lower(node.getAttribute('aria-label'));
  const role = lower(node.getAttribute('role'));
  const text = lower(textFrom(node));
  const className = lower(node.getAttribute('class'));

  if (!isEditableCandidate(node)) score -= 0.35;
  if (id === 'prompt-textarea') score += 0.35;
  if (testId.includes('prompt-textarea')) score += 0.35;
  if (node instanceof HTMLTextAreaElement) score += 0.25;
  if (role === 'textbox') score += 0.22;
  if (contentEditableMode(node)) score += 0.18;
  if (includesAny(placeholder, ['message', 'ask anything', 'chatgpt', 'prompt'])) score += 0.2;
  if (includesAny(dataPlaceholder, ['message', 'ask anything', 'chatgpt', 'prompt'])) score += 0.2;
  if (includesAny(aria, ['message', 'prompt', 'ask', 'chatgpt'])) score += 0.16;
  if (className.includes('composer') || className.includes('prompt')) score += 0.08;
  if (includesAny(id + ' ' + testId + ' ' + placeholder + ' ' + dataPlaceholder + ' ' + aria, ['search', 'filter', 'rename', 'title', 'email', 'recipient'])) score -= 0.28;
  if (text.length > 0 && text.length < 16_000) score += 0.04;
  if (text.length > 24_000) score -= 0.2;
  return score;
}

function outputScore(node: Element): number {
  const text = textFrom(node) || '';
  let score = isVisible(node) ? 0.35 : 0.04;
  const className = lower(node.getAttribute('class'));
  const dataTestId = lower(node.getAttribute('data-testid'));
  const role = lower(node.getAttribute('role'));
  const roleForTurn = authorRole(node);

  if (roleForTurn === 'assistant') score += 0.55;
  if (roleForTurn === 'user') score -= 0.55;
  if (dataTestId.includes('conversation-turn')) score += 0.18;
  if (node.tagName === 'ARTICLE') score += 0.16;
  if (className.includes('markdown')) score += 0.14;
  if (className.includes('assistant')) score += 0.18;
  if (className.includes('message')) score += 0.08;
  if (role === 'main') score -= 0.08;
  if (text.length > 30) score += 0.12;
  if (text.length > 250) score += 0.1;
  if (text.length > 5000) score -= 0.08;
  if (text.length > 20_000) score -= 0.25;
  return score;
}


function sendControlSignal(button: HTMLButtonElement): SendControlSignal {
  const text = lower(button.textContent);
  const aria = lower(button.getAttribute('aria-label'));
  const title = lower(button.getAttribute('title'));
  const testId = lower(button.getAttribute('data-testid'));
  const id = lower(button.getAttribute('id'));
  const type = lower(button.getAttribute('type'));
  const combined = `${text} ${aria} ${title} ${id} ${testId}`;
  const explicitSendIntent = testId === 'send-button'
    || testId.includes('send-button')
    || testId.includes('send-message')
    || id === 'composer-submit-button'
    || id === 'send-button'
    || aria === 'send'
    || aria.includes('send message')
    || aria.includes('send prompt')
    || title === 'send'
    || title.includes('send message')
    || text === 'send';
  const formSubmitIntent = type === 'submit';
  const nonSendControl = includesAny(combined, NON_SEND_CONTROL_TERMS);
  const exactPlusControl = id === 'composer-plus-btn'
    || testId === 'composer-plus-btn';
  return {
    intent: explicitSendIntent || formSubmitIntent,
    explicit: explicitSendIntent,
    submit: formSubmitIntent,
    disqualified: exactPlusControl || (nonSendControl && !explicitSendIntent),
    combined,
  };
}

function userTurnScore(node: Element): number {
  const text = textFrom(node) || '';
  let score = isVisible(node) ? 0.34 : 0.03;
  const className = lower(node.getAttribute('class'));
  const dataTestId = lower(node.getAttribute('data-testid'));
  const role = lower(node.getAttribute('role'));
  const roleForTurn = authorRole(node);

  if (roleForTurn === 'user') score += 0.55;
  if (roleForTurn === 'assistant') score -= 0.55;
  if (dataTestId.includes('conversation-turn')) score += 0.16;
  if (node.tagName === 'ARTICLE') score += 0.12;
  if (className.includes('user')) score += 0.18;
  if (className.includes('message')) score += 0.06;
  if (roleForTurn === 'assistant' || className.includes('assistant')) score -= 0.45;
  if (role === 'main') score -= 0.12;
  if (node.matches('textarea, input, [contenteditable="true"], [role="textbox"]')) score -= 0.8;
  if (node.closest('form, [data-testid*="composer"], [class*="composer"]')) score -= 0.5;
  if (text.length > 12) score += 0.08;
  if (text.length > 5000) score -= 0.16;
  return score;
}

function sendButtonScore(button: HTMLButtonElement, composer: Element | null = null): number {
  let score = isVisible(button) ? 0.3 : 0.02;
  const text = lower(button.textContent);
  const aria = lower(button.getAttribute('aria-label'));
  const title = lower(button.getAttribute('title'));
  const testId = lower(button.getAttribute('data-testid'));
  const type = lower(button.getAttribute('type'));
  const disabled = button.disabled || button.getAttribute('aria-disabled') === 'true';
  const signal = sendControlSignal(button);

  if (disabled) score -= 0.8;
  if (!signal.intent) score -= 0.35;
  if (signal.disqualified) score -= 1.0;
  if (testId === 'send-button' || testId.includes('send')) score += 0.5;
  if (aria === 'send' || aria.includes('send message') || aria.includes('send prompt')) score += 0.45;
  if (title === 'send' || title.includes('send message')) score += 0.32;
  if (text === 'send') score += 0.3;
  if (type === 'submit') score += 0.18;
  if (composer) {
    const sameForm = button.form
      && (composer instanceof HTMLInputElement || composer instanceof HTMLTextAreaElement
        ? composer.form === button.form
        : Boolean(composer.closest('form') && composer.closest('form') === button.form));
    const composerRoot = findComposerActionRoot(composer, button.ownerDocument);
    if (sameForm) score += 0.2;
    if (composerRoot !== button.ownerDocument && composerRoot.contains(button)) score += 0.16;
    const buttonDialog = button.closest('dialog, [role="dialog"], [role="alertdialog"]');
    const composerDialog = composer.closest('dialog, [role="dialog"], [role="alertdialog"]');
    if (buttonDialog && buttonDialog !== composerDialog) score -= 0.35;
  } else {
    score -= 0.12;
  }
  if (button.closest('nav, header, aside')) score -= 0.18;
  return score;
}

function routePostureAllowsSubmit(posture: RoutePosture): boolean {
  return posture === 'plain-chat';
}

function findComposerActionRoot(composer: Element | null, document: Document): Element | Document {
  if (!composer) return document;
  return composer.closest('form, [data-testid*="composer"], [class*="composer"], [role="form"]') || composer.parentElement || document;
}

function inventoryContexts(document: Document, win: Window): LiveDocumentContext[] {
  return collectLiveFrameInventory(document, win).contexts;
}

function rank(selectors: string[], document: Document, scorer: (node: Element) => number, win: Window): RankedNode[] {
  const seen = new Set<Element>();
  const ranked: RankedNode[] = [];
  for (const context of inventoryContexts(document, win)) {
    let index = 0;
    for (const selector of selectors) {
      for (const node of Array.from(context.document.querySelectorAll(selector))) {
        if (seen.has(node)) continue;
        seen.add(node);
        ranked.push({ node, context, index, score: scorer(node) });
        index += 1;
      }
    }
  }
  return ranked.sort((left, right) => (right.score - left.score) || (left.context.depth - right.context.depth) || (right.index - left.index));
}

function bestVisibleElement(selectors: string[], document: Document, scorer: (node: Element) => number, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null } {
  const best = rank(selectors, document, scorer, win).find(({ node, score }) => score > 0.35 && node instanceof HTMLElement);
  return {
    node: best?.node instanceof HTMLElement ? best.node : null,
    context: best?.context ?? null,
  };
}

function findPromptComposer(document: Document, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null } {
  const overridden = overrideNode(surfaceOverrides.composer, document);
  if (overridden && isEditableCandidate(overridden)) {
    return { node: overridden, context: topContext(document, win) };
  }
  return bestVisibleElement(PROMPT_SELECTORS, document, promptScore, win);
}


function documentOrderIndex(node: Element | null): number | undefined {
  if (!node) return undefined;
  const nodes = Array.from(node.ownerDocument.querySelectorAll('*'));
  const index = nodes.indexOf(node);
  return index >= 0 ? index : undefined;
}

function outputDocumentOrder(left: RankedNode, right: RankedNode): number {
  if (left.node.ownerDocument !== right.node.ownerDocument) {
    return (left.context.depth - right.context.depth) || (left.index - right.index);
  }
  if (left.node === right.node) return 0;
  const position = left.node.compareDocumentPosition(right.node);
  if (position & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
  if (position & Node.DOCUMENT_POSITION_PRECEDING) return 1;
  return left.index - right.index;
}

function isAssistantOutputCandidate(node: Element): boolean {
  const roleForTurn = authorRole(node);
  if (roleForTurn) return roleForTurn === 'assistant';
  const className = lower(node.getAttribute('class'));
  const dataTestId = lower(node.getAttribute('data-testid'));
  return className.includes('assistant') || dataTestId.includes('assistant') || node.tagName === 'ARTICLE';
}

function isUserTurnCandidate(node: Element): boolean {
  const roleForTurn = authorRole(node);
  if (roleForTurn) return roleForTurn === 'user';
  const className = lower(node.getAttribute('class'));
  const dataTestId = lower(node.getAttribute('data-testid'));
  return className.includes('user') || dataTestId.includes('user') || node.tagName === 'ARTICLE';
}

function latestOutputMatch(document: Document, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null; score: number; assistant_like: boolean } {
  const candidates = rank(OUTPUT_SELECTORS, document, outputScore, win)
    .filter(({ node, score }) => score > 0.35 && Boolean(textFrom(node)) && node instanceof HTMLElement);
  const assistantLike = candidates.filter(({ node }) => isAssistantOutputCandidate(node));
  const ordered = (assistantLike.length ? assistantLike : candidates).slice().sort(outputDocumentOrder);
  const best = ordered[ordered.length - 1];
  return {
    node: best?.node instanceof HTMLElement ? best.node : null,
    context: best?.context ?? null,
    score: best?.score ?? 0,
    assistant_like: Boolean(best && isAssistantOutputCandidate(best.node)),
  };
}

function findLatestOutputNode(document: Document, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null } {
  const match = latestOutputMatch(document, win);
  return { node: match.node, context: match.context };
}

function latestOutputWitness(document: Document, win: Window): LatestOutputWitness {
  const match = latestOutputMatch(document, win);
  const node = match.node;
  const context = match.context;
  const roleForTurn = authorRole(node);
  return {
    text: textFrom(node),
    selector_hint: node ? selectorHint(node, 'output') : null,
    selection_policy: 'latest-visible-assistant-like-node-in-dom-order',
    assistant_like: match.assistant_like || roleForTurn === 'assistant',
    author_role: roleForTurn,
    author_role_source: authorRoleSource(node),
    node_tag: node ? node.tagName.toLowerCase() : null,
    candidate_score: Number(match.score.toFixed(3)),
    ...(typeof documentOrderIndex(node) === 'number' ? { document_order_index: documentOrderIndex(node) } : {}),
    ...(typeof context?.depth === 'number' ? { frame_depth: context.depth } : {}),
    ...(context?.frame_path ? { frame_path: context.frame_path } : {}),
  };
}

function latestUserTurnMatch(document: Document, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null; score: number; user_like: boolean } {
  const candidates = rank(USER_TURN_SELECTORS, document, userTurnScore, win)
    .filter(({ node, score }) => score > 0.35 && Boolean(textFrom(node)) && node instanceof HTMLElement);
  const userLike = candidates.filter(({ node }) => isUserTurnCandidate(node));
  const ordered = (userLike.length ? userLike : candidates).slice().sort(outputDocumentOrder);
  const best = ordered[ordered.length - 1];
  return {
    node: best?.node instanceof HTMLElement ? best.node : null,
    context: best?.context ?? null,
    score: best?.score ?? 0,
    user_like: Boolean(best && isUserTurnCandidate(best.node)),
  };
}

function latestUserTurnWitness(document: Document, win: Window): UserTurnWitness {
  const match = latestUserTurnMatch(document, win);
  const node = match.node;
  const context = match.context;
  const roleForTurn = authorRole(node);
  return {
    text: textFrom(node),
    selector_hint: node ? selectorHint(node, 'user-turn') : null,
    selection_policy: 'latest-visible-user-like-node-in-dom-order',
    user_like: match.user_like || roleForTurn === 'user',
    author_role: roleForTurn,
    author_role_source: authorRoleSource(node),
    node_tag: node ? node.tagName.toLowerCase() : null,
    candidate_score: Number(match.score.toFixed(3)),
    ...(typeof documentOrderIndex(node) === 'number' ? { document_order_index: documentOrderIndex(node) } : {}),
    ...(typeof context?.depth === 'number' ? { frame_depth: context.depth } : {}),
    ...(context?.frame_path ? { frame_path: context.frame_path } : {}),
  };
}

function findLikelySendButton(document: Document, win: Window, composer: Element | null = null): { node: HTMLButtonElement | null; context: LiveDocumentContext | null; score: number; scope: Element | Document | null; signal: SendControlSignal | null } {
  const overridden = overrideNode(surfaceOverrides.send, document);
  if (overridden instanceof HTMLButtonElement) {
    const signal = sendControlSignal(overridden);
    // The override says "look here" — it does NOT say "click anything". A node
    // that trips the non-send disqualifiers (the "Add files" decoy) is still
    // rejected, and we fall through to the normal search.
    if (!signal.disqualified) {
      return { node: overridden, context: topContext(document, win), score: sendButtonScore(overridden, composer), scope: document, signal };
    }
  }
  const seen = new Set<Element>();
  const ranked: Array<{ button: HTMLButtonElement; context: LiveDocumentContext; index: number; score: number; scope: Element | Document | null }> = [];
  for (const context of inventoryContexts(document, win)) {
    let index = 0;
    const contextComposer = composer && composer.ownerDocument === context.document ? composer : null;
    const scopedRoot = findComposerActionRoot(contextComposer, context.document);
    const scopes: Array<Element | Document> = scopedRoot === context.document ? [context.document] : [scopedRoot, context.document];
    for (const scope of scopes) {
      for (const selector of SEND_BUTTON_SELECTORS) {
        for (const node of Array.from(scope.querySelectorAll(selector))) {
          if (seen.has(node) || !(node instanceof HTMLButtonElement)) continue;
          seen.add(node);
          ranked.push({ button: node, context, index, score: sendButtonScore(node, contextComposer), scope });
          index += 1;
        }
      }
    }
  }
  const best = ranked
    .filter(({ button, score }) => {
      const signal = sendControlSignal(button);
      return score > SEND_BUTTON_MIN_SCORE
        && signal.intent
        && !signal.disqualified
        && !button.disabled
        && button.getAttribute('aria-disabled') !== 'true';
    })
    .sort((left, right) => (right.score - left.score)
      || (left.context.depth - right.context.depth)
      || (right.index - left.index))[0];
  return {
    node: best?.button ?? null,
    context: best?.context ?? null,
    score: best?.score ?? 0,
    scope: best?.scope ?? null,
    signal: best?.button ? sendControlSignal(best.button) : null,
  };
}

function findBlockedComposerControl(document: Document, win: Window, composer: Element | null = null): { node: HTMLButtonElement | null; context: LiveDocumentContext | null; score: number; signal: SendControlSignal | null } {
  const ranked: Array<{ button: HTMLButtonElement; context: LiveDocumentContext; index: number; score: number; signal: SendControlSignal }> = [];
  for (const context of inventoryContexts(document, win)) {
    let index = 0;
    const contextComposer = composer && composer.ownerDocument === context.document ? composer : null;
    const scopedRoot = findComposerActionRoot(contextComposer, context.document);
    const scopes: Array<Element | Document> = scopedRoot === context.document ? [context.document] : [scopedRoot, context.document];
    for (const scope of scopes) {
      for (const node of Array.from(scope.querySelectorAll('button'))) {
        if (!(node instanceof HTMLButtonElement)) continue;
        const signal = sendControlSignal(node);
        if (!signal.disqualified) continue;
        ranked.push({ button: node, context, index, score: sendButtonScore(node, contextComposer), signal });
        index += 1;
      }
    }
  }
  const best = ranked.sort((left, right) => (right.score - left.score)
    || (left.context.depth - right.context.depth)
    || (right.index - left.index))[0];
  return {
    node: best?.button ?? null,
    context: best?.context ?? null,
    score: best?.score ?? 0,
    signal: best?.signal ?? null,
  };
}

function generationControlScore(button: HTMLButtonElement, terms: string[]): number {
  if (!isVisible(button) || button.disabled || button.getAttribute('aria-disabled') === 'true') return 0;
  const text = lower(button.textContent);
  const aria = lower(button.getAttribute('aria-label'));
  const title = lower(button.getAttribute('title'));
  const testId = lower(button.getAttribute('data-testid'));
  const combined = `${text} ${aria} ${title} ${testId}`;
  if (!includesAny(combined, terms)) return 0;
  let score = 0.45;
  if (includesAny(aria, terms) || includesAny(title, terms)) score += 0.22;
  if (includesAny(testId, terms.map((term) => term.replace(/\s+/g, '-')))) score += 0.12;
  if (button.closest('main, [role="main"]')) score += 0.08;
  if (button.closest('nav, header, aside')) score -= 0.2;
  return score;
}

function findGenerationControl(document: Document, win: Window, terms: string[]): { node: HTMLButtonElement | null; context: LiveDocumentContext | null; score: number } {
  const ranked: Array<{ button: HTMLButtonElement; context: LiveDocumentContext; index: number; score: number }> = [];
  for (const context of inventoryContexts(document, win)) {
    let index = 0;
    for (const button of Array.from(context.document.querySelectorAll('button'))) {
      if (!(button instanceof HTMLButtonElement)) continue;
      const score = generationControlScore(button, terms);
      if (score <= 0.35) continue;
      ranked.push({ button, context, index, score });
      index += 1;
    }
  }
  const best = ranked.sort((left, right) => (right.score - left.score) || (left.context.depth - right.context.depth) || (right.index - left.index))[0];
  return { node: best?.button ?? null, context: best?.context ?? null, score: best?.score ?? 0 };
}

function generationState(document: Document, win: Window): {
  state: 'streaming-or-stoppable' | 'needs-continue' | 'settled-or-idle';
  stop: { node: HTMLButtonElement | null; context: LiveDocumentContext | null; score: number };
  continue: { node: HTMLButtonElement | null; context: LiveDocumentContext | null; score: number };
} {
  const stop = findGenerationControl(document, win, GENERATION_STOP_TERMS);
  const continueControl = findGenerationControl(document, win, GENERATION_CONTINUE_TERMS);
  if (stop.node) return { state: 'streaming-or-stoppable', stop, continue: continueControl };
  if (continueControl.node) return { state: 'needs-continue', stop, continue: continueControl };
  return { state: 'settled-or-idle', stop, continue: continueControl };
}

function setNativeValue(node: HTMLInputElement | HTMLTextAreaElement, text: string): void {
  const prototype = Object.getPrototypeOf(node) as HTMLInputElement | HTMLTextAreaElement;
  const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
  if (descriptor?.set) {
    descriptor.set.call(node, text);
  } else {
    node.value = text;
  }
}

function dispatchEditableEvents(node: Element, text: string): void {
  node.dispatchEvent(new InputEvent('beforeinput', { bubbles: true, cancelable: true, data: text, inputType: 'insertText' }));
  node.dispatchEvent(new InputEvent('input', { bubbles: true, data: text, inputType: 'insertText' }));
  node.dispatchEvent(new Event('change', { bubbles: true }));
}

function readbackMatches(node: Element, expected: string): boolean {
  const actual = (textFrom(node) || '').replace(/\s+/g, ' ').trim();
  const target = expected.replace(/\s+/g, ' ').trim();
  return actual === target;
}

function writeIntoElement(node: HTMLElement, text: string): boolean {
  node.focus();

  if (node instanceof HTMLTextAreaElement || node instanceof HTMLInputElement) {
    setNativeValue(node, text);
    dispatchEditableEvents(node, text);
    return readbackMatches(node, text);
  }

  if (contentEditableMode(node) || node.getAttribute('role') === 'textbox') {
    const doc = node.ownerDocument;
    const selection = doc.getSelection();
    if (selection) {
      const range = doc.createRange();
      range.selectNodeContents(node);
      selection.removeAllRanges();
      selection.addRange(range);
    }
    let inserted = false;
    try {
      inserted = doc.execCommand('insertText', false, text);
    } catch {
      inserted = false;
    }
    if (!inserted) {
      node.textContent = text;
    }
    dispatchEditableEvents(node, text);
    return readbackMatches(node, text);
  }

  return false;
}

function sanitizeHtml(node: Element | null): string | null {
  if (!node) return null;
  const clone = node.cloneNode(true) as Element;
  clone.querySelectorAll('img, svg, button, input, textarea, script, style, video, canvas').forEach((child) => child.remove());
  clone.querySelectorAll('*').forEach((el) => {
    for (const attr of Array.from(el.attributes)) {
      if (!['class', 'role', 'data-testid', 'aria-label', 'placeholder', 'data-placeholder', 'data-message-author-role'].includes(attr.name)) {
        el.removeAttribute(attr.name);
      }
    }
  });
  return (clone.outerHTML || '').replace(/\s+/g, ' ').slice(0, 3000);
}

function compactVisibleText(nodes: Element[], limit = 2400): string {
  return nodes
    .filter((node) => isVisible(node))
    .map((node) => textFrom(node) || '')
    .join(' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, limit)
    .toLowerCase();
}

function activeShellText(document: Document): string {
  return compactVisibleText(Array.from(document.querySelectorAll([
    'dialog[open]',
    '[role="dialog"]',
    '[role="alertdialog"]',
    '[aria-modal="true"]',
    'main [aria-current="page"]',
    'main [aria-selected="true"]',
    'main [aria-pressed="true"]',
    'main [data-state="active"]',
    '[data-testid*="composer"] [aria-pressed="true"]',
    '[data-testid*="tools"] [aria-pressed="true"]',
  ].join(','))));
}

function classifyRouteDetails(url: string, document: Document, win: Window): RouteClassification {
  let pathname = '/';
  try {
    pathname = new URL(url).pathname.toLowerCase();
  } catch {
    pathname = '/';
  }

  const promptPresent = Boolean(findPromptComposer(document, win).node);
  const evidence: string[] = [`path:${pathname}`, promptPresent ? 'composer:present' : 'composer:missing'];
  const shellText = activeShellText(document);

  if (includesAny(pathname, ['/auth/', '/login']) || (!promptPresent && includesAny(shellText, ['log in', 'sign up', 'stay logged out']))) {
    evidence.push('auth-or-marketing-signal');
    return { posture: 'login-or-marketing', pathname, prompt_present: promptPresent, evidence };
  }

  if (pathname === '/' || pathname.startsWith('/c/')) {
    if (promptPresent) {
      evidence.push('plain-chat-path-and-composer');
      return { posture: 'plain-chat', pathname, prompt_present: promptPresent, evidence };
    }
  }

  if (includesAny(pathname, ['/agent', '/tasks', '/task/'])) {
    evidence.push('agent-or-task-path');
    return { posture: 'agent-or-tool', pathname, prompt_present: promptPresent, evidence };
  }
  if (includesAny(pathname, ['/canvas', '/artifact'])) {
    evidence.push('canvas-or-artifact-path');
    return { posture: 'canvas-or-artifact', pathname, prompt_present: promptPresent, evidence };
  }
  if (includesAny(pathname, ['/g/', '/gpts', '/project', '/projects'])) {
    evidence.push('project-or-gpt-path');
    return { posture: 'project-or-gpt', pathname, prompt_present: promptPresent, evidence };
  }

  if (includesAny(shellText, ['agent mode', 'take over', 'browser task'])) {
    evidence.push('active-agent-shell-signal');
    return { posture: 'agent-or-tool', pathname, prompt_present: promptPresent, evidence };
  }
  if (includesAny(shellText, ['canvas', 'artifact'])) {
    evidence.push('active-canvas-shell-signal');
    return { posture: 'canvas-or-artifact', pathname, prompt_present: promptPresent, evidence };
  }
  if (includesAny(shellText, ['gpt builder', 'custom gpt', 'project settings'])) {
    evidence.push('active-project-shell-signal');
    return { posture: 'project-or-gpt', pathname, prompt_present: promptPresent, evidence };
  }

  if (promptPresent) {
    evidence.push('composer-present-no-blocking-route-signal');
    return { posture: 'plain-chat', pathname, prompt_present: promptPresent, evidence };
  }

  evidence.push('no-supported-route-signal');
  return { posture: 'unknown', pathname, prompt_present: promptPresent, evidence };
}

function classifyRoute(url: string, document: Document, win: Window): RoutePosture {
  return classifyRouteDetails(url, document, win).posture;
}

function matchChatGptDocument(url: string, document: Document): boolean {
  try {
    const parsed = new URL(url);
    if (parsed.hostname !== 'chatgpt.com' && !parsed.hostname.endsWith('.chatgpt.com')) return false;
  } catch {
    return false;
  }
  return Boolean(document);
}

export const chatgptAdapter: PageAdapter = {
  name: 'chatgpt',
  origin_patterns: ['https://chatgpt.com/'],
  capabilities: {
    read_prompt: true,
    write_prompt: true,
    submit_prompt: true,
    read_latest_output: true,
    read_selection: true,
    debug_candidates: true,
    fixture_capture: true,
    generation_state: true,
    continue_generation: true,
    surface_probe: true,
    attach_files: true,
  },

  matches(url: string, document: Document): boolean {
    return matchChatGptDocument(url, document);
  },

  readPrompt(document: Document): string | null {
    return textFrom(findPromptComposer(document, window).node);
  },

  writePrompt(document: Document, text: string): boolean {
    const node = findPromptComposer(document, window).node;
    if (!node) return false;
    return writeIntoElement(node, text);
  },

  readLatestOutput(document: Document): string | null {
    return latestOutputWitness(document, window).text;
  },

  readLatestOutputWitness(document: Document): LatestOutputWitness {
    return latestOutputWitness(document, window);
  },

  readLatestUserTurnWitness(document: Document): UserTurnWitness {
    return latestUserTurnWitness(document, window);
  },

  readSelection(window: Window): string | null {
    return window.getSelection()?.toString().trim() || null;
  },

  debugCandidates(document: Document): CandidateReport {
    const inputs: CandidateInfo[] = rank(PROMPT_SELECTORS, document, promptScore, window)
      .slice(0, 16)
      .map(({ node, context }) => candidateInfo(node, promptScore(node), 'prompt', context.window))
      .sort((a, b) => b.score - a.score);

    const outputs: CandidateInfo[] = rank(OUTPUT_SELECTORS, document, outputScore, window)
      .slice(0, 16)
      .map(({ node, context }) => candidateInfo(node, outputScore(node), 'output', context.window))
      .sort((a, b) => b.score - a.score);

    return { inputs, outputs };
  },

  captureFixture(document: Document, window: Window): FixtureCapture {
    const inventory = collectLiveFrameInventory(document, window);
    const promptMatch = findPromptComposer(document, window);
    const outputWitness = latestOutputWitness(document, window);
    const userTurnWitness = latestUserTurnWitness(document, window);
    const outputMatch = latestOutputMatch(document, window);
    const submitMatch = findLikelySendButton(document, window, promptMatch.node);
    const blockedControl = findBlockedComposerControl(document, window, promptMatch.node);
    const debug = this.debugCandidates(document);
    const route = classifyRouteDetails(window.location.href, document, window);
    const generation = generationState(document, window);
    const submitCandidate = submitMatch.node && submitMatch.context ? candidateInfo(submitMatch.node, submitMatch.score || 1, 'button', submitMatch.context.window) : null;
    const blockedCandidate = blockedControl.node && blockedControl.context ? candidateInfo(blockedControl.node, blockedControl.score || 1, 'blocked-composer-control', blockedControl.context.window) : null;
    const stopCandidate = generation.stop.node && generation.stop.context ? candidateInfo(generation.stop.node, generation.stop.score || 1, 'generation-stop', generation.stop.context.window) : null;
    const continueCandidate = generation.continue.node && generation.continue.context ? candidateInfo(generation.continue.node, generation.continue.score || 1, 'generation-continue', generation.continue.context.window) : null;
    return {
      adapter: 'chatgpt',
      url: window.location.href,
      title: document.title,
      prompt: this.readPrompt(document),
      latest_output: outputWitness.text,
      latest_output_witness: outputWitness,
      latest_user_turn_witness: userTurnWitness,
      selection: this.readSelection(window),
      candidates: debug,
      html_samples: {
        prompt: sanitizeHtml(promptMatch.node),
        latest_output: sanitizeHtml(outputMatch.node),
        submit: sanitizeHtml(submitMatch.node),
      },
      metadata: {
        surface_route: route.pathname,
        route_posture: route.posture,
        route_evidence: route.evidence,
        route_prompt_present: route.prompt_present,
        prompt_selector: promptMatch.node ? selectorHint(promptMatch.node, 'prompt') : null,
        latest_output_selector: outputWitness.selector_hint,
        latest_output_order_policy: outputWitness.selection_policy,
        latest_output_assistant_like: outputWitness.assistant_like,
        latest_output_author_role: outputWitness.author_role,
        latest_output_author_role_source: outputWitness.author_role_source,
        latest_output_candidate_score: outputWitness.candidate_score,
        latest_output_document_order_index: outputWitness.document_order_index,
        latest_user_turn_selector: userTurnWitness.selector_hint,
        latest_user_turn_order_policy: userTurnWitness.selection_policy,
        latest_user_turn_user_like: userTurnWitness.user_like,
        latest_user_turn_author_role: userTurnWitness.author_role,
        latest_user_turn_author_role_source: userTurnWitness.author_role_source,
        latest_user_turn_candidate_score: userTurnWitness.candidate_score,
        latest_user_turn_document_order_index: userTurnWitness.document_order_index,
        latest_turn_pair_same_frame: Boolean(outputWitness.frame_path && userTurnWitness.frame_path && outputWitness.frame_path === userTurnWitness.frame_path),
        latest_turn_pair_user_before_assistant: typeof userTurnWitness.document_order_index === 'number' && typeof outputWitness.document_order_index === 'number' ? userTurnWitness.document_order_index < outputWitness.document_order_index : false,
        generation_state: generation.state,
        generation_stop_control_present: Boolean(generation.stop.node),
        generation_continue_control_present: Boolean(generation.continue.node),
        generation_stop_selector: generation.stop.node ? selectorHint(generation.stop.node, 'generation-stop') : null,
        generation_continue_selector: generation.continue.node ? selectorHint(generation.continue.node, 'generation-continue') : null,
        generation_stop_score: generation.stop.score,
        generation_continue_score: generation.continue.score,
        submit_selector: submitMatch.node ? selectorHint(submitMatch.node, 'button') : null,
        submit_score: submitMatch.score,
        submit_signal_intent: submitMatch.signal?.intent ?? false,
        submit_signal_explicit: submitMatch.signal?.explicit ?? false,
        submit_signal_submit_type: submitMatch.signal?.submit ?? false,
        submit_signal_disqualified: submitMatch.signal?.disqualified ?? false,
        observed_live_send_selector: OBSERVED_LIVE_SEND_SELECTOR,
        observed_live_send_testid: OBSERVED_LIVE_SEND_TESTID,
        observed_live_send_aria_label: OBSERVED_LIVE_SEND_ARIA_LABEL,
        submit_expected_live_selector: OBSERVED_LIVE_SEND_SELECTOR,
        blocked_composer_control_selector: blockedControl.node ? selectorHint(blockedControl.node, 'blocked-composer-control') : null,
        blocked_composer_control_score: blockedControl.score,
        blocked_composer_control_disqualified: blockedControl.signal?.disqualified ?? false,
        submit_scope_selector: submitMatch.scope && submitMatch.scope !== document && submitMatch.scope instanceof Element ? selectorHint(submitMatch.scope, 'submit-scope') : null,
        action_policy: {
          submit_method: 'button-click-only',
          keyboard_submit_enabled: false,
          route_posture_allows_submit: routePostureAllowsSubmit(route.posture),
          prompt_present_for_submit: Boolean(this.readPrompt(document)),
          submit_button_found: Boolean(submitMatch.node),
          submit_button_min_score: SEND_BUTTON_MIN_SCORE,
          submit_button_requires_explicit_send_intent: true,
          submit_button_rejects_non_send_composer_controls: true,
          observed_live_send_selector: OBSERVED_LIVE_SEND_SELECTOR,
          observed_live_send_testid: OBSERVED_LIVE_SEND_TESTID,
          observed_live_send_aria_label: OBSERVED_LIVE_SEND_ARIA_LABEL,
          submit_button_live_surface_lock: '#composer-submit-button[data-testid=send-button]',
          blocked_composer_plus_control_present: Boolean(blockedControl.node),
          empty_composer_missing_send_is_allowed: true,
        },
        ...buildLiveFixtureMetadata(document, promptMatch.node, submitMatch.node, debug.inputs[0] ?? null, submitCandidate, {
          inventory,
          inputCandidates: debug.inputs,
          outputCandidates: debug.outputs,
          submitCandidates: [submitCandidate, blockedCandidate, stopCandidate, continueCandidate].filter((candidate): candidate is CandidateInfo => Boolean(candidate)),
        }),
      },
    };
  },

  submitPrompt(document: Document): boolean {
    const route = classifyRouteDetails(window.location.href, document, window);
    if (!routePostureAllowsSubmit(route.posture)) return false;
    const composer = findPromptComposer(document, window).node;
    if (!composer || !this.readPrompt(document)) return false;
    const sendish = findLikelySendButton(document, window, composer).node;
    if (!sendish) return false;
    composer.focus();
    sendish.click();
    return true;
  },

  generationSnapshot(document: Document, win: Window): GenerationSnapshot {
    const generation = generationState(document, win);
    return {
      state: generation.state,
      stop_present: Boolean(generation.stop.node),
      continue_present: Boolean(generation.continue.node),
      stop_selector: generation.stop.node ? selectorHint(generation.stop.node, 'generation-stop') : null,
      continue_selector: generation.continue.node ? selectorHint(generation.continue.node, 'generation-continue') : null,
    };
  },

  continueGeneration(document: Document, win: Window): boolean {
    const control = findGenerationControl(document, win, GENERATION_CONTINUE_TERMS);
    if (!control.node) return false;
    control.node.click();
    return true;
  },

  attachmentReadiness(document: Document): {
    ok: boolean;
    error?: string;
    input_selector?: string | null;
    authentication?: string;
  } {
    const authentication = authenticationState(document);
    if (authentication.posture !== 'authenticated') {
      return {
        ok: false,
        error: authentication.posture === 'anonymous'
          ? 'ChatGPT is logged out; file attachment requires an authenticated browser session'
          : 'ChatGPT authentication could not be verified; refusing to transfer a file',
        authentication: authentication.posture,
      };
    }
    const input = findFileInput(document);
    if (!input) {
      return {
        ok: false,
        error: 'no <input type="file"> found in the page',
        authentication: authentication.posture,
      };
    }
    return {
      ok: true,
      input_selector: selectorHint(input, 'file-input'),
      authentication: authentication.posture,
    };
  },

  /**
   * Put files into the composer.
   *
   * We do NOT click "Add files and more" and drive a native file picker — a page
   * cannot script an OS dialog, and trying is how automation projects end up
   * shipping fragile robot-mouse code. Instead we write straight into the hidden
   * <input type="file"> with a synthetic DataTransfer, which is exactly what the
   * drop handler does.
   */
  attachFiles(document: Document, files: Array<{ name: string; mime: string; bytes: Uint8Array }>): {
    ok: boolean;
    error?: string;
    input_selector?: string | null;
    files_before: number;
    files_after: number;
  } {
    const readiness = this.attachmentReadiness?.(document);
    if (!readiness?.ok) {
      return {
        ok: false,
        error: readiness?.error || 'file attachment is not available',
        files_before: 0,
        files_after: 0,
      };
    }
    const input = findFileInput(document);
    if (!input) {
      return { ok: false, error: 'no <input type="file"> found in the page', files_before: 0, files_after: 0 };
    }
    const filesBefore = input.files?.length ?? 0;

    try {
      const transfer = new DataTransfer();
      // Preserve anything already attached: a second --attach must add, not replace.
      for (const existing of Array.from(input.files ?? [])) transfer.items.add(existing);
      for (const file of files) {
        if (!file.bytes || file.bytes.byteLength === 0) {
          // The 0-byte trap. An empty File object is truthy and attaches happily;
          // ChatGPT then receives an empty archive and the whole run is poisoned
          // downstream in a way that looks like a model failure. Refuse it here.
          return { ok: false, error: `refusing to attach zero-byte file: ${file.name}`, files_before: filesBefore, files_after: filesBefore };
        }
        const blob = new Blob([file.bytes as unknown as BlobPart], { type: file.mime || 'application/octet-stream' });
        transfer.items.add(new File([blob], file.name, { type: file.mime || 'application/octet-stream' }));
      }

      input.files = transfer.files;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    } catch (error) {
      return {
        ok: false,
        error: `could not populate file input: ${error instanceof Error ? error.message : String(error)}`,
        files_before: filesBefore,
        files_after: input.files?.length ?? 0,
      };
    }

    return {
      ok: true,
      input_selector: selectorHint(input, 'file-input'),
      files_before: filesBefore,
      files_after: input.files?.length ?? 0,
    };
  },

  clearAttachments(document: Document): {
    ok: boolean;
    error?: string;
    inputs_seen: number;
    files_before: number;
    files_after: number;
  } {
    const inputs = findFileInputs(document);
    if (!inputs.length) {
      return {
        ok: false,
        error: 'no <input type="file"> found in the page',
        inputs_seen: 0,
        files_before: 0,
        files_after: 0,
      };
    }

    const filesBefore = inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
    try {
      for (const input of inputs) {
        input.files = new DataTransfer().files;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    } catch (error) {
      return {
        ok: false,
        error: `could not clear file input: ${error instanceof Error ? error.message : String(error)}`,
        inputs_seen: inputs.length,
        files_before: filesBefore,
        files_after: inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0),
      };
    }
    const filesAfter = inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
    return {
      ok: filesAfter === 0,
      inputs_seen: inputs.length,
      files_before: filesBefore,
      files_after: filesAfter,
    };
  },

  composerKeys(document: Document): string[] {
    return composerControlKeys(document);
  },

  attachmentWitness(
    document: Document,
    keysBefore: string[],
    expectedName = '',
    expectedNameVisibleBefore = false,
  ): {
    input_files: number;
    added_keys: string[];
    added_controls: unknown[];
    known_chip_keys: string[];
    expected_name_visible: boolean;
    expected_name_newly_visible: boolean;
    chip_present: boolean;
  } {
    const inputs = findFileInputs(document);
    const delta = composerControlDelta(document, keysBefore);
    const added = delta.added_keys;
    const addedControls = delta.added_controls;
    const knownChipKeys = addedControls
      .filter((control) => control.classification === 'attachment-chip')
      .map((control) => control.key);
    const input = inputs[0] ?? null;
    const composerRegion = input?.closest('form, [data-testid*="composer"], [class*="composer"], [role="form"]') ?? null;
    const expectedNameVisible = Boolean(
      expectedName
      && composerRegion
      && (textFrom(composerRegion) || '').toLocaleLowerCase().includes(expectedName.toLocaleLowerCase()),
    );
    const expectedNameNewlyVisible = expectedNameVisible && !expectedNameVisibleBefore;
    return {
      input_files: inputs.reduce((count, candidate) => count + (candidate.files?.length ?? 0), 0),
      added_keys: added,
      added_controls: addedControls,
      known_chip_keys: knownChipKeys,
      expected_name_visible: expectedNameVisible,
      expected_name_newly_visible: expectedNameNewlyVisible,
      // A new unrelated control is not an attachment witness. Before the live
      // chip is in the role atlas, require the uploaded filename to be visible
      // in the same composer as the new control.
      chip_present: knownChipKeys.length > 0 || (added.length > 0 && expectedNameNewlyVisible),
    };
  },

  stopGeneration(document: Document, win: Window): boolean {
    const control = findGenerationControl(document, win, GENERATION_STOP_TERMS);
    if (!control.node) return false;
    control.node.click();
    return true;
  },

  newChat(document: Document): boolean {
    const button = document.querySelector('[data-testid="create-new-chat-button"]');
    if (button instanceof HTMLElement && isVisible(button)) {
      button.click();
      return true;
    }
    return false;
  },

  surfaceProbe(document: Document, win: Window): SurfaceProbeReport {
    const route = classifyRouteDetails(win.location.href, document, win);
    const composer = findPromptComposer(document, win).node;
    const send = findLikelySendButton(document, win, composer).node;
    const generation = generationState(document, win);
    const assistant = findLatestOutputNode(document, win).node;
    const user = latestUserTurnMatch(document, win).node;

    return buildSurfaceProbe(document, {
      url: win.location.href,
      route: { pathname: route.pathname, posture: route.posture },
      composer,
      send,
      stop: generation.stop.node,
      continueControl: generation.continue.node,
      latestAssistant: assistant,
      latestUser: user,
      expectedComposerSelector: OBSERVED_LIVE_PROMPT_SELECTOR,
      expectedSendSelector: OBSERVED_LIVE_SEND_SELECTOR,
      generationState: generation.state,
    });
  },
};

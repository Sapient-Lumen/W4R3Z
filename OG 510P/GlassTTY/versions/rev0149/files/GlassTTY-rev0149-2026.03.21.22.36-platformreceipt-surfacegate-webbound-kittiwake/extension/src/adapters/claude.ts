import type { CandidateInfo, CandidateReport, FixtureCapture, PageAdapter } from './base';
import { buildLiveFixtureMetadata, candidateInfo, collectLiveFrameInventory, isVisible, selectorHint, textFrom, type LiveDocumentContext } from '../content/generic';

interface RankedNode {
  node: Element;
  context: LiveDocumentContext;
  index: number;
  score: number;
}

function promptScore(node: Element): number {
  let score = isVisible(node) ? 0.6 : 0.05;
  const placeholder = (node.getAttribute('placeholder') || '').toLowerCase();
  const aria = (node.getAttribute('aria-label') || '').toLowerCase();
  const role = (node.getAttribute('role') || '').toLowerCase();
  const text = (textFrom(node) || '').toLowerCase();

  if (node.tagName === 'TEXTAREA') score += 0.25;
  if (role === 'textbox') score += 0.2;
  if (node.getAttribute('contenteditable') === 'true') score += 0.15;
  if (placeholder.includes('message') || placeholder.includes('claude') || placeholder.includes('talk')) score += 0.2;
  if (aria.includes('message') || aria.includes('claude') || aria.includes('prompt')) score += 0.2;
  if (text.length > 0 && text.length < 8000) score += 0.05;
  return score;
}

function outputScore(node: Element): number {
  const text = textFrom(node) || '';
  let score = isVisible(node) ? 0.4 : 0.05;
  const className = (node.getAttribute('class') || '').toLowerCase();
  const dataTestId = (node.getAttribute('data-testid') || '').toLowerCase();

  if (node.tagName === 'ARTICLE') score += 0.15;
  if (className.includes('assistant') || dataTestId.includes('assistant')) score += 0.2;
  if (className.includes('message') || dataTestId.includes('message')) score += 0.15;
  if (text.length > 40) score += 0.15;
  if (text.length > 400) score += 0.1;
  if (text.length > 12000) score -= 0.2;
  return score;
}

function inventoryContexts(document: Document, win: Window): LiveDocumentContext[] {
  return collectLiveFrameInventory(document, win).contexts;
}

function rank(selectors: string[], document: Document, scorer: (node: Element) => number, win: Window): RankedNode[] {
  return inventoryContexts(document, win)
    .flatMap((context) => selectors.flatMap((selector) =>
      Array.from(context.document.querySelectorAll(selector)).map((node, index) => ({ node, context, index, score: scorer(node) }))
    ))
    .sort((a, b) => (b.score - a.score) || (a.context.depth - b.context.depth) || (b.index - a.index));
}

function bestVisibleElement(selectors: string[], document: Document, scorer: (node: Element) => number, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null } {
  const best = rank(selectors, document, scorer, win)[0];
  return {
    node: best?.node instanceof HTMLElement ? best.node : null,
    context: best?.context ?? null,
  };
}

function findPromptComposer(document: Document, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null } {
  return bestVisibleElement([
    'textarea',
    '[contenteditable="true"]',
    '[role="textbox"]',
  ], document, promptScore, win);
}

function findLatestOutputNode(document: Document, win: Window): { node: HTMLElement | null; context: LiveDocumentContext | null } {
  const best = rank([
    '[data-testid*="assistant"]',
    '[data-testid*="message"]',
    'article',
    'main article',
    '[class*="assistant"]',
    '[class*="message"]',
    '.prose',
    'main',
    '[role="main"]',
  ], document, outputScore, win).filter(({ node }) => Boolean(textFrom(node)))[0];
  return {
    node: best?.node instanceof HTMLElement ? best.node : null,
    context: best?.context ?? null,
  };
}

function findLikelySendButton(document: Document, win: Window): { node: HTMLButtonElement | null; context: LiveDocumentContext | null } {
  const ranked = inventoryContexts(document, win)
    .flatMap((context) => Array.from(context.document.querySelectorAll('button')).map((button, index) => ({ button, context, index })))
    .filter(({ button }) => {
      const text = (button.textContent || '').trim().toLowerCase();
      const label = (button.getAttribute('aria-label') || '').trim().toLowerCase();
      if (!isVisible(button)) return false;
      return text === 'send' || label.includes('send');
    })
    .sort((left, right) => left.context.depth - right.context.depth || right.index - left.index);
  const best = ranked[0];
  return {
    node: best?.button instanceof HTMLButtonElement ? best.button : null,
    context: best?.context ?? null,
  };
}

function clickLikelySendButton(document: Document, win: Window): boolean {
  const sendish = findLikelySendButton(document, win).node;
  if (sendish) {
    sendish.click();
    return true;
  }
  return false;
}

function sanitizeHtml(node: Element | null): string | null {
  if (!node) return null;
  const clone = node.cloneNode(true) as Element;
  clone.querySelectorAll('img, svg, button, input, textarea, script, style').forEach((child) => child.remove());
  clone.querySelectorAll('*').forEach((el) => {
    for (const attr of Array.from(el.attributes)) {
      if (!['class', 'role', 'data-testid', 'aria-label', 'placeholder'].includes(attr.name)) {
        el.removeAttribute(attr.name);
      }
    }
  });
  return (clone.outerHTML || '').replace(/\s+/g, ' ').slice(0, 3000);
}

export const claudeAdapter: PageAdapter = {
  name: 'claude',
  origin_patterns: ['https://claude.ai/'],
  capabilities: {
    read_prompt: true,
    write_prompt: true,
    submit_prompt: true,
    read_latest_output: true,
    read_selection: true,
    debug_candidates: true,
    fixture_capture: true,
  },

  matches(url: string): boolean {
    return url.startsWith('https://claude.ai/');
  },

  readPrompt(document: Document): string | null {
    return textFrom(findPromptComposer(document, window).node);
  },

  writePrompt(document: Document, text: string): boolean {
    const node = findPromptComposer(document, window).node;
    if (!node) return false;

    if (node instanceof HTMLTextAreaElement || node instanceof HTMLInputElement) {
      node.focus();
      node.value = text;
      node.dispatchEvent(new Event('input', { bubbles: true }));
      node.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    }

    if (node.getAttribute('contenteditable') === 'true') {
      node.focus();
      node.textContent = text;
      node.dispatchEvent(new InputEvent('input', { bubbles: true, data: text, inputType: 'insertText' }));
      return true;
    }

    return false;
  },

  readLatestOutput(document: Document): string | null {
    return textFrom(findLatestOutputNode(document, window).node);
  },

  readSelection(window: Window): string | null {
    return window.getSelection()?.toString().trim() || null;
  },

  debugCandidates(document: Document): CandidateReport {
    const inputSelectors = ['textarea', '[contenteditable="true"]', '[role="textbox"]'];
    const outputSelectors = ['[data-testid*="assistant"]', '[data-testid*="message"]', 'article', 'main', '[role="main"]', '.prose'];

    const inputs: CandidateInfo[] = rank(inputSelectors, document, promptScore, window)
      .slice(0, 12)
      .map(({ node, context }) => candidateInfo(node, promptScore(node), 'prompt', context.window))
      .sort((a, b) => b.score - a.score);

    const outputs: CandidateInfo[] = rank(outputSelectors, document, outputScore, window)
      .slice(0, 12)
      .map(({ node, context }) => candidateInfo(node, outputScore(node), 'output', context.window))
      .sort((a, b) => b.score - a.score);

    return { inputs, outputs };
  },

  captureFixture(document: Document, window: Window): FixtureCapture {
    const inventory = collectLiveFrameInventory(document, window);
    const promptMatch = findPromptComposer(document, window);
    const outputMatch = findLatestOutputNode(document, window);
    const submitMatch = findLikelySendButton(document, window);
    const debug = this.debugCandidates(document);
    const submitCandidate = submitMatch.node && submitMatch.context ? candidateInfo(submitMatch.node, 1, 'button', submitMatch.context.window) : null;
    return {
      adapter: 'claude',
      url: window.location.href,
      title: document.title,
      prompt: this.readPrompt(document),
      latest_output: this.readLatestOutput(document),
      selection: this.readSelection(window),
      candidates: debug,
      html_samples: {
        prompt: sanitizeHtml(promptMatch.node),
        latest_output: sanitizeHtml(outputMatch.node),
        submit: sanitizeHtml(submitMatch.node),
      },
      metadata: {
        prompt_selector: promptMatch.node ? selectorHint(promptMatch.node, 'prompt') : null,
        latest_output_selector: outputMatch.node ? selectorHint(outputMatch.node, 'output') : null,
        ...buildLiveFixtureMetadata(document, promptMatch.node, submitMatch.node, debug.inputs[0] ?? null, submitCandidate, {
          inventory,
          inputCandidates: debug.inputs,
          outputCandidates: debug.outputs,
          submitCandidates: submitCandidate ? [submitCandidate] : [],
        }),
      },
    };
  },

  submitPrompt(document: Document): boolean {
    return clickLikelySendButton(document, window);
  },
};

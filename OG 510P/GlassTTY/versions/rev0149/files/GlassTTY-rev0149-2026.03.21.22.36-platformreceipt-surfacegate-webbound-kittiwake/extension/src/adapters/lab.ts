import type { CandidateInfo, CandidateReport, FixtureCapture, PageAdapter } from './base';
import { buildLiveFixtureMetadata, candidateInfo, collectLiveFrameInventory, isVisible, textFrom, type LiveDocumentContext } from '../content/generic';

interface NodeMatch {
  node: HTMLElement;
  context: LiveDocumentContext;
}

function contexts(document: Document, win: Window): LiveDocumentContext[] {
  return collectLiveFrameInventory(document, win).contexts;
}

function byAttr(document: Document, name: string): HTMLElement | null {
  const node = document.querySelector(`[data-glasstty-role="${name}"]`);
  return node instanceof HTMLElement ? node : null;
}

function matchesForRole(document: Document, win: Window, name: string): NodeMatch[] {
  return contexts(document, win)
    .flatMap((context) => {
      const node = byAttr(context.document, name);
      return node ? [{ node, context }] : [];
    })
    .sort((left, right) => {
      const leftVisible = isVisible(left.node) ? 1 : 0;
      const rightVisible = isVisible(right.node) ? 1 : 0;
      if (leftVisible !== rightVisible) return rightVisible - leftVisible;
      return left.context.depth - right.context.depth;
    });
}

function firstMatch(document: Document, win: Window, name: string): NodeMatch | null {
  return matchesForRole(document, win, name)[0] ?? null;
}

function candidate(match: NodeMatch | null, selector: string): CandidateInfo[] {
  if (!match) return [];
  return [candidateInfo(match.node, 1, selector, match.context.window)];
}

function candidates(document: Document, win: Window, name: string, selector: string): CandidateInfo[] {
  return matchesForRole(document, win, name).map((match) => candidateInfo(match.node, 1, selector, match.context.window));
}

function sample(match: NodeMatch | null): string | null {
  if (!match) return null;
  return (match.node.outerHTML || '').replace(/\s+/g, ' ').slice(0, 1500);
}

export const labAdapter: PageAdapter = {
  name: 'fixturelab',
  origin_patterns: ['http://127.0.0.1:8765/', 'http://localhost:8765/'],
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
    return url.startsWith('http://127.0.0.1:8765/') || url.startsWith('http://localhost:8765/');
  },

  readPrompt(document: Document): string | null {
    const match = firstMatch(document, window, 'prompt');
    return match?.node instanceof HTMLTextAreaElement || match?.node instanceof HTMLInputElement ? match.node.value : textFrom(match?.node ?? null);
  },

  writePrompt(document: Document, text: string): boolean {
    const match = firstMatch(document, window, 'prompt');
    const node = match?.node;
    if (!node) return false;
    if (node instanceof HTMLTextAreaElement || node instanceof HTMLInputElement) {
      node.focus();
      node.value = text;
      node.dispatchEvent(new Event('input', { bubbles: true }));
      node.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    }
    node.textContent = text;
    node.dispatchEvent(new InputEvent('input', { bubbles: true, data: text, inputType: 'insertText' }));
    return true;
  },

  readLatestOutput(document: Document): string | null {
    return textFrom(firstMatch(document, window, 'latest-output')?.node ?? null);
  },

  readSelection(window: Window): string | null {
    return window.getSelection()?.toString().trim() || null;
  },

  debugCandidates(document: Document): CandidateReport {
    return {
      inputs: candidates(document, window, 'prompt', '[data-glasstty-role="prompt"]'),
      outputs: candidates(document, window, 'latest-output', '[data-glasstty-role="latest-output"]'),
    };
  },

  captureFixture(document: Document, window: Window): FixtureCapture {
    const inventory = collectLiveFrameInventory(document, window);
    const promptMatch = firstMatch(document, window, 'prompt');
    const latestMatch = firstMatch(document, window, 'latest-output');
    const submitMatch = firstMatch(document, window, 'submit');
    const inputCandidates = candidates(document, window, 'prompt', '[data-glasstty-role="prompt"]');
    const outputCandidates = candidates(document, window, 'latest-output', '[data-glasstty-role="latest-output"]');
    const submitCandidates = candidates(document, window, 'submit', '[data-glasstty-role="submit"]');
    const promptCandidate = inputCandidates[0] ?? null;
    const submitCandidate = submitCandidates[0] ?? null;
    return {
      adapter: 'fixturelab',
      url: window.location.href,
      title: document.title,
      prompt: this.readPrompt(document),
      latest_output: this.readLatestOutput(document),
      selection: this.readSelection(window),
      candidates: {
        inputs: inputCandidates,
        outputs: outputCandidates,
      },
      html_samples: {
        prompt: sample(promptMatch),
        latest_output: sample(latestMatch),
        submit: sample(submitMatch),
      },
      metadata: {
        generator: firstMatch(document, window, 'meta-generator')?.node.textContent?.trim() || 'fixture-lab',
        ...buildLiveFixtureMetadata(document, promptMatch?.node ?? null, submitMatch?.node ?? null, promptCandidate, submitCandidate, {
          inventory,
          inputCandidates,
          outputCandidates,
          submitCandidates,
        }),
      },
    };
  },

  submitPrompt(document: Document): boolean {
    const button = firstMatch(document, window, 'submit')?.node;
    if (button instanceof HTMLButtonElement) {
      button.click();
      return true;
    }
    return false;
  },
};

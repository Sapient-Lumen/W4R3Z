import { buildLiveFixtureMetadata, candidateInfo, collectLiveFrameInventory, isVisible, textFrom } from '../content/generic';
function contexts(document, win) {
    return collectLiveFrameInventory(document, win).contexts;
}
function byAttr(document, name) {
    const node = document.querySelector(`[data-glasstty-role="${name}"]`);
    return node instanceof HTMLElement ? node : null;
}
function matchesForRole(document, win, name) {
    return contexts(document, win)
        .flatMap((context) => {
        const node = byAttr(context.document, name);
        return node ? [{ node, context }] : [];
    })
        .sort((left, right) => {
        const leftVisible = isVisible(left.node) ? 1 : 0;
        const rightVisible = isVisible(right.node) ? 1 : 0;
        if (leftVisible !== rightVisible)
            return rightVisible - leftVisible;
        return left.context.depth - right.context.depth;
    });
}
function firstMatch(document, win, name) {
    return matchesForRole(document, win, name)[0] ?? null;
}
function candidate(match, selector) {
    if (!match)
        return [];
    return [candidateInfo(match.node, 1, selector, match.context.window)];
}
function candidates(document, win, name, selector) {
    return matchesForRole(document, win, name).map((match) => candidateInfo(match.node, 1, selector, match.context.window));
}
function sample(match) {
    if (!match)
        return null;
    return (match.node.outerHTML || '').replace(/\s+/g, ' ').slice(0, 1500);
}
export const labAdapter = {
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
    matches(url) {
        return url.startsWith('http://127.0.0.1:8765/') || url.startsWith('http://localhost:8765/');
    },
    readPrompt(document) {
        const match = firstMatch(document, window, 'prompt');
        return match?.node instanceof HTMLTextAreaElement || match?.node instanceof HTMLInputElement ? match.node.value : textFrom(match?.node ?? null);
    },
    writePrompt(document, text) {
        const match = firstMatch(document, window, 'prompt');
        const node = match?.node;
        if (!node)
            return false;
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
    readLatestOutput(document) {
        return textFrom(firstMatch(document, window, 'latest-output')?.node ?? null);
    },
    readSelection(window) {
        return window.getSelection()?.toString().trim() || null;
    },
    debugCandidates(document) {
        return {
            inputs: candidates(document, window, 'prompt', '[data-glasstty-role="prompt"]'),
            outputs: candidates(document, window, 'latest-output', '[data-glasstty-role="latest-output"]'),
        };
    },
    captureFixture(document, window) {
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
    submitPrompt(document) {
        const button = firstMatch(document, window, 'submit')?.node;
        if (button instanceof HTMLButtonElement) {
            button.click();
            return true;
        }
        return false;
    },
};

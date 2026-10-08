import { isVisible, textFrom } from '../content/generic';
function findPromptComposer(document) {
    const selectors = ['textarea', '[contenteditable="true"]', '[role="textbox"]'];
    for (const selector of selectors) {
        const nodes = Array.from(document.querySelectorAll(selector));
        const match = nodes.find((node) => isVisible(node));
        if (match instanceof HTMLElement)
            return match;
    }
    return null;
}
function clickLikelySendButton(document) {
    const buttons = Array.from(document.querySelectorAll('button'));
    const sendish = buttons.find((button) => {
        const text = (button.textContent || '').trim().toLowerCase();
        const label = (button.getAttribute('aria-label') || '').trim().toLowerCase();
        if (!isVisible(button))
            return false;
        return text === 'send' || label.includes('send');
    });
    if (sendish instanceof HTMLButtonElement) {
        sendish.click();
        return true;
    }
    return false;
}
export const claudeAdapter = {
    name: 'claude',
    matches(url) {
        return url.startsWith('https://claude.ai/');
    },
    readPrompt(document) {
        return textFrom(findPromptComposer(document));
    },
    writePrompt(document, text) {
        const node = findPromptComposer(document);
        if (!node)
            return false;
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
    readLatestOutput(document) {
        const candidates = Array.from(document.querySelectorAll('main, article, [role="main"]'));
        const visible = candidates.filter((node) => isVisible(node));
        const texts = visible.map((node) => textFrom(node)).filter((t) => Boolean(t));
        if (texts.length === 0)
            return null;
        return texts[texts.length - 1];
    },
    readSelection(window) {
        return window.getSelection()?.toString().trim() || null;
    },
    debugCandidates(document) {
        const inputSelectors = ['textarea', '[contenteditable="true"]', '[role="textbox"]'];
        const inputs = [];
        for (const selector of inputSelectors) {
            for (const node of Array.from(document.querySelectorAll(selector)).slice(0, 5)) {
                inputs.push({
                    selector_hint: selector,
                    score: isVisible(node) ? 0.75 : 0.2,
                    text_length: (textFrom(node) || '').length,
                    visible: isVisible(node),
                });
            }
        }
        const outputs = Array.from(document.querySelectorAll('main, article, [role="main"]')).slice(0, 5).map((node) => ({
            selector_hint: node.tagName.toLowerCase(),
            score: isVisible(node) ? 0.5 : 0.1,
            text_length: (textFrom(node) || '').length,
            visible: isVisible(node),
        }));
        return { inputs, outputs };
    },
    submitPrompt(document) {
        return clickLikelySendButton(document);
    },
};

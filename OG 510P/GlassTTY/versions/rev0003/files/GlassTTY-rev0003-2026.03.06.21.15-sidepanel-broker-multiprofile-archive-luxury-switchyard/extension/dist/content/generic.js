export function isVisible(el) {
    if (!el)
        return false;
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
}
export function textFrom(el) {
    if (!el)
        return null;
    if (el instanceof HTMLTextAreaElement)
        return el.value;
    if (el instanceof HTMLInputElement)
        return el.value;
    return el.textContent?.trim() || null;
}

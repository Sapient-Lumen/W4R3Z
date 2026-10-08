export function isVisible(el: Element | null): boolean {
  if (!el) return false;
  const rect = (el as HTMLElement).getBoundingClientRect();
  const style = window.getComputedStyle(el as HTMLElement);
  return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
}

export function textFrom(el: Element | null): string | null {
  if (!el) return null;
  if (el instanceof HTMLTextAreaElement) return el.value;
  if (el instanceof HTMLInputElement) return el.value;
  return el.textContent?.trim() || null;
}

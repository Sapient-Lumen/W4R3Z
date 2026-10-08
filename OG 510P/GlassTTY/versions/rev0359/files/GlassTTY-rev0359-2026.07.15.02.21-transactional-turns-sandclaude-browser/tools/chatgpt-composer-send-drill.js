// GlassTTY ChatGPT Composer Send Drill
// rev0330 paste-safe opt-in mutation probe. Paste into DevTools on chatgpt.com.
// Local-only: no network writes, no storage reads, no prompt submission.
(async function glassTtyChatGptComposerSendDrill() {
  'use strict';

  var VERSION = 'rev0330-2026.06.12.23.09';
  var PROBE = 'GLASSTTY-SEND-PROBE-DO-NOT-SUBMIT';

  function str(value) {
    return value == null ? '' : String(value);
  }

  function compact(value, limit) {
    var max = typeof limit === 'number' ? limit : 2000;
    return str(value).replace(/\s+/g, ' ').trim().slice(0, max);
  }

  function lower(value) {
    return compact(value).toLowerCase();
  }

  function attr(el, name) {
    return el && el.getAttribute ? el.getAttribute(name) : null;
  }

  function q(root, selector) {
    try {
      return Array.prototype.slice.call(root.querySelectorAll(selector));
    } catch (error) {
      return [];
    }
  }

  function hasAny(text, terms) {
    var hay = lower(text);
    return terms.some(function (term) {
      return hay.indexOf(term) !== -1;
    });
  }

  var NON_SEND_TERMS = [
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
    'create image'
  ];

  function rectOf(el) {
    try {
      var r = el.getBoundingClientRect();
      return {
        x: Math.round(r.x),
        y: Math.round(r.y),
        width: Math.round(r.width),
        height: Math.round(r.height),
        top: Math.round(r.top),
        bottom: Math.round(r.bottom)
      };
    } catch (error) {
      return null;
    }
  }

  function visible(el) {
    if (!el || !(el instanceof Element)) return false;
    var r = rectOf(el);
    if (!r || r.width <= 0 || r.height <= 0) return false;
    var s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0';
  }

  function hashText(value) {
    var input = compact(value, 200000);
    var hash = 2166136261;
    for (var i = 0; i < input.length; i += 1) {
      hash ^= input.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return input ? 'fnv1a32:' + (hash >>> 0).toString(16) : null;
  }

  function cssEsc(value) {
    if (globalThis.CSS && CSS.escape) return CSS.escape(str(value));
    return str(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }

  function selector(el) {
    if (!el || !el.tagName) return null;
    var id = attr(el, 'id');
    if (id && q(document, '#' + cssEsc(id)).length === 1) return '#' + cssEsc(id);
    var testid = attr(el, 'data-testid');
    if (testid) {
      var byTest = '[data-testid=' + JSON.stringify(testid) + ']';
      if (q(document, byTest).length === 1) return byTest;
    }
    var parts = [];
    var node = el;
    while (node && node.nodeType === 1 && parts.length < 6) {
      if (node === document.documentElement) break;
      var tag = node.tagName.toLowerCase();
      var nth = 1;
      var prev = node.previousElementSibling;
      while (prev) {
        if (prev.tagName === node.tagName) nth += 1;
        prev = prev.previousElementSibling;
      }
      parts.unshift(tag + ':nth-of-type(' + nth + ')');
      node = node.parentElement;
    }
    return parts.join(' > ');
  }

  function contentEditableMode(el) {
    var raw = attr(el, 'contenteditable');
    if (raw == null) return null;
    var mode = lower(raw);
    if (mode === 'false') return null;
    return mode || 'true';
  }

  function editable(el) {
    if (!el || !el.tagName) return false;
    var tag = el.tagName.toLowerCase();
    if (tag === 'textarea') return true;
    if (tag === 'input') {
      return ['button', 'submit', 'hidden', 'checkbox', 'radio', 'file']
        .indexOf(lower(el.type)) === -1;
    }
    return Boolean(contentEditableMode(el)) || attr(el, 'role') === 'textbox';
  }

  function textOf(el) {
    if (!el) return '';
    if (el instanceof HTMLTextAreaElement) return el.value || '';
    if (el instanceof HTMLInputElement) return el.value || '';
    return el.textContent || '';
  }

  function promptScore(el) {
    var score = visible(el) ? 0.45 : 0.03;
    var id = lower(attr(el, 'id'));
    var testid = lower(attr(el, 'data-testid'));
    var placeholder = lower(attr(el, 'placeholder'));
    var dataPlaceholder = lower(attr(el, 'data-placeholder'));
    var aria = lower(attr(el, 'aria-label'));
    var klass = lower(attr(el, 'class'));
    if (!editable(el)) score -= 0.35;
    if (id === 'prompt-textarea') score += 0.35;
    if (testid.indexOf('prompt-textarea') !== -1) score += 0.35;
    if (el instanceof HTMLTextAreaElement) score += 0.25;
    if (attr(el, 'role') === 'textbox') score += 0.22;
    if (contentEditableMode(el)) score += 0.18;
    if (hasAny(placeholder, ['message', 'ask anything', 'prompt'])) score += 0.20;
    if (hasAny(dataPlaceholder, ['message', 'ask anything', 'prompt'])) {
      score += 0.20;
    }
    if (hasAny(aria, ['message', 'prompt', 'ask chatgpt'])) score += 0.16;
    if (klass.indexOf('composer') !== -1) score += 0.08;
    if (klass.indexOf('prompt') !== -1) score += 0.08;
    return Number(score.toFixed(3));
  }

  function sendSignal(button) {
    var text = lower(button.textContent);
    var aria = lower(attr(button, 'aria-label'));
    var title = lower(attr(button, 'title'));
    var testid = lower(attr(button, 'data-testid'));
    var type = lower(attr(button, 'type'));
    var all = [text, aria, title, testid].join(' ');
    var explicit = testid === 'send-button' || testid.indexOf('send') !== -1 ||
      aria === 'send' || aria.indexOf('send message') !== -1 ||
      aria.indexOf('send prompt') !== -1 || title === 'send' ||
      title.indexOf('send message') !== -1 || text === 'send';
    var submit = type === 'submit';
    var nonSend = hasAny(all, NON_SEND_TERMS);
    return {
      intent: explicit || submit,
      disqualified: nonSend && !explicit,
      combined_hash: hashText(all)
    };
  }

  function sendScore(button, prompt) {
    var score = visible(button) ? 0.30 : 0.02;
    var text = lower(button.textContent);
    var aria = lower(attr(button, 'aria-label'));
    var title = lower(attr(button, 'title'));
    var testid = lower(attr(button, 'data-testid'));
    var type = lower(attr(button, 'type'));
    var disabled = button.disabled || attr(button, 'aria-disabled') === 'true';
    var signal = sendSignal(button);
    if (disabled) score -= 0.80;
    if (!signal.intent) score -= 0.35;
    if (signal.disqualified) score -= 1.00;
    if (testid === 'send-button' || testid.indexOf('send') !== -1) {
      score += 0.50;
    }
    if (aria === 'send' || aria.indexOf('send message') !== -1) score += 0.45;
    if (aria.indexOf('send prompt') !== -1) score += 0.45;
    if (title === 'send' || title.indexOf('send message') !== -1) score += 0.32;
    if (text === 'send') score += 0.30;
    if (type === 'submit') score += 0.18;
    if (prompt) {
      var root = prompt.closest([
        'form',
        '[data-testid*=composer]',
        '[class*=composer]',
        '[role=form]'
      ].join(','));
      if (button.form && prompt.form && button.form === prompt.form) score += 0.20;
      if (root && root.contains(button)) score += 0.16;
    } else {
      score -= 0.12;
    }
    if (button.closest('nav, header, aside')) score -= 0.18;
    return Number(score.toFixed(3));
  }

  function bySelectors(selectors) {
    var seen = new Set();
    var out = [];
    selectors.forEach(function (sel) {
      q(document, sel).forEach(function (el) {
        if (seen.has(el)) return;
        seen.add(el);
        out.push(el);
      });
    });
    return out;
  }

  function candidate(button, prompt) {
    if (!button) return null;
    var signal = sendSignal(button);
    return {
      selector: selector(button),
      score: sendScore(button, prompt),
      visible: visible(button),
      tag: button.tagName ? button.tagName.toLowerCase() : null,
      id: attr(button, 'id'),
      role: attr(button, 'role'),
      data_testid: attr(button, 'data-testid'),
      aria_label: attr(button, 'aria-label'),
      title: attr(button, 'title'),
      type: attr(button, 'type'),
      disabled: Boolean(button.disabled),
      aria_disabled: attr(button, 'aria-disabled'),
      rect: rectOf(button),
      intent: signal.intent,
      disqualified: signal.disqualified,
      combined_hash: signal.combined_hash
    };
  }

  function sleep(ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms);
    });
  }

  function dispatchEditEvents(el, text) {
    el.dispatchEvent(new InputEvent('beforeinput', {
      bubbles: true,
      cancelable: true,
      data: text,
      inputType: 'insertText'
    }));
    el.dispatchEvent(new InputEvent('input', {
      bubbles: true,
      data: text,
      inputType: 'insertText'
    }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function setNativeValue(el, text) {
    var proto = Object.getPrototypeOf(el);
    var desc = Object.getOwnPropertyDescriptor(proto, 'value');
    if (desc && desc.set) desc.set.call(el, text);
    else el.value = text;
  }

  function writeText(el, text) {
    if (!el) return false;
    el.focus();
    if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) {
      setNativeValue(el, text);
      dispatchEditEvents(el, text);
      return compact(textOf(el)) === compact(text);
    }
    if (contentEditableMode(el) || attr(el, 'role') === 'textbox') {
      var selection = document.getSelection();
      if (selection) {
        var range = document.createRange();
        range.selectNodeContents(el);
        selection.removeAllRanges();
        selection.addRange(range);
      }
      var inserted = false;
      try {
        inserted = document.execCommand('insertText', false, text);
      } catch (error) {
        inserted = false;
      }
      if (!inserted) el.textContent = text;
      dispatchEditEvents(el, text);
      return compact(textOf(el)) === compact(text);
    }
    return false;
  }

  function summarizePrompt(el) {
    if (!el) return null;
    return {
      selector: selector(el),
      score: promptScore(el),
      visible: visible(el),
      tag: el.tagName ? el.tagName.toLowerCase() : null,
      id: attr(el, 'id'),
      role: attr(el, 'role'),
      data_testid: attr(el, 'data-testid'),
      aria_label: attr(el, 'aria-label'),
      contenteditable: attr(el, 'contenteditable'),
      text_length: compact(textOf(el), 200000).length,
      text_hash: hashText(textOf(el))
    };
  }

  function sendSnapshot(prompt) {
    var buttons = bySelectors([
      'button[data-testid="send-button"]',
      'button[aria-label*="Send" i]',
      'button[title*="Send" i]',
      'form button[type="submit"]',
      'button'
    ]).sort(function (a, b) {
      return sendScore(b, prompt) - sendScore(a, prompt);
    });
    var valid = buttons.filter(function (button) {
      var signal = sendSignal(button);
      return sendScore(button, prompt) > 0.45 && signal.intent &&
        !signal.disqualified && !button.disabled &&
        attr(button, 'aria-disabled') !== 'true';
    });
    return {
      total_buttons: buttons.length,
      valid_count: valid.length,
      best_valid: candidate(valid[0] || null, prompt),
      top_scored: buttons.slice(0, 8).map(function (button) {
        return candidate(button, prompt);
      })
    };
  }

  function copyText(text) {
    if (typeof globalThis.copy === 'function') {
      globalThis.copy(text);
      return { ok: true, method: 'devtools-copy' };
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text);
      return { ok: true, method: 'navigator.clipboard.writeText' };
    }
    return { ok: false, method: null, error: 'no-copy-api' };
  }

  function downloadText(filename, text) {
    var blob = new Blob([text], { type: 'application/json' });
    var href = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = href;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    setTimeout(function () {
      URL.revokeObjectURL(href);
      link.remove();
    }, 0);
    return filename;
  }

  var promptSelectors = [
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
    '[contenteditable="plaintext-only"]'
  ];
  var prompts = bySelectors(promptSelectors).sort(function (a, b) {
    return promptScore(b) - promptScore(a);
  });
  var promptNode = prompts[0] || null;
  var beforeText = textOf(promptNode);
  var warnings = [];
  if (location.hostname !== 'chatgpt.com' &&
      !location.hostname.endsWith('.chatgpt.com')) {
    warnings.push('Not on chatgpt.com; findings may not match target.');
  }
  if (!promptNode) warnings.push('No prompt editor found.');

  var before = {
    prompt: summarizePrompt(promptNode),
    send: sendSnapshot(promptNode)
  };
  var writeOk = promptNode ? writeText(promptNode, PROBE) : false;
  await sleep(350);
  var afterWrite = {
    prompt: summarizePrompt(promptNode),
    send: sendSnapshot(promptNode)
  };
  var restoreOk = promptNode ? writeText(promptNode, beforeText) : false;
  await sleep(150);
  var afterRestore = {
    prompt: summarizePrompt(promptNode),
    send: sendSnapshot(promptNode)
  };
  if (!writeOk) warnings.push('Probe write did not read back exactly.');
  if (!restoreOk) warnings.push('Composer restore did not read back exactly.');
  if (!afterWrite.send.best_valid) {
    warnings.push('No valid send button appeared after probe write.');
  }

  var report = {
    schema_version: 1,
    tool: 'glasstty-chatgpt-composer-send-drill',
    version: VERSION,
    captured_at: new Date().toISOString(),
    local_only: true,
    mutates_composer: true,
    restores_composer: true,
    no_prompt_submission: true,
    no_network_writes: true,
    no_storage_reads: true,
    probe_text_hash: hashText(PROBE),
    page: {
      origin: location.origin,
      host: location.host,
      pathname: location.pathname,
      ready_state: document.readyState,
      visibility_state: document.visibilityState
    },
    before: before,
    write_probe: {
      ok: writeOk,
      readback_length: compact(textOf(promptNode), 200000).length,
      readback_hash: hashText(textOf(promptNode))
    },
    after_write: afterWrite,
    restore: {
      ok: restoreOk,
      original_length: compact(beforeText, 200000).length,
      original_hash: hashText(beforeText)
    },
    after_restore: afterRestore,
    warnings: warnings
  };

  var json = JSON.stringify(report);
  var line = 'GLASSTTY_SEND_DRILL_JSON=' + json;
  globalThis.__GLASSTTY_CHATGPT_SEND_DRILL__ = report;
  globalThis.__GLASSTTY_CHATGPT_SEND_DRILL_JSON__ = json;
  globalThis.__GLASSTTY_PRINT_SEND_DRILL__ = function () {
    console.log(line);
    return report;
  };
  globalThis.__GLASSTTY_COPY_SEND_DRILL__ = function () {
    return copyText(json);
  };
  globalThis.__GLASSTTY_DOWNLOAD_SEND_DRILL__ = function () {
    var stamp = new Date().toISOString().replace(/[^0-9]/g, '').slice(0, 14);
    return downloadText('glasstty-chatgpt-send-drill-' + stamp + '.json', json);
  };
  console.groupCollapsed('GlassTTY ChatGPT composer send drill ' + VERSION);
  console.log('Send drill object:', report);
  console.log(line);
  console.log('Fallback helpers:', [
    '__GLASSTTY_PRINT_SEND_DRILL__()',
    '__GLASSTTY_COPY_SEND_DRILL__()',
    '__GLASSTTY_DOWNLOAD_SEND_DRILL__()'
  ]);
  console.groupEnd();
  return report;
}());

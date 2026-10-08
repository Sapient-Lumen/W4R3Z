// GlassTTY ChatGPT Sendpath Probe
// rev0330 paste-safe edition. Paste into DevTools on chatgpt.com.
// Local-only: writes a draft, restores it, never submits a prompt.
(function glassTtyChatGptSendpathProbe() {
  'use strict';

  var VERSION = 'rev0331-2026.06.12.23.34';
  var OPTIONS = Object.assign({
    draft_text: 'GLASSTTY-SENDPATH-DRAFT-DO-NOT-SUBMIT',
    restore_prompt: true,
    allow_non_empty_prompt: false,
    wait_ms: 450
  }, globalThis.GLASSTTY_SENDPATH_PROBE_OPTIONS || {});

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

  function hashText(value) {
    var input = compact(value, 200000);
    var hash = 2166136261;
    for (var i = 0; i < input.length; i += 1) {
      hash ^= input.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return input ? 'fnv1a32:' + (hash >>> 0).toString(16) : null;
  }

  function hasAny(value, terms) {
    var hay = lower(value);
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
    return s.display !== 'none' && s.visibility !== 'hidden' &&
      s.opacity !== '0';
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

  function cssEsc(value) {
    if (globalThis.CSS && CSS.escape) return CSS.escape(str(value));
    return str(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }

  function selector(el) {
    if (!el || !el.tagName) return null;
    var id = attr(el, 'id');
    if (id && q(document, '#' + cssEsc(id)).length === 1) {
      return '#' + cssEsc(id);
    }
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
    if (hasAny(placeholder, ['message', 'ask anything', 'prompt'])) {
      score += 0.20;
    }
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
      combined: all
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
      if (button.form && prompt.form && button.form === prompt.form) {
        score += 0.20;
      }
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

  function candidate(el, score) {
    if (!el) return null;
    return {
      selector: selector(el),
      score: score,
      visible: visible(el),
      tag: el.tagName ? el.tagName.toLowerCase() : null,
      id: attr(el, 'id'),
      role: attr(el, 'role'),
      data_testid: attr(el, 'data-testid'),
      aria_label: attr(el, 'aria-label'),
      title: attr(el, 'title'),
      type: attr(el, 'type'),
      disabled: Boolean(el.disabled),
      aria_disabled: attr(el, 'aria-disabled'),
      rect: rectOf(el),
      text_length: compact(textOf(el), 200000).length,
      text_hash: hashText(textOf(el))
    };
  }

  function bestSend(prompt) {
    var buttons = bySelectors([
      'button[data-testid="send-button"]',
      'button[aria-label*="Send" i]',
      'button[title*="Send" i]',
      'form button[type="submit"]',
      'button'
    ]).sort(function (a, b) {
      return sendScore(b, prompt) - sendScore(a, prompt);
    });
    var allowed = buttons.filter(function (button) {
      var signal = sendSignal(button);
      return sendScore(button, prompt) > 0.45 && signal.intent &&
        !signal.disqualified && !button.disabled &&
        attr(button, 'aria-disabled') !== 'true';
    });
    return {
      best: allowed[0] || null,
      top: buttons[0] || null,
      total: buttons.length,
      top_five: buttons.slice(0, 5).map(function (button) {
        return candidate(button, sendScore(button, prompt));
      })
    };
  }

  function fireEditableEvents(el, data) {
    try {
      el.dispatchEvent(new InputEvent('beforeinput', {
        bubbles: true,
        cancelable: true,
        data: data,
        inputType: data ? 'insertText' : 'deleteContentBackward'
      }));
    } catch (error) {}
    try {
      el.dispatchEvent(new InputEvent('input', {
        bubbles: true,
        data: data,
        inputType: data ? 'insertText' : 'deleteContentBackward'
      }));
    } catch (error) {
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function writeText(el, text) {
    if (!el) return false;
    el.focus();
    if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) {
      el.value = text;
      fireEditableEvents(el, text);
      return compact(textOf(el), 200000) === compact(text, 200000);
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
      if (!inserted || compact(textOf(el), 200000) !== compact(text, 200000)) {
        el.textContent = text;
      }
      fireEditableEvents(el, text);
      return compact(textOf(el), 200000) === compact(text, 200000);
    }
    return false;
  }

  function sleep(ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms);
    });
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

  async function run() {
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
    var prompt = prompts[0] || null;
    var original = textOf(prompt);
    var before = bestSend(prompt);
    var didWrite = false;
    var readback = false;
    var didRestore = false;
    var restoreMatches = false;
    var aborted = false;
    var warnings = [];
    if (!prompt) {
      aborted = true;
      warnings.push('No prompt editor was found.');
    } else if (compact(original) && !OPTIONS.allow_non_empty_prompt) {
      aborted = true;
      warnings.push('Prompt already has draft text; refusing to overwrite.');
    } else {
      didWrite = writeText(prompt, OPTIONS.draft_text);
      readback = compact(textOf(prompt)) === compact(OPTIONS.draft_text);
      if (!didWrite || !readback) {
        warnings.push('Draft write/readback did not fully match.');
      }
      await sleep(Number(OPTIONS.wait_ms) || 450);
    }
    var after = bestSend(prompt);
    if (prompt && !aborted && OPTIONS.restore_prompt) {
      didRestore = writeText(prompt, original);
      restoreMatches = compact(textOf(prompt)) === compact(original);
      if (!restoreMatches) warnings.push('Prompt restore did not fully match.');
    }
    var result = {
      schema_version: 1,
      tool: 'glasstty-chatgpt-sendpath-probe',
      version: VERSION,
      captured_at: new Date().toISOString(),
      local_only: true,
      paste_transport: {
        edition: 'sendpath-safe-ascii',
        no_eval: true,
        no_script_tag_injection: true,
        no_network_writes: true,
        no_storage_reads: true,
        no_prompt_submission: true
      },
      page: {
        origin: location.origin,
        host: location.host,
        pathname: location.pathname,
        ready_state: document.readyState,
        visibility_state: document.visibilityState
      },
      prompt: {
        selector: selector(prompt),
        score: prompt ? promptScore(prompt) : 0,
        visible: prompt ? visible(prompt) : false,
        original_length: compact(original, 200000).length,
        original_hash: hashText(original),
        draft_length: compact(OPTIONS.draft_text, 200000).length,
        draft_hash: hashText(OPTIONS.draft_text)
      },
      write_result: {
        attempted: Boolean(prompt && !aborted),
        aborted: aborted,
        wrote_draft: didWrite,
        readback_matches_draft: readback,
        restore_requested: Boolean(OPTIONS.restore_prompt),
        restored: didRestore,
        restore_matches_original: restoreMatches
      },
      send_before: {
        best_selector: before.best ? selector(before.best) : null,
        best_score: before.best ? sendScore(before.best, prompt) : 0,
        top_candidate: candidate(
          before.top,
          before.top ? sendScore(before.top, prompt) : 0
        ),
        top_five: before.top_five,
        total_buttons_seen: before.total
      },
      send_after_draft: {
        best_selector: after.best ? selector(after.best) : null,
        best_score: after.best ? sendScore(after.best, prompt) : 0,
        top_candidate: candidate(
          after.top,
          after.top ? sendScore(after.top, prompt) : 0
        ),
        top_five: after.top_five,
        total_buttons_seen: after.total
      },
      adapter_recommendation: {
        prompt_selector: selector(prompt),
        send_ready_after_draft: Boolean(after.best),
        best_send_selector_after_draft: after.best ? selector(after.best) : null,
        best_send_score_after_draft: after.best ?
          sendScore(after.best, prompt) : 0,
        submit_was_not_attempted: true
      },
      warnings: warnings
    };
    var json = JSON.stringify(result);
    var line = 'GLASSTTY_SENDPATH_PROBE_JSON=' + json;
    globalThis.__GLASSTTY_CHATGPT_SENDPATH_PROBE__ = result;
    globalThis.__GLASSTTY_CHATGPT_SENDPATH_PROBE_JSON__ = json;
    globalThis.__GLASSTTY_PRINT_SENDPATH_PROBE__ = function () {
      console.log(line);
      return result;
    };
    globalThis.__GLASSTTY_COPY_SENDPATH_PROBE__ = function () {
      return copyText(json);
    };
    globalThis.__GLASSTTY_DOWNLOAD_SENDPATH_PROBE__ = function () {
      var stamp = new Date().toISOString().replace(/[^0-9]/g, '').slice(0, 14);
      return downloadText(
        'glasstty-chatgpt-sendpath-probe-' + stamp + '.json',
        json
      );
    };
    console.groupCollapsed('GlassTTY ChatGPT sendpath probe ' + VERSION);
    console.log('Probe object:', result);
    console.log(line);
    console.log('Fallback helpers:', [
      '__GLASSTTY_PRINT_SENDPATH_PROBE__()',
      '__GLASSTTY_COPY_SENDPATH_PROBE__()',
      '__GLASSTTY_DOWNLOAD_SENDPATH_PROBE__()'
    ]);
    console.groupEnd();
    return result;
  }

  return run();
}());

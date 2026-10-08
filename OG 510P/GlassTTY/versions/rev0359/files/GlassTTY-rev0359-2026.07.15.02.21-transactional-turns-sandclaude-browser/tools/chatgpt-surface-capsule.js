// GlassTTY ChatGPT Surface Capsule
// rev0330 send-guard small edition. Paste into DevTools on chatgpt.com.
// Local-only: no network writes, no storage reads, no prompt submission.
(function glassTtyChatGptSurfaceCapsule() {
  'use strict';

  var VERSION = 'rev0331-2026.06.12.23.34';

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

  function hasAny(text, terms) {
    var hay = lower(text);
    return terms.some(function (term) {
      return hay.indexOf(term) !== -1;
    });
  }



  var SEND_MIN_SCORE = 0.45;

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

  function sendSignal(button) {
    var text = lower(button.textContent);
    var aria = lower(attr(button, 'aria-label'));
    var title = lower(attr(button, 'title'));
    var testid = lower(attr(button, 'data-testid'));
    var id = lower(attr(button, 'id'));
    var type = lower(attr(button, 'type'));
    var all = [text, aria, title, id, testid].join(' ');
    var explicit = testid === 'send-button' ||
      testid.indexOf('send-button') !== -1 ||
      testid.indexOf('send-message') !== -1 ||
      id === 'composer-submit-button' || id === 'send-button' ||
      aria === 'send' || aria.indexOf('send message') !== -1 ||
      aria.indexOf('send prompt') !== -1 || title === 'send' ||
      title.indexOf('send message') !== -1 || text === 'send';
    var submit = type === 'submit';
    var nonSend = hasAny(all, NON_SEND_TERMS);
    var exactPlus = id === 'composer-plus-btn' || testid === 'composer-plus-btn';
    return {
      intent: explicit || submit,
      disqualified: exactPlus || (nonSend && !explicit),
      combined: all
    };
  }

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
    if (hasAny([id, testid, placeholder, dataPlaceholder, aria].join(' '), [
      'search',
      'filter',
      'rename',
      'title',
      'email',
      'recipient'
    ])) score -= 0.28;
    return Number(score.toFixed(3));
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

  function topCounts(values) {
    var map = new Map();
    values.forEach(function (value) {
      var key = str(value).trim();
      if (!key) return;
      map.set(key, (map.get(key) || 0) + 1);
    });
    return Array.prototype.slice.call(map.entries())
      .sort(function (a, b) { return b[1] - a[1] || a[0].localeCompare(b[0]); })
      .slice(0, 20)
      .map(function (entry) { return { value: entry[0], count: entry[1] }; });
  }

  function candidate(el, score) {
    if (!el) return null;
    var roleNode = el.closest ? el.closest('[data-message-author-role]') : null;
    return {
      selector: selector(el),
      score: typeof score === 'number' ? score : null,
      visible: visible(el),
      tag: el.tagName ? el.tagName.toLowerCase() : null,
      id: attr(el, 'id'),
      role: attr(el, 'role'),
      data_testid: attr(el, 'data-testid'),
      aria_label: attr(el, 'aria-label'),
      placeholder: attr(el, 'placeholder'),
      data_placeholder: attr(el, 'data-placeholder'),
      contenteditable: attr(el, 'contenteditable'),
      disabled: Boolean(el.disabled),
      rect: rectOf(el),
      text_length: compact(textOf(el), 200000).length,
      text_hash: hashText(textOf(el)),
      nearest_author_role: roleNode ? attr(roleNode, 'data-message-author-role') : null
    };
  }

  function probe(selectors) {
    return selectors.map(function (sel) {
      var items = bySelectors([sel]);
      return {
        selector: sel,
        count: items.length,
        visible_count: items.filter(visible).length,
        first_selectors: items.slice(0, 6).map(selector)
      };
    });
  }

  function routeGuess(promptPresent) {
    var path = location.pathname.toLowerCase();
    var evidence = ['path:' + path, promptPresent ? 'composer:present' :
      'composer:missing'];
    if (path.indexOf('/auth/') !== -1 || path.indexOf('/login') !== -1) {
      evidence.push('auth-path');
      return { posture: 'login-or-marketing', evidence: evidence };
    }
    if ((path === '/' || path.indexOf('/c/') === 0) && promptPresent) {
      evidence.push('plain-chat-path-and-composer');
      return { posture: 'plain-chat', evidence: evidence };
    }
    if (path.indexOf('/g/') !== -1 || path.indexOf('/gpts') !== -1) {
      evidence.push('gpt-or-project-path');
      return { posture: 'project-or-gpt', evidence: evidence };
    }
    if (promptPresent) {
      evidence.push('composer-present-no-blocking-route-signal');
      return { posture: 'plain-chat', evidence: evidence };
    }
    evidence.push('no-supported-route-signal');
    return { posture: 'unknown', evidence: evidence };
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
  var sendSelectors = [
    'button[data-testid="send-button"]',
    'button[aria-label*="Send" i]',
    'button[title*="Send" i]',
    'form button[type="submit"]',
    'button'
  ];
  var outputSelectors = [
    '[data-message-author-role="assistant"]',
    '[data-testid*="conversation-turn"]',
    'article',
    'main article',
    'main [class*="markdown"]',
    '.markdown'
  ];

  var prompts = bySelectors(promptSelectors).sort(function (a, b) {
    return promptScore(b) - promptScore(a);
  });
  var bestPrompt = prompts[0] || null;
  var buttons = bySelectors(['button']);
  var sends = bySelectors(sendSelectors).sort(function (a, b) {
    return sendScore(b, bestPrompt) - sendScore(a, bestPrompt);
  });
  var sendCandidates = sends.filter(function (button) {
    var signal = sendSignal(button);
    return sendScore(button, bestPrompt) > 0.45 && signal.intent &&
      !signal.disqualified && !button.disabled &&
      attr(button, 'aria-disabled') !== 'true';
  });
  var bestSend = sendCandidates[0] || null;
  var roleNodes = bySelectors(['[data-message-author-role]']);
  var assistants = roleNodes.filter(function (el) {
    return lower(attr(el, 'data-message-author-role')) === 'assistant';
  });
  var users = roleNodes.filter(function (el) {
    return lower(attr(el, 'data-message-author-role')) === 'user';
  });
  var promptPresent = prompts.some(function (el) {
    return promptScore(el) > 0.35 && visible(el);
  });
  var route = routeGuess(promptPresent);
  var all = q(document, '*');
  var dataTestIds = all.map(function (el) { return attr(el, 'data-testid'); });
  var roles = all.map(function (el) { return attr(el, 'role'); });
  var tags = all.map(function (el) { return el.tagName.toLowerCase(); });
  var states = all.map(function (el) {
    return attr(el, 'data-state') ? 'data-state=' + attr(el, 'data-state') : null;
  });
  var capsule = {
    capsule_schema_version: 1,
    tool: 'glasstty-chatgpt-surface-capsule',
    version: VERSION,
    captured_at: new Date().toISOString(),
    local_only: true,
    paste_transport: {
      edition: 'capsule-safe-ascii',
      no_eval: true,
      no_script_tag_injection: true,
      no_network_writes: true,
      no_storage_reads: true
    },
    page: {
      origin: location.origin,
      host: location.host,
      pathname: location.pathname,
      title_length: str(document.title).length,
      title_hash: hashText(document.title),
      lang: document.documentElement.lang || null,
      ready_state: document.readyState,
      visibility_state: document.visibilityState
    },
    environment: {
      user_agent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      viewport: {
        width: innerWidth,
        height: innerHeight,
        device_pixel_ratio: devicePixelRatio
      },
      focused: document.hasFocus()
    },
    route_posture_guess: {
      posture: route.posture,
      pathname: location.pathname,
      prompt_present: promptPresent,
      evidence: route.evidence
    },
    counts: {
      elements: all.length,
      visible_elements: all.filter(visible).length,
      buttons: buttons.length,
      forms: q(document, 'form').length,
      iframes: q(document, 'iframe').length,
      role_textbox: q(document, '[role="textbox"]').length,
      contenteditable: q(document, '[contenteditable]').length,
      message_author_role_nodes: roleNodes.length,
      assistant_role_nodes: assistants.length,
      user_role_nodes: users.length,
      data_testid_top: topCounts(dataTestIds),
      role_top: topCounts(roles),
      tag_top: topCounts(tags),
      state_attr_top: topCounts(states)
    },
    adapter_recommendation: {
      best_prompt_selector: bestPrompt ? selector(bestPrompt) : null,
      best_prompt_score: bestPrompt ? promptScore(bestPrompt) : 0,
      best_send_selector: bestSend ? selector(bestSend) : null,
      best_send_score: bestSend ? sendScore(bestSend, bestPrompt) : 0,
      latest_assistant_selector: assistants.length ?
        selector(assistants[assistants.length - 1]) : null,
      latest_user_selector: users.length ? selector(users[users.length - 1]) : null,
      has_explicit_author_roles: roleNodes.length > 0,
      plain_chat_submit_allowed_by_route_guess: route.posture === 'plain-chat'
    },
    send_readiness: {
      strict_send_found: Boolean(bestSend),
      strict_send_min_score: SEND_MIN_SCORE,
      composer_text_length: bestPrompt ? textOf(bestPrompt).length : 0,
      empty_composer_missing_send_is_allowed: Boolean(
        bestPrompt && !String(textOf(bestPrompt)).trim() && !bestSend
      ),
      blocked_send_control_found: Boolean(blockedSend),
      blocked_best_control_selector: blockedSend ? selector(blockedSend) : null,
      blocked_best_control_score: blockedSend ? sendScore(blockedSend, bestPrompt) : 0,
      blocked_best_control_disqualified: Boolean(
        blockedSend && sendSignal(blockedSend).disqualified
      )
    },
    top_candidates: {
      prompt: candidate(bestPrompt, bestPrompt ? promptScore(bestPrompt) : 0),
      send: candidate(bestSend, bestSend ? sendScore(bestSend, bestPrompt) : 0),
      assistant: candidate(assistants[assistants.length - 1], null),
      user: candidate(users[users.length - 1], null)
    },
    selector_probe: {
      prompt: probe(promptSelectors),
      send: probe(sendSelectors),
      output: probe(outputSelectors)
    },
    warnings: []
  };

  if (location.hostname !== 'chatgpt.com' &&
      !location.hostname.endsWith('.chatgpt.com')) {
    capsule.warnings.push('Not on chatgpt.com; findings may not match target.');
  }
  if (!capsule.adapter_recommendation.best_prompt_selector) {
    capsule.warnings.push('No likely prompt editor found.');
  }
  if (!capsule.adapter_recommendation.best_send_selector) {
    capsule.warnings.push(
      'No likely send button found; empty composer may cause this.'
    );
  }
  if (!roleNodes.length) {
    capsule.warnings.push('No data-message-author-role nodes in mounted DOM.');
  }

  var json = JSON.stringify(capsule);
  var line = 'GLASSTTY_SURFACE_CAPSULE_JSON=' + json;
  globalThis.__GLASSTTY_CHATGPT_SURFACE_CAPSULE__ = capsule;
  globalThis.__GLASSTTY_CHATGPT_SURFACE_CAPSULE_JSON__ = json;
  globalThis.__GLASSTTY_PRINT_SURFACE_CAPSULE__ = function () {
    console.log(line);
    return capsule;
  };
  globalThis.__GLASSTTY_PROMPT_SURFACE_CAPSULE__ = function () {
    prompt('Copy this GlassTTY surface capsule JSON:', json);
    return capsule;
  };
  globalThis.__GLASSTTY_COPY_SURFACE_CAPSULE__ = function () {
    return copyText(json);
  };
  globalThis.__GLASSTTY_DOWNLOAD_SURFACE_CAPSULE__ = function () {
    var stamp = new Date().toISOString().replace(/[^0-9]/g, '').slice(0, 14);
    return downloadText('glasstty-chatgpt-surface-capsule-' + stamp + '.json', json);
  };
  console.groupCollapsed('GlassTTY ChatGPT surface capsule ' + VERSION);
  console.log('Capsule object:', capsule);
  console.log(line);
  console.log('Fallback helpers:', [
    '__GLASSTTY_PRINT_SURFACE_CAPSULE__()',
    '__GLASSTTY_PROMPT_SURFACE_CAPSULE__()',
    '__GLASSTTY_COPY_SURFACE_CAPSULE__()',
    '__GLASSTTY_DOWNLOAD_SURFACE_CAPSULE__()'
  ]);
  console.groupEnd();
  return capsule;
}());

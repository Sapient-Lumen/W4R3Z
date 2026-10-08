// ==UserScript==
// @name         GlassTTY ChatGPT Surface Oracle
// @namespace    https://glasstty.local/chatgpt
// @version      rev0335-2026.06.13.02.14
// @description  Local ChatGPT surface collector, observer, and send-state drill.
// @author       GlassTTY
// @match        https://chatgpt.com/*
// @run-at       document-idle
// @noframes
// @grant        GM_registerMenuCommand
// @grant        GM_setClipboard
// @grant        GM_download
// @grant        GM_addStyle
// ==/UserScript==
(function glassTtyChatGptSurfaceOracle() {
  'use strict';

  var VERSION = 'rev0335-2026.06.13.02.14';
  var TOOL = 'glasstty-chatgpt-surface-oracle-userscript';
  var CHECKPOINT_PROMPT = 'Reply with exactly this text and nothing else: '
    + 'GLASSTTY-CHECKPOINT';
  var CHECKPOINT_REPLY = 'GLASSTTY-CHECKPOINT';
  var SAMPLE_LIMIT = 96;
  var MAX_MUTATIONS = 240;
  var MAX_ITEMS = 40;
  var OPTIONS = Object.assign({
    include_message_text_samples: false,
    include_editable_text_samples: false,
    include_generic_text_samples: false,
    include_ui_text_samples: true,
    mutation_log_enabled: false,
    mutation_log_text_samples: false,
    write_drill_restore: true,
    write_drill_text: 'GLASSTTY-SEND-STATE-PROBE',
    checkpoint_prompt: CHECKPOINT_PROMPT,
    checkpoint_reply: CHECKPOINT_REPLY,
    checkpoint_timeout_ms: 90000,
    auto_copy_results: true
  }, window.GLASSTTY_SURFACE_ORACLE_OPTIONS || {});

  var STATE = {
    installed_at: nowIso(),
    last_report: null,
    last_capsule: null,
    last_drill: null,
    last_proof: null,
    last_object: null,
    last_object_prefix: null,
    mutation_observer: null,
    route_interval: null,
    route_href: location.href,
    mutation_log: []
  };

  var NON_SEND_TERMS = [
    'add files', 'add file', 'add photos', 'add photo',
    'add files and more', 'composer-plus', 'plus-btn', 'attach',
    'attachment', 'upload', 'file', 'files', 'voice', 'dictate',
    'microphone', 'audio', 'stop', 'cancel', 'search', 'tools',
    'tool', 'deep research', 'model', 'picker', 'reasoning',
    'library', 'canvas', 'email', 'recipient', 'image',
    'create image', 'more', 'menu'
  ];

  var EXPECTED_SURFACE_CONTRACT = {
    contract_version: 'rev0335',
    host: 'chatgpt.com',
    route_posture: 'plain-chat',
    prompt_selector: '#prompt-textarea',
    strict_send_selector: '#composer-submit-button',
    strict_send_testid: 'send-button',
    strict_send_aria_label: 'Send prompt',
    known_blocked_selector: '#composer-plus-btn',
    known_blocked_aria_label: 'Add files and more',
    min_prompt_score: 0.9,
    min_send_score: 0.9,
    min_assistant_roles: 1,
    min_user_roles: 1
  };

  var PROMPT_SELECTORS = [
    '#prompt-textarea', '[data-testid="prompt-textarea"]',
    'textarea[placeholder*="Message" i]',
    'textarea[placeholder*="Ask" i]', 'textarea',
    '[contenteditable="true"][role="textbox"]',
    '[contenteditable="plaintext-only"][role="textbox"]',
    '[role="textbox"]', 'main [data-placeholder*="Message" i]',
    'main [data-placeholder*="Ask" i]',
    'main .ProseMirror[contenteditable]',
    'main [contenteditable="true"]',
    'main [contenteditable="plaintext-only"]', '[contenteditable="true"]',
    '[contenteditable="plaintext-only"]'
  ];

  var SEND_SELECTORS = [
    '#composer-submit-button', 'button#composer-submit-button',
    'button[data-testid="send-button"]', 'button[aria-label*="Send" i]',
    'button[title*="Send" i]', 'form button[type="submit"]', 'button'
  ];

  var OUTPUT_SELECTORS = [
    '[data-message-author-role="assistant"]',
    '[data-message-author-role="assistant"] [class*="markdown"]',
    '[data-testid*="conversation-turn"]', 'article', 'main article',
    'main [class*="markdown"]', '.markdown', '[class*="assistant"]',
    '[class*="message"]', 'main', '[role="main"]'
  ];

  var USER_SELECTORS = [
    '[data-message-author-role="user"]',
    '[data-message-author-role="user"] [class*="message"]',
    '[data-testid*="conversation-turn"]', 'article', 'main article',
    '[class*="user"]', '[class*="message"]'
  ];

  function nowIso() {
    return new Date().toISOString();
  }

  function sleep(ms) {
    return new Promise(function(resolve) {
      window.setTimeout(resolve, ms);
    });
  }

  function compact(value, limit) {
    var text = String(value || '').replace(/\s+/g, ' ').trim();
    return text.slice(0, limit || 20000);
  }

  function lower(value) {
    return compact(value || '').toLowerCase();
  }

  function attr(el, name) {
    return el && el.getAttribute ? el.getAttribute(name) : null;
  }

  function queryAll(root, selector) {
    try {
      return Array.prototype.slice.call(root.querySelectorAll(selector));
    } catch (_error) {
      return [];
    }
  }

  function cssEscape(value) {
    if (window.CSS && CSS.escape) {
      return CSS.escape(String(value));
    }
    return String(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }

  function uniq(items) {
    var seen = Object.create(null);
    var out = [];
    items.forEach(function(item) {
      var key = String(item || '').trim();
      if (!key || seen[key]) return;
      seen[key] = true;
      out.push(key);
    });
    return out;
  }

  function topCounts(values, limit) {
    var counts = Object.create(null);
    values.forEach(function(value) {
      var key = String(value || '').trim();
      if (!key) return;
      counts[key] = (counts[key] || 0) + 1;
    });
    return Object.keys(counts).sort(function(a, b) {
      return counts[b] - counts[a] || a.localeCompare(b);
    }).slice(0, limit || 30).map(function(value) {
      return { value: value, count: counts[value] };
    });
  }

  function rectOf(el) {
    try {
      var rect = el.getBoundingClientRect();
      return {
        x: Math.round(rect.x), y: Math.round(rect.y),
        width: Math.round(rect.width), height: Math.round(rect.height),
        top: Math.round(rect.top), left: Math.round(rect.left),
        bottom: Math.round(rect.bottom), right: Math.round(rect.right)
      };
    } catch (_error) {
      return null;
    }
  }

  function styleOf(el) {
    try {
      var style = getComputedStyle(el);
      return {
        display: style.display, visibility: style.visibility,
        opacity: style.opacity, position: style.position,
        pointerEvents: style.pointerEvents, zIndex: style.zIndex,
        overflow: style.overflow
      };
    } catch (_error) {
      return null;
    }
  }

  function isVisible(el) {
    if (!el || !(el instanceof Element)) return false;
    var rect = rectOf(el);
    var style = styleOf(el);
    return Boolean(rect && style && rect.width > 0 && rect.height > 0
      && style.display !== 'none' && style.visibility !== 'hidden'
      && style.opacity !== '0');
  }

  function textOf(el) {
    if (!el) return '';
    if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
      return el.value || '';
    }
    return el.textContent || '';
  }

  function fnv1a(value) {
    var text = String(value || '').slice(0, 500000);
    var hash = 2166136261;
    for (var index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return 'fnv1a32:' + (hash >>> 0).toString(16).padStart(8, '0');
  }

  function textFingerprint(el, bucket) {
    var raw = textOf(el);
    var normalized = compact(raw, 500000);
    var result = {
      normalized_length: normalized.length,
      raw_length: String(raw || '').length,
      line_count: String(raw || '').split(/\r?\n/).length,
      hash: normalized ? fnv1a(normalized) : null
    };
    if (shouldSampleText(el, bucket) && normalized) {
      result.sample = normalized.slice(0, SAMPLE_LIMIT);
      result.sample_policy = 'ui-label-or-explicitly-enabled';
    }
    return result;
  }

  function authorRoleElement(el) {
    try {
      return el && el.closest ? el.closest('[data-message-author-role]') : null;
    } catch (_error) {
      return null;
    }
  }

  function authorRole(el) {
    return lower(attr(authorRoleElement(el), 'data-message-author-role')) || null;
  }

  function isEditable(el) {
    if (!el) return false;
    var tag = el.tagName ? el.tagName.toLowerCase() : '';
    var type = lower(el.type);
    if (tag === 'textarea') return true;
    if (tag === 'input' && ['button', 'submit', 'hidden', 'checkbox',
      'radio', 'file'].indexOf(type) < 0) return true;
    var ce = attr(el, 'contenteditable');
    return Boolean((ce !== null && lower(ce) !== 'false')
      || attr(el, 'role') === 'textbox');
  }

  function shouldSampleText(el, bucket) {
    if (!el) return false;
    if (authorRole(el) && !OPTIONS.include_message_text_samples) return false;
    if (isEditable(el) && !OPTIONS.include_editable_text_samples) return false;
    if (OPTIONS.include_generic_text_samples) return true;
    if (!OPTIONS.include_ui_text_samples) return false;
    var tag = el.tagName ? el.tagName.toLowerCase() : '';
    if (['button', 'summary', 'label', 'option'].indexOf(tag) >= 0) return true;
    return /button|control|dialog|form|nav|toolbar|selector/.test(bucket || '');
  }

  function uniqueSelector(el) {
    if (!el || !el.tagName) return null;
    var doc = el.ownerDocument || document;
    var id = attr(el, 'id');
    if (id) {
      var idSelector = '#' + cssEscape(id);
      if (queryAll(doc, idSelector).length === 1) return idSelector;
    }
    var testid = attr(el, 'data-testid');
    if (testid) {
      var testSelector = '[data-testid=' + JSON.stringify(testid) + ']';
      if (queryAll(doc, testSelector).length === 1) return testSelector;
    }
    var parts = [];
    var node = el;
    while (node && node.nodeType === 1 && node !== doc.documentElement
      && parts.length < 8) {
      var tag = node.tagName.toLowerCase();
      var nodeId = attr(node, 'id');
      if (nodeId) {
        parts.unshift(tag + '#' + cssEscape(nodeId));
        break;
      }
      var nth = 1;
      var previous = node.previousElementSibling;
      while (previous) {
        if (previous.tagName === node.tagName) nth += 1;
        previous = previous.previousElementSibling;
      }
      parts.unshift(tag + ':nth-of-type(' + nth + ')');
      node = node.parentElement;
    }
    return parts.join(' > ') || el.tagName.toLowerCase();
  }

  function classTokens(el) {
    return uniq(String(attr(el, 'class') || '').split(/\s+/)).slice(0, 12);
  }

  function ancestry(el) {
    var out = [];
    var node = el;
    while (node && node instanceof Element && out.length < 7) {
      out.push({
        tag: node.tagName.toLowerCase(), id: attr(node, 'id') || undefined,
        role: attr(node, 'role') || undefined,
        testid: attr(node, 'data-testid') || undefined,
        author_role: attr(node, 'data-message-author-role') || undefined,
        classes: classTokens(node).slice(0, 5)
      });
      node = node.parentElement;
    }
    return out;
  }

  function nearestContext(el) {
    var form = el && el.closest ? el.closest('form') : null;
    var dialog = el && el.closest ? el.closest(
      'dialog, [role="dialog"], [role="alertdialog"], [aria-modal="true"]'
    ) : null;
    var composer = el && el.closest ? el.closest(
      'form, [data-testid*="composer"], [class*="composer"], [role="form"]'
    ) : null;
    var message = authorRoleElement(el);
    return {
      form_selector: form ? uniqueSelector(form) : null,
      dialog_selector: dialog ? uniqueSelector(dialog) : null,
      composer_selector: composer ? uniqueSelector(composer) : null,
      message_selector: message ? uniqueSelector(message) : null,
      message_author_role: message ? attr(message, 'data-message-author-role') : null
    };
  }

  function elementSummary(el, bucket, extra) {
    if (!el) return null;
    var roleNode = authorRoleElement(el);
    var turnId = attr(el, 'data-turn-id') || attr(roleNode, 'data-turn-id');
    return Object.assign({
      bucket: bucket || 'generic', tag: el.tagName ? el.tagName.toLowerCase() : null,
      selector: uniqueSelector(el), visible: isVisible(el), rect: rectOf(el),
      style: styleOf(el), id: attr(el, 'id'), role: attr(el, 'role'),
      data_testid: attr(el, 'data-testid'),
      data_message_author_role: attr(el, 'data-message-author-role'),
      nearest_author_role: authorRole(el),
      nearest_author_role_source: roleNode ? (roleNode === el ? 'self' : 'ancestor') : null,
      aria_label: attr(el, 'aria-label'), title: attr(el, 'title'),
      placeholder: attr(el, 'placeholder'),
      data_placeholder: attr(el, 'data-placeholder'), name: attr(el, 'name'),
      type: attr(el, 'type'), contenteditable: attr(el, 'contenteditable'),
      disabled: Boolean(el.disabled), readOnly: Boolean(el.readOnly),
      class_tokens: classTokens(el), data_turn_id_present: Boolean(turnId),
      data_turn_id_hash: turnId ? fnv1a(turnId) : null,
      child_element_count: el.children ? el.children.length : 0,
      descendant_counts: {
        buttons: queryAll(el, 'button').length,
        links: queryAll(el, 'a[href]').length,
        code_blocks: queryAll(el, 'pre, code').length,
        images: queryAll(el, 'img, picture, svg').length,
        inputs: queryAll(el, 'input, textarea, [contenteditable], [role="textbox"]').length
      },
      text: textFingerprint(el, bucket || 'generic'),
      nearest: nearestContext(el), ancestry: ancestry(el)
    }, extra || {});
  }

  function promptScore(el) {
    var score = isVisible(el) ? 0.45 : 0.03;
    var id = lower(attr(el, 'id'));
    var testid = lower(attr(el, 'data-testid'));
    var placeholder = lower(attr(el, 'placeholder'));
    var dataPlaceholder = lower(attr(el, 'data-placeholder'));
    var aria = lower(attr(el, 'aria-label'));
    var role = lower(attr(el, 'role'));
    var klass = lower(attr(el, 'class'));
    if (!isEditable(el)) score -= 0.35;
    if (id === 'prompt-textarea') score += 0.35;
    if (testid.indexOf('prompt-textarea') >= 0) score += 0.35;
    if (el instanceof HTMLTextAreaElement) score += 0.25;
    if (role === 'textbox') score += 0.22;
    if (attr(el, 'contenteditable') !== null) score += 0.18;
    if (hasAny(placeholder, ['message', 'ask anything', 'chatgpt', 'prompt'])) {
      score += 0.2;
    }
    if (hasAny(dataPlaceholder, ['message', 'ask anything', 'chatgpt', 'prompt'])) {
      score += 0.2;
    }
    if (hasAny(aria, ['message', 'prompt', 'ask', 'chatgpt'])) score += 0.16;
    if (klass.indexOf('composer') >= 0 || klass.indexOf('prompt') >= 0) score += 0.08;
    if (hasAny(id + ' ' + testid + ' ' + aria, ['search', 'filter', 'email'])) {
      score -= 0.28;
    }
    return Number(score.toFixed(3));
  }

  function hasAny(value, terms) {
    return terms.some(function(term) {
      return value.indexOf(term) >= 0;
    });
  }

  function sendControlSignal(button) {
    var text = lower(button.textContent);
    var aria = lower(attr(button, 'aria-label'));
    var title = lower(attr(button, 'title'));
    var testid = lower(attr(button, 'data-testid'));
    var id = lower(attr(button, 'id'));
    var type = lower(attr(button, 'type'));
    var combined = [text, aria, title, testid, id, type].join(' ');
    var explicit = testid === 'send-button'
      || testid.indexOf('send-button') >= 0
      || testid.indexOf('send-message') >= 0
      || id === 'composer-submit-button' || id === 'send-button'
      || aria === 'send' || aria.indexOf('send message') >= 0
      || aria.indexOf('send prompt') >= 0
      || title === 'send' || title.indexOf('send message') >= 0
      || text === 'send';
    var submit = type === 'submit';
    var blocked = id === 'composer-plus-btn' || testid === 'composer-plus-btn'
      || (hasAny(combined, NON_SEND_TERMS) && !explicit);
    return { intent: explicit || submit, explicit: explicit, submit: submit,
      disqualified: blocked, combined: combined };
  }

  function composerRoot(composer) {
    if (!composer) return document;
    return composer.closest(
      'form, [data-testid*="composer"], [class*="composer"], [role="form"]'
    ) || composer.parentElement || document;
  }

  function sendButtonScore(button, composer) {
    var score = isVisible(button) ? 0.3 : 0.02;
    var signal = sendControlSignal(button);
    var text = lower(button.textContent);
    var aria = lower(attr(button, 'aria-label'));
    var title = lower(attr(button, 'title'));
    var testid = lower(attr(button, 'data-testid'));
    var type = lower(attr(button, 'type'));
    var disabled = button.disabled || attr(button, 'aria-disabled') === 'true';
    if (disabled) score -= 0.8;
    if (!signal.intent) score -= 0.35;
    if (signal.disqualified) score -= 1.0;
    if (testid === 'send-button' || testid.indexOf('send') >= 0) score += 0.5;
    if (aria === 'send' || aria.indexOf('send message') >= 0) score += 0.45;
    if (aria.indexOf('send prompt') >= 0) score += 0.45;
    if (title === 'send' || title.indexOf('send message') >= 0) score += 0.32;
    if (text === 'send') score += 0.3;
    if (type === 'submit') score += 0.18;
    if (composer) {
      var root = composerRoot(composer);
      if (root !== document && root.contains(button)) score += 0.16;
      var form = composer.closest ? composer.closest('form') : null;
      if (form && button.form && button.form === form) score += 0.2;
    } else {
      score -= 0.12;
    }
    if (button.closest('nav, header, aside')) score -= 0.18;
    return Number(score.toFixed(3));
  }

  function outputScore(el) {
    var score = isVisible(el) ? 0.35 : 0.04;
    var role = authorRole(el);
    var klass = lower(attr(el, 'class'));
    var testid = lower(attr(el, 'data-testid'));
    var text = textOf(el);
    if (role === 'assistant') score += 0.55;
    if (role === 'user') score -= 0.55;
    if (testid.indexOf('conversation-turn') >= 0) score += 0.18;
    if (el.tagName === 'ARTICLE') score += 0.16;
    if (klass.indexOf('markdown') >= 0) score += 0.14;
    if (klass.indexOf('assistant') >= 0) score += 0.18;
    if (text.length > 30) score += 0.12;
    if (text.length > 5000) score -= 0.08;
    return Number(score.toFixed(3));
  }

  function userScore(el) {
    var score = isVisible(el) ? 0.34 : 0.03;
    var role = authorRole(el);
    var klass = lower(attr(el, 'class'));
    var testid = lower(attr(el, 'data-testid'));
    var text = textOf(el);
    if (role === 'user') score += 0.55;
    if (role === 'assistant') score -= 0.55;
    if (testid.indexOf('conversation-turn') >= 0) score += 0.16;
    if (klass.indexOf('user') >= 0) score += 0.18;
    if (text.length > 12) score += 0.08;
    if (text.length > 5000) score -= 0.16;
    return Number(score.toFixed(3));
  }

  function ranked(selectors, scorer) {
    var seen = [];
    var rows = [];
    selectors.forEach(function(selector) {
      queryAll(document, selector).forEach(function(el) {
        if (seen.indexOf(el) >= 0) return;
        seen.push(el);
        rows.push({ node: el, score: scorer(el) });
      });
    });
    return rows.sort(function(a, b) {
      return b.score - a.score;
    });
  }

  function bestPrompt() {
    var row = ranked(PROMPT_SELECTORS, promptScore).filter(function(item) {
      return item.node instanceof HTMLElement && item.score > 0.35;
    })[0];
    return row || null;
  }

  function sendCandidates(composer) {
    var root = composerRoot(composer);
    var scopes = root === document ? [document] : [root, document];
    var seen = [];
    var out = [];
    scopes.forEach(function(scope) {
      SEND_SELECTORS.forEach(function(selector) {
        queryAll(scope, selector).forEach(function(button) {
          if (!(button instanceof HTMLButtonElement)) return;
          if (seen.indexOf(button) >= 0) return;
          seen.push(button);
          out.push({
            node: button, score: sendButtonScore(button, composer),
            signal: sendControlSignal(button), scope: scope === document ? 'document' : 'composer'
          });
        });
      });
    });
    return out.sort(function(a, b) {
      return b.score - a.score;
    });
  }

  function bestStrictSend(composer) {
    return sendCandidates(composer).filter(function(item) {
      return item.score >= 0.45 && item.signal.intent && !item.signal.disqualified
        && !item.node.disabled && attr(item.node, 'aria-disabled') !== 'true';
    })[0] || null;
  }

  function bestBlockedSend(composer) {
    return sendCandidates(composer).filter(function(item) {
      return item.signal.disqualified;
    })[0] || null;
  }

  function latestByRole(role) {
    var nodes = queryAll(document, '[data-message-author-role="' + role + '"]');
    return nodes[nodes.length - 1] || null;
  }

  function selectorProbe(selectors) {
    return selectors.map(function(selector) {
      var nodes = queryAll(document, selector);
      return {
        selector: selector, count: nodes.length,
        visible_count: nodes.filter(isVisible).length,
        first_selectors: nodes.slice(0, 8).map(uniqueSelector)
      };
    });
  }

  function routePosture() {
    var pathname = location.pathname.toLowerCase();
    var promptPresent = Boolean(bestPrompt());
    var evidence = ['path:' + pathname, promptPresent ? 'composer:present'
      : 'composer:missing'];
    if ((pathname === '/' || pathname.indexOf('/c/') === 0) && promptPresent) {
      evidence.push('plain-chat-path-and-composer');
      return { posture: 'plain-chat', pathname: pathname,
        prompt_present: promptPresent, evidence: evidence };
    }
    if (pathname.indexOf('/auth/') >= 0 || pathname.indexOf('/login') >= 0) {
      evidence.push('auth-path');
      return { posture: 'login-or-marketing', pathname: pathname,
        prompt_present: promptPresent, evidence: evidence };
    }
    if (hasAny(pathname, ['/agent', '/tasks', '/task/'])) {
      evidence.push('agent-or-task-path');
      return { posture: 'agent-or-tool', pathname: pathname,
        prompt_present: promptPresent, evidence: evidence };
    }
    if (hasAny(pathname, ['/canvas', '/artifact'])) {
      evidence.push('canvas-or-artifact-path');
      return { posture: 'canvas-or-artifact', pathname: pathname,
        prompt_present: promptPresent, evidence: evidence };
    }
    if (hasAny(pathname, ['/g/', '/gpts', '/project', '/projects'])) {
      evidence.push('project-or-gpt-path');
      return { posture: 'project-or-gpt', pathname: pathname,
        prompt_present: promptPresent, evidence: evidence };
    }
    if (promptPresent) evidence.push('composer-present-no-blocking-route-signal');
    return { posture: promptPresent ? 'plain-chat' : 'unknown', pathname: pathname,
      prompt_present: promptPresent, evidence: evidence };
  }

  function scriptInventory() {
    return queryAll(document, 'script[src]').slice(0, 80).map(function(script) {
      try {
        var url = new URL(script.src, location.href);
        return { origin: url.origin, pathname: url.pathname,
          async: script.async, defer: script.defer, type: attr(script, 'type') };
      } catch (_error) {
        return { src_length: String(script.src || '').length,
          async: script.async, defer: script.defer, type: attr(script, 'type') };
      }
    });
  }

  function resourceInventory() {
    var entries = [];
    try {
      entries = performance.getEntriesByType('resource') || [];
    } catch (_error) {
      entries = [];
    }
    return entries.slice(-80).map(function(entry) {
      var item = { initiatorType: entry.initiatorType || null,
        duration_ms: Math.round(entry.duration || 0), transferSize: entry.transferSize || 0 };
      try {
        var url = new URL(entry.name, location.href);
        item.origin = url.origin;
        item.pathname = url.pathname.slice(0, 120);
      } catch (_error) {
        item.name_length = String(entry.name || '').length;
      }
      return item;
    });
  }

  function frameInventory() {
    return queryAll(document, 'iframe').map(function(frame, index) {
      var item = { index: index, selector: uniqueSelector(frame), visible: isVisible(frame),
        rect: rectOf(frame), id: attr(frame, 'id'), name: attr(frame, 'name'),
        title: attr(frame, 'title'), sandbox: attr(frame, 'sandbox'),
        allow: attr(frame, 'allow'), accessible: false, src_origin: null,
        src_pathname: null };
      try {
        var url = new URL(attr(frame, 'src') || frame.src || '', location.href);
        item.src_origin = url.origin;
        item.src_pathname = url.pathname;
      } catch (_error) {}
      try {
        var doc = frame.contentDocument || frame.contentWindow.document;
        item.accessible = Boolean(doc && doc.documentElement);
        item.accessible_title_length = doc.title ? doc.title.length : 0;
        item.accessible_element_count = queryAll(doc, '*').length;
      } catch (_error) {
        item.accessible = false;
      }
      return item;
    });
  }

  function summarize(name, rows, mapper) {
    return {
      name: name, total: rows.length,
      visible_total: rows.map(function(row) {
        return row.node || row;
      }).filter(isVisible).length,
      included: Math.min(rows.length, MAX_ITEMS),
      items: rows.slice(0, MAX_ITEMS).map(mapper)
    };
  }

  function captureReport(kind) {
    var started = performance.now();
    var all = queryAll(document, '*');
    var prompt = bestPrompt();
    var composer = prompt ? prompt.node : null;
    var sends = sendCandidates(composer);
    var strictSend = bestStrictSend(composer);
    var blockedSend = bestBlockedSend(composer);
    var assistant = latestByRole('assistant');
    var user = latestByRole('user');
    var roleNodes = queryAll(document, '[data-message-author-role]');
    var buttons = queryAll(document, 'button');
    var tags = all.map(function(el) { return el.tagName.toLowerCase(); });
    var roles = all.map(function(el) { return attr(el, 'role'); }).filter(Boolean);
    var testids = all.map(function(el) { return attr(el, 'data-testid'); }).filter(Boolean);
    var stateAttrs = [];
    all.forEach(function(el) {
      ['data-state', 'aria-busy', 'aria-current', 'aria-selected',
        'aria-pressed', 'aria-expanded'].forEach(function(name) {
        var value = attr(el, name);
        if (value) stateAttrs.push(name + '=' + value);
      });
    });
    var report = {
      schema_version: 1, tool: TOOL, version: VERSION,
      report_kind: kind || 'full', captured_at: nowIso(), local_only: true,
      userscript: {
        manager: typeof GM_info === 'object' && GM_info.scriptHandler
          ? GM_info.scriptHandler : null,
        script_name: typeof GM_info === 'object' && GM_info.script
          ? GM_info.script.name : null,
        grants: ['GM_registerMenuCommand', 'GM_setClipboard', 'GM_download']
      },
      privacy_defaults: {
        message_text_samples_included: Boolean(OPTIONS.include_message_text_samples),
        editable_text_samples_included: Boolean(OPTIONS.include_editable_text_samples),
        generic_text_samples_included: Boolean(OPTIONS.include_generic_text_samples),
        ui_text_samples_included: Boolean(OPTIONS.include_ui_text_samples),
        no_cookie_read: true, no_local_storage_read: true,
        no_session_storage_read: true, no_indexed_db_read: true,
        no_network_writes: true, no_auto_submit: true
      },
      page: {
        href_hash: fnv1a(location.href), origin: location.origin, host: location.host,
        pathname: location.pathname, search_param_keys: Array.from(
          new URLSearchParams(location.search).keys()
        ).sort(), title_length: document.title.length,
        title_hash: fnv1a(document.title), lang: document.documentElement.lang || null,
        ready_state: document.readyState, visibility_state: document.visibilityState
      },
      environment: {
        user_agent: navigator.userAgent, platform: navigator.platform,
        language: navigator.language, languages: navigator.languages,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        viewport: { width: innerWidth, height: innerHeight,
          device_pixel_ratio: devicePixelRatio }, focused: document.hasFocus(),
        is_secure_context: isSecureContext,
        cross_origin_isolated: crossOriginIsolated
      },
      framework_markers: {
        next_data_present: Boolean(document.getElementById('__NEXT_DATA__')),
        app_roots: selectorProbe(['#__next', '[data-reactroot]', '[data-radix-portal]',
          '[id^="radix-"]', '[data-state]']),
        scripts: scriptInventory(), resources: resourceInventory()
      },
      route_posture_guess: routePosture(),
      counts: {
        elements: all.length, visible_elements: all.filter(isVisible).length,
        buttons: buttons.length, forms: queryAll(document, 'form').length,
        iframes: queryAll(document, 'iframe').length,
        role_textbox: queryAll(document, '[role="textbox"]').length,
        contenteditable: queryAll(document, '[contenteditable]').length,
        message_author_role_nodes: roleNodes.length,
        assistant_role_nodes: queryAll(document,
          '[data-message-author-role="assistant"]').length,
        user_role_nodes: queryAll(document, '[data-message-author-role="user"]').length,
        conversation_turn_like_nodes: queryAll(document,
          '[data-testid*="conversation-turn"], article').length,
        markdown_or_code_blocks: queryAll(document,
          'main [class*="markdown"], .markdown, pre, code').length,
        data_testid_top: topCounts(testids), role_top: topCounts(roles),
        tag_top: topCounts(tags), state_attr_top: topCounts(stateAttrs)
      },
      selector_probe: {
        prompt: selectorProbe(PROMPT_SELECTORS), send: selectorProbe(SEND_SELECTORS),
        output: selectorProbe(OUTPUT_SELECTORS), user_turn: selectorProbe(USER_SELECTORS),
        generation: selectorProbe(['button[aria-label*="Stop" i]',
          'button[aria-label*="Continue" i]', '[aria-busy="true"]'])
      },
      composer_state: composerState(composer),
      send_state: sendState(composer, strictSend, blockedSend, sends),
      adapter_recommendation: {
        best_prompt_selector: prompt ? uniqueSelector(prompt.node) : null,
        best_prompt_score: prompt ? prompt.score : 0,
        best_send_selector: strictSend ? uniqueSelector(strictSend.node) : null,
        best_send_score: strictSend ? strictSend.score : 0,
        blocked_send_selector: blockedSend ? uniqueSelector(blockedSend.node) : null,
        blocked_send_score: blockedSend ? blockedSend.score : 0,
        latest_assistant_selector: assistant ? uniqueSelector(assistant) : null,
        latest_user_selector: user ? uniqueSelector(user) : null,
        has_explicit_author_roles: roleNodes.length > 0,
        plain_chat_submit_allowed_by_route_guess: routePosture().posture === 'plain-chat'
      },
      top_candidates: {
        prompt: prompt ? elementSummary(prompt.node, 'prompt', { score: prompt.score }) : null,
        send: strictSend ? elementSummary(strictSend.node, 'send', {
          score: strictSend.score, signal: strictSend.signal
        }) : null,
        blocked_send: blockedSend ? elementSummary(blockedSend.node, 'blocked_send', {
          score: blockedSend.score, signal: blockedSend.signal
        }) : null,
        assistant: assistant ? elementSummary(assistant, 'assistant') : null,
        user: user ? elementSummary(user, 'user') : null
      },
      candidates: kind === 'capsule' ? undefined : {
        prompt_editors: summarize('prompt_editors', ranked(PROMPT_SELECTORS,
          promptScore), function(item) {
          return elementSummary(item.node, 'prompt', { score: item.score });
        }),
        send_buttons: summarize('send_buttons', sends, function(item) {
          return elementSummary(item.node, 'send', {
            score: item.score, signal: item.signal, scope: item.scope
          });
        }),
        assistant_messages: summarize('assistant_messages', queryAll(document,
          '[data-message-author-role="assistant"]'), function(node) {
          return elementSummary(node, 'assistant');
        }),
        user_messages: summarize('user_messages', queryAll(document,
          '[data-message-author-role="user"]'), function(node) {
          return elementSummary(node, 'user');
        })
      },
      active_element: document.activeElement ? elementSummary(document.activeElement,
        'active_element') : null,
      frames: frameInventory(),
      mutation_log: STATE.mutation_log.slice(-80),
      warnings: [], runtime_ms: null
    };
    report.runtime_ms = Math.round(performance.now() - started);
    report.surface_contract_drift = surfaceContractDrift(report);
    if (report.surface_contract_drift.verdict !== 'surface-contract-ok') {
      report.warnings.push('Surface contract drift: '
        + report.surface_contract_drift.verdict);
    }
    if (!composer) report.warnings.push('No prompt composer found.');
    if (!strictSend) {
      report.warnings.push('No strict send button found; this is expected when empty.');
    }
    if (blockedSend) {
      report.warnings.push('A non-send composer control was blocked as a send candidate.');
    }
    if (!roleNodes.length) report.warnings.push('No data-message-author-role nodes found.');
    STATE.last_report = report;
    STATE.last_capsule = makeCapsule(report);
    return report;
  }

  function composerState(composer) {
    if (!composer) return { present: false };
    var root = composerRoot(composer);
    return {
      present: true, selector: uniqueSelector(composer), root_selector: uniqueSelector(root),
      tag: composer.tagName.toLowerCase(), role: attr(composer, 'role'),
      contenteditable: attr(composer, 'contenteditable'), text: textFingerprint(composer,
        'composer'), focused: composer === document.activeElement,
      placeholder_nodes: queryAll(root, '[data-placeholder], [placeholder]').slice(0, 8)
        .map(function(node) { return elementSummary(node, 'placeholder'); }),
      root_buttons: queryAll(root, 'button').slice(0, 20).map(function(button) {
        return elementSummary(button, 'composer_button', {
          score: sendButtonScore(button, composer), signal: sendControlSignal(button)
        });
      })
    };
  }

  function sendState(composer, strictSend, blockedSend, sends) {
    return {
      strict_send_found: Boolean(strictSend),
      blocked_send_control_found: Boolean(blockedSend),
      empty_composer_missing_send_is_allowed: !strictSend,
      best_strict_send: strictSend ? elementSummary(strictSend.node, 'send', {
        score: strictSend.score, signal: strictSend.signal
      }) : null,
      best_blocked_control: blockedSend ? elementSummary(blockedSend.node,
        'blocked_send', { score: blockedSend.score, signal: blockedSend.signal }) : null,
      top_button_signals: sends.slice(0, 12).map(function(item) {
        return elementSummary(item.node, 'send_candidate', {
          score: item.score, signal: item.signal, scope: item.scope
        });
      })
    };
  }

  function surfaceContractDrift(report) {
    var contract = EXPECTED_SURFACE_CONTRACT;
    var blockers = [];
    var warnings = [];
    var adapter = report.adapter_recommendation || {};
    var counts = report.counts || {};
    var send = report.send_state && report.send_state.best_strict_send
      ? report.send_state.best_strict_send : {};
    var blocked = report.send_state && report.send_state.best_blocked_control
      ? report.send_state.best_blocked_control : {};
    if (report.page.host !== contract.host) {
      blockers.push({ signal: 'not_chatgpt_host', observed: report.page.host });
    }
    if (report.route_posture_guess.posture !== contract.route_posture) {
      blockers.push({ signal: 'not_plain_chat_route',
        observed: report.route_posture_guess.posture });
    }
    if (adapter.best_prompt_selector !== contract.prompt_selector
      || adapter.best_prompt_score < contract.min_prompt_score) {
      blockers.push({ signal: 'prompt_contract_mismatch',
        selector: adapter.best_prompt_selector, score: adapter.best_prompt_score });
    }
    if (adapter.best_send_selector !== contract.strict_send_selector
      || adapter.best_send_score < contract.min_send_score) {
      blockers.push({ signal: 'strict_send_contract_mismatch',
        selector: adapter.best_send_selector, score: adapter.best_send_score });
    }
    if (send.data_testid && send.data_testid !== contract.strict_send_testid) {
      blockers.push({ signal: 'strict_send_testid_changed',
        observed: send.data_testid });
    }
    if (send.aria_label && send.aria_label !== contract.strict_send_aria_label) {
      warnings.push({ signal: 'strict_send_label_changed',
        observed: send.aria_label });
    }
    if (blocked.selector !== contract.known_blocked_selector) {
      warnings.push({ signal: 'known_non_send_control_missing',
        observed: blocked.selector || null });
    }
    if (counts.assistant_role_nodes < contract.min_assistant_roles) {
      blockers.push({ signal: 'assistant_roles_below_contract',
        observed: counts.assistant_role_nodes });
    }
    if (counts.user_role_nodes < contract.min_user_roles) {
      blockers.push({ signal: 'user_roles_below_contract',
        observed: counts.user_role_nodes });
    }
    return {
      contract_version: contract.contract_version,
      verdict: blockers.length ? 'surface-drift-blocker'
        : warnings.length ? 'surface-drift-warning' : 'surface-contract-ok',
      blockers: blockers, warnings: warnings,
      summary: {
        prompt_selector: adapter.best_prompt_selector,
        strict_send_selector: adapter.best_send_selector,
        strict_send_testid: send.data_testid || null,
        strict_send_aria_label: send.aria_label || null,
        blocked_send_selector: blocked.selector || null,
        route_posture: report.route_posture_guess.posture,
        assistant_role_nodes: counts.assistant_role_nodes,
        user_role_nodes: counts.user_role_nodes
      }
    };
  }

  function makeCapsule(report) {
    return {
      capsule_schema_version: 2, tool: TOOL, version: VERSION,
      source_report_kind: report.report_kind, captured_at: report.captured_at,
      page: report.page, environment: report.environment,
      route_posture_guess: report.route_posture_guess, counts: report.counts,
      adapter_recommendation: report.adapter_recommendation,
      composer_state: {
        present: report.composer_state.present,
        selector: report.composer_state.selector,
        text: report.composer_state.text
      },
      send_state: report.send_state,
      surface_contract_drift: report.surface_contract_drift,
      warnings: report.warnings
    };
  }

  function readComposer(composer) {
    return textOf(composer);
  }

  function setNativeValue(node, text) {
    var proto = Object.getPrototypeOf(node);
    var descriptor = Object.getOwnPropertyDescriptor(proto, 'value');
    if (descriptor && descriptor.set) descriptor.set.call(node, text);
    else node.value = text;
  }

  function dispatchEditEvents(node, text) {
    try {
      node.dispatchEvent(new InputEvent('beforeinput', {
        bubbles: true, cancelable: true, data: text, inputType: 'insertText'
      }));
    } catch (_error) {}
    try {
      node.dispatchEvent(new InputEvent('input', {
        bubbles: true, data: text, inputType: 'insertText'
      }));
    } catch (_error2) {}
    node.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function writeComposer(composer, text) {
    composer.focus();
    if (composer instanceof HTMLInputElement || composer instanceof HTMLTextAreaElement) {
      setNativeValue(composer, text);
      dispatchEditEvents(composer, text);
      return readComposer(composer).trim() === text.trim();
    }
    if (attr(composer, 'contenteditable') !== null || attr(composer, 'role') === 'textbox') {
      var doc = composer.ownerDocument;
      var selection = doc.getSelection();
      if (selection) {
        var range = doc.createRange();
        range.selectNodeContents(composer);
        selection.removeAllRanges();
        selection.addRange(range);
      }
      var inserted = false;
      try {
        inserted = doc.execCommand('insertText', false, text);
      } catch (_error) {
        inserted = false;
      }
      if (!inserted) composer.textContent = text;
      dispatchEditEvents(composer, text);
      return compact(readComposer(composer)) === compact(text);
    }
    return false;
  }

  async function runSendDrill() {
    var before = captureReport('send-drill-before');
    var prompt = bestPrompt();
    var composer = prompt ? prompt.node : null;
    var originalText = composer ? readComposer(composer) : '';
    var originalHtml = composer && !(composer instanceof HTMLInputElement)
      && !(composer instanceof HTMLTextAreaElement) ? composer.innerHTML : null;
    var writeOk = false;
    if (composer) writeOk = writeComposer(composer, OPTIONS.write_drill_text);
    await sleep(450);
    var after = captureReport('send-drill-after-write');
    if (composer && OPTIONS.write_drill_restore) {
      if (composer instanceof HTMLInputElement || composer instanceof HTMLTextAreaElement) {
        setNativeValue(composer, originalText);
        dispatchEditEvents(composer, originalText);
      } else if (originalHtml !== null) {
        composer.innerHTML = originalHtml;
        dispatchEditEvents(composer, originalText);
      }
      await sleep(150);
    }
    var restored = composer ? compact(readComposer(composer)) === compact(originalText) : false;
    var result = {
      schema_version: 1, tool: TOOL, version: VERSION,
      drill: 'send-state-write-readback-no-submit', captured_at: nowIso(),
      local_only: true, prompt_selector: prompt ? uniqueSelector(prompt.node) : null,
      write_text_hash: fnv1a(OPTIONS.write_drill_text), write_ok: writeOk,
      restored: restored, before_capsule: makeCapsule(before),
      after_capsule: makeCapsule(after), submitted: false
    };
    STATE.last_drill = result;
    var prefix = 'GLASSTTY_USER_SURFACE_DRILL_JSON=';
    logJson(prefix, result);
    await rememberAndCopy(prefix, result);
    return result;
  }

  function startObserver() {
    if (STATE.mutation_observer) return { already_running: true };
    STATE.mutation_log = [];
    STATE.mutation_observer = new MutationObserver(function(mutations) {
      mutations.slice(0, 24).forEach(function(mutation) {
        var target = mutation.target instanceof Element ? mutation.target : null;
        STATE.mutation_log.push({
          at: nowIso(), type: mutation.type,
          target: target ? elementSummary(target, 'mutation_target') : null,
          attribute_name: mutation.attributeName || null,
          added_nodes: mutation.addedNodes ? mutation.addedNodes.length : 0,
          removed_nodes: mutation.removedNodes ? mutation.removedNodes.length : 0,
          route_href_hash: fnv1a(location.href)
        });
      });
      if (STATE.mutation_log.length > MAX_MUTATIONS) {
        STATE.mutation_log = STATE.mutation_log.slice(-MAX_MUTATIONS);
      }
    });
    STATE.mutation_observer.observe(document.body || document.documentElement, {
      childList: true, subtree: true, attributes: true, characterData: false,
      attributeFilter: ['aria-label', 'aria-disabled', 'disabled', 'data-testid',
        'data-state', 'aria-busy', 'aria-expanded', 'contenteditable']
    });
    STATE.route_href = location.href;
    STATE.route_interval = window.setInterval(function() {
      if (location.href !== STATE.route_href) {
        STATE.mutation_log.push({ at: nowIso(), type: 'route-change',
          from_hash: fnv1a(STATE.route_href), to_hash: fnv1a(location.href),
          pathname: location.pathname });
        STATE.route_href = location.href;
      }
    }, 500);
    return { started: true, at: nowIso() };
  }

  function stopObserver() {
    if (STATE.mutation_observer) STATE.mutation_observer.disconnect();
    STATE.mutation_observer = null;
    if (STATE.route_interval) window.clearInterval(STATE.route_interval);
    STATE.route_interval = null;
    return { stopped: true, entries: STATE.mutation_log.length };
  }

  async function armedCheckpointProof() {
    var message = 'GlassTTY will write and submit the checkpoint prompt in this chat.';
    if (!window.confirm(message + '\n\nContinue?')) return { cancelled: true };
    var prompt = bestPrompt();
    if (!prompt) return { error: 'no prompt composer' };
    var writeOk = writeComposer(prompt.node, OPTIONS.checkpoint_prompt);
    await sleep(450);
    var send = bestStrictSend(prompt.node);
    var preSubmit = captureReport('armed-proof-before-submit');
    if (!writeOk || !send) {
      return { error: 'write or strict send unavailable', write_ok: writeOk,
        pre_submit_capsule: makeCapsule(preSubmit) };
    }
    if (!window.confirm('Submit visible GLASSTTY checkpoint prompt now?')) {
      return { cancelled: true, write_ok: writeOk,
        pre_submit_capsule: makeCapsule(preSubmit) };
    }
    send.node.click();
    var deadline = Date.now() + Number(OPTIONS.checkpoint_timeout_ms || 90000);
    var matched = false;
    var latest = null;
    while (Date.now() < deadline) {
      await sleep(1000);
      latest = latestByRole('assistant');
      if (latest && compact(textOf(latest)).indexOf(OPTIONS.checkpoint_reply) >= 0) {
        matched = true;
        break;
      }
    }
    var finalReport = captureReport('armed-proof-after-submit');
    var result = {
      schema_version: 1, tool: TOOL, version: VERSION,
      proof: 'armed-checkpoint-submit', submitted: true,
      expected_reply: OPTIONS.checkpoint_reply, matched: matched,
      final_capsule: makeCapsule(finalReport), captured_at: nowIso()
    };
    STATE.last_proof = result;
    var prefix = 'GLASSTTY_USER_SURFACE_PROOF_JSON=';
    logJson(prefix, result);
    await rememberAndCopy(prefix, result);
    return result;
  }

  function notify(message) {
    try {
      var node = document.createElement('div');
      node.className = 'glasstty-oracle-note';
      node.textContent = message;
      document.documentElement.appendChild(node);
      window.setTimeout(function() { node.remove(); }, 2500);
    } catch (_error) {}
  }

  async function rememberAndCopy(prefix, object) {
    STATE.last_object = object;
    STATE.last_object_prefix = prefix;
    var line = prefix + JSON.stringify(object);
    if (!OPTIONS.auto_copy_results) return { line: line, copy: { ok: false } };
    try {
      var copied = await copyText(line);
      notify(copied.ok ? 'GlassTTY report copied' : 'GlassTTY report ready');
      return { line: line, copy: copied };
    } catch (error) {
      notify('GlassTTY copy failed; see console');
      return { line: line, copy: { ok: false, error: String(error) } };
    }
  }

  function logJson(prefix, object) {
    var json = JSON.stringify(object);
    console.log(prefix + json);
    return json;
  }

  function downloadText(name, text) {
    var blob = new Blob([text], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    try {
      if (typeof GM_download === 'function') {
        GM_download({ url: url, name: name, saveAs: true });
      } else {
        var anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = name;
        document.documentElement.appendChild(anchor);
        anchor.click();
        anchor.remove();
      }
    } finally {
      window.setTimeout(function() { URL.revokeObjectURL(url); }, 10000);
    }
  }

  async function copyText(text) {
    if (typeof GM_setClipboard === 'function') {
      GM_setClipboard(text, 'text');
      return { ok: true, method: 'GM_setClipboard' };
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return { ok: true, method: 'navigator.clipboard.writeText' };
    }
    window.prompt('Copy this GlassTTY JSON:', text);
    return { ok: false, method: 'prompt-fallback' };
  }

  async function captureAndPrint(kind) {
    var report = captureReport(kind || 'full');
    var capsule = makeCapsule(report);
    STATE.last_report = report;
    STATE.last_capsule = capsule;
    if (kind === 'capsule') {
      var capPrefix = 'GLASSTTY_USER_SURFACE_CAPSULE_JSON=';
      logJson(capPrefix, capsule);
      await rememberAndCopy(capPrefix, capsule);
      return capsule;
    }
    var reportPrefix = 'GLASSTTY_USER_SURFACE_REPORT_JSON=';
    logJson(reportPrefix, report);
    logJson('GLASSTTY_USER_SURFACE_CAPSULE_JSON=', capsule);
    await rememberAndCopy(reportPrefix, report);
    return report;
  }

  function latestObject() {
    return STATE.last_object || STATE.last_proof || STATE.last_drill
      || STATE.last_report || STATE.last_capsule || captureReport('capsule');
  }

  function latestPrefix() {
    if (STATE.last_object_prefix) return STATE.last_object_prefix;
    if (STATE.last_proof) return 'GLASSTTY_USER_SURFACE_PROOF_JSON=';
    if (STATE.last_drill) return 'GLASSTTY_USER_SURFACE_DRILL_JSON=';
    if (STATE.last_report) return 'GLASSTTY_USER_SURFACE_REPORT_JSON=';
    return 'GLASSTTY_USER_SURFACE_CAPSULE_JSON=';
  }

  function exportLast() {
    var object = latestObject();
    var name = 'glasstty-chatgpt-surface-oracle-' + Date.now() + '.json';
    downloadText(name, JSON.stringify(object, null, 2));
  }

  function copyLast() {
    var object = latestObject();
    return rememberAndCopy(latestPrefix(), object);
  }

  function copyDrift() {
    var report = STATE.last_report || captureReport('drift-check');
    var drift = report.surface_contract_drift;
    return rememberAndCopy('GLASSTTY_USER_SURFACE_DRIFT_JSON=', drift);
  }

  function registerMenu(name, callback) {
    if (typeof GM_registerMenuCommand === 'function') {
      GM_registerMenuCommand(name, function() {
        Promise.resolve().then(callback).catch(function(error) {
          console.error('GlassTTY oracle menu failed:', error);
        });
      });
    }
  }

  function installStyle() {
    if (typeof GM_addStyle !== 'function') return;
    GM_addStyle('.glasstty-oracle-note{position:fixed;right:12px;bottom:12px;'
      + 'z-index:2147483647;background:#111;color:#fff;padding:8px 10px;'
      + 'font:12px sans-serif;border-radius:8px;opacity:.85}');
  }

  function installApi() {
    window.__GLASSTTY_SURFACE_ORACLE__ = {
      version: VERSION, options: OPTIONS, state: STATE,
      captureCapsule: function() { return captureAndPrint('capsule'); },
      captureFull: function() { return captureAndPrint('full'); },
      runSendDrill: runSendDrill,
      startObserver: startObserver,
      stopObserver: stopObserver,
      exportLast: exportLast,
      copyLast: copyLast,
      copyDrift: copyDrift,
      armedCheckpointProof: armedCheckpointProof
    };
    window.__GLASSTTY_CAPTURE_SURFACE_ORACLE__ = function() {
      return captureAndPrint('full');
    };
    window.__GLASSTTY_RUN_SEND_DRILL__ = runSendDrill;
  }

  function installMenus() {
    registerMenu('GlassTTY: capture capsule', function() {
      return captureAndPrint('capsule');
    });
    registerMenu('GlassTTY: capture full report', function() {
      return captureAndPrint('full');
    });
    registerMenu('GlassTTY: run safe send-state drill', runSendDrill);
    registerMenu('GlassTTY: start mutation observer', function() {
      console.log('GlassTTY observer:', startObserver());
    });
    registerMenu('GlassTTY: stop mutation observer', function() {
      console.log('GlassTTY observer:', stopObserver());
    });
    registerMenu('GlassTTY: copy last report', copyLast);
    registerMenu('GlassTTY: copy drift verdict', copyDrift);
    registerMenu('GlassTTY: export last report', exportLast);
    registerMenu('GlassTTY: ARMED checkpoint proof', armedCheckpointProof);
  }

  installStyle();
  installApi();
  installMenus();
  if (OPTIONS.mutation_log_enabled) startObserver();
  console.log('GlassTTY ChatGPT surface oracle userscript ' + VERSION + ' installed.');
  console.log('Use Tampermonkey menu or window.__GLASSTTY_SURFACE_ORACLE__.');
}());

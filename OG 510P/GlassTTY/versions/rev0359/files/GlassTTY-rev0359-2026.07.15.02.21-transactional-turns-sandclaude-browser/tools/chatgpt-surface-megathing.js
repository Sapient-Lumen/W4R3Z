// GlassTTY ChatGPT Surface Megathing
// rev0330 send-guard edition. Paste into DevTools on ChatGPT.
// Local-only: no network writes, no storage reads, no prompt submission.
(async function glassTtyChatGptSurfaceMegathing() {
  'use strict';

  var VERSION = 'rev0330-2026.06.12.23.11';
  var DEFAULTS = {
    maxElementsPerBucket: 80,
    maxSelectorSamples: 12,
    maxHashChars: 500000,
    maxTextSampleChars: 96,
    includeMessageTextSamples: false,
    includeEditableTextSamples: false,
    includeGenericTextSamples: false,
    includeUiTextSamples: true,
    copyToClipboard: true,
    storeGlobal: true
  };
  var OPTIONS = Object.assign(
    {},
    DEFAULTS,
    globalThis.GLASSTTY_SURFACE_INSPECTOR_OPTIONS || {}
  );

  function str(value) {
    return value == null ? '' : String(value);
  }

  function compact(value, limit) {
    var max = typeof limit === 'number' ? limit : 20000;
    return str(value).replace(/\s+/g, ' ').trim().slice(0, max);
  }

  function lower(value) {
    return compact(value).toLowerCase();
  }

  function attr(el, name) {
    return el && el.getAttribute ? el.getAttribute(name) : null;
  }

  function hasAny(text, terms) {
    var hay = lower(text);
    return terms.some(function (term) {
      return hay.indexOf(term) !== -1;
    });
  }

  function q(root, selector) {
    try {
      return Array.prototype.slice.call(root.querySelectorAll(selector));
    } catch (error) {
      return [];
    }
  }

  function uniq(values) {
    var seen = new Set();
    var out = [];
    values.forEach(function (value) {
      var normalized = typeof value === 'string' ? value.trim() : '';
      if (!normalized || seen.has(normalized)) return;
      seen.add(normalized);
      out.push(normalized);
    });
    return out;
  }

  function counts(values, limit) {
    var max = typeof limit === 'number' ? limit : 30;
    var map = new Map();
    values.forEach(function (value) {
      var key = typeof value === 'string' ? value.trim() : '';
      if (!key) return;
      map.set(key, (map.get(key) || 0) + 1);
    });
    return Array.prototype.slice.call(map.entries())
      .sort(function (a, b) {
        return b[1] - a[1] || a[0].localeCompare(b[0]);
      })
      .slice(0, max)
      .map(function (entry) {
        return { value: entry[0], count: entry[1] };
      });
  }

  function cssEsc(value) {
    if (globalThis.CSS && CSS.escape) return CSS.escape(str(value));
    return str(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
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
        left: Math.round(r.left),
        bottom: Math.round(r.bottom),
        right: Math.round(r.right)
      };
    } catch (error) {
      return null;
    }
  }

  function styleOf(el) {
    try {
      var s = getComputedStyle(el);
      return {
        display: s.display,
        visibility: s.visibility,
        opacity: s.opacity,
        position: s.position,
        pointerEvents: s.pointerEvents,
        zIndex: s.zIndex,
        overflow: s.overflow
      };
    } catch (error) {
      return null;
    }
  }

  function visible(el) {
    if (!el || !(el instanceof Element)) return false;
    var r = rectOf(el);
    var s = styleOf(el);
    if (!r || !s) return false;
    if (r.width <= 0 || r.height <= 0) return false;
    return s.display !== 'none' &&
      s.visibility !== 'hidden' &&
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
    var badInput = ['button', 'submit', 'hidden', 'checkbox', 'radio', 'file'];
    if (tag === 'textarea') return true;
    if (tag === 'input') return badInput.indexOf(lower(el.type)) === -1;
    if (contentEditableMode(el)) return true;
    return attr(el, 'role') === 'textbox';
  }

  function textOf(el) {
    if (!el) return '';
    if (el instanceof HTMLTextAreaElement) return el.value || '';
    if (el instanceof HTMLInputElement) return el.value || '';
    return el.textContent || '';
  }

  async function sha(value) {
    var input = str(value).slice(0, OPTIONS.maxHashChars);
    try {
      if (crypto && crypto.subtle && TextEncoder) {
        var bytes = new TextEncoder().encode(input);
        var digest = await crypto.subtle.digest('SHA-256', bytes);
        return Array.prototype.slice.call(new Uint8Array(digest))
          .map(function (b) {
            return b.toString(16).padStart(2, '0');
          })
          .join('');
      }
    } catch (error) {
      // Fall back to non-cryptographic FNV-1a below.
    }
    var h = 2166136261;
    for (var i = 0; i < input.length; i += 1) {
      h ^= input.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return 'fnv1a32:' + (h >>> 0).toString(16).padStart(8, '0');
  }

  function roleNode(el) {
    try {
      return el && el.closest ? el.closest('[data-message-author-role]') : null;
    } catch (error) {
      return null;
    }
  }

  function authorRole(el) {
    return lower(attr(roleNode(el), 'data-message-author-role')) || null;
  }

  function classTokens(el, limit) {
    var max = typeof limit === 'number' ? limit : 20;
    return uniq(str(attr(el, 'class')).split(/\s+/)).slice(0, max);
  }

  function simpleSelector(el) {
    if (!el || !el.tagName) return null;
    var doc = el.ownerDocument || document;
    var id = attr(el, 'id');
    if (id) {
      var byId = '#' + cssEsc(id);
      if (q(doc, byId).length === 1) return byId;
    }
    var testId = attr(el, 'data-testid');
    if (testId) {
      var byTest = '[data-testid=' + JSON.stringify(testId) + ']';
      if (q(doc, byTest).length === 1) return byTest;
    }
    var parts = [];
    var node = el;
    while (node && node.nodeType === 1 && parts.length < 8) {
      if (node === doc.documentElement) break;
      var tag = node.tagName.toLowerCase();
      var nodeId = attr(node, 'id');
      if (nodeId) {
        parts.unshift(tag + '#' + cssEsc(nodeId));
        break;
      }
      var nth = 1;
      var prev = node.previousElementSibling;
      while (prev) {
        if (prev.tagName === node.tagName) nth += 1;
        prev = prev.previousElementSibling;
      }
      parts.unshift(tag + ':nth-of-type(' + nth + ')');
      node = node.parentElement;
    }
    return parts.join(' > ') || el.tagName.toLowerCase();
  }

  function selectorHints(el) {
    if (!el || !el.tagName) return [];
    var tag = el.tagName.toLowerCase();
    var hints = [];
    if (attr(el, 'id')) hints.push('#' + cssEsc(attr(el, 'id')));
    if (attr(el, 'data-testid')) {
      hints.push(tag + '[data-testid=' +
        JSON.stringify(attr(el, 'data-testid')) + ']');
    }
    if (attr(el, 'data-message-author-role')) {
      hints.push(tag + '[data-message-author-role=' +
        JSON.stringify(attr(el, 'data-message-author-role')) + ']');
    }
    if (attr(el, 'role')) {
      hints.push(tag + '[role=' + JSON.stringify(attr(el, 'role')) + ']');
    }
    if (attr(el, 'aria-label')) {
      hints.push(tag + '[aria-label*=' +
        JSON.stringify(compact(attr(el, 'aria-label')).slice(0, 32)) + ']');
    }
    if (attr(el, 'placeholder')) {
      hints.push(tag + '[placeholder*=' +
        JSON.stringify(compact(attr(el, 'placeholder')).slice(0, 32)) + ']');
    }
    if (attr(el, 'data-placeholder')) {
      hints.push(tag + '[data-placeholder*=' +
        JSON.stringify(compact(attr(el, 'data-placeholder')).slice(0, 32)) +
        ']');
    }
    hints.push(simpleSelector(el));
    return uniq(hints).filter(Boolean).slice(0, 8);
  }

  function ancestry(el) {
    var chain = [];
    var node = el;
    while (node && node instanceof Element && chain.length < 8) {
      chain.push({
        tag: node.tagName.toLowerCase(),
        id: attr(node, 'id') || undefined,
        role: attr(node, 'role') || undefined,
        testid: attr(node, 'data-testid') || undefined,
        author_role: attr(node, 'data-message-author-role') || undefined,
        classes: classTokens(node, 6)
      });
      node = node.parentElement;
    }
    return chain;
  }

  function nearest(el) {
    var form = el && el.closest ? el.closest('form') : null;
    var dialog = el && el.closest ? el.closest([
      'dialog',
      '[role="dialog"]',
      '[role="alertdialog"]',
      '[aria-modal="true"]'
    ].join(',')) : null;
    var composer = el && el.closest ? el.closest([
      'form',
      '[data-testid*="composer"]',
      '[class*="composer"]',
      '[role="form"]'
    ].join(',')) : null;
    var msg = roleNode(el);
    return {
      form_selector: form ? simpleSelector(form) : null,
      dialog_selector: dialog ? simpleSelector(dialog) : null,
      composer_selector: composer ? simpleSelector(composer) : null,
      message_selector: msg ? simpleSelector(msg) : null,
      message_author_role: msg ? attr(msg, 'data-message-author-role') : null
    };
  }

  function sampleAllowed(el, bucket) {
    if (!el) return false;
    if (authorRole(el) && !OPTIONS.includeMessageTextSamples) return false;
    if (editable(el) && !OPTIONS.includeEditableTextSamples) return false;
    if (OPTIONS.includeGenericTextSamples) return true;
    if (!OPTIONS.includeUiTextSamples) return false;
    var tag = el.tagName ? el.tagName.toLowerCase() : '';
    if (['button', 'summary', 'label', 'option'].indexOf(tag) !== -1) {
      return true;
    }
    return /button|control|dialog|form|nav|toolbar|selector/i.test(str(bucket)) &&
      !authorRole(el);
  }

  async function textFingerprint(el, bucket) {
    var raw = textOf(el);
    var normalized = compact(raw, OPTIONS.maxHashChars);
    var result = {
      normalized_length: normalized.length,
      raw_length: str(raw).length,
      line_count: str(raw).split(/\r?\n/).length,
      hash_scope: normalized.length > OPTIONS.maxHashChars ?
        'first-' + OPTIONS.maxHashChars + '-chars' :
        'full-normalized-text',
      sha256: normalized ? await sha(normalized) : null
    };
    if (sampleAllowed(el, bucket) && normalized) {
      result.sample = normalized.slice(0, OPTIONS.maxTextSampleChars);
      result.sample_redaction_policy = 'ui-label-or-explicitly-enabled';
    }
    return result;
  }

  function contextList() {
    var out = [{ doc: document, win: window, depth: 0, path: 'top' }];
    q(document, 'iframe').forEach(function (frame, index) {
      try {
        var doc = frame.contentDocument || frame.contentWindow.document;
        if (!doc || !doc.documentElement) return;
        out.push({
          doc: doc,
          win: frame.contentWindow,
          depth: 1,
          path: 'top>iframe[' + index + ']'
        });
      } catch (error) {
        // Cross-origin frame; inventory records it separately.
      }
    });
    return out;
  }

  var contexts = contextList();
  var docContext = new Map();
  contexts.forEach(function (ctx) {
    docContext.set(ctx.doc, ctx);
  });

  function itemsBySelectors(selectors) {
    var seen = new Set();
    var out = [];
    contexts.forEach(function (ctx) {
      selectors.forEach(function (selector) {
        q(ctx.doc, selector).forEach(function (el) {
          if (seen.has(el)) return;
          seen.add(el);
          out.push({ el: el, ctx: ctx });
        });
      });
    });
    return out;
  }

  function ctxFor(el) {
    return docContext.get(el.ownerDocument) || {
      doc: el.ownerDocument,
      win: null,
      depth: null,
      path: 'unknown'
    };
  }

  async function elementSummary(item, bucket, extra) {
    var el = item.el || item;
    var ctx = item.ctx || ctxFor(el);
    var rn = roleNode(el);
    var turn = attr(el, 'data-turn-id') || attr(rn, 'data-turn-id');
    return Object.assign({
      bucket: bucket,
      frame_path: ctx.path,
      frame_depth: ctx.depth,
      tag: el.tagName ? el.tagName.toLowerCase() : null,
      selector: simpleSelector(el),
      selector_hints: selectorHints(el),
      visible: visible(el),
      rect: rectOf(el),
      style: styleOf(el),
      id: attr(el, 'id'),
      role: attr(el, 'role'),
      data_testid: attr(el, 'data-testid'),
      data_message_author_role: attr(el, 'data-message-author-role'),
      nearest_author_role: authorRole(el),
      nearest_author_role_source: rn ? (rn === el ? 'self' : 'ancestor') : null,
      data_message_model_slug: attr(el, 'data-message-model-slug') ||
        attr(rn, 'data-message-model-slug'),
      data_turn_id_present: Boolean(turn),
      data_turn_id_length: turn ? turn.length : 0,
      data_turn_id_sha256: turn ? await sha(turn) : null,
      aria_label: attr(el, 'aria-label'),
      aria_describedby: attr(el, 'aria-describedby'),
      aria_labelledby: attr(el, 'aria-labelledby'),
      aria_disabled: attr(el, 'aria-disabled'),
      aria_busy: attr(el, 'aria-busy'),
      aria_current: attr(el, 'aria-current'),
      aria_selected: attr(el, 'aria-selected'),
      aria_pressed: attr(el, 'aria-pressed'),
      title: attr(el, 'title'),
      placeholder: attr(el, 'placeholder'),
      data_placeholder: attr(el, 'data-placeholder'),
      name: attr(el, 'name'),
      type: attr(el, 'type'),
      contenteditable: attr(el, 'contenteditable'),
      disabled: Boolean(el.disabled),
      readOnly: Boolean(el.readOnly),
      class_tokens: classTokens(el),
      child_element_count: el.children ? el.children.length : 0,
      descendant_counts: {
        buttons: q(el, 'button').length,
        links: q(el, 'a[href]').length,
        code_blocks: q(el, 'pre, code').length,
        media: q(el, 'img, picture, svg, video, canvas').length,
        inputs: q(el, [
          'input',
          'textarea',
          '[contenteditable="true"]',
          '[role="textbox"]'
        ].join(',')).length
      },
      text: await textFingerprint(el, bucket),
      nearest: nearest(el),
      ancestry: ancestry(el)
    }, extra || {});
  }

  function promptScore(el) {
    var score = visible(el) ? 0.45 : 0.03;
    var id = lower(attr(el, 'id'));
    var testid = lower(attr(el, 'data-testid'));
    var placeholder = lower(attr(el, 'placeholder'));
    var dataPlaceholder = lower(attr(el, 'data-placeholder'));
    var aria = lower(attr(el, 'aria-label'));
    var role = lower(attr(el, 'role'));
    var klass = lower(attr(el, 'class'));
    var text = lower(textOf(el));
    if (!editable(el)) score -= 0.35;
    if (id === 'prompt-textarea') score += 0.35;
    if (testid.indexOf('prompt-textarea') !== -1) score += 0.35;
    if (el instanceof HTMLTextAreaElement) score += 0.25;
    if (role === 'textbox') score += 0.22;
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
    if (hasAny(id + ' ' + testid + ' ' + aria + ' ' + placeholder + ' ' +
      dataPlaceholder, [
      'search',
      'filter',
      'rename',
      'title',
      'email',
      'recipient'
    ])) score -= 0.28;
    if (text.length > 0 && text.length < 16000) score += 0.04;
    if (text.length > 24000) score -= 0.20;
    return Number(score.toFixed(3));
  }

  function composerRoot(el) {
    if (!el || !el.closest) return null;
    return el.closest([
      'form',
      '[data-testid*="composer"]',
      '[class*="composer"]',
      '[role="form"]'
    ].join(',')) || el.parentElement;
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

  function genScore(button, terms) {
    if (!visible(button)) return 0;
    if (button.disabled || attr(button, 'aria-disabled') === 'true') return 0;
    var text = lower(button.textContent);
    var aria = lower(attr(button, 'aria-label'));
    var title = lower(attr(button, 'title'));
    var testid = lower(attr(button, 'data-testid'));
    var all = [text, aria, title, testid].join(' ');
    if (!hasAny(all, terms)) return 0;
    var score = 0.45;
    if (hasAny(aria, terms) || hasAny(title, terms)) score += 0.22;
    if (button.closest('main, [role="main"]')) score += 0.08;
    if (button.closest('nav, header, aside')) score -= 0.20;
    return Number(score.toFixed(3));
  }

  function scoreSort(scoreFn) {
    return function (a, b) {
      var left = scoreFn(a.el);
      var right = scoreFn(b.el);
      return right - left;
    };
  }

  async function summarize(bucket, items, scoreFn) {
    var rows = [];
    var limited = items.slice(0, OPTIONS.maxElementsPerBucket);
    for (var i = 0; i < limited.length; i += 1) {
      var item = limited[i];
      var score = scoreFn ? scoreFn(item.el) : undefined;
      rows.push(await elementSummary(item, bucket, {
        score: typeof score === 'number' ? Number(score.toFixed(3)) : undefined,
        bucket_index: i,
        document_order_index: q(item.el.ownerDocument, '*').indexOf(item.el)
      }));
    }
    return {
      name: bucket,
      total: items.length,
      included: rows.length,
      visible_total: items.filter(function (item) {
        return visible(item.el);
      }).length,
      items: rows
    };
  }

  function probe(selectors) {
    return selectors.map(function (selector) {
      var items = itemsBySelectors([selector]);
      return {
        selector: selector,
        count: items.length,
        visible_count: items.filter(function (item) {
          return visible(item.el);
        }).length,
        first_selectors: items
          .slice(0, OPTIONS.maxSelectorSamples)
          .map(function (item) {
            return simpleSelector(item.el);
          })
      };
    });
  }

  function inspectNextData() {
    var node = document.getElementById('__NEXT_DATA__');
    if (!node || !node.textContent) return { present: false };
    try {
      var parsed = JSON.parse(node.textContent);
      return {
        present: true,
        byte_length: node.textContent.length,
        build_id: parsed.buildId || null,
        page: parsed.page || null,
        query_keys: parsed.query ? Object.keys(parsed.query).sort() : [],
        prop_top_keys: parsed.props ? Object.keys(parsed.props).sort() : []
      };
    } catch (error) {
      return {
        present: true,
        byte_length: node.textContent.length,
        parse_error: str(error && error.message || error)
      };
    }
  }

  function scriptInventory() {
    return q(document, 'script').slice(0, 100).map(function (script) {
      var item = {
        has_src: Boolean(script.src),
        has_nonce: Boolean(attr(script, 'nonce')),
        type: attr(script, 'type'),
        async: script.async,
        defer: script.defer
      };
      if (script.src) {
        try {
          var url = new URL(script.src, location.href);
          item.src_origin = url.origin;
          item.src_pathname = url.pathname;
        } catch (error) {
          item.src_length = str(script.src).length;
        }
      } else {
        item.inline_text_length = str(script.textContent).length;
      }
      return item;
    });
  }

  function frameInventory() {
    return q(document, 'iframe').map(function (frame, index) {
      var item = {
        index: index,
        selector: simpleSelector(frame),
        visible: visible(frame),
        rect: rectOf(frame),
        id: attr(frame, 'id'),
        name: attr(frame, 'name'),
        title: attr(frame, 'title'),
        sandbox: attr(frame, 'sandbox'),
        allow: attr(frame, 'allow'),
        loading: attr(frame, 'loading'),
        src_origin: null,
        src_pathname: null,
        accessible: false,
        accessible_title: null,
        accessible_url_pathname: null,
        accessible_element_count: null
      };
      try {
        var url = new URL(attr(frame, 'src') || frame.src || '', location.href);
        item.src_origin = url.origin;
        item.src_pathname = url.pathname;
      } catch (error) {
        // Leave src fields null.
      }
      try {
        var doc = frame.contentDocument || frame.contentWindow.document;
        item.accessible = Boolean(doc && doc.documentElement);
        item.accessible_title = doc.title || null;
        item.accessible_url_pathname = new URL(doc.location.href).pathname;
        item.accessible_element_count = q(doc, '*').length;
      } catch (error) {
        item.accessible = false;
      }
      return item;
    });
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
  var outputSelectors = [
    '[data-message-author-role="assistant"]',
    '[data-message-author-role="assistant"] [class*="markdown"]',
    '[data-testid*="conversation-turn"]',
    'article',
    'main article',
    'main [class*="markdown"]',
    '.markdown',
    '[class*="assistant"]',
    '[class*="message"]',
    'main',
    '[role="main"]'
  ];
  var userSelectors = [
    '[data-message-author-role="user"]',
    '[data-message-author-role="user"] [class*="message"]',
    '[data-testid*="conversation-turn"]',
    'article',
    'main article',
    '[class*="user"]',
    '[class*="message"]'
  ];
  var sendSelectors = [
    'button[data-testid="send-button"]',
    'button[aria-label*="Send" i]',
    'button[title*="Send" i]',
    'form button[type="submit"]',
    'button'
  ];
  var stopTerms = [
    'stop generating',
    'stop streaming',
    'stop response',
    'stop responding',
    'stop'
  ];
  var continueTerms = [
    'continue generating',
    'continue response',
    'continue'
  ];

  var started = performance.now();
  var allElements = itemsBySelectors(['*']);
  var buttons = itemsBySelectors(['button']);
  var prompts = itemsBySelectors(promptSelectors).sort(scoreSort(promptScore));
  var bestPrompt = prompts.length ? prompts[0].el : null;
  var sends = itemsBySelectors(sendSelectors).sort(function (a, b) {
    return sendScore(b.el, bestPrompt) - sendScore(a.el, bestPrompt);
  });
  var stops = buttons.filter(function (item) {
    return genScore(item.el, stopTerms) > 0.35;
  });
  var continues = buttons.filter(function (item) {
    return genScore(item.el, continueTerms) > 0.35;
  });
  var roleNodes = itemsBySelectors(['[data-message-author-role]']);
  var assistantNodes = roleNodes.filter(function (item) {
    return authorRole(item.el) === 'assistant';
  });
  var userNodes = roleNodes.filter(function (item) {
    return authorRole(item.el) === 'user';
  });
  var turns = itemsBySelectors([
    '[data-testid*="conversation-turn"]',
    'article'
  ]);
  var markdown = itemsBySelectors([
    'main [class*="markdown"]',
    '.markdown',
    'pre',
    'code'
  ]);
  var dialogs = itemsBySelectors([
    'dialog',
    '[role="dialog"]',
    '[role="alertdialog"]',
    '[aria-modal="true"]',
    '[data-radix-portal]'
  ]);
  var forms = itemsBySelectors(['form']);
  var mains = itemsBySelectors(['main', '[role="main"]']);
  var navs = itemsBySelectors([
    'nav',
    'aside',
    'header',
    '[role="navigation"]',
    '[data-testid*="sidebar"]',
    '[class*="sidebar"]'
  ]);
  var composerRoots = itemsBySelectors([
    'form',
    '[data-testid*="composer"]',
    '[class*="composer"]',
    '[role="form"]'
  ]).filter(function (item) {
    return q(item.el, [
      'textarea',
      'input',
      '[contenteditable="true"]',
      '[role="textbox"]'
    ].join(',')).length ||
      /composer/i.test(str(attr(item.el, 'class')) + attr(item.el, 'data-testid'));
  });

  function routeGuess() {
    var path = location.pathname.toLowerCase();
    var promptPresent = prompts.some(function (item) {
      return promptScore(item.el) > 0.35 && visible(item.el);
    });
    var shellText = compact(itemsBySelectors([
      'dialog[open]',
      '[role="dialog"]',
      '[role="alertdialog"]',
      '[aria-modal="true"]',
      'main [aria-current="page"]',
      'main [aria-selected="true"]',
      'main [aria-pressed="true"]',
      'main [data-state="active"]',
      '[data-testid*="composer"] [aria-pressed="true"]',
      '[data-testid*="tools"] [aria-pressed="true"]'
    ]).filter(function (item) {
      return visible(item.el);
    }).map(function (item) {
      return textOf(item.el);
    }).join(' '), 2400).toLowerCase();
    var evidence = [
      'path:' + path,
      promptPresent ? 'composer:present' : 'composer:missing'
    ];
    function shellHas(terms) {
      return terms.some(function (term) {
        return shellText.indexOf(term) !== -1 || path.indexOf(term) !== -1;
      });
    }
    if (path.indexOf('/auth/') !== -1 || path.indexOf('/login') !== -1) {
      evidence.push('auth-path');
      return { posture: 'login-or-marketing', evidence: evidence };
    }
    if (!promptPresent && shellHas(['log in', 'sign up', 'stay logged out'])) {
      evidence.push('auth-shell');
      return { posture: 'login-or-marketing', evidence: evidence };
    }
    if (shellHas(['/agent', '/tasks', '/task/', 'agent mode'])) {
      evidence.push('agent-or-tool-signal');
      return { posture: 'agent-or-tool', evidence: evidence };
    }
    if (shellHas(['/canvas', '/artifact', 'canvas', 'artifact'])) {
      evidence.push('canvas-or-artifact-signal');
      return { posture: 'canvas-or-artifact', evidence: evidence };
    }
    if (shellHas(['/g/', '/gpts', '/project', '/projects'])) {
      evidence.push('project-or-gpt-signal');
      return { posture: 'project-or-gpt', evidence: evidence };
    }
    if ((path === '/' || path.indexOf('/c/') === 0) && promptPresent) {
      evidence.push('plain-chat-path-and-composer');
      return { posture: 'plain-chat', evidence: evidence };
    }
    if (promptPresent) {
      evidence.push('composer-present-no-blocking-route-signal');
      return { posture: 'plain-chat', evidence: evidence };
    }
    evidence.push('no-supported-route-signal');
    return { posture: 'unknown', evidence: evidence };
  }

  var dataTestIds = allElements.map(function (item) {
    return attr(item.el, 'data-testid');
  }).filter(Boolean);
  var roles = allElements.map(function (item) {
    return attr(item.el, 'role');
  }).filter(Boolean);
  var tags = allElements.map(function (item) {
    return item.el.tagName ? item.el.tagName.toLowerCase() : '';
  }).filter(Boolean);
  var authorRoles = roleNodes.map(function (item) {
    return attr(item.el, 'data-message-author-role');
  }).filter(Boolean);
  var stateAttrs = [];
  allElements.forEach(function (item) {
    [
      'data-state',
      'aria-busy',
      'aria-current',
      'aria-selected',
      'aria-pressed',
      'aria-expanded'
    ].forEach(function (name) {
      var value = attr(item.el, name);
      if (value) stateAttrs.push(name + '=' + value);
    });
  });

  var route = routeGuess();
  var report = {
    schema_version: 2,
    tool: 'glasstty-chatgpt-surface-megathing',
    version: VERSION,
    captured_at: new Date().toISOString(),
    local_only: true,
    paste_transport: {
      edition: 'safe-wrapped-ascii',
      max_line_length_claim: 79,
      no_eval: true,
      no_script_tag_injection: true,
      no_network_writes: true,
      no_storage_reads: true,
      fallback_capsule_line: true,
      local_download_helper: true
    },
    privacy_defaults: {
      message_text_samples_included: Boolean(OPTIONS.includeMessageTextSamples),
      editable_text_samples_included: Boolean(OPTIONS.includeEditableTextSamples),
      generic_text_samples_included: Boolean(OPTIONS.includeGenericTextSamples),
      ui_text_samples_included: Boolean(OPTIONS.includeUiTextSamples)
    },
    page: {
      href: location.href,
      origin: location.origin,
      host: location.host,
      pathname: location.pathname,
      search_param_keys: Array.from(new URLSearchParams(location.search).keys())
        .sort(),
      hash_present: Boolean(location.hash),
      title: document.title,
      referrer_origin: (function () {
        try {
          return document.referrer ? new URL(document.referrer).origin : null;
        } catch (error) {
          return null;
        }
      })(),
      lang: document.documentElement.lang || null,
      dir: document.documentElement.dir || null,
      ready_state: document.readyState,
      visibility_state: document.visibilityState
    },
    environment: {
      user_agent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      languages: navigator.languages,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      viewport: {
        width: innerWidth,
        height: innerHeight,
        device_pixel_ratio: devicePixelRatio
      },
      screen: {
        width: screen.width,
        height: screen.height,
        availWidth: screen.availWidth,
        availHeight: screen.availHeight
      },
      is_secure_context: isSecureContext,
      cross_origin_isolated: crossOriginIsolated,
      focused: document.hasFocus()
    },
    framework_markers: {
      next_data: inspectNextData(),
      root_markers: probe([
        '#__next',
        '[data-reactroot]',
        '[id^="radix-"]',
        '[data-radix-portal]',
        '[data-headlessui-state]',
        '[data-state]'
      ]),
      scripts: scriptInventory()
    },
    security_markers: {
      meta_csp_count: q(document, 'meta[http-equiv="Content-Security-Policy" i]')
        .length,
      script_nonce_count: q(document, 'script[nonce]').length,
      script_src_count: q(document, 'script[src]').length,
      inline_script_count: q(document, 'script:not([src])').length,
      trusted_types_available: Boolean(globalThis.trustedTypes)
    },
    counts: {
      contexts: contexts.length,
      elements: allElements.length,
      visible_elements: allElements.filter(function (item) {
        return visible(item.el);
      }).length,
      inputs: itemsBySelectors(['input']).length,
      textareas: itemsBySelectors(['textarea']).length,
      contenteditable: itemsBySelectors(['[contenteditable="true"]']).length,
      role_textbox: itemsBySelectors(['[role="textbox"]']).length,
      buttons: buttons.length,
      forms: forms.length,
      dialogs: dialogs.length,
      iframes: q(document, 'iframe').length,
      main_regions: mains.length,
      nav_regions: navs.length,
      message_author_role_nodes: roleNodes.length,
      assistant_role_nodes: assistantNodes.length,
      user_role_nodes: userNodes.length,
      conversation_turn_like_nodes: turns.length,
      markdown_or_code_blocks: markdown.length,
      data_testid_top: counts(dataTestIds),
      role_top: counts(roles),
      tag_top: counts(tags),
      author_role_top: counts(authorRoles),
      state_attr_top: counts(stateAttrs)
    },
    route_posture_guess: {
      posture: route.posture,
      pathname: location.pathname,
      prompt_present: prompts.some(function (item) {
        return promptScore(item.el) > 0.35 && visible(item.el);
      }),
      evidence: route.evidence
    },
    selector_probe: {
      prompt: probe(promptSelectors),
      output: probe(outputSelectors),
      user_turn: probe(userSelectors),
      send: probe(sendSelectors),
      generation: probe([
        'button[data-testid*="stop" i]',
        'button[aria-label*="Stop" i]',
        'button[aria-label*="Continue" i]',
        '[aria-busy="true"]',
        '[data-state="open"]'
      ]),
      overlays: probe([
        'dialog[open]',
        '[role="dialog"]',
        '[role="alertdialog"]',
        '[aria-modal="true"]',
        '[data-radix-portal]'
      ])
    },
    candidates: {},
    active_element: null,
    frames: frameInventory(),
    body_fingerprint: await textFingerprint(document.body, 'body'),
    adapter_recommendation: null,
    warnings: [],
    runtime_ms: null,
    clipboard: {
      attempted: false,
      ok: false,
      method: null,
      error: null
    }
  };

  report.candidates.prompt_editors = await summarize(
    'prompt_editors',
    prompts,
    promptScore
  );
  report.candidates.send_buttons = await summarize(
    'send_buttons',
    sends,
    function (el) { return sendScore(el, bestPrompt); }
  );
  report.candidates.stop_controls = await summarize(
    'stop_controls',
    stops,
    function (el) { return genScore(el, stopTerms); }
  );
  report.candidates.continue_controls = await summarize(
    'continue_controls',
    continues,
    function (el) { return genScore(el, continueTerms); }
  );
  report.candidates.assistant_messages = await summarize(
    'assistant_messages',
    assistantNodes
  );
  report.candidates.user_messages = await summarize('user_messages', userNodes);
  report.candidates.conversation_turns = await summarize('conversation_turns', turns);
  report.candidates.markdown_blocks = await summarize('markdown_blocks', markdown);
  report.candidates.composer_roots = await summarize('composer_roots', composerRoots);
  report.candidates.forms = await summarize('forms', forms);
  report.candidates.dialogs_and_overlays = await summarize(
    'dialogs_and_overlays',
    dialogs
  );
  report.candidates.main_regions = await summarize('main_regions', mains);
  report.candidates.nav_sidebar_header_regions = await summarize(
    'nav_sidebar_header_regions',
    navs
  );
  if (document.activeElement) {
    report.active_element = await elementSummary(
      document.activeElement,
      'active_element'
    );
  }

  var sendCandidates = sends.filter(function (item) {
    var signal = sendSignal(item.el);
    return sendScore(item.el, bestPrompt) > SEND_MIN_SCORE && signal.intent &&
      !signal.disqualified && !item.el.disabled &&
      attr(item.el, 'aria-disabled') !== 'true';
  });
  var bestSend = sendCandidates.length ? sendCandidates[0].el : null;
  var blockedSend = !bestSend && sends.length ? sends[0].el : null;
  report.send_readiness = {
    strict_send_found: Boolean(bestSend),
    strict_send_min_score: SEND_MIN_SCORE,
    composer_text_length: bestPrompt ? textOf(bestPrompt).length : 0,
    empty_composer_missing_send_is_allowed: Boolean(
      bestPrompt && !String(textOf(bestPrompt)).trim() && !bestSend
    ),
    blocked_best_control_selector: blockedSend ? simpleSelector(blockedSend) : null,
    blocked_best_control_score: blockedSend ? sendScore(blockedSend, bestPrompt) : 0,
    blocked_best_control_disqualified: Boolean(
      blockedSend && sendSignal(blockedSend).disqualified
    )
  };
  report.adapter_recommendation = {
    best_prompt_selector: bestPrompt ? simpleSelector(bestPrompt) : null,
    best_prompt_score: bestPrompt ? promptScore(bestPrompt) : 0,
    best_prompt_visible: bestPrompt ? visible(bestPrompt) : false,
    best_send_selector: bestSend ? simpleSelector(bestSend) : null,
    best_send_score: bestSend ? sendScore(bestSend, bestPrompt) : 0,
    best_send_visible: bestSend ? visible(bestSend) : false,
    generation_state_guess: stops.length ? 'streaming-or-stoppable' :
      continues.length ? 'needs-continue' : 'settled-or-idle',
    latest_assistant_selector: assistantNodes.length ?
      simpleSelector(assistantNodes[assistantNodes.length - 1].el) : null,
    latest_user_selector: userNodes.length ?
      simpleSelector(userNodes[userNodes.length - 1].el) : null,
    has_explicit_author_roles: roleNodes.length > 0,
    has_prompt_textarea_id: Boolean(document.getElementById('prompt-textarea')),
    plain_chat_submit_allowed_by_route_guess: route.posture === 'plain-chat'
  };

  if (location.hostname !== 'chatgpt.com' &&
      !location.hostname.endsWith('.chatgpt.com')) {
    report.warnings.push('Not on chatgpt.com; results may not match target.');
  }
  if (!report.adapter_recommendation.best_prompt_selector) {
    report.warnings.push('No likely prompt editor found.');
  }
  if (!report.adapter_recommendation.best_send_selector) {
    report.warnings.push('No likely send button found. Empty composer can cause this.');
  }
  if (!roleNodes.length) {
    report.warnings.push('No data-message-author-role nodes in mounted DOM.');
  }
  if (report.frames.some(function (frame) { return !frame.accessible; })) {
    report.warnings.push('At least one iframe is cross-origin/inaccessible.');
  }

  function firstItem(summary) {
    return summary && summary.items && summary.items.length ?
      summary.items[0] : null;
  }

  function miniCandidate(item) {
    if (!item) return null;
    return {
      selector: item.selector || null,
      score: typeof item.score === 'number' ? item.score : null,
      visible: Boolean(item.visible),
      frame_path: item.frame_path || null,
      tag: item.tag || null,
      id: item.id || null,
      role: item.role || null,
      data_testid: item.data_testid || null,
      aria_label: item.aria_label || null,
      placeholder: item.placeholder || null,
      data_placeholder: item.data_placeholder || null,
      contenteditable: item.contenteditable || null,
      disabled: Boolean(item.disabled),
      text_length: item.text ? item.text.normalized_length : null,
      text_sha256: item.text ? item.text.sha256 : null,
      nearest_author_role: item.nearest_author_role || null,
      nearest_author_role_source: item.nearest_author_role_source || null
    };
  }

  function probeMini(rows) {
    return (rows || []).map(function (row) {
      return {
        selector: row.selector,
        count: row.count,
        visible_count: row.visible_count,
        first_selectors: row.first_selectors
      };
    });
  }

  function buildCapsule(source) {
    var rec = source.adapter_recommendation || {};
    var cands = source.candidates || {};
    return {
      capsule_schema_version: 1,
      source_tool: source.tool,
      source_version: source.version,
      captured_at: source.captured_at,
      local_only: true,
      page: {
        origin: source.page.origin,
        host: source.page.host,
        pathname: source.page.pathname,
        title_length: str(source.page.title).length,
        lang: source.page.lang,
        ready_state: source.page.ready_state,
        visibility_state: source.page.visibility_state
      },
      environment: {
        user_agent: source.environment.user_agent,
        platform: source.environment.platform,
        viewport: source.environment.viewport,
        focused: source.environment.focused
      },
      route_posture_guess: source.route_posture_guess,
      counts: source.counts,
      security_markers: source.security_markers,
      adapter_recommendation: rec,
      send_readiness: source.send_readiness || null,
      top_candidates: {
        prompt: miniCandidate(firstItem(cands.prompt_editors)),
        send: miniCandidate(
          rec.best_send_selector ? firstItem(cands.send_buttons) : null
        ),
        blocked_send_control: miniCandidate(
          rec.best_send_selector ? null : firstItem(cands.send_buttons)
        ),
        assistant: miniCandidate(firstItem(cands.assistant_messages)),
        user: miniCandidate(firstItem(cands.user_messages)),
        composer: miniCandidate(firstItem(cands.composer_roots))
      },
      selector_probe: {
        prompt: probeMini(source.selector_probe.prompt),
        send: probeMini(source.selector_probe.send),
        output: probeMini(source.selector_probe.output),
        user_turn: probeMini(source.selector_probe.user_turn)
      },
      warnings: source.warnings,
      runtime_ms: source.runtime_ms,
      privacy_defaults: source.privacy_defaults
    };
  }

  async function copyText(text) {
    if (typeof globalThis.copy === 'function') {
      globalThis.copy(text);
      return { ok: true, method: 'devtools-copy' };
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return { ok: true, method: 'navigator.clipboard.writeText' };
    }
    return { ok: false, method: null, error: 'no-copy-api' };
  }

  function safeFileStamp() {
    return new Date().toISOString().replace(/[^0-9]/g, '').slice(0, 14);
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

  report.runtime_ms = Math.round(performance.now() - started);
  var capsule = buildCapsule(report);
  var capsuleJson = JSON.stringify(capsule);
  var capsuleLine = 'GLASSTTY_SURFACE_CAPSULE_JSON=' + capsuleJson;
  report.transport_status = {
    full_json_global: Boolean(OPTIONS.storeGlobal),
    capsule_json_global: Boolean(OPTIONS.storeGlobal),
    capsule_line_console: true,
    copy_helper_global: Boolean(OPTIONS.storeGlobal),
    download_helper_global: Boolean(OPTIONS.storeGlobal),
    prompt_helper_global: Boolean(OPTIONS.storeGlobal)
  };
  var json = JSON.stringify(report, null, 2);

  if (OPTIONS.copyToClipboard) {
    report.clipboard.attempted = true;
    try {
      var copyResult = await copyText(json);
      report.clipboard.ok = copyResult.ok;
      report.clipboard.method = copyResult.method;
      report.clipboard.target = 'full-report';
      if (!copyResult.ok) report.clipboard.error = copyResult.error || null;
    } catch (error) {
      report.clipboard.error = str(error && error.message || error);
    }
    if (!report.clipboard.ok) {
      try {
        var capsuleCopy = await copyText(capsuleJson);
        report.clipboard.ok = capsuleCopy.ok;
        report.clipboard.method = capsuleCopy.method;
        report.clipboard.target = 'capsule';
        if (!capsuleCopy.ok && !report.clipboard.error) {
          report.clipboard.error = capsuleCopy.error || null;
        }
      } catch (error2) {
        if (!report.clipboard.error) {
          report.clipboard.error = str(error2 && error2.message || error2);
        }
      }
    }
  }

  capsule = buildCapsule(report);
  capsuleJson = JSON.stringify(capsule);
  capsuleLine = 'GLASSTTY_SURFACE_CAPSULE_JSON=' + capsuleJson;
  json = JSON.stringify(report, null, 2);

  if (OPTIONS.storeGlobal) {
    globalThis.__GLASSTTY_CHATGPT_SURFACE_REPORT__ = report;
    globalThis.__GLASSTTY_CHATGPT_SURFACE_REPORT_JSON__ = json;
    globalThis.__GLASSTTY_CHATGPT_SURFACE_CAPSULE__ = capsule;
    globalThis.__GLASSTTY_CHATGPT_SURFACE_CAPSULE_JSON__ = capsuleJson;
    globalThis.__GLASSTTY_PRINT_SURFACE_CAPSULE__ = function () {
      console.log(capsuleLine);
      return capsule;
    };
    globalThis.__GLASSTTY_PROMPT_SURFACE_CAPSULE__ = function () {
      prompt('Copy this GlassTTY surface capsule JSON:', capsuleJson);
      return capsule;
    };
    globalThis.__GLASSTTY_COPY_SURFACE_REPORT__ = function (kind) {
      var text = kind === 'full' ? json : capsuleJson;
      return copyText(text);
    };
    globalThis.__GLASSTTY_DOWNLOAD_SURFACE_REPORT__ = function (kind) {
      var full = kind === 'full';
      var name = 'glasstty-chatgpt-surface-' + VERSION + '-';
      name += full ? 'full-' : 'capsule-';
      name += safeFileStamp() + '.json';
      return downloadText(name, full ? json : capsuleJson);
    };
  }

  console.groupCollapsed('GlassTTY ChatGPT surface megathing ' + VERSION);
  console.log('Report object:', report);
  console.log('Report JSON:', json);
  console.log('Capsule object:', capsule);
  console.log(capsuleLine);
  console.log('Clipboard:', report.clipboard.ok ?
    'copied ' + report.clipboard.target + ' with ' + report.clipboard.method :
    'not copied; use __GLASSTTY_PRINT_SURFACE_CAPSULE__()');
  console.log('Export helpers:', [
    '__GLASSTTY_PRINT_SURFACE_CAPSULE__()',
    '__GLASSTTY_PROMPT_SURFACE_CAPSULE__()',
    "__GLASSTTY_COPY_SURFACE_REPORT__(\'capsule\')",
    "__GLASSTTY_COPY_SURFACE_REPORT__(\'full\')",
    "__GLASSTTY_DOWNLOAD_SURFACE_REPORT__(\'capsule\')",
    "__GLASSTTY_DOWNLOAD_SURFACE_REPORT__(\'full\')"
  ]);
  console.groupEnd();
  return report;
}());

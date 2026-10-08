// GlassTTY ChatGPT Page-World Rest Probe
// rev0331-2026.06.12.23.34. Paste into DevTools on https://chatgpt.com/.
// Local-only: no network writes, no storage reads, no prompt submission.
(function glassTtyChatGptPageWorldRestProbe() {
  'use strict';

  var VERSION = 'rev0331-2026.06.12.23.34';

  function nowIso() {
    return new Date().toISOString();
  }

  function compact(value, limit) {
    return String(value || '').replace(/\s+/g, ' ').trim().slice(0, limit || 2000);
  }

  function fnv1a(value) {
    var text = String(value || '').slice(0, 300000);
    var hash = 2166136261;
    for (var index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return 'fnv1a32:' + (hash >>> 0).toString(16).padStart(8, '0');
  }

  function queryAll(selector) {
    try {
      return Array.prototype.slice.call(document.querySelectorAll(selector));
    } catch (_error) {
      return [];
    }
  }

  function attr(el, name) {
    return el && el.getAttribute ? el.getAttribute(name) : null;
  }

  function safeType(value) {
    try {
      if (value === null) return 'null';
      if (Array.isArray(value)) return 'array';
      return typeof value;
    } catch (_error) {
      return 'inaccessible';
    }
  }

  function safeWindowKeys() {
    var keys = [];
    try {
      keys = Object.getOwnPropertyNames(window);
    } catch (_error) {
      keys = [];
    }
    return keys.filter(function(key) {
      var low = key.toLowerCase();
      return key.indexOf('__') >= 0 || low.indexOf('webpack') >= 0
        || low.indexOf('next') >= 0 || low.indexOf('react') >= 0
        || low.indexOf('chat') >= 0 || low.indexOf('openai') >= 0;
    }).sort().slice(0, 160).map(function(key) {
      var valueType = 'unknown';
      try {
        valueType = safeType(window[key]);
      } catch (_error2) {
        valueType = 'throws-on-read';
      }
      return { key: key, type: valueType };
    });
  }

  function nextDataSummary() {
    var node = document.getElementById('__NEXT_DATA__');
    if (!node || !node.textContent) return { present: false };
    try {
      var parsed = JSON.parse(node.textContent);
      return {
        present: true,
        byte_length: node.textContent.length,
        build_id_hash: parsed.buildId ? fnv1a(parsed.buildId) : null,
        page: parsed.page || null,
        query_keys: parsed.query ? Object.keys(parsed.query).sort() : [],
        prop_top_keys: parsed.props ? Object.keys(parsed.props).sort() : []
      };
    } catch (error) {
      return { present: true, byte_length: node.textContent.length,
        parse_error: String(error && error.message || error) };
    }
  }

  function reactHookSummary() {
    var hook = window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
    if (!hook) return { present: false };
    var renderers = [];
    try {
      if (hook.renderers && hook.renderers.forEach) {
        hook.renderers.forEach(function(renderer, id) {
          renderers.push({ id_hash: fnv1a(String(id)), keys: Object.keys(renderer || {}) });
        });
      }
    } catch (error) {
      return { present: true, error: String(error && error.message || error) };
    }
    return { present: true, hook_keys: Object.keys(hook).sort(), renderers: renderers };
  }

  function resources() {
    var entries = [];
    try {
      entries = performance.getEntriesByType('resource') || [];
    } catch (_error) {
      entries = [];
    }
    return entries.slice(-120).map(function(entry) {
      var item = { initiatorType: entry.initiatorType || null,
        duration_ms: Math.round(entry.duration || 0),
        transferSize: entry.transferSize || 0 };
      try {
        var url = new URL(entry.name, location.href);
        item.origin = url.origin;
        item.pathname = url.pathname.slice(0, 140);
      } catch (_error2) {
        item.name_length = String(entry.name || '').length;
      }
      return item;
    });
  }

  function scriptNonces() {
    return queryAll('script').slice(0, 120).map(function(script) {
      return {
        has_src: Boolean(script.src),
        src_hash: script.src ? fnv1a(script.src) : null,
        nonce_present: Boolean(script.nonce || attr(script, 'nonce')),
        type: attr(script, 'type') || null,
        text_length: script.src ? 0 : String(script.textContent || '').length
      };
    });
  }

  function editingCapabilities() {
    var supported = null;
    try {
      supported = document.queryCommandSupported
        ? document.queryCommandSupported('insertText') : null;
    } catch (_error) {
      supported = null;
    }
    return {
      InputEvent: typeof InputEvent,
      beforeinput_supported: 'onbeforeinput' in document.documentElement,
      input_supported: 'oninput' in document.documentElement,
      CompositionEvent: typeof CompositionEvent,
      ClipboardEvent: typeof ClipboardEvent,
      execCommand_insertText_supported: supported,
      active_element_tag: document.activeElement && document.activeElement.tagName
        ? document.activeElement.tagName.toLowerCase() : null,
      active_element_id: document.activeElement ? attr(document.activeElement, 'id') : null
    };
  }

  var report = {
    schema_version: 1,
    tool: 'glasstty-chatgpt-pageworld-restprobe',
    version: VERSION,
    captured_at: nowIso(),
    local_only: true,
    no_network_writes: true,
    no_storage_reads: true,
    no_prompt_submission: true,
    page: {
      origin: location.origin,
      host: location.host,
      pathname: location.pathname,
      href_hash: fnv1a(location.href),
      title_hash: fnv1a(document.title),
      ready_state: document.readyState
    },
    page_world: {
      devtools_copy_present: typeof copy === 'function',
      next_data: nextDataSummary(),
      react_hook: reactHookSummary(),
      selected_window_keys: safeWindowKeys(),
      editing_capabilities: editingCapabilities(),
      script_nonces: scriptNonces(),
      resources: resources()
    },
    dom_crosscheck: {
      prompt_textarea_count: queryAll('#prompt-textarea').length,
      prompt_textarea_hash: queryAll('#prompt-textarea')[0]
        ? fnv1a(compact(queryAll('#prompt-textarea')[0].textContent, 300000)) : null,
      message_author_role_nodes: queryAll('[data-message-author-role]').length,
      assistant_role_nodes: queryAll('[data-message-author-role="assistant"]').length,
      user_role_nodes: queryAll('[data-message-author-role="user"]').length,
      send_button_count: queryAll('button[data-testid="send-button"]').length,
      composer_plus_count: queryAll('#composer-plus-btn').length
    }
  };

  var json = JSON.stringify(report);
  window.__GLASSTTY_PAGEWORLD_REST_REPORT__ = report;
  window.__GLASSTTY_PAGEWORLD_REST_REPORT_JSON__ = json;
  console.log('GLASSTTY_PAGEWORLD_REST_JSON=' + json);
  console.log('GlassTTY page-world rest probe report:', report);
  return report;
}());

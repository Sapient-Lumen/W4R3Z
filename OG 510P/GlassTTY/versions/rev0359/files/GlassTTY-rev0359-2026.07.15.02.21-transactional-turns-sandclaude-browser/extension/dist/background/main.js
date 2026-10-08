"use strict";
(() => {
  // src/content/generic.ts
  function safeTrim(value) {
    if (typeof value !== "string") return null;
    const compact = value.replace(/\s+/g, " ").trim();
    return compact || null;
  }
  function isVisible(el) {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 && style.visibility !== "hidden" && style.display !== "none";
  }
  function textFrom(el) {
    if (!el) return null;
    if (el instanceof HTMLTextAreaElement) return safeTrim(el.value);
    if (el instanceof HTMLInputElement) return safeTrim(el.value);
    return safeTrim(el.textContent);
  }
  function selectorIdentity(node) {
    const id = safeTrim(node.getAttribute("id"));
    if (id) return `#${id}`;
    const name = safeTrim(node.getAttribute("name"));
    if (name) return `[name=${JSON.stringify(name)}]`;
    return null;
  }
  function selectorHint(node, fallback) {
    const parts = [node.tagName.toLowerCase()];
    const identity = selectorIdentity(node);
    const role = safeTrim(node.getAttribute("role"));
    const placeholder = safeTrim(node.getAttribute("placeholder"));
    const dataPlaceholder = safeTrim(node.getAttribute("data-placeholder"));
    const aria = safeTrim(node.getAttribute("aria-label"));
    if (identity) parts.push(identity);
    if (role) parts.push(`[role=${JSON.stringify(role)}]`);
    if (placeholder) parts.push(`[placeholder*=${JSON.stringify(placeholder.slice(0, 24))}]`);
    if (dataPlaceholder) parts.push(`[data-placeholder*=${JSON.stringify(dataPlaceholder.slice(0, 24))}]`);
    if (aria) parts.push(`[aria-label*=${JSON.stringify(aria.slice(0, 24))}]`);
    return parts.join(" ") || fallback;
  }
  function uniqueStrings(values) {
    const out = [];
    const seen = /* @__PURE__ */ new Set();
    for (const value of values) {
      const trimmed = safeTrim(value);
      if (!trimmed || seen.has(trimmed)) continue;
      seen.add(trimmed);
      out.push(trimmed);
    }
    return out;
  }
  function labelTexts(node) {
    if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement || node instanceof HTMLOutputElement || node instanceof HTMLProgressElement || node instanceof HTMLMeterElement) {
      return uniqueStrings(Array.from(node.labels || []).map((label) => label.textContent));
    }
    const labelledBy = safeTrim(node.getAttribute("aria-labelledby"));
    if (!labelledBy) return [];
    return uniqueStrings(labelledBy.split(/\s+/).map((id) => node.ownerDocument.getElementById(id)?.textContent ?? null));
  }
  function descriptionTexts(node) {
    const describedBy = safeTrim(node.getAttribute("aria-describedby"));
    if (!describedBy) return [];
    return uniqueStrings(describedBy.split(/\s+/).map((id) => node.ownerDocument.getElementById(id)?.textContent ?? null));
  }
  function nearestLegend(node) {
    const fieldset = node.closest("fieldset");
    return safeTrim(fieldset?.querySelector("legend")?.textContent ?? null);
  }
  function nearestDialog(node) {
    const dialog = node.closest('dialog, [role="dialog"], [role="alertdialog"]');
    if (!(dialog instanceof Element)) return {};
    const role = safeTrim(dialog.getAttribute("role")) || (dialog.tagName === "DIALOG" ? "dialog" : null) || void 0;
    const labelledBy = safeTrim(dialog.getAttribute("aria-labelledby"));
    const labelFromRef = labelledBy ? uniqueStrings(labelledBy.split(/\s+/).map((id) => dialog.ownerDocument.getElementById(id)?.textContent ?? null))[0] : null;
    const name = labelFromRef || safeTrim(dialog.getAttribute("aria-label")) || safeTrim(dialog.querySelector("h1, h2, h3, [data-dialog-title], legend")?.textContent ?? null) || void 0;
    let modal;
    if (dialog instanceof HTMLDialogElement) {
      try {
        modal = dialog.matches(":modal");
      } catch {
        modal = dialog.hasAttribute("open");
      }
    } else {
      modal = dialog.getAttribute("aria-modal") === "true";
    }
    const open = dialog instanceof HTMLDialogElement ? dialog.open : dialog.hasAttribute("open") || dialog.getAttribute("aria-hidden") === "false";
    return { ...name ? { name } : {}, ...role ? { role } : {}, ...typeof modal === "boolean" ? { modal } : {}, open };
  }
  function formContext(node) {
    const form = node.closest("form");
    if (!(form instanceof HTMLFormElement)) return {};
    const labelledBy = safeTrim(form.getAttribute("aria-labelledby"));
    const labelFromRef = labelledBy ? uniqueStrings(labelledBy.split(/\s+/).map((id) => form.ownerDocument.getElementById(id)?.textContent ?? null))[0] : null;
    const name = labelFromRef || safeTrim(form.getAttribute("aria-label")) || safeTrim(form.querySelector("legend, h1, h2, h3, h4, h5, h6")?.textContent ?? null) || void 0;
    const action = safeTrim(form.getAttribute("action")) || safeTrim(form.action) || void 0;
    const method = safeTrim(form.getAttribute("method")) || safeTrim(form.method) || void 0;
    return { ...name ? { name } : {}, ...action ? { action } : {}, ...method ? { method } : {} };
  }
  function frameChainForWindow(win) {
    const chain = [];
    let current = win;
    while (current && current.top !== current) {
      try {
        const frame = current.frameElement;
        if (!(frame instanceof HTMLIFrameElement)) break;
        chain.unshift({
          selector: selectorHint(frame, "iframe"),
          ...safeTrim(frame.name) ? { name: safeTrim(frame.name) } : {},
          ...safeTrim(frame.title) ? { title: safeTrim(frame.title) } : {}
        });
        current = current.parent;
      } catch {
        break;
      }
    }
    return chain;
  }
  function frameContext(win) {
    const chain = frameChainForWindow(win);
    if (!chain.length) return {};
    const leaf = chain[chain.length - 1];
    const pathSelectors = chain.map((entry) => entry.selector);
    const pathNames = uniqueStrings(chain.map((entry) => entry.name ?? null));
    const pathTitles = uniqueStrings(chain.map((entry) => entry.title ?? null));
    return {
      selector: leaf.selector,
      ...leaf.name ? { name: leaf.name } : {},
      ...leaf.title ? { title: leaf.title } : {},
      ...pathSelectors.length ? { path: pathSelectors.join(" >> "), pathSelectors } : {},
      ...pathNames.length ? { pathNames } : {},
      ...pathTitles.length ? { pathTitles } : {},
      depth: chain.length
    };
  }
  function controlKind(node) {
    const role = safeTrim(node.getAttribute("role"));
    if (role) return role;
    if (node instanceof HTMLTextAreaElement) return "textarea";
    if (node instanceof HTMLSelectElement) return node.multiple ? "listbox" : "combobox";
    if (node instanceof HTMLInputElement) return `input:${(node.type || "text").toLowerCase()}`;
    if (node instanceof HTMLButtonElement) return "button";
    if (node.getAttribute("contenteditable") === "" || node.getAttribute("contenteditable") === "true") return "contenteditable";
    return node.tagName.toLowerCase();
  }
  function selectedOptions(node) {
    if (!(node instanceof HTMLSelectElement)) return [];
    return uniqueStrings(Array.from(node.selectedOptions).map((option) => option.label || option.textContent));
  }
  function optionLabels(node) {
    if (!(node instanceof HTMLSelectElement)) return [];
    return uniqueStrings(Array.from(node.options).map((option) => option.label || option.textContent));
  }
  function autocompleteValue(node) {
    if (!(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement)) return null;
    return safeTrim(node.autocomplete || node.getAttribute("autocomplete"));
  }
  function inputModeValue(node) {
    const attr = safeTrim(node.getAttribute("inputmode"));
    if (attr) return attr;
    if (node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement) {
      return safeTrim(node.inputMode);
    }
    return null;
  }
  function choiceGroup(node) {
    if (node instanceof HTMLInputElement && ["checkbox", "radio"].includes((node.type || "").toLowerCase())) {
      return safeTrim(node.name) || nearestLegend(node);
    }
    return null;
  }
  function constraintHints(node) {
    const hints = [];
    if (node instanceof HTMLInputElement) {
      if (safeTrim(node.pattern)) hints.push(`pattern:${node.pattern}`);
      if (node.maxLength > -1) hints.push(`maxlength:${node.maxLength}`);
      if (node.minLength > -1) hints.push(`minlength:${node.minLength}`);
      if (safeTrim(node.min)) hints.push(`min:${node.min}`);
      if (safeTrim(node.max)) hints.push(`max:${node.max}`);
      if (safeTrim(node.step)) hints.push(`step:${node.step}`);
    } else if (node instanceof HTMLTextAreaElement) {
      if (node.maxLength > -1) hints.push(`maxlength:${node.maxLength}`);
      if (node.minLength > -1) hints.push(`minlength:${node.minLength}`);
    }
    return uniqueStrings(hints);
  }
  function constraintFlags(node) {
    if (!(node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement)) return [];
    const validity = node.validity;
    const flags = [];
    const known = ["badInput", "customError", "patternMismatch", "rangeOverflow", "rangeUnderflow", "stepMismatch", "tooLong", "tooShort", "typeMismatch", "valueMissing"];
    for (const key of known) {
      if (validity[key]) flags.push(key);
    }
    return flags;
  }
  function candidateInfo(node, score, fallback, win = window) {
    const labels = labelTexts(node);
    const descriptions = descriptionTexts(node);
    const fieldsetLegend = nearestLegend(node);
    const dialog = nearestDialog(node);
    const form = formContext(node);
    const frame = frameContext(win);
    const selected = selectedOptions(node);
    const options = optionLabels(node);
    const placeholder = safeTrim(node.getAttribute("placeholder")) || void 0;
    const name = safeTrim(node.getAttribute("name")) || void 0;
    const explicitRole = safeTrim(node.getAttribute("role")) || void 0;
    const accessibleNames = uniqueStrings([
      safeTrim(node.getAttribute("aria-label")),
      ...labels,
      placeholder,
      name
    ]);
    const textSample = safeTrim(node.textContent)?.slice(0, 120) || void 0;
    const control = controlKind(node) || void 0;
    const checkedState = node instanceof HTMLInputElement && ["checkbox", "radio"].includes((node.type || "").toLowerCase()) ? node.checked ? "checked" : "unchecked" : void 0;
    const readonly = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement ? node.readOnly : void 0;
    const disabled = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement || node instanceof HTMLButtonElement ? node.disabled : void 0;
    const multiple = node instanceof HTMLInputElement || node instanceof HTMLSelectElement ? Boolean(node.multiple) : void 0;
    const required = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement ? node.required : void 0;
    const invalid = node instanceof HTMLInputElement || node instanceof HTMLTextAreaElement || node instanceof HTMLSelectElement ? node.matches(":invalid") : void 0;
    const autoComplete = autocompleteValue(node) || void 0;
    const inputMode = inputModeValue(node) || void 0;
    const hintList = constraintHints(node);
    const flagList = constraintFlags(node);
    const choice = choiceGroup(node) || void 0;
    const submitAction = node instanceof HTMLButtonElement || node instanceof HTMLInputElement && ["submit", "button"].includes((node.type || "").toLowerCase()) ? form.action || void 0 : void 0;
    const submitMethod = node instanceof HTMLButtonElement || node instanceof HTMLInputElement && ["submit", "button"].includes((node.type || "").toLowerCase()) ? form.method || void 0 : void 0;
    const submitTarget = node instanceof HTMLButtonElement || node instanceof HTMLInputElement ? safeTrim(node.getAttribute("formtarget")) || void 0 : void 0;
    return {
      selector_hint: selectorHint(node, fallback),
      score: Number(score.toFixed(3)),
      text_length: (textFrom(node) || "").length,
      visible: isVisible(node),
      ...labels[0] ? { label_text: labels[0] } : {},
      ...labels.length ? { labels } : {},
      ...accessibleNames[0] ? { accessible_name: accessibleNames[0] } : {},
      ...accessibleNames.length ? { accessible_names: accessibleNames } : {},
      ...descriptions[0] ? { description_text: descriptions[0] } : {},
      ...descriptions.length ? { descriptions } : {},
      ...fieldsetLegend ? { fieldset_legend: fieldsetLegend, fieldset_legends: [fieldsetLegend] } : {},
      ...dialog.name ? { dialog_name: dialog.name } : {},
      ...dialog.role ? { dialog_role: dialog.role } : {},
      ...typeof dialog.modal === "boolean" ? { dialog_modal: dialog.modal } : {},
      ...typeof dialog.open === "boolean" ? { dialog_open: dialog.open } : {},
      ...control ? { control_kind: control } : {},
      ...form.name ? { form_name: form.name } : {},
      ...form.action ? { form_action: form.action } : {},
      ...form.method ? { form_method: form.method } : {},
      ...frame.selector ? { frame_selector: frame.selector } : {},
      ...frame.name ? { frame_name: frame.name } : {},
      ...frame.title ? { frame_title: frame.title } : {},
      ...frame.path ? { frame_path: frame.path } : {},
      ...typeof frame.depth === "number" ? { frame_depth: frame.depth } : {},
      ...frame.pathSelectors?.length ? { frame_path_selectors: frame.pathSelectors } : {},
      ...frame.pathNames?.length ? { frame_path_names: frame.pathNames } : {},
      ...frame.pathTitles?.length ? { frame_path_titles: frame.pathTitles } : {},
      ...options.length ? { option_count: options.length, option_labels: options } : {},
      ...selected.length ? { selected_options: selected, selected_count: selected.length } : {},
      ...typeof required === "boolean" ? { required } : {},
      ...typeof invalid === "boolean" ? { invalid } : {},
      ...checkedState ? { checked_state: checkedState } : {},
      ...typeof disabled === "boolean" ? { disabled } : {},
      ...typeof readonly === "boolean" ? { readonly } : {},
      ...typeof multiple === "boolean" ? { multiple } : {},
      ...autoComplete ? { autocomplete: autoComplete } : {},
      ...inputMode ? { input_mode: inputMode } : {},
      ...hintList.length ? { constraint_hints: hintList } : {},
      ...flagList.length ? { constraint_flags: flagList } : {},
      ...choice ? { choice_group: choice } : {},
      ...placeholder ? { placeholder } : {},
      ...name ? { name } : {},
      ...explicitRole ? { role: explicitRole } : {},
      ...textSample ? { text_sample: textSample } : {},
      ...submitAction ? { submit_action: submitAction } : {},
      ...submitMethod ? { submit_method: submitMethod } : {},
      ...submitTarget ? { submit_target: submitTarget } : {}
    };
  }
  function iframeSampleFromElement(iframe, ownerDocument, depth, extra = {}) {
    const src = safeTrim(iframe.getAttribute("src")) || void 0;
    let resolvedSrc;
    if (src) {
      try {
        resolvedSrc = new URL(src, ownerDocument.baseURI).href;
      } catch {
        resolvedSrc = void 0;
      }
    }
    const name = safeTrim(iframe.getAttribute("name")) || void 0;
    const title = safeTrim(iframe.getAttribute("title")) || void 0;
    return {
      selectorHint: selectorHint(iframe, "iframe"),
      depth,
      ...src ? { src } : {},
      ...resolvedSrc ? { resolvedSrc } : {},
      ...name ? { name } : {},
      ...title ? { title } : {},
      ...extra
    };
  }
  function accessibleFrameContext(parent, iframe) {
    try {
      const frameWindow = iframe.contentWindow;
      const frameDocument = iframe.contentDocument || frameWindow?.document || null;
      if (!frameWindow || !frameDocument || !frameDocument.documentElement) return null;
      const selector = selectorHint(iframe, "iframe");
      const name = safeTrim(iframe.getAttribute("name")) || void 0;
      const title = safeTrim(iframe.getAttribute("title")) || void 0;
      const pathSelectors = [...parent.frame_path_selectors, selector];
      const pathNames = uniqueStrings([...parent.frame_path_names, name]);
      const pathTitles = uniqueStrings([...parent.frame_path_titles, title]);
      return {
        document: frameDocument,
        window: frameWindow,
        depth: parent.depth + 1,
        frame_selector: selector,
        ...name ? { frame_name: name } : {},
        ...title ? { frame_title: title } : {},
        ...pathSelectors.length ? { frame_path: pathSelectors.join(" >> ") } : {},
        frame_path_selectors: pathSelectors,
        frame_path_names: pathNames,
        frame_path_titles: pathTitles
      };
    } catch {
      return null;
    }
  }
  function collectLiveFrameInventory(rootDocument = document, rootWindow = window, maxDepth = 4) {
    const rootContext = {
      document: rootDocument,
      window: rootWindow,
      depth: 0,
      frame_path_selectors: [],
      frame_path_names: [],
      frame_path_titles: []
    };
    const contexts = [rootContext];
    const queue = [rootContext];
    const iframeSamples = [];
    const blockedIframeSamples = [];
    const visitedDocuments = /* @__PURE__ */ new Set([rootDocument]);
    let accessibleIframeCount = 0;
    let blockedIframeCount = 0;
    let maxFrameDepth = 0;
    while (queue.length) {
      const context = queue.shift();
      maxFrameDepth = Math.max(maxFrameDepth, context.depth);
      if (context.depth >= maxDepth) continue;
      const iframes = Array.from(context.document.querySelectorAll("iframe"));
      for (const iframe of iframes) {
        if (!(iframe instanceof HTMLIFrameElement)) continue;
        const nextContext = accessibleFrameContext(context, iframe);
        const pathSelectors = [...context.frame_path_selectors, selectorHint(iframe, "iframe")];
        const path = pathSelectors.join(" >> ");
        if (nextContext && !visitedDocuments.has(nextContext.document)) {
          accessibleIframeCount += 1;
          visitedDocuments.add(nextContext.document);
          contexts.push(nextContext);
          queue.push(nextContext);
          iframeSamples.push(iframeSampleFromElement(iframe, context.document, context.depth + 1, {
            accessible: true,
            ...path ? { framePath: path, framePathSelectors: pathSelectors } : {}
          }));
          continue;
        }
        if (nextContext) {
          iframeSamples.push(iframeSampleFromElement(iframe, context.document, context.depth + 1, {
            accessible: true,
            ...path ? { framePath: path, framePathSelectors: pathSelectors } : {}
          }));
          continue;
        }
        blockedIframeCount += 1;
        const blocked = iframeSampleFromElement(iframe, context.document, context.depth + 1, {
          accessible: false,
          reason: "cross-origin-or-inaccessible",
          ...path ? { framePath: path, framePathSelectors: pathSelectors } : {}
        });
        iframeSamples.push(blocked);
        blockedIframeSamples.push(blocked);
      }
    }
    const totalIframeCount = iframeSamples.length;
    const frameCaptureStatus = totalIframeCount === 0 ? "no_iframes" : accessibleIframeCount === 0 && blockedIframeCount > 0 ? "blocked_only" : blockedIframeCount > 0 ? "partial" : "full";
    const frameCaptureRatio = totalIframeCount > 0 ? Number((accessibleIframeCount / totalIframeCount).toFixed(3)) : 1;
    return {
      contexts,
      iframe_samples: iframeSamples.slice(0, 16),
      accessible_iframe_count: accessibleIframeCount,
      blocked_iframe_count: blockedIframeCount,
      blocked_iframe_samples: blockedIframeSamples.slice(0, 8),
      blocked_iframe_names: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.name === "string" ? sample.name : null)),
      blocked_iframe_titles: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.title === "string" ? sample.title : null)),
      blocked_frame_paths: uniqueStrings(blockedIframeSamples.map((sample) => typeof sample.framePath === "string" ? sample.framePath : null)),
      traversed_document_count: contexts.length,
      total_iframe_count: totalIframeCount,
      frame_capture_ratio: frameCaptureRatio,
      frame_capture_status: frameCaptureStatus,
      max_frame_depth: maxFrameDepth,
      frame_paths: uniqueStrings(contexts.slice(1).map((context) => context.frame_path ?? null))
    };
  }
  function semanticOutlineFromInventory(inventory, inputs, submits = []) {
    const headings = uniqueStrings(inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll("h1, h2, h3, h4, h5, h6")).map((heading) => heading.textContent)));
    const forms = inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll("form")));
    const dialogs = inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]')));
    const iframes = inventory.iframe_samples;
    const allCandidates = [...inputs, ...submits];
    const stateFlags = uniqueStrings(allCandidates.flatMap((item) => {
      const flags = [];
      if (item.required) flags.push("required");
      if (item.invalid) flags.push("invalid");
      if (item.disabled) flags.push("disabled");
      if (item.readonly) flags.push("readonly");
      if (item.multiple) flags.push("multiple");
      if (item.checked_state) flags.push(`checked:${item.checked_state}`);
      return flags;
    }));
    const linkHosts = uniqueStrings(inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll("a[href]")).map((link) => {
      try {
        return new URL(link.href, context.document.baseURI).host;
      } catch {
        return null;
      }
    })));
    return {
      heading_outline: headings,
      prompt_labels: uniqueStrings(inputs.flatMap((item) => [item.label_text, ...item.labels || []])),
      accessible_names: uniqueStrings(inputs.flatMap((item) => [item.accessible_name, ...item.accessible_names || []])),
      prompt_descriptions: uniqueStrings(inputs.flatMap((item) => [item.description_text, ...item.descriptions || []])),
      submit_labels: uniqueStrings(submits.flatMap((item) => [item.accessible_name, item.label_text, item.text_sample])),
      form_names: uniqueStrings([
        ...inputs.map((item) => item.form_name || null),
        ...forms.map((form) => safeTrim(form.getAttribute("aria-label")) || safeTrim(form.querySelector("legend, h1, h2, h3, h4, h5, h6")?.textContent ?? null))
      ]),
      form_actions: uniqueStrings([
        ...inputs.map((item) => item.form_action || null),
        ...submits.map((item) => item.submit_action || item.form_action || null),
        ...forms.map((form) => form instanceof HTMLFormElement ? safeTrim(form.action) : null)
      ]),
      fieldset_legends: uniqueStrings(inputs.flatMap((item) => [item.fieldset_legend, ...item.fieldset_legends || []])),
      dialog_names: uniqueStrings([
        ...inputs.map((item) => item.dialog_name || null),
        ...dialogs.map((dialog) => safeTrim(dialog.getAttribute("aria-label")) || safeTrim(dialog.querySelector("h1, h2, h3, legend")?.textContent ?? null))
      ]),
      iframe_names: uniqueStrings([
        ...inputs.flatMap((item) => [item.frame_name, ...item.frame_path_names || []]),
        ...iframes.map((frame) => typeof frame.name === "string" ? frame.name : null)
      ]),
      iframe_titles: uniqueStrings([
        ...inputs.flatMap((item) => [item.frame_title, ...item.frame_path_titles || []]),
        ...iframes.map((frame) => typeof frame.title === "string" ? frame.title : null)
      ]),
      frame_paths: uniqueStrings([
        ...inputs.map((item) => item.frame_path || null),
        ...inventory.frame_paths,
        ...iframes.map((frame) => typeof frame.framePath === "string" ? frame.framePath : null)
      ]),
      control_kinds: uniqueStrings(inputs.map((item) => item.control_kind || null)),
      option_labels: uniqueStrings(inputs.flatMap((item) => item.option_labels || [])),
      choice_groups: uniqueStrings(inputs.map((item) => item.choice_group || null)),
      autocomplete_tokens: uniqueStrings(inputs.map((item) => item.autocomplete || null)),
      state_flags: stateFlags,
      constraint_hints: uniqueStrings(inputs.flatMap((item) => item.constraint_hints || [])),
      link_hosts: linkHosts
    };
  }
  function dialogSamplesFromInventory(inventory) {
    return inventory.contexts.flatMap((context) => Array.from(context.document.querySelectorAll('dialog, [role="dialog"], [role="alertdialog"]')).slice(0, 8).map((dialog) => {
      const ctx = nearestDialog(dialog);
      return {
        selectorHint: selectorHint(dialog, "dialog"),
        ...ctx.name ? { name: ctx.name } : {},
        ...ctx.role ? { role: ctx.role } : {},
        ...typeof ctx.modal === "boolean" ? { modal: ctx.modal } : {},
        ...typeof ctx.open === "boolean" ? { open: ctx.open } : {},
        ...context.frame_path ? { framePath: context.frame_path, framePathSelectors: context.frame_path_selectors } : {}
      };
    })).slice(0, 16);
  }
  function iframeSamplesFromInventory(inventory) {
    return inventory.iframe_samples.slice(0, 16);
  }
  function countAcrossContexts(inventory, selector) {
    return inventory.contexts.reduce((total, context) => total + context.document.querySelectorAll(selector).length, 0);
  }
  function buildLiveFixtureMetadata(document2, inputNode, submitNode = null, inputInfo, submitInfo, options = {}) {
    const inventory = options.inventory || collectLiveFrameInventory(document2, window);
    const computedInput = inputNode ? inputInfo || candidateInfo(inputNode, 1, selectorHint(inputNode, "input")) : null;
    const computedSubmit = submitNode ? submitInfo || candidateInfo(submitNode, 1, selectorHint(submitNode, "button")) : null;
    const inputs = options.inputCandidates?.length ? options.inputCandidates : computedInput ? [computedInput] : [];
    const outputs = options.outputCandidates?.length ? options.outputCandidates : [];
    const submits = options.submitCandidates?.length ? options.submitCandidates : computedSubmit ? [computedSubmit] : [];
    const primaryInput = computedInput || inputs[0] || null;
    const primaryOutput = outputs[0] || null;
    const primarySubmit = computedSubmit || submits[0] || null;
    const outline = semanticOutlineFromInventory(inventory, inputs, submits);
    const dialogs = dialogSamplesFromInventory(inventory);
    const iframes = iframeSamplesFromInventory(inventory);
    const frameCaptureWarning = inventory.frame_capture_status === "partial" ? `frame capture is partial: ${inventory.accessible_iframe_count}/${inventory.total_iframe_count} iframes were accessible and ${inventory.blocked_iframe_count} were blocked` : inventory.frame_capture_status === "blocked_only" ? `frame capture could not descend into any iframe: ${inventory.blocked_iframe_count} blocked iframe${inventory.blocked_iframe_count === 1 ? "" : "s"} observed` : null;
    return {
      link_count: countAcrossContexts(inventory, "a[href]"),
      form_count: countAcrossContexts(inventory, "form"),
      dialog_count: countAcrossContexts(inventory, 'dialog, [role="dialog"], [role="alertdialog"]'),
      iframe_count: countAcrossContexts(inventory, "iframe"),
      heading_count: countAcrossContexts(inventory, "h1, h2, h3, h4, h5, h6"),
      accessible_iframe_count: inventory.accessible_iframe_count,
      blocked_iframe_count: inventory.blocked_iframe_count,
      blocked_iframe_names: inventory.blocked_iframe_names,
      blocked_iframe_titles: inventory.blocked_iframe_titles,
      blocked_frame_paths: inventory.blocked_frame_paths,
      traversed_document_count: inventory.traversed_document_count,
      total_iframe_count: inventory.total_iframe_count,
      frame_capture_ratio: inventory.frame_capture_ratio,
      frame_capture_status: inventory.frame_capture_status,
      ...frameCaptureWarning ? { frame_capture_warning: frameCaptureWarning } : {},
      max_frame_depth: inventory.max_frame_depth,
      frame_paths: outline.frame_paths,
      blocked_iframe_samples: inventory.blocked_iframe_samples,
      split_scope_detected: (primaryInput?.frame_path ?? null) !== (primaryOutput?.frame_path ?? null),
      top_input_label: primaryInput?.label_text ?? null,
      top_input_accessible_name: primaryInput?.accessible_name ?? primaryInput?.label_text ?? null,
      top_input_description: primaryInput?.description_text ?? null,
      top_output_label: primaryOutput?.accessible_name ?? primaryOutput?.label_text ?? primaryOutput?.text_sample ?? null,
      top_output_frame_path: primaryOutput?.frame_path ?? null,
      top_output_frame_depth: primaryOutput?.frame_depth ?? null,
      top_fieldset_legend: primaryInput?.fieldset_legend ?? null,
      top_dialog_name: primaryInput?.dialog_name ?? null,
      top_form_name: primaryInput?.form_name ?? null,
      top_input_frame_path: primaryInput?.frame_path ?? null,
      top_input_frame_depth: primaryInput?.frame_depth ?? null,
      top_option_count: primaryInput?.option_count ?? null,
      top_selected_option: primaryInput?.selected_options?.[0] ?? null,
      top_checked_state: primaryInput?.checked_state ?? null,
      top_disabled: primaryInput?.disabled ?? false,
      top_readonly: primaryInput?.readonly ?? false,
      top_multiple: primaryInput?.multiple ?? false,
      top_selected_count: primaryInput?.selected_count ?? null,
      top_autocomplete: primaryInput?.autocomplete ?? null,
      top_input_mode: primaryInput?.input_mode ?? null,
      top_choice_group: primaryInput?.choice_group ?? null,
      top_constraint_hints: primaryInput?.constraint_hints ?? [],
      top_constraint_flags: primaryInput?.constraint_flags ?? [],
      top_submit_label: primarySubmit?.accessible_name ?? primarySubmit?.label_text ?? primarySubmit?.text_sample ?? null,
      top_submit_action: primarySubmit?.submit_action ?? primarySubmit?.form_action ?? null,
      top_submit_frame_path: primarySubmit?.frame_path ?? null,
      submit_candidates: submits,
      semantic_outline: outline,
      dialog_samples: dialogs,
      iframe_samples: iframes,
      form_actions: outline.form_actions
    };
  }

  // src/adapters/surface-probe.ts
  var SURFACE_PROBE_VERSION = "rev0359";
  var VOLATILE_ID_PATTERNS = [/^radix-/i, /^:r[0-9a-z]+:$/i, /^headlessui-/i, /^mui-/i, /^react-aria-/i];
  function isVolatileId(id) {
    if (!id) return true;
    return VOLATILE_ID_PATTERNS.some((pattern) => pattern.test(id));
  }
  var ROLE_ATLAS = [
    // The prompt editor itself. It is picked up by the interactive-node sweep
    // (role=textbox), and leaving it 'unknown' would make every healthy composer
    // report an oddity — the classic detector that nobody reads.
    { role: "composer", ids: ["prompt-textarea"], testIds: ["prompt-textarea"], terms: ["chat with chatgpt", "ask chatgpt"] },
    { role: "send", ids: ["composer-submit-button"], testIds: ["send-button"], terms: ["send prompt", "send message"] },
    { role: "stop", testIds: ["stop-button"], terms: ["stop generating", "stop streaming", "stop responding", "stop response"] },
    { role: "continue", terms: ["continue generating", "continue response"] },
    {
      role: "attach",
      ids: ["composer-plus-btn", "upload-files", "upload-photos", "upload-camera"],
      testIds: ["composer-plus-btn", "upload-photos-input"],
      terms: ["add files and more", "add files", "add photos", "attach", "upload file"]
    },
    { role: "dictate", terms: ["dictate", "microphone", "voice mode", "start dictation", "start voice"] },
    { role: "model-picker", testIds: ["model-switcher-dropdown-button"], terms: ["model selector", "switch model", "choose model"] },
    // The composer pill. Live report shows it as a __composer-pill button whose
    // text is the current effort tier ("Pro"). Its id is volatile (radix-*), so it
    // is matched by class/text, never by id.
    { role: "effort-pill", classes: ["__composer-pill"], terms: ["instant", "medium", "high", "extra high", "pro"] },
    { role: "tools", terms: ["tools", "deep research", "create image", "canvas"] },
    { role: "search", terms: ["search chats", "search"] },
    { role: "copy", testIds: ["copy-turn-action-button"], terms: ["copy", "copy code", "copy response"] },
    { role: "edit", terms: ["edit message", "edit in canvas"] },
    { role: "regenerate", terms: ["regenerate", "try again", "retry"] },
    { role: "feedback", testIds: ["good-response-turn-action-button", "bad-response-turn-action-button"], terms: ["good response", "bad response", "thumbs"] },
    { role: "scroll", terms: ["scroll to bottom"] },
    { role: "new-chat", testIds: ["create-new-chat-button"], terms: ["new chat"] },
    { role: "conversation-options", testIds: ["conversation-options-button"], terms: ["conversation options", "open conversation options", "pin "] },
    { role: "citation", testIds: ["webpage-citation-pill"], terms: ["sources"] },
    { role: "sidebar", testIds: ["close-sidebar-button"], terms: ["sidebar", "open sidebar", "close sidebar"] },
    { role: "account", testIds: ["accounts-profile-button"], terms: ["account", "profile", "settings", "upgrade", "log in", "sign up", "download apps"] },
    { role: "share", terms: ["share"] },
    { role: "close", terms: ["close", "dismiss"] },
    // The signed-in root page renders these legal/help links inside the composer
    // form. Match exact link text so a future action button containing the same
    // words remains visible to the oddity hunter.
    { role: "nav", exactTexts: ["terms", "privacy policy", "learn more"] }
  ];
  function lower(value) {
    return (value || "").trim().toLowerCase();
  }
  function classify(control) {
    const id = lower(control.id);
    const testId = lower(control.test_id);
    const text = lower(control.text);
    const combined = [control.aria_label, control.title, control.text, control.test_id].map(lower).filter(Boolean).join(" | ");
    for (const matcher of ROLE_ATLAS) {
      const evidence = [];
      if (matcher.ids?.some((candidate) => candidate === id)) evidence.push(`id=${id}`);
      if (matcher.testIds?.some((candidate) => candidate === testId)) evidence.push(`data-testid=${testId}`);
      if (matcher.classes?.some((candidate) => control.class_tokens?.includes(candidate))) {
        evidence.push(`class=${matcher.classes.find((candidate) => control.class_tokens?.includes(candidate))}`);
      }
      if (matcher.terms?.some((term) => combined.includes(term))) {
        const hit = matcher.terms.find((term) => combined.includes(term));
        evidence.push(`term=${hit}`);
      }
      if (matcher.exactTexts?.some((candidate) => candidate === text)) evidence.push(`text=${text}`);
      if (evidence.length) return { role: matcher.role, evidence };
    }
    return { role: "unknown", evidence: [] };
  }
  function regionOf(node) {
    if (node.closest('[role="dialog"], dialog, [aria-modal="true"]')) return "dialog";
    if (node.closest('[role="alert"], [role="status"], [aria-live]')) return "banner";
    if (node.closest('form, #composer-background, [data-testid="composer"], [class*="composer"]')) return "composer";
    if (node.closest('nav, aside, [role="navigation"], [role="complementary"]')) return "sidebar";
    if (node.closest('header, [role="banner"]')) return "header";
    if (node.closest('main, [role="main"], article')) return "transcript";
    return "page";
  }
  function controlKey(control) {
    if (control.id && !isVolatileId(control.id)) return `id:${control.id}`;
    if (control.test_id) return `testid:${control.test_id}`;
    if (control.aria_label) return `aria:${lower(control.aria_label)}`;
    if (control.text) return `text:${lower(control.text).slice(0, 40)}`;
    return `sel:${control.selector_hint}`;
  }
  var INTERACTIVE_SELECTOR = [
    "button",
    '[role="button"]',
    '[role="menuitem"]',
    '[role="tab"]',
    '[role="switch"]',
    "a[href]",
    'input:not([type="hidden"])',
    "select",
    "textarea"
  ].join(", ");
  function probeControls(document2) {
    const controls = [];
    const seen = /* @__PURE__ */ new Set();
    for (const node of Array.from(document2.querySelectorAll(INTERACTIVE_SELECTOR))) {
      if (seen.has(node)) continue;
      seen.add(node);
      const el = node;
      const text = textFrom(node);
      const partial = {
        selector_hint: selectorHint(node, "control"),
        tag: node.tagName.toLowerCase(),
        id: node.getAttribute("id") || null,
        test_id: node.getAttribute("data-testid") || null,
        aria_label: node.getAttribute("aria-label") || null,
        title: node.getAttribute("title") || null,
        text: text ? text.slice(0, 120) : null,
        role_attr: node.getAttribute("role") || null,
        type_attr: node.getAttribute("type") || null,
        disabled: el.disabled === true || node.getAttribute("aria-disabled") === "true",
        visible: isVisible(node),
        class_tokens: Array.from(node.classList),
        region: regionOf(node)
      };
      const { role, evidence } = classify(partial);
      const withRole = { ...partial, classification: role, evidence };
      controls.push({ ...withRole, key: controlKey(withRole), id_stable: Boolean(partial.id) && !isVolatileId(partial.id) });
    }
    return controls;
  }
  function probeAnchors(document2, found, expected) {
    const anchor = (name, node, expectedSelector, detail = {}) => ({
      name,
      found: Boolean(node),
      selector_hint: node ? selectorHint(node, name) : null,
      expected_selector: expectedSelector,
      matches_expectation: Boolean(node && expectedSelector && node.matches(expectedSelector)),
      detail
    });
    return [
      anchor("composer", found.composer, expected.composer, { editable: found.composer?.isContentEditable ?? null }),
      anchor("send", found.send, expected.send, {
        test_id: found.send?.getAttribute("data-testid") ?? null,
        aria_label: found.send?.getAttribute("aria-label") ?? null,
        disabled: found.send ? found.send.disabled : null
      }),
      anchor("generation_stop", found.stop, null, {}),
      anchor("generation_continue", found.continue, null, {}),
      anchor("latest_assistant_turn", found.latestAssistant, null, {}),
      anchor("latest_user_turn", found.latestUser, null, {})
    ];
  }
  function collectOddities(controls, anchors, composer) {
    const oddities = [];
    for (const control of controls) {
      if (!control.visible) continue;
      if (control.classification === "unknown" && control.region === "composer") {
        oddities.push({
          kind: "unknown-control",
          severity: "warn",
          region: "composer",
          summary: `unclassified control in the composer: ${control.selector_hint}`,
          control
        });
      } else if (control.classification === "unknown" && control.region === "dialog") {
        oddities.push({
          kind: "dialog",
          severity: "warn",
          region: "dialog",
          summary: `unclassified control inside a modal dialog: ${control.selector_hint}`,
          control
        });
      }
    }
    const dialogControls = controls.filter((control) => control.region === "dialog" && control.visible);
    if (dialogControls.length) {
      oddities.push({
        kind: "dialog",
        severity: "warn",
        region: "dialog",
        summary: `a modal dialog is open (${dialogControls.length} control(s)); it may be intercepting clicks`
      });
    }
    const bannerControls = controls.filter((control) => control.region === "banner" && control.visible);
    if (bannerControls.length) {
      oddities.push({
        kind: "banner",
        severity: "info",
        region: "banner",
        summary: `a live/alert region is present (${bannerControls.length} control(s)); possible nag, error, or rate-limit notice`
      });
    }
    for (const item of anchors) {
      if (!item.found) {
        if (item.name === "send" && composer.present && composer.empty) {
          oddities.push({
            kind: "send-hidden-empty-composer",
            severity: "info",
            region: "composer",
            summary: "no send control, but the composer is empty \u2014 ChatGPT only renders send once you type. Probe with a draft for a definitive reading.",
            anchor: "send"
          });
          continue;
        }
        const critical = item.name === "composer" || item.name === "send";
        oddities.push({
          kind: "missing-anchor",
          severity: critical ? "critical" : "info",
          region: "page",
          summary: `anchor not found: ${item.name}`,
          anchor: item.name
        });
      } else if (item.expected_selector && !item.matches_expectation) {
        oddities.push({
          kind: "unexpected-anchor-selector",
          severity: "critical",
          region: "page",
          summary: `anchor '${item.name}' resolved to ${item.selector_hint}, which does not match the expected selector ${item.expected_selector}`,
          anchor: item.name
        });
      }
    }
    return oddities;
  }
  var FILE_INPUT_SELECTORS = [
    'form input[type="file"]',
    '[class*="composer"] input[type="file"]',
    'input[type="file"]'
  ];
  function findFileInputs(document2) {
    const inputs = [];
    const seen = /* @__PURE__ */ new Set();
    for (const selector of FILE_INPUT_SELECTORS) {
      for (const node of Array.from(document2.querySelectorAll(selector))) {
        if (node instanceof HTMLInputElement && node.type === "file" && !node.disabled && !seen.has(node)) {
          seen.add(node);
          inputs.push(node);
        }
      }
    }
    return inputs;
  }
  function findFileInput(document2) {
    return findFileInputs(document2)[0] ?? null;
  }
  function authenticationState(document2) {
    const visible = (selector) => Array.from(document2.querySelectorAll(selector)).some(isVisible);
    const loginControlPresent = visible('[data-testid="login-button"]');
    const signupControlPresent = visible('[data-testid="signup-button"]');
    const accountControlPresent = visible('[data-testid="accounts-profile-button"]');
    const anonymous = loginControlPresent || signupControlPresent;
    return {
      posture: anonymous ? "anonymous" : accountControlPresent ? "authenticated" : "unknown",
      login_control_present: loginControlPresent,
      signup_control_present: signupControlPresent,
      account_control_present: accountControlPresent
    };
  }
  function composerState(document2, composer, controls) {
    const fileInputs = findFileInputs(document2);
    const fileInput = fileInputs[0] ?? null;
    const text = composer ? (composer.textContent || "").trim() : "";
    const inputFiles = fileInputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
    const attachmentChips = controls.filter((control) => control.region === "composer" && control.visible && control.classification === "attachment-chip").length;
    return {
      present: Boolean(composer),
      empty: text.length === 0,
      text_length: text.length,
      file_input_present: Boolean(fileInput),
      file_input_selector: fileInput ? selectorHint(fileInput, "file-input") : null,
      file_input_multiple: Boolean(fileInput?.multiple),
      attachment_chip_count: attachmentChips,
      attached_file_count: Math.max(inputFiles, attachmentChips)
    };
  }
  function composerControlKeys(document2) {
    return probeControls(document2).filter((control) => control.region === "composer" && control.visible).map((control) => control.key);
  }
  function composerControlDelta(document2, keysBefore) {
    const remaining = /* @__PURE__ */ new Map();
    for (const key of keysBefore) remaining.set(key, (remaining.get(key) || 0) + 1);
    const addedControls = [];
    for (const control of probeControls(document2)) {
      if (control.region !== "composer" || !control.visible) continue;
      const prior = remaining.get(control.key) || 0;
      if (prior > 0) {
        remaining.set(control.key, prior - 1);
      } else {
        addedControls.push(control);
      }
    }
    return {
      added_keys: addedControls.map((control) => control.key),
      added_controls: addedControls
    };
  }
  function buildSurfaceProbe(document2, inputs) {
    const controls = probeControls(document2);
    const composer = composerState(document2, inputs.composer, controls);
    const authentication = authenticationState(document2);
    const anchors = probeAnchors(
      document2,
      {
        composer: inputs.composer,
        send: inputs.send,
        stop: inputs.stop,
        continue: inputs.continueControl,
        latestAssistant: inputs.latestAssistant,
        latestUser: inputs.latestUser
      },
      { composer: inputs.expectedComposerSelector, send: inputs.expectedSendSelector }
    );
    const oddities = collectOddities(controls, anchors, composer);
    const byRole = {};
    for (const control of controls) {
      byRole[control.classification] = (byRole[control.classification] || 0) + 1;
    }
    return {
      probe_version: SURFACE_PROBE_VERSION,
      captured_at: (/* @__PURE__ */ new Date()).toISOString(),
      url: inputs.url,
      route: inputs.route,
      authentication,
      composer,
      capabilities: {
        // Each of these maps 1:1 onto a GlassTTY command that breaks if it is false.
        write_prompt: Boolean(inputs.composer),
        // null when the composer is empty: ChatGPT hides send until you type, so a
        // missing send button here proves nothing either way. Claiming `false`
        // would flag a healthy page as broken (see the note on `capabilities`).
        submit_prompt: inputs.send ? true : composer.present && composer.empty ? null : false,
        detect_generation: inputs.generationState !== "unknown",
        read_latest_output: Boolean(inputs.latestAssistant),
        read_user_turn: Boolean(inputs.latestUser),
        continue_generation: Boolean(inputs.continueControl),
        attach_files: composer.file_input_present && authentication.posture === "authenticated"
      },
      anchors,
      controls,
      oddities,
      counts: {
        controls: controls.length,
        visible_controls: controls.filter((control) => control.visible).length,
        unknown_controls: controls.filter((control) => control.classification === "unknown").length,
        oddities: oddities.length,
        critical_oddities: oddities.filter((oddity) => oddity.severity === "critical").length,
        ...byRole
      }
    };
  }

  // src/adapters/chatgpt.ts
  var PROMPT_SELECTORS = [
    "#prompt-textarea",
    '[data-testid="prompt-textarea"]',
    'textarea[placeholder*="Message" i]',
    'textarea[placeholder*="Ask" i]',
    "textarea",
    '[contenteditable="true"][role="textbox"]',
    '[contenteditable="plaintext-only"][role="textbox"]',
    '[role="textbox"]',
    'main [data-placeholder*="Message" i]',
    'main [data-placeholder*="Ask" i]',
    "main .ProseMirror[contenteditable]",
    'main [contenteditable="true"]',
    'main [contenteditable="plaintext-only"]',
    '[contenteditable="true"]',
    '[contenteditable="plaintext-only"]'
  ];
  var OUTPUT_SELECTORS = [
    '[data-message-author-role="assistant"]',
    '[data-testid*="conversation-turn"]',
    "article",
    "main article",
    'main [class*="markdown"]',
    ".markdown",
    '[class*="assistant"]',
    '[class*="message"]',
    "main",
    '[role="main"]'
  ];
  var USER_TURN_SELECTORS = [
    '[data-message-author-role="user"]',
    '[data-testid*="conversation-turn"]',
    "article",
    "main article",
    '[class*="user"]',
    '[class*="message"]'
  ];
  var OBSERVED_LIVE_PROMPT_SELECTOR = "#prompt-textarea";
  var OBSERVED_LIVE_SEND_SELECTOR = "#composer-submit-button";
  var OBSERVED_LIVE_SEND_TESTID = "send-button";
  var OBSERVED_LIVE_SEND_ARIA_LABEL = "Send prompt";
  var SEND_BUTTON_SELECTORS = [
    "#composer-submit-button",
    "button#composer-submit-button",
    'button[data-testid="send-button"]',
    'button[aria-label*="Send" i]',
    'button[title*="Send" i]',
    'form button[type="submit"]',
    "button"
  ];
  var SEND_BUTTON_MIN_SCORE = 0.45;
  var GENERATION_STOP_TERMS = [
    "stop generating",
    "stop streaming",
    "stop response",
    "stop responding",
    "stop"
  ];
  var GENERATION_CONTINUE_TERMS = [
    "continue generating",
    "continue response",
    "continue"
  ];
  var NON_SEND_CONTROL_TERMS = [
    "add files",
    "add file",
    "add photos",
    "add photo",
    "add files and more",
    "composer-plus",
    "plus",
    "attach",
    "attachment",
    "upload",
    "file",
    "files",
    "voice",
    "dictate",
    "microphone",
    "audio",
    "stop",
    "cancel",
    "search",
    "tools",
    "tool",
    "deep research",
    "model",
    "picker",
    "reasoning",
    "library",
    "canvas",
    "email",
    "recipient",
    "image",
    "create image",
    "start dictation",
    "copy response",
    "copy message",
    "edit message",
    "good response",
    "bad response",
    "download apps",
    "sources",
    "extra high",
    "prompt 1",
    "prompt 2",
    "prompt 3",
    "prompt 4",
    "prompt 5",
    "prompt 6",
    "prompt 7",
    "prompt 8"
  ];
  var surfaceOverrides = {};
  function topContext(document2, win) {
    return inventoryContexts(document2, win)[0];
  }
  function overrideNode(selector, document2) {
    if (!selector) return null;
    let node = null;
    try {
      node = document2.querySelector(selector);
    } catch {
      return null;
    }
    if (!node || !(node instanceof HTMLElement)) return null;
    return isVisible(node) ? node : null;
  }
  function lower2(value) {
    return (value || "").trim().toLowerCase();
  }
  function includesAny(value, terms) {
    return terms.some((term) => value.includes(term));
  }
  function authorRoleElement(node) {
    return node?.closest("[data-message-author-role]") ?? null;
  }
  function authorRole(node) {
    return lower2(authorRoleElement(node)?.getAttribute("data-message-author-role")) || null;
  }
  function authorRoleSource(node) {
    const roleElement = authorRoleElement(node);
    if (!roleElement) return null;
    return roleElement === node ? "self" : "ancestor";
  }
  function contentEditableMode(node) {
    const raw = node.getAttribute("contenteditable");
    if (raw === null) return null;
    const value = lower2(raw);
    if (value === "false") return null;
    return value || "true";
  }
  function isEditableCandidate(node) {
    if (node instanceof HTMLTextAreaElement) return !node.disabled && !node.readOnly;
    if (node instanceof HTMLInputElement) return !node.disabled && !node.readOnly;
    return Boolean(contentEditableMode(node)) || node.getAttribute("role") === "textbox";
  }
  function promptScore(node) {
    let score = isVisible(node) ? 0.45 : 0.03;
    const id = lower2(node.getAttribute("id"));
    const testId = lower2(node.getAttribute("data-testid"));
    const placeholder = lower2(node.getAttribute("placeholder"));
    const dataPlaceholder = lower2(node.getAttribute("data-placeholder"));
    const aria = lower2(node.getAttribute("aria-label"));
    const role = lower2(node.getAttribute("role"));
    const text = lower2(textFrom(node));
    const className = lower2(node.getAttribute("class"));
    if (!isEditableCandidate(node)) score -= 0.35;
    if (id === "prompt-textarea") score += 0.35;
    if (testId.includes("prompt-textarea")) score += 0.35;
    if (node instanceof HTMLTextAreaElement) score += 0.25;
    if (role === "textbox") score += 0.22;
    if (contentEditableMode(node)) score += 0.18;
    if (includesAny(placeholder, ["message", "ask anything", "chatgpt", "prompt"])) score += 0.2;
    if (includesAny(dataPlaceholder, ["message", "ask anything", "chatgpt", "prompt"])) score += 0.2;
    if (includesAny(aria, ["message", "prompt", "ask", "chatgpt"])) score += 0.16;
    if (className.includes("composer") || className.includes("prompt")) score += 0.08;
    if (includesAny(id + " " + testId + " " + placeholder + " " + dataPlaceholder + " " + aria, ["search", "filter", "rename", "title", "email", "recipient"])) score -= 0.28;
    if (text.length > 0 && text.length < 16e3) score += 0.04;
    if (text.length > 24e3) score -= 0.2;
    return score;
  }
  function outputScore(node) {
    const text = textFrom(node) || "";
    let score = isVisible(node) ? 0.35 : 0.04;
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    const role = lower2(node.getAttribute("role"));
    const roleForTurn = authorRole(node);
    if (roleForTurn === "assistant") score += 0.55;
    if (roleForTurn === "user") score -= 0.55;
    if (dataTestId.includes("conversation-turn")) score += 0.18;
    if (node.tagName === "ARTICLE") score += 0.16;
    if (className.includes("markdown")) score += 0.14;
    if (className.includes("assistant")) score += 0.18;
    if (className.includes("message")) score += 0.08;
    if (role === "main") score -= 0.08;
    if (text.length > 30) score += 0.12;
    if (text.length > 250) score += 0.1;
    if (text.length > 5e3) score -= 0.08;
    if (text.length > 2e4) score -= 0.25;
    return score;
  }
  function sendControlSignal(button) {
    const text = lower2(button.textContent);
    const aria = lower2(button.getAttribute("aria-label"));
    const title = lower2(button.getAttribute("title"));
    const testId = lower2(button.getAttribute("data-testid"));
    const id = lower2(button.getAttribute("id"));
    const type = lower2(button.getAttribute("type"));
    const combined = `${text} ${aria} ${title} ${id} ${testId}`;
    const explicitSendIntent = testId === "send-button" || testId.includes("send-button") || testId.includes("send-message") || id === "composer-submit-button" || id === "send-button" || aria === "send" || aria.includes("send message") || aria.includes("send prompt") || title === "send" || title.includes("send message") || text === "send";
    const formSubmitIntent = type === "submit";
    const nonSendControl = includesAny(combined, NON_SEND_CONTROL_TERMS);
    const exactPlusControl = id === "composer-plus-btn" || testId === "composer-plus-btn";
    return {
      intent: explicitSendIntent || formSubmitIntent,
      explicit: explicitSendIntent,
      submit: formSubmitIntent,
      disqualified: exactPlusControl || nonSendControl && !explicitSendIntent,
      combined
    };
  }
  function userTurnScore(node) {
    const text = textFrom(node) || "";
    let score = isVisible(node) ? 0.34 : 0.03;
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    const role = lower2(node.getAttribute("role"));
    const roleForTurn = authorRole(node);
    if (roleForTurn === "user") score += 0.55;
    if (roleForTurn === "assistant") score -= 0.55;
    if (dataTestId.includes("conversation-turn")) score += 0.16;
    if (node.tagName === "ARTICLE") score += 0.12;
    if (className.includes("user")) score += 0.18;
    if (className.includes("message")) score += 0.06;
    if (roleForTurn === "assistant" || className.includes("assistant")) score -= 0.45;
    if (role === "main") score -= 0.12;
    if (node.matches('textarea, input, [contenteditable="true"], [role="textbox"]')) score -= 0.8;
    if (node.closest('form, [data-testid*="composer"], [class*="composer"]')) score -= 0.5;
    if (text.length > 12) score += 0.08;
    if (text.length > 5e3) score -= 0.16;
    return score;
  }
  function sendButtonScore(button, composer = null) {
    let score = isVisible(button) ? 0.3 : 0.02;
    const text = lower2(button.textContent);
    const aria = lower2(button.getAttribute("aria-label"));
    const title = lower2(button.getAttribute("title"));
    const testId = lower2(button.getAttribute("data-testid"));
    const type = lower2(button.getAttribute("type"));
    const disabled = button.disabled || button.getAttribute("aria-disabled") === "true";
    const signal = sendControlSignal(button);
    if (disabled) score -= 0.8;
    if (!signal.intent) score -= 0.35;
    if (signal.disqualified) score -= 1;
    if (testId === "send-button" || testId.includes("send")) score += 0.5;
    if (aria === "send" || aria.includes("send message") || aria.includes("send prompt")) score += 0.45;
    if (title === "send" || title.includes("send message")) score += 0.32;
    if (text === "send") score += 0.3;
    if (type === "submit") score += 0.18;
    if (composer) {
      const sameForm = button.form && (composer instanceof HTMLInputElement || composer instanceof HTMLTextAreaElement ? composer.form === button.form : Boolean(composer.closest("form") && composer.closest("form") === button.form));
      const composerRoot = findComposerActionRoot(composer, button.ownerDocument);
      if (sameForm) score += 0.2;
      if (composerRoot !== button.ownerDocument && composerRoot.contains(button)) score += 0.16;
      const buttonDialog = button.closest('dialog, [role="dialog"], [role="alertdialog"]');
      const composerDialog = composer.closest('dialog, [role="dialog"], [role="alertdialog"]');
      if (buttonDialog && buttonDialog !== composerDialog) score -= 0.35;
    } else {
      score -= 0.12;
    }
    if (button.closest("nav, header, aside")) score -= 0.18;
    return score;
  }
  function routePostureAllowsSubmit(posture) {
    return posture === "plain-chat";
  }
  function findComposerActionRoot(composer, document2) {
    if (!composer) return document2;
    return composer.closest('form, [data-testid*="composer"], [class*="composer"], [role="form"]') || composer.parentElement || document2;
  }
  function inventoryContexts(document2, win) {
    return collectLiveFrameInventory(document2, win).contexts;
  }
  function rank(selectors, document2, scorer, win) {
    const seen = /* @__PURE__ */ new Set();
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      for (const selector of selectors) {
        for (const node of Array.from(context.document.querySelectorAll(selector))) {
          if (seen.has(node)) continue;
          seen.add(node);
          ranked.push({ node, context, index, score: scorer(node) });
          index += 1;
        }
      }
    }
    return ranked.sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index);
  }
  function bestVisibleElement(selectors, document2, scorer, win) {
    const best = rank(selectors, document2, scorer, win).find(({ node, score }) => score > 0.35 && node instanceof HTMLElement);
    return {
      node: best?.node instanceof HTMLElement ? best.node : null,
      context: best?.context ?? null
    };
  }
  function findPromptComposer(document2, win) {
    const overridden = overrideNode(surfaceOverrides.composer, document2);
    if (overridden && isEditableCandidate(overridden)) {
      return { node: overridden, context: topContext(document2, win) };
    }
    return bestVisibleElement(PROMPT_SELECTORS, document2, promptScore, win);
  }
  function documentOrderIndex(node) {
    if (!node) return void 0;
    const nodes = Array.from(node.ownerDocument.querySelectorAll("*"));
    const index = nodes.indexOf(node);
    return index >= 0 ? index : void 0;
  }
  function outputDocumentOrder(left, right) {
    if (left.node.ownerDocument !== right.node.ownerDocument) {
      return left.context.depth - right.context.depth || left.index - right.index;
    }
    if (left.node === right.node) return 0;
    const position = left.node.compareDocumentPosition(right.node);
    if (position & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
    if (position & Node.DOCUMENT_POSITION_PRECEDING) return 1;
    return left.index - right.index;
  }
  function isAssistantOutputCandidate(node) {
    const roleForTurn = authorRole(node);
    if (roleForTurn) return roleForTurn === "assistant";
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    return className.includes("assistant") || dataTestId.includes("assistant") || node.tagName === "ARTICLE";
  }
  function isUserTurnCandidate(node) {
    const roleForTurn = authorRole(node);
    if (roleForTurn) return roleForTurn === "user";
    const className = lower2(node.getAttribute("class"));
    const dataTestId = lower2(node.getAttribute("data-testid"));
    return className.includes("user") || dataTestId.includes("user") || node.tagName === "ARTICLE";
  }
  function latestOutputMatch(document2, win) {
    const candidates = rank(OUTPUT_SELECTORS, document2, outputScore, win).filter(({ node, score }) => score > 0.35 && Boolean(textFrom(node)) && node instanceof HTMLElement);
    const assistantLike = candidates.filter(({ node }) => isAssistantOutputCandidate(node));
    const ordered = (assistantLike.length ? assistantLike : candidates).slice().sort(outputDocumentOrder);
    const best = ordered[ordered.length - 1];
    return {
      node: best?.node instanceof HTMLElement ? best.node : null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      assistant_like: Boolean(best && isAssistantOutputCandidate(best.node))
    };
  }
  function findLatestOutputNode(document2, win) {
    const match = latestOutputMatch(document2, win);
    return { node: match.node, context: match.context };
  }
  function latestOutputWitness(document2, win) {
    const match = latestOutputMatch(document2, win);
    const node = match.node;
    const context = match.context;
    const roleForTurn = authorRole(node);
    return {
      text: textFrom(node),
      selector_hint: node ? selectorHint(node, "output") : null,
      selection_policy: "latest-visible-assistant-like-node-in-dom-order",
      assistant_like: match.assistant_like || roleForTurn === "assistant",
      author_role: roleForTurn,
      author_role_source: authorRoleSource(node),
      node_tag: node ? node.tagName.toLowerCase() : null,
      candidate_score: Number(match.score.toFixed(3)),
      ...typeof documentOrderIndex(node) === "number" ? { document_order_index: documentOrderIndex(node) } : {},
      ...typeof context?.depth === "number" ? { frame_depth: context.depth } : {},
      ...context?.frame_path ? { frame_path: context.frame_path } : {}
    };
  }
  function latestUserTurnMatch(document2, win) {
    const candidates = rank(USER_TURN_SELECTORS, document2, userTurnScore, win).filter(({ node, score }) => score > 0.35 && Boolean(textFrom(node)) && node instanceof HTMLElement);
    const userLike = candidates.filter(({ node }) => isUserTurnCandidate(node));
    const ordered = (userLike.length ? userLike : candidates).slice().sort(outputDocumentOrder);
    const best = ordered[ordered.length - 1];
    return {
      node: best?.node instanceof HTMLElement ? best.node : null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      user_like: Boolean(best && isUserTurnCandidate(best.node))
    };
  }
  function latestUserTurnWitness(document2, win) {
    const match = latestUserTurnMatch(document2, win);
    const node = match.node;
    const context = match.context;
    const roleForTurn = authorRole(node);
    return {
      text: textFrom(node),
      selector_hint: node ? selectorHint(node, "user-turn") : null,
      selection_policy: "latest-visible-user-like-node-in-dom-order",
      user_like: match.user_like || roleForTurn === "user",
      author_role: roleForTurn,
      author_role_source: authorRoleSource(node),
      node_tag: node ? node.tagName.toLowerCase() : null,
      candidate_score: Number(match.score.toFixed(3)),
      ...typeof documentOrderIndex(node) === "number" ? { document_order_index: documentOrderIndex(node) } : {},
      ...typeof context?.depth === "number" ? { frame_depth: context.depth } : {},
      ...context?.frame_path ? { frame_path: context.frame_path } : {}
    };
  }
  function findLikelySendButton(document2, win, composer = null) {
    const overridden = overrideNode(surfaceOverrides.send, document2);
    if (overridden instanceof HTMLButtonElement) {
      const signal = sendControlSignal(overridden);
      if (!signal.disqualified) {
        return { node: overridden, context: topContext(document2, win), score: sendButtonScore(overridden, composer), scope: document2, signal };
      }
    }
    const seen = /* @__PURE__ */ new Set();
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      const contextComposer = composer && composer.ownerDocument === context.document ? composer : null;
      const scopedRoot = findComposerActionRoot(contextComposer, context.document);
      const scopes = scopedRoot === context.document ? [context.document] : [scopedRoot, context.document];
      for (const scope of scopes) {
        for (const selector of SEND_BUTTON_SELECTORS) {
          for (const node of Array.from(scope.querySelectorAll(selector))) {
            if (seen.has(node) || !(node instanceof HTMLButtonElement)) continue;
            seen.add(node);
            ranked.push({ button: node, context, index, score: sendButtonScore(node, contextComposer), scope });
            index += 1;
          }
        }
      }
    }
    const best = ranked.filter(({ button, score }) => {
      const signal = sendControlSignal(button);
      return score > SEND_BUTTON_MIN_SCORE && signal.intent && !signal.disqualified && !button.disabled && button.getAttribute("aria-disabled") !== "true";
    }).sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index)[0];
    return {
      node: best?.button ?? null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      scope: best?.scope ?? null,
      signal: best?.button ? sendControlSignal(best.button) : null
    };
  }
  function findBlockedComposerControl(document2, win, composer = null) {
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      const contextComposer = composer && composer.ownerDocument === context.document ? composer : null;
      const scopedRoot = findComposerActionRoot(contextComposer, context.document);
      const scopes = scopedRoot === context.document ? [context.document] : [scopedRoot, context.document];
      for (const scope of scopes) {
        for (const node of Array.from(scope.querySelectorAll("button"))) {
          if (!(node instanceof HTMLButtonElement)) continue;
          const signal = sendControlSignal(node);
          if (!signal.disqualified) continue;
          ranked.push({ button: node, context, index, score: sendButtonScore(node, contextComposer), signal });
          index += 1;
        }
      }
    }
    const best = ranked.sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index)[0];
    return {
      node: best?.button ?? null,
      context: best?.context ?? null,
      score: best?.score ?? 0,
      signal: best?.signal ?? null
    };
  }
  function generationControlScore(button, terms) {
    if (!isVisible(button) || button.disabled || button.getAttribute("aria-disabled") === "true") return 0;
    const text = lower2(button.textContent);
    const aria = lower2(button.getAttribute("aria-label"));
    const title = lower2(button.getAttribute("title"));
    const testId = lower2(button.getAttribute("data-testid"));
    const combined = `${text} ${aria} ${title} ${testId}`;
    if (!includesAny(combined, terms)) return 0;
    let score = 0.45;
    if (includesAny(aria, terms) || includesAny(title, terms)) score += 0.22;
    if (includesAny(testId, terms.map((term) => term.replace(/\s+/g, "-")))) score += 0.12;
    if (button.closest('main, [role="main"]')) score += 0.08;
    if (button.closest("nav, header, aside")) score -= 0.2;
    return score;
  }
  function findGenerationControl(document2, win, terms) {
    const ranked = [];
    for (const context of inventoryContexts(document2, win)) {
      let index = 0;
      for (const button of Array.from(context.document.querySelectorAll("button"))) {
        if (!(button instanceof HTMLButtonElement)) continue;
        const score = generationControlScore(button, terms);
        if (score <= 0.35) continue;
        ranked.push({ button, context, index, score });
        index += 1;
      }
    }
    const best = ranked.sort((left, right) => right.score - left.score || left.context.depth - right.context.depth || right.index - left.index)[0];
    return { node: best?.button ?? null, context: best?.context ?? null, score: best?.score ?? 0 };
  }
  function generationState(document2, win) {
    const stop = findGenerationControl(document2, win, GENERATION_STOP_TERMS);
    const continueControl = findGenerationControl(document2, win, GENERATION_CONTINUE_TERMS);
    if (stop.node) return { state: "streaming-or-stoppable", stop, continue: continueControl };
    if (continueControl.node) return { state: "needs-continue", stop, continue: continueControl };
    return { state: "settled-or-idle", stop, continue: continueControl };
  }
  function setNativeValue(node, text) {
    const prototype = Object.getPrototypeOf(node);
    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
    if (descriptor?.set) {
      descriptor.set.call(node, text);
    } else {
      node.value = text;
    }
  }
  function dispatchEditableEvents(node, text) {
    node.dispatchEvent(new InputEvent("beforeinput", { bubbles: true, cancelable: true, data: text, inputType: "insertText" }));
    node.dispatchEvent(new InputEvent("input", { bubbles: true, data: text, inputType: "insertText" }));
    node.dispatchEvent(new Event("change", { bubbles: true }));
  }
  function readbackMatches(node, expected) {
    const actual = (textFrom(node) || "").replace(/\s+/g, " ").trim();
    const target = expected.replace(/\s+/g, " ").trim();
    return actual === target;
  }
  function writeIntoElement(node, text) {
    node.focus();
    if (node instanceof HTMLTextAreaElement || node instanceof HTMLInputElement) {
      setNativeValue(node, text);
      dispatchEditableEvents(node, text);
      return readbackMatches(node, text);
    }
    if (contentEditableMode(node) || node.getAttribute("role") === "textbox") {
      const doc = node.ownerDocument;
      const selection = doc.getSelection();
      if (selection) {
        const range = doc.createRange();
        range.selectNodeContents(node);
        selection.removeAllRanges();
        selection.addRange(range);
      }
      let inserted = false;
      try {
        inserted = doc.execCommand("insertText", false, text);
      } catch {
        inserted = false;
      }
      if (!inserted) {
        node.textContent = text;
      }
      dispatchEditableEvents(node, text);
      return readbackMatches(node, text);
    }
    return false;
  }
  function sanitizeHtml(node) {
    if (!node) return null;
    const clone = node.cloneNode(true);
    clone.querySelectorAll("img, svg, button, input, textarea, script, style, video, canvas").forEach((child) => child.remove());
    clone.querySelectorAll("*").forEach((el) => {
      for (const attr of Array.from(el.attributes)) {
        if (!["class", "role", "data-testid", "aria-label", "placeholder", "data-placeholder", "data-message-author-role"].includes(attr.name)) {
          el.removeAttribute(attr.name);
        }
      }
    });
    return (clone.outerHTML || "").replace(/\s+/g, " ").slice(0, 3e3);
  }
  function compactVisibleText(nodes, limit = 2400) {
    return nodes.filter((node) => isVisible(node)).map((node) => textFrom(node) || "").join(" ").replace(/\s+/g, " ").trim().slice(0, limit).toLowerCase();
  }
  function activeShellText(document2) {
    return compactVisibleText(Array.from(document2.querySelectorAll([
      "dialog[open]",
      '[role="dialog"]',
      '[role="alertdialog"]',
      '[aria-modal="true"]',
      'main [aria-current="page"]',
      'main [aria-selected="true"]',
      'main [aria-pressed="true"]',
      'main [data-state="active"]',
      '[data-testid*="composer"] [aria-pressed="true"]',
      '[data-testid*="tools"] [aria-pressed="true"]'
    ].join(","))));
  }
  function classifyRouteDetails(url, document2, win) {
    let pathname = "/";
    try {
      pathname = new URL(url).pathname.toLowerCase();
    } catch {
      pathname = "/";
    }
    const promptPresent = Boolean(findPromptComposer(document2, win).node);
    const evidence = [`path:${pathname}`, promptPresent ? "composer:present" : "composer:missing"];
    const shellText = activeShellText(document2);
    if (includesAny(pathname, ["/auth/", "/login"]) || !promptPresent && includesAny(shellText, ["log in", "sign up", "stay logged out"])) {
      evidence.push("auth-or-marketing-signal");
      return { posture: "login-or-marketing", pathname, prompt_present: promptPresent, evidence };
    }
    if (pathname === "/" || pathname.startsWith("/c/")) {
      if (promptPresent) {
        evidence.push("plain-chat-path-and-composer");
        return { posture: "plain-chat", pathname, prompt_present: promptPresent, evidence };
      }
    }
    if (includesAny(pathname, ["/agent", "/tasks", "/task/"])) {
      evidence.push("agent-or-task-path");
      return { posture: "agent-or-tool", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(pathname, ["/canvas", "/artifact"])) {
      evidence.push("canvas-or-artifact-path");
      return { posture: "canvas-or-artifact", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(pathname, ["/g/", "/gpts", "/project", "/projects"])) {
      evidence.push("project-or-gpt-path");
      return { posture: "project-or-gpt", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(shellText, ["agent mode", "take over", "browser task"])) {
      evidence.push("active-agent-shell-signal");
      return { posture: "agent-or-tool", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(shellText, ["canvas", "artifact"])) {
      evidence.push("active-canvas-shell-signal");
      return { posture: "canvas-or-artifact", pathname, prompt_present: promptPresent, evidence };
    }
    if (includesAny(shellText, ["gpt builder", "custom gpt", "project settings"])) {
      evidence.push("active-project-shell-signal");
      return { posture: "project-or-gpt", pathname, prompt_present: promptPresent, evidence };
    }
    if (promptPresent) {
      evidence.push("composer-present-no-blocking-route-signal");
      return { posture: "plain-chat", pathname, prompt_present: promptPresent, evidence };
    }
    evidence.push("no-supported-route-signal");
    return { posture: "unknown", pathname, prompt_present: promptPresent, evidence };
  }
  function matchChatGptDocument(url, document2) {
    try {
      const parsed = new URL(url);
      if (parsed.hostname !== "chatgpt.com" && !parsed.hostname.endsWith(".chatgpt.com")) return false;
    } catch {
      return false;
    }
    return Boolean(document2);
  }
  var chatgptAdapter = {
    name: "chatgpt",
    origin_patterns: ["https://chatgpt.com/"],
    capabilities: {
      read_prompt: true,
      write_prompt: true,
      submit_prompt: true,
      read_latest_output: true,
      read_selection: true,
      debug_candidates: true,
      fixture_capture: true,
      generation_state: true,
      continue_generation: true,
      surface_probe: true,
      attach_files: true
    },
    matches(url, document2) {
      return matchChatGptDocument(url, document2);
    },
    readPrompt(document2) {
      return textFrom(findPromptComposer(document2, window).node);
    },
    writePrompt(document2, text) {
      const node = findPromptComposer(document2, window).node;
      if (!node) return false;
      return writeIntoElement(node, text);
    },
    readLatestOutput(document2) {
      return latestOutputWitness(document2, window).text;
    },
    readLatestOutputWitness(document2) {
      return latestOutputWitness(document2, window);
    },
    readLatestUserTurnWitness(document2) {
      return latestUserTurnWitness(document2, window);
    },
    readSelection(window2) {
      return window2.getSelection()?.toString().trim() || null;
    },
    debugCandidates(document2) {
      const inputs = rank(PROMPT_SELECTORS, document2, promptScore, window).slice(0, 16).map(({ node, context }) => candidateInfo(node, promptScore(node), "prompt", context.window)).sort((a, b) => b.score - a.score);
      const outputs = rank(OUTPUT_SELECTORS, document2, outputScore, window).slice(0, 16).map(({ node, context }) => candidateInfo(node, outputScore(node), "output", context.window)).sort((a, b) => b.score - a.score);
      return { inputs, outputs };
    },
    captureFixture(document2, window2) {
      const inventory = collectLiveFrameInventory(document2, window2);
      const promptMatch = findPromptComposer(document2, window2);
      const outputWitness = latestOutputWitness(document2, window2);
      const userTurnWitness = latestUserTurnWitness(document2, window2);
      const outputMatch = latestOutputMatch(document2, window2);
      const submitMatch = findLikelySendButton(document2, window2, promptMatch.node);
      const blockedControl = findBlockedComposerControl(document2, window2, promptMatch.node);
      const debug = this.debugCandidates(document2);
      const route = classifyRouteDetails(window2.location.href, document2, window2);
      const generation = generationState(document2, window2);
      const submitCandidate = submitMatch.node && submitMatch.context ? candidateInfo(submitMatch.node, submitMatch.score || 1, "button", submitMatch.context.window) : null;
      const blockedCandidate = blockedControl.node && blockedControl.context ? candidateInfo(blockedControl.node, blockedControl.score || 1, "blocked-composer-control", blockedControl.context.window) : null;
      const stopCandidate = generation.stop.node && generation.stop.context ? candidateInfo(generation.stop.node, generation.stop.score || 1, "generation-stop", generation.stop.context.window) : null;
      const continueCandidate = generation.continue.node && generation.continue.context ? candidateInfo(generation.continue.node, generation.continue.score || 1, "generation-continue", generation.continue.context.window) : null;
      return {
        adapter: "chatgpt",
        url: window2.location.href,
        title: document2.title,
        prompt: this.readPrompt(document2),
        latest_output: outputWitness.text,
        latest_output_witness: outputWitness,
        latest_user_turn_witness: userTurnWitness,
        selection: this.readSelection(window2),
        candidates: debug,
        html_samples: {
          prompt: sanitizeHtml(promptMatch.node),
          latest_output: sanitizeHtml(outputMatch.node),
          submit: sanitizeHtml(submitMatch.node)
        },
        metadata: {
          surface_route: route.pathname,
          route_posture: route.posture,
          route_evidence: route.evidence,
          route_prompt_present: route.prompt_present,
          prompt_selector: promptMatch.node ? selectorHint(promptMatch.node, "prompt") : null,
          latest_output_selector: outputWitness.selector_hint,
          latest_output_order_policy: outputWitness.selection_policy,
          latest_output_assistant_like: outputWitness.assistant_like,
          latest_output_author_role: outputWitness.author_role,
          latest_output_author_role_source: outputWitness.author_role_source,
          latest_output_candidate_score: outputWitness.candidate_score,
          latest_output_document_order_index: outputWitness.document_order_index,
          latest_user_turn_selector: userTurnWitness.selector_hint,
          latest_user_turn_order_policy: userTurnWitness.selection_policy,
          latest_user_turn_user_like: userTurnWitness.user_like,
          latest_user_turn_author_role: userTurnWitness.author_role,
          latest_user_turn_author_role_source: userTurnWitness.author_role_source,
          latest_user_turn_candidate_score: userTurnWitness.candidate_score,
          latest_user_turn_document_order_index: userTurnWitness.document_order_index,
          latest_turn_pair_same_frame: Boolean(outputWitness.frame_path && userTurnWitness.frame_path && outputWitness.frame_path === userTurnWitness.frame_path),
          latest_turn_pair_user_before_assistant: typeof userTurnWitness.document_order_index === "number" && typeof outputWitness.document_order_index === "number" ? userTurnWitness.document_order_index < outputWitness.document_order_index : false,
          generation_state: generation.state,
          generation_stop_control_present: Boolean(generation.stop.node),
          generation_continue_control_present: Boolean(generation.continue.node),
          generation_stop_selector: generation.stop.node ? selectorHint(generation.stop.node, "generation-stop") : null,
          generation_continue_selector: generation.continue.node ? selectorHint(generation.continue.node, "generation-continue") : null,
          generation_stop_score: generation.stop.score,
          generation_continue_score: generation.continue.score,
          submit_selector: submitMatch.node ? selectorHint(submitMatch.node, "button") : null,
          submit_score: submitMatch.score,
          submit_signal_intent: submitMatch.signal?.intent ?? false,
          submit_signal_explicit: submitMatch.signal?.explicit ?? false,
          submit_signal_submit_type: submitMatch.signal?.submit ?? false,
          submit_signal_disqualified: submitMatch.signal?.disqualified ?? false,
          observed_live_send_selector: OBSERVED_LIVE_SEND_SELECTOR,
          observed_live_send_testid: OBSERVED_LIVE_SEND_TESTID,
          observed_live_send_aria_label: OBSERVED_LIVE_SEND_ARIA_LABEL,
          submit_expected_live_selector: OBSERVED_LIVE_SEND_SELECTOR,
          blocked_composer_control_selector: blockedControl.node ? selectorHint(blockedControl.node, "blocked-composer-control") : null,
          blocked_composer_control_score: blockedControl.score,
          blocked_composer_control_disqualified: blockedControl.signal?.disqualified ?? false,
          submit_scope_selector: submitMatch.scope && submitMatch.scope !== document2 && submitMatch.scope instanceof Element ? selectorHint(submitMatch.scope, "submit-scope") : null,
          action_policy: {
            submit_method: "button-click-only",
            keyboard_submit_enabled: false,
            route_posture_allows_submit: routePostureAllowsSubmit(route.posture),
            prompt_present_for_submit: Boolean(this.readPrompt(document2)),
            submit_button_found: Boolean(submitMatch.node),
            submit_button_min_score: SEND_BUTTON_MIN_SCORE,
            submit_button_requires_explicit_send_intent: true,
            submit_button_rejects_non_send_composer_controls: true,
            observed_live_send_selector: OBSERVED_LIVE_SEND_SELECTOR,
            observed_live_send_testid: OBSERVED_LIVE_SEND_TESTID,
            observed_live_send_aria_label: OBSERVED_LIVE_SEND_ARIA_LABEL,
            submit_button_live_surface_lock: "#composer-submit-button[data-testid=send-button]",
            blocked_composer_plus_control_present: Boolean(blockedControl.node),
            empty_composer_missing_send_is_allowed: true
          },
          ...buildLiveFixtureMetadata(document2, promptMatch.node, submitMatch.node, debug.inputs[0] ?? null, submitCandidate, {
            inventory,
            inputCandidates: debug.inputs,
            outputCandidates: debug.outputs,
            submitCandidates: [submitCandidate, blockedCandidate, stopCandidate, continueCandidate].filter((candidate) => Boolean(candidate))
          })
        }
      };
    },
    submitPrompt(document2) {
      const route = classifyRouteDetails(window.location.href, document2, window);
      if (!routePostureAllowsSubmit(route.posture)) return false;
      const composer = findPromptComposer(document2, window).node;
      if (!composer || !this.readPrompt(document2)) return false;
      const sendish = findLikelySendButton(document2, window, composer).node;
      if (!sendish) return false;
      composer.focus();
      sendish.click();
      return true;
    },
    generationSnapshot(document2, win) {
      const generation = generationState(document2, win);
      return {
        state: generation.state,
        stop_present: Boolean(generation.stop.node),
        continue_present: Boolean(generation.continue.node),
        stop_selector: generation.stop.node ? selectorHint(generation.stop.node, "generation-stop") : null,
        continue_selector: generation.continue.node ? selectorHint(generation.continue.node, "generation-continue") : null
      };
    },
    continueGeneration(document2, win) {
      const control = findGenerationControl(document2, win, GENERATION_CONTINUE_TERMS);
      if (!control.node) return false;
      control.node.click();
      return true;
    },
    attachmentReadiness(document2) {
      const authentication = authenticationState(document2);
      if (authentication.posture !== "authenticated") {
        return {
          ok: false,
          error: authentication.posture === "anonymous" ? "ChatGPT is logged out; file attachment requires an authenticated browser session" : "ChatGPT authentication could not be verified; refusing to transfer a file",
          authentication: authentication.posture
        };
      }
      const input = findFileInput(document2);
      if (!input) {
        return {
          ok: false,
          error: 'no <input type="file"> found in the page',
          authentication: authentication.posture
        };
      }
      return {
        ok: true,
        input_selector: selectorHint(input, "file-input"),
        authentication: authentication.posture
      };
    },
    /**
     * Put files into the composer.
     *
     * We do NOT click "Add files and more" and drive a native file picker — a page
     * cannot script an OS dialog, and trying is how automation projects end up
     * shipping fragile robot-mouse code. Instead we write straight into the hidden
     * <input type="file"> with a synthetic DataTransfer, which is exactly what the
     * drop handler does.
     */
    attachFiles(document2, files) {
      const readiness = this.attachmentReadiness?.(document2);
      if (!readiness?.ok) {
        return {
          ok: false,
          error: readiness?.error || "file attachment is not available",
          files_before: 0,
          files_after: 0
        };
      }
      const input = findFileInput(document2);
      if (!input) {
        return { ok: false, error: 'no <input type="file"> found in the page', files_before: 0, files_after: 0 };
      }
      const filesBefore = input.files?.length ?? 0;
      try {
        const transfer = new DataTransfer();
        for (const existing of Array.from(input.files ?? [])) transfer.items.add(existing);
        for (const file of files) {
          if (!file.bytes || file.bytes.byteLength === 0) {
            return { ok: false, error: `refusing to attach zero-byte file: ${file.name}`, files_before: filesBefore, files_after: filesBefore };
          }
          const blob = new Blob([file.bytes], { type: file.mime || "application/octet-stream" });
          transfer.items.add(new File([blob], file.name, { type: file.mime || "application/octet-stream" }));
        }
        input.files = transfer.files;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.dispatchEvent(new Event("change", { bubbles: true }));
      } catch (error) {
        return {
          ok: false,
          error: `could not populate file input: ${error instanceof Error ? error.message : String(error)}`,
          files_before: filesBefore,
          files_after: input.files?.length ?? 0
        };
      }
      return {
        ok: true,
        input_selector: selectorHint(input, "file-input"),
        files_before: filesBefore,
        files_after: input.files?.length ?? 0
      };
    },
    clearAttachments(document2) {
      const inputs = findFileInputs(document2);
      if (!inputs.length) {
        return {
          ok: false,
          error: 'no <input type="file"> found in the page',
          inputs_seen: 0,
          files_before: 0,
          files_after: 0
        };
      }
      const filesBefore = inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
      try {
        for (const input of inputs) {
          input.files = new DataTransfer().files;
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
      } catch (error) {
        return {
          ok: false,
          error: `could not clear file input: ${error instanceof Error ? error.message : String(error)}`,
          inputs_seen: inputs.length,
          files_before: filesBefore,
          files_after: inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0)
        };
      }
      const filesAfter = inputs.reduce((count, input) => count + (input.files?.length ?? 0), 0);
      return {
        ok: filesAfter === 0,
        inputs_seen: inputs.length,
        files_before: filesBefore,
        files_after: filesAfter
      };
    },
    composerKeys(document2) {
      return composerControlKeys(document2);
    },
    attachmentWitness(document2, keysBefore, expectedName = "", expectedNameVisibleBefore = false) {
      const inputs = findFileInputs(document2);
      const delta = composerControlDelta(document2, keysBefore);
      const added = delta.added_keys;
      const addedControls = delta.added_controls;
      const knownChipKeys = addedControls.filter((control) => control.classification === "attachment-chip").map((control) => control.key);
      const input = inputs[0] ?? null;
      const composerRegion = input?.closest('form, [data-testid*="composer"], [class*="composer"], [role="form"]') ?? null;
      const expectedNameVisible = Boolean(
        expectedName && composerRegion && (textFrom(composerRegion) || "").toLocaleLowerCase().includes(expectedName.toLocaleLowerCase())
      );
      const expectedNameNewlyVisible = expectedNameVisible && !expectedNameVisibleBefore;
      return {
        input_files: inputs.reduce((count, candidate) => count + (candidate.files?.length ?? 0), 0),
        added_keys: added,
        added_controls: addedControls,
        known_chip_keys: knownChipKeys,
        expected_name_visible: expectedNameVisible,
        expected_name_newly_visible: expectedNameNewlyVisible,
        // A new unrelated control is not an attachment witness. Before the live
        // chip is in the role atlas, require the uploaded filename to be visible
        // in the same composer as the new control.
        chip_present: knownChipKeys.length > 0 || added.length > 0 && expectedNameNewlyVisible
      };
    },
    stopGeneration(document2, win) {
      const control = findGenerationControl(document2, win, GENERATION_STOP_TERMS);
      if (!control.node) return false;
      control.node.click();
      return true;
    },
    newChat(document2) {
      const button = document2.querySelector('[data-testid="create-new-chat-button"]');
      if (button instanceof HTMLElement && isVisible(button)) {
        button.click();
        return true;
      }
      return false;
    },
    surfaceProbe(document2, win) {
      const route = classifyRouteDetails(win.location.href, document2, win);
      const composer = findPromptComposer(document2, win).node;
      const send = findLikelySendButton(document2, win, composer).node;
      const generation = generationState(document2, win);
      const assistant = findLatestOutputNode(document2, win).node;
      const user = latestUserTurnMatch(document2, win).node;
      return buildSurfaceProbe(document2, {
        url: win.location.href,
        route: { pathname: route.pathname, posture: route.posture },
        composer,
        send,
        stop: generation.stop.node,
        continueControl: generation.continue.node,
        latestAssistant: assistant,
        latestUser: user,
        expectedComposerSelector: OBSERVED_LIVE_PROMPT_SELECTOR,
        expectedSendSelector: OBSERVED_LIVE_SEND_SELECTOR,
        generationState: generation.state
      });
    }
  };

  // src/adapters/index.ts
  var adapters = [chatgptAdapter];
  function supportedOrigins() {
    return adapters.flatMap((adapter) => adapter.origin_patterns);
  }
  function supportedMatchPatterns() {
    return Array.from(new Set(supportedOrigins().map((origin) => `${origin}*`)));
  }
  function adapterDescriptors() {
    return adapters.map((adapter) => ({
      name: adapter.name,
      origin_patterns: adapter.origin_patterns,
      capabilities: adapter.capabilities
    }));
  }

  // src/shared/browser.ts
  async function getActiveTab() {
    const tabs = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
    return tabs[0];
  }
  async function getTabById(tabId) {
    if (!tabId) return void 0;
    try {
      return await chrome.tabs.get(tabId);
    } catch {
      return void 0;
    }
  }
  function isSupportedUrl(url) {
    if (!url) return false;
    return supportedOrigins().some((origin) => url.startsWith(origin));
  }

  // src/shared/native-lane.ts
  function parsedTime(value) {
    if (!value) return Number.NaN;
    return Date.parse(value);
  }
  function snapshotIsFresh(snapshot, now, maxAgeMs = 15e3) {
    const capturedAt = parsedTime(snapshot?.capturedAt);
    return Boolean(snapshot && Number.isFinite(capturedAt) && now - capturedAt <= maxAgeMs);
  }
  function snapshotLooksReachable(snapshot, lastNativeStatusError, now) {
    return Boolean(snapshot && !lastNativeStatusError && (snapshot.native_host || snapshotIsFresh(snapshot, now)));
  }
  function oneShotLooksReachable(nativeConnection) {
    return Boolean(nativeConnection?.lastOneShotProbeOk && !nativeConnection?.lastOneShotProbeError);
  }
  function deriveNativeLaneDiagnosis(input) {
    const nativeConnection = input.nativeConnection;
    const snapshot = input.lastNativeStatusSnapshot;
    const now = typeof input.now === "number" ? input.now : Date.now();
    const persistentConnected = nativeConnection?.connected === true;
    const persistentHealthy = persistentConnected && nativeConnection?.lastHealthOk !== false && !nativeConnection?.lastHealthError;
    const oneShotReachable = oneShotLooksReachable(nativeConnection);
    const snapshotReachable = snapshotLooksReachable(snapshot, input.lastNativeStatusError, now);
    const reconnectPending = Boolean(!persistentConnected && nativeConnection?.reconnectScheduledFor);
    const persistentBrokerRole = nativeConnection?.persistentBroker?.role;
    const oneShotBrokerRole = nativeConnection?.lastOneShotProbeBroker?.role;
    const snapshotBrokerRole = snapshot?.broker?.role;
    if (persistentHealthy) {
      return {
        status: "persistent_healthy",
        summary: "Persistent connectNative() lane is healthy.",
        recommendedAction: "No action needed.",
        persistentConnected: true,
        persistentBrokerRole,
        oneShotBrokerRole,
        snapshotBrokerRole,
        reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
        reconnectAttempt: nativeConnection?.reconnectAttempt,
        snapshotMatchesPersistent: snapshot?.matches_persistent_host
      };
    }
    if (persistentConnected) {
      return {
        status: "persistent_degraded",
        summary: oneShotReachable || snapshotReachable ? "Persistent lane is connected but health is degraded; one-shot native diagnostics still reach the host." : "Persistent lane is connected but health is degraded.",
        recommendedAction: oneShotReachable || snapshotReachable ? "Reseat the long-lived native port and compare persistent vs one-shot host identity." : "Inspect the native host log and reconnect the long-lived native port.",
        persistentConnected: true,
        persistentBrokerRole,
        oneShotBrokerRole,
        snapshotBrokerRole,
        reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
        reconnectAttempt: nativeConnection?.reconnectAttempt,
        snapshotMatchesPersistent: snapshot?.matches_persistent_host
      };
    }
    if (oneShotReachable || snapshotReachable) {
      return {
        status: reconnectPending ? "reconnect_pending" : "oneshot_only",
        summary: reconnectPending ? "One-shot sendNativeMessage() diagnostics reach the native host, but the persistent connectNative() lane is still disconnected and waiting to reconnect." : "One-shot sendNativeMessage() diagnostics reach the native host, but the persistent connectNative() lane is disconnected.",
        recommendedAction: reconnectPending ? "Wait for or trigger an immediate persistent reconnect; the host manifest appears reachable." : "Trigger an immediate persistent reconnect; the host manifest appears reachable.",
        persistentConnected: false,
        persistentBrokerRole,
        oneShotBrokerRole,
        snapshotBrokerRole,
        reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
        reconnectAttempt: nativeConnection?.reconnectAttempt,
        snapshotMatchesPersistent: snapshot?.matches_persistent_host
      };
    }
    if (nativeConnection?.lastHealthError || nativeConnection?.lastOneShotProbeError || nativeConnection?.lastDisconnectReason || input.lastNativeStatusError) {
      return {
        status: "native_host_unreachable",
        summary: "Neither the persistent lane nor one-shot diagnostics currently confirm native-host reachability.",
        recommendedAction: "Inspect native-host installation, manifest targets, and browser logs, then retry reconnect.",
        persistentConnected: false,
        persistentBrokerRole,
        oneShotBrokerRole,
        snapshotBrokerRole,
        reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
        reconnectAttempt: nativeConnection?.reconnectAttempt,
        snapshotMatchesPersistent: snapshot?.matches_persistent_host
      };
    }
    return {
      status: "unknown",
      summary: "Native-lane state has not been established yet.",
      recommendedAction: "Run bridge.status or bridge.probe to collect native-lane evidence.",
      persistentConnected,
      persistentBrokerRole,
      oneShotBrokerRole,
      snapshotBrokerRole,
      reconnectScheduledFor: nativeConnection?.reconnectScheduledFor,
      reconnectAttempt: nativeConnection?.reconnectAttempt,
      snapshotMatchesPersistent: snapshot?.matches_persistent_host
    };
  }

  // src/shared/persistent-history.ts
  var DEFAULT_MAX_WORKER_BOOTS = 12;
  var DEFAULT_MAX_NATIVE_EVENTS = 40;
  function trimNewest(items, maxItems) {
    if (items.length <= maxItems) return items;
    return items.slice(items.length - maxItems);
  }
  function normalizeWorkerBoots(value) {
    if (!Array.isArray(value)) return [];
    return value.flatMap((item) => {
      if (!item || typeof item !== "object") return [];
      const record = item;
      const bootId = typeof record.bootId === "string" ? record.bootId : null;
      const bootAt = typeof record.bootAt === "string" ? record.bootAt : null;
      const bootCount = typeof record.bootCount === "number" && Number.isFinite(record.bootCount) ? Math.max(1, Math.trunc(record.bootCount)) : null;
      if (!bootId || !bootAt || bootCount === null) return [];
      return [{ bootId, bootAt, bootCount }];
    });
  }
  function normalizeNativeEvents(value) {
    if (!Array.isArray(value)) return [];
    return value.flatMap((item) => {
      if (!item || typeof item !== "object") return [];
      const record = item;
      const at = typeof record.at === "string" ? record.at : null;
      const bootId = typeof record.bootId === "string" ? record.bootId : null;
      const kind = typeof record.kind === "string" ? record.kind : null;
      if (!at || !bootId || !kind) return [];
      return [{
        at,
        bootId,
        kind,
        trigger: typeof record.trigger === "string" ? record.trigger : void 0,
        reason: typeof record.reason === "string" ? record.reason : void 0,
        diagnosisStatus: typeof record.diagnosisStatus === "string" ? record.diagnosisStatus : void 0,
        diagnosisSummary: typeof record.diagnosisSummary === "string" ? record.diagnosisSummary : void 0,
        persistentBrokerRole: typeof record.persistentBrokerRole === "string" ? record.persistentBrokerRole : void 0,
        oneShotBrokerRole: typeof record.oneShotBrokerRole === "string" ? record.oneShotBrokerRole : void 0,
        snapshotBrokerRole: typeof record.snapshotBrokerRole === "string" ? record.snapshotBrokerRole : void 0,
        nativeHost: typeof record.nativeHost === "string" ? record.nativeHost : void 0,
        socketPath: typeof record.socketPath === "string" ? record.socketPath : void 0,
        hostBootId: typeof record.hostBootId === "string" ? record.hostBootId : void 0,
        hostPid: typeof record.hostPid === "number" && Number.isFinite(record.hostPid) ? Math.trunc(record.hostPid) : void 0
      }];
    });
  }
  function normalizePersistentBridgeHistory(value, options = {}) {
    const maxWorkerBoots = options.maxWorkerBoots ?? DEFAULT_MAX_WORKER_BOOTS;
    const maxNativeEvents = options.maxNativeEvents ?? DEFAULT_MAX_NATIVE_EVENTS;
    const record = value && typeof value === "object" ? value : {};
    return {
      updatedAt: typeof record.updatedAt === "string" ? record.updatedAt : void 0,
      workerBoots: trimNewest(normalizeWorkerBoots(record.workerBoots), maxWorkerBoots),
      nativeEvents: trimNewest(normalizeNativeEvents(record.nativeEvents), maxNativeEvents)
    };
  }
  function recordPersistentWorkerBoot(history, boot, options = {}) {
    const maxWorkerBoots = options.maxWorkerBoots ?? DEFAULT_MAX_WORKER_BOOTS;
    const existing = history.workerBoots.filter((entry) => entry.bootId !== boot.bootId);
    return {
      ...history,
      updatedAt: boot.bootAt,
      workerBoots: trimNewest([...existing, boot], maxWorkerBoots)
    };
  }
  function appendPersistentNativeEvent(history, event, options = {}) {
    const maxNativeEvents = options.maxNativeEvents ?? DEFAULT_MAX_NATIVE_EVENTS;
    return {
      ...history,
      updatedAt: event.at,
      nativeEvents: trimNewest([...history.nativeEvents, event], maxNativeEvents)
    };
  }
  function timeSortKey(value) {
    const parsed = Date.parse(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  function mostRecentReason(events, kind) {
    for (let index = events.length - 1; index >= 0; index -= 1) {
      const event = events[index];
      if (event.kind === kind && event.reason) return event.reason;
    }
    return void 0;
  }
  function bootIdsWithinWindow(boots, now, windowMs) {
    return new Set(
      boots.filter((boot) => {
        const parsed = Date.parse(boot.bootAt);
        return Number.isFinite(parsed) && now - parsed <= windowMs;
      }).map((boot) => boot.bootId)
    );
  }
  function derivePersistentRuntimeHint(history, runtime, now = Date.now()) {
    const currentBootId = runtime.currentBootId;
    const workerBoots = [...history.workerBoots].sort((a, b) => timeSortKey(a.bootAt) - timeSortKey(b.bootAt));
    const nativeEvents = [...history.nativeEvents].sort((a, b) => timeSortKey(a.at) - timeSortKey(b.at));
    const bootCount = Math.max(workerBoots.length, typeof runtime.bootCount === "number" && Number.isFinite(runtime.bootCount) ? Math.trunc(runtime.bootCount) : 0);
    if (!currentBootId || !workerBoots.length && !nativeEvents.length) {
      return {
        status: "none",
        summary: "No persistent cross-restart bridge history yet.",
        recommendedAction: "Run bridge.status or bridge.probe once to seed durable diagnostics.",
        currentBootId,
        currentBootSeenConnected: false,
        currentBootSeenOneShot: false,
        previousBootSeenConnected: false,
        bootCount
      };
    }
    const currentBootEvents = nativeEvents.filter((event) => event.bootId === currentBootId);
    const previousBootEvents = nativeEvents.filter((event) => event.bootId !== currentBootId);
    const currentBootSeenConnected = currentBootEvents.some((event) => event.kind === "native.connected");
    const currentBootSeenOneShot = currentBootEvents.some((event) => event.kind === "native.oneshot_reachable");
    const previousBootSeenConnected = previousBootEvents.some((event) => event.kind === "native.connected");
    const recentBootCount = bootIdsWithinWindow(workerBoots, now, 15 * 6e4).size;
    const recentDisconnectReason = mostRecentReason(nativeEvents, "native.disconnected");
    const recentReconnectFailureReason = mostRecentReason(nativeEvents, "native.reconnect_failed");
    if (currentBootSeenConnected) {
      return {
        status: "current_boot_connected",
        summary: "The current service-worker boot has already re-established the persistent native lane.",
        recommendedAction: "No durable-resume action needed.",
        currentBootId,
        currentBootSeenConnected,
        currentBootSeenOneShot,
        previousBootSeenConnected,
        bootCount,
        recentDisconnectReason,
        recentReconnectFailureReason
      };
    }
    if (currentBootSeenOneShot) {
      return {
        status: "current_boot_oneshot_only",
        summary: "This service-worker boot has durable proof that one-shot native diagnostics work, but it has not yet re-established the persistent native port.",
        recommendedAction: "Trigger or inspect the persistent reconnect path now; the host manifest appears reachable from this boot.",
        currentBootId,
        currentBootSeenConnected,
        currentBootSeenOneShot,
        previousBootSeenConnected,
        bootCount,
        recentDisconnectReason,
        recentReconnectFailureReason
      };
    }
    if (recentBootCount >= 3 && previousBootSeenConnected) {
      return {
        status: "restart_churn",
        summary: "Recent history shows repeated service-worker boots without the current boot reclaiming the persistent native lane.",
        recommendedAction: "Inspect reconnect traces and browser/native-host logs; MV3 restart churn may be masking a deeper reconnect failure.",
        currentBootId,
        currentBootSeenConnected,
        currentBootSeenOneShot,
        previousBootSeenConnected,
        bootCount,
        recentDisconnectReason,
        recentReconnectFailureReason
      };
    }
    if (previousBootSeenConnected) {
      return {
        status: "restart_pending",
        summary: "A previous worker boot held the persistent native lane, but the current boot has not yet proven it reclaimed that port.",
        recommendedAction: "Run bridge.status or bridge.probe and check whether the reconnect alarm or explicit reseat path restores the port.",
        currentBootId,
        currentBootSeenConnected,
        currentBootSeenOneShot,
        previousBootSeenConnected,
        bootCount,
        recentDisconnectReason,
        recentReconnectFailureReason
      };
    }
    return {
      status: "current_boot_unproven",
      summary: "The current service-worker boot has not yet established durable native-lane evidence.",
      recommendedAction: "Collect bridge.status or bridge.probe once on this boot before drawing conclusions.",
      currentBootId,
      currentBootSeenConnected,
      currentBootSeenOneShot,
      previousBootSeenConnected,
      bootCount,
      recentDisconnectReason,
      recentReconnectFailureReason
    };
  }
  function buildPersistentDiagnosticsSnapshot(rawHistory, runtime, _diagnosis, now = Date.now()) {
    const history = normalizePersistentBridgeHistory(rawHistory);
    return {
      ...history,
      runtimeHint: derivePersistentRuntimeHint(history, runtime, now),
      updatedAt: history.updatedAt
    };
  }

  // src/shared/protocol.ts
  function makeEnvelope(type, payload, tab_id) {
    return {
      version: "0.1",
      request_id: crypto.randomUUID(),
      type,
      tab_id,
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      payload
    };
  }
  function replyTo(request, type, payload, tab_id) {
    return {
      version: "0.1",
      request_id: request.request_id,
      type,
      tab_id: tab_id ?? request.tab_id,
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      payload
    };
  }

  // src/shared/receivers.ts
  function compactString(value) {
    if (typeof value !== "string") return void 0;
    const trimmed = value.trim();
    return trimmed || void 0;
  }
  function compactStrings(values) {
    if (!Array.isArray(values)) return void 0;
    const normalized = values.map((value) => compactString(value)).filter((value) => Boolean(value));
    return normalized.length ? normalized : void 0;
  }
  function compactNumbers(values) {
    if (!Array.isArray(values)) return void 0;
    const normalized = values.filter((value) => typeof value === "number");
    return normalized.length ? normalized : void 0;
  }
  function compactOrigin(value) {
    const trimmed = compactString(value);
    if (!trimmed) return void 0;
    try {
      return new URL(trimmed).origin;
    } catch {
      return trimmed;
    }
  }
  function hostnameFromUrl(value) {
    const trimmed = compactString(value);
    if (!trimmed) return void 0;
    try {
      return new URL(trimmed).hostname || void 0;
    } catch {
      return void 0;
    }
  }
  function originFromUrl(value) {
    const trimmed = compactString(value);
    if (!trimmed) return void 0;
    try {
      return new URL(trimmed).origin;
    } catch {
      return void 0;
    }
  }
  function inferredFramePathHosts(receiver) {
    const fromState = compactStrings(receiver.framePathHosts);
    if (fromState?.length) return fromState;
    const currentHost = hostnameFromUrl(receiver.frameUrl) ?? hostnameFromUrl(receiver.frameOrigin);
    if (currentHost) return [currentHost];
    return void 0;
  }
  function isReceiverLifecyclePreferred(receiver) {
    const lifecycle = compactString(receiver.documentLifecycle);
    return !lifecycle || lifecycle === "active";
  }
  function isOutermostReceiver(receiver) {
    if (compactString(receiver.frameType) === "outermost_frame") return true;
    if (typeof receiver.frameDepth === "number") return receiver.frameDepth <= 0;
    if (Array.isArray(receiver.framePathFrameIds) && receiver.framePathFrameIds.length > 0) return receiver.framePathFrameIds.length === 1;
    if (typeof receiver.parentFrameId === "number") return receiver.parentFrameId < 0;
    return receiver.frameId === 0;
  }
  function contentReceiverFramePathLabel(receiver) {
    const explicit = compactString(receiver.framePathLabel);
    if (explicit) return explicit;
    const hosts = inferredFramePathHosts(receiver);
    if (hosts?.length) {
      const prefix = !isOutermostReceiver(receiver) ? ["top-frame"] : [];
      return [...prefix, ...hosts].join(" \u2192 ");
    }
    if (typeof receiver.frameId === "number") {
      return isOutermostReceiver(receiver) ? "top-frame" : `top-frame \u2192 frame:${receiver.frameId}`;
    }
    return void 0;
  }
  function contentReceiverKey(receiver) {
    const documentId = compactString(receiver.documentId);
    if (documentId) return `doc:${documentId}`;
    if (typeof receiver.frameId === "number") return `frame:${receiver.frameId}`;
    return null;
  }
  function contentReceiverLabel(receiver) {
    const segments = [];
    if (typeof receiver.frameId === "number") {
      segments.push(isOutermostReceiver(receiver) ? "top-frame" : `frame:${receiver.frameId}`);
    }
    const documentId = compactString(receiver.documentId);
    if (documentId) {
      segments.push(`doc:${documentId.slice(0, 8)}`);
    }
    const frameType = compactString(receiver.frameType);
    if (frameType && frameType !== "outermost_frame") segments.push(frameType);
    const host = hostnameFromUrl(receiver.frameUrl) ?? hostnameFromUrl(receiver.frameOrigin);
    if (host) segments.push(host);
    const framePath = contentReceiverFramePathLabel(receiver);
    if (framePath && framePath !== host && framePath !== "top-frame") segments.push(framePath);
    if (typeof receiver.frameDepth === "number" && receiver.frameDepth > 0) segments.push(`depth:${receiver.frameDepth}`);
    if (receiver.receiverReady === true) segments.push("ready");
    else if (receiver.receiverReady === false) segments.push("observed");
    const lifecycle = compactString(receiver.documentLifecycle);
    if (lifecycle) segments.push(lifecycle);
    return segments.join(" \xB7 ") || "receiver";
  }
  function describeContentReceiverResolution(receiver, options = {}) {
    const depth = typeof receiver.frameDepth === "number" ? receiver.frameDepth : void 0;
    const lifecycle = compactString(receiver.documentLifecycle);
    const ready = receiver.receiverReady === true;
    const summary = {
      receiverKey: contentReceiverKey(receiver),
      receiverLabel: contentReceiverLabel(receiver),
      lifecyclePreferred: isReceiverLifecyclePreferred(receiver),
      activeOutermost: isOutermostReceiver(receiver) && isReceiverLifecyclePreferred(receiver),
      outermost: isOutermostReceiver(receiver),
      ready,
      ...typeof depth === "number" ? { frameDepth: depth } : {},
      ...compactString(receiver.lastSeenAt) ? { lastSeenAt: compactString(receiver.lastSeenAt) } : {},
      ...lifecycle ? { documentLifecycle: lifecycle } : {},
      rankingVector: {
        lifecyclePreferred: isReceiverLifecyclePreferred(receiver),
        outermost: isOutermostReceiver(receiver),
        ready,
        ...typeof depth === "number" ? { frameDepth: depth } : {},
        ...compactString(receiver.lastSeenAt) ? { lastSeenAt: compactString(receiver.lastSeenAt) } : {}
      },
      reasons: [
        isReceiverLifecyclePreferred(receiver) ? "lifecycle=active_or_unknown" : `lifecycle=${lifecycle ?? "unknown"}`,
        isOutermostReceiver(receiver) ? "frame=outermost" : "frame=subframe",
        ready ? "receiver=ready" : "receiver=observed_only",
        typeof depth === "number" ? `frameDepth=${depth}` : "frameDepth=unknown",
        compactString(receiver.lastSeenAt) ? `lastSeenAt=${compactString(receiver.lastSeenAt)}` : "lastSeenAt=unknown"
      ],
      ...typeof options.rank === "number" ? { rank: options.rank } : {}
    };
    return summary;
  }
  function sortReceivers(receivers) {
    return [...receivers].sort((left, right) => {
      const leftLifecyclePreferred = isReceiverLifecyclePreferred(left) ? 1 : 0;
      const rightLifecyclePreferred = isReceiverLifecyclePreferred(right) ? 1 : 0;
      if (leftLifecyclePreferred !== rightLifecyclePreferred) return rightLifecyclePreferred - leftLifecyclePreferred;
      const leftTop = isOutermostReceiver(left) ? 1 : 0;
      const rightTop = isOutermostReceiver(right) ? 1 : 0;
      if (leftTop !== rightTop) return rightTop - leftTop;
      const leftReady = left.receiverReady === true ? 1 : 0;
      const rightReady = right.receiverReady === true ? 1 : 0;
      if (leftReady !== rightReady) return rightReady - leftReady;
      const leftDepth = typeof left.frameDepth === "number" ? left.frameDepth : Number.MAX_SAFE_INTEGER;
      const rightDepth = typeof right.frameDepth === "number" ? right.frameDepth : Number.MAX_SAFE_INTEGER;
      if (leftDepth !== rightDepth) return leftDepth - rightDepth;
      return String(right.lastSeenAt).localeCompare(String(left.lastSeenAt));
    });
  }
  function findOverrideReceiver(receivers = [], overrideKey) {
    const wanted = compactString(overrideKey);
    if (!wanted) return null;
    return sortReceivers(receivers).find((receiver) => contentReceiverKey(receiver) === wanted) ?? null;
  }
  function mergeContentReceivers(existing = [], incoming) {
    if (!incoming) return sortReceivers(existing);
    const key = contentReceiverKey(incoming);
    if (!key) return sortReceivers(existing);
    const incomingDocumentId = compactString(incoming.documentId);
    const incomingFrameId = typeof incoming.frameId === "number" ? incoming.frameId : void 0;
    const nowish = compactString(incoming.lastSeenAt) || (/* @__PURE__ */ new Date()).toISOString();
    const normalizedIncoming = {
      ...compactString(incoming.documentId) ? { documentId: compactString(incoming.documentId) } : {},
      ...typeof incoming.frameId === "number" ? { frameId: incoming.frameId } : {},
      ...compactString(incoming.documentLifecycle) ? { documentLifecycle: compactString(incoming.documentLifecycle) } : {},
      ...compactString(incoming.adapter) ? { adapter: compactString(incoming.adapter) } : {},
      ...typeof incoming.receiverReady === "boolean" ? { receiverReady: incoming.receiverReady } : {},
      ...compactString(incoming.frameType) ? { frameType: compactString(incoming.frameType) } : {},
      ...typeof incoming.parentFrameId === "number" ? { parentFrameId: incoming.parentFrameId } : {},
      ...compactString(incoming.parentDocumentId) ? { parentDocumentId: compactString(incoming.parentDocumentId) } : {},
      ...compactString(incoming.frameUrl) ? { frameUrl: compactString(incoming.frameUrl) } : {},
      ...compactOrigin(incoming.frameOrigin) ?? originFromUrl(incoming.frameUrl) ? { frameOrigin: compactOrigin(incoming.frameOrigin) ?? originFromUrl(incoming.frameUrl) } : {},
      ...typeof incoming.frameDepth === "number" ? { frameDepth: incoming.frameDepth } : {},
      ...compactNumbers(incoming.framePathFrameIds) ? { framePathFrameIds: compactNumbers(incoming.framePathFrameIds) } : {},
      ...compactStrings(incoming.framePathUrls) ? { framePathUrls: compactStrings(incoming.framePathUrls) } : {},
      ...compactStrings(incoming.framePathHosts) ? { framePathHosts: compactStrings(incoming.framePathHosts) } : {},
      ...compactString(incoming.framePathLabel) ?? contentReceiverFramePathLabel(incoming) ? { framePathLabel: compactString(incoming.framePathLabel) ?? contentReceiverFramePathLabel(incoming) } : {},
      lastSeenAt: nowish
    };
    const merged = [];
    let replaced = false;
    for (const receiver of existing) {
      const receiverKey = contentReceiverKey(receiver);
      if (receiverKey === key) {
        merged.push({ ...receiver, ...normalizedIncoming, lastSeenAt: nowish });
        replaced = true;
        continue;
      }
      const receiverFrameId = typeof receiver.frameId === "number" ? receiver.frameId : void 0;
      const receiverDocumentId = compactString(receiver.documentId);
      const shouldEvictSameFrameDocument = typeof incomingFrameId === "number" && receiverFrameId === incomingFrameId && incomingDocumentId && receiverDocumentId !== incomingDocumentId;
      if (shouldEvictSameFrameDocument) {
        continue;
      }
      merged.push(receiver);
    }
    if (!replaced) merged.push(normalizedIncoming);
    return sortReceivers(merged).slice(0, 8);
  }
  function reconcileContentReceivers(existing = [], liveFrames = []) {
    if (!existing.length) {
      return { receivers: [], removed: [], removedKeys: [], retainedKeys: [] };
    }
    const liveIndex = /* @__PURE__ */ new Map();
    for (const frame of liveFrames) {
      const key = contentReceiverKey(frame);
      if (!key) continue;
      liveIndex.set(key, frame);
    }
    if (!liveIndex.size) {
      return { receivers: sortReceivers(existing), removed: [], removedKeys: [], retainedKeys: existing.map((receiver) => contentReceiverKey(receiver)).filter((value) => Boolean(value)) };
    }
    const receivers = [];
    const removed = [];
    const retainedKeys = [];
    const removedKeys = [];
    for (const receiver of sortReceivers(existing)) {
      const key = contentReceiverKey(receiver);
      if (!key) {
        receivers.push(receiver);
        continue;
      }
      const live = liveIndex.get(key);
      if (!live) {
        removed.push(receiver);
        removedKeys.push(key);
        continue;
      }
      retainedKeys.push(key);
      receivers.push({
        ...receiver,
        ...compactString(live.documentId) ? { documentId: compactString(live.documentId) } : {},
        ...typeof live.frameId === "number" ? { frameId: live.frameId } : {},
        ...compactString(live.documentLifecycle) ? { documentLifecycle: compactString(live.documentLifecycle) } : {},
        ...compactString(live.frameType) ? { frameType: compactString(live.frameType) } : {},
        ...typeof live.parentFrameId === "number" ? { parentFrameId: live.parentFrameId } : {},
        ...compactString(live.parentDocumentId) ? { parentDocumentId: compactString(live.parentDocumentId) } : {},
        ...compactString(live.frameUrl) ? { frameUrl: compactString(live.frameUrl) } : {},
        ...compactOrigin(live.frameOrigin) ?? originFromUrl(live.frameUrl) ? { frameOrigin: compactOrigin(live.frameOrigin) ?? originFromUrl(live.frameUrl) } : {},
        ...typeof live.frameDepth === "number" ? { frameDepth: live.frameDepth } : {},
        ...compactNumbers(live.framePathFrameIds) ? { framePathFrameIds: compactNumbers(live.framePathFrameIds) } : {},
        ...compactStrings(live.framePathUrls) ? { framePathUrls: compactStrings(live.framePathUrls) } : {},
        ...compactStrings(live.framePathHosts) ? { framePathHosts: compactStrings(live.framePathHosts) } : {},
        ...compactString(live.framePathLabel) ?? contentReceiverFramePathLabel(live) ? { framePathLabel: compactString(live.framePathLabel) ?? contentReceiverFramePathLabel(live) } : {}
      });
    }
    return { receivers: sortReceivers(receivers), removed, removedKeys, retainedKeys };
  }
  function describeContentReceiverAudit(receivers = [], options = {}) {
    const summary = summarizeContentReceivers(receivers, options);
    const sorted = sortReceivers(receivers);
    const rankedMatches = sorted.map((receiver, index) => describeContentReceiverResolution(receiver, { rank: index + 1 }));
    const selected = preferredContentReceiver(receivers, options);
    return {
      resolverPolicy: {
        priorities: ["lifecyclePreferred", "outermost", "ready", "frameDepth", "lastSeenAt"],
        overrideKey: options.overrideKey ?? null,
        overrideMatched: Boolean(compactString(options.overrideKey) && summary.receiverOverrideStatus === "active"),
        selectionPolicy: summary.receiverSelectionPolicy,
        inventoryStatus: summary.receiverInventoryStatus
      },
      ...selected ? { receiverResolution: describeContentReceiverResolution(selected, { rank: rankedMatches.find((candidate) => candidate.receiverKey === contentReceiverKey(selected))?.rank }) } : {},
      rankedMatches
    };
  }
  function preferredContentReceiver(receivers = [], options = {}) {
    if (!receivers.length) return null;
    const override = findOverrideReceiver(receivers, options.overrideKey);
    if (override) return override;
    const sorted = sortReceivers(receivers);
    const lifecyclePreferred = sorted.filter((receiver) => isReceiverLifecyclePreferred(receiver));
    return lifecyclePreferred.find((receiver) => isOutermostReceiver(receiver) && receiver.receiverReady === true) ?? (lifecyclePreferred.length === 1 && lifecyclePreferred[0].receiverReady === true ? lifecyclePreferred[0] : null) ?? lifecyclePreferred.find((receiver) => receiver.receiverReady === true) ?? (lifecyclePreferred.length === 1 ? lifecyclePreferred[0] : null) ?? lifecyclePreferred.find((receiver) => isOutermostReceiver(receiver)) ?? sorted.find((receiver) => isOutermostReceiver(receiver) && receiver.receiverReady === true) ?? (sorted.length === 1 && sorted[0].receiverReady === true ? sorted[0] : null) ?? sorted.find((receiver) => receiver.receiverReady === true) ?? (sorted.length === 1 ? sorted[0] : null) ?? sorted.find((receiver) => isOutermostReceiver(receiver)) ?? sorted[0] ?? null;
  }
  function summarizeContentReceivers(receivers = [], options = {}) {
    const frameIds = Array.from(new Set(receivers.filter((receiver) => typeof receiver.frameId === "number").map((receiver) => receiver.frameId))).sort((left, right) => left - right);
    const documentIds = Array.from(new Set(receivers.map((receiver) => compactString(receiver.documentId)).filter((value) => Boolean(value))));
    const readyReceiverCount = receivers.filter((receiver) => receiver.receiverReady === true).length;
    const lifecyclePreferredReceivers = receivers.filter((receiver) => isReceiverLifecyclePreferred(receiver));
    const preferredReadyReceiverCount = lifecyclePreferredReceivers.filter((receiver) => receiver.receiverReady === true).length;
    const effectiveReadyReceiverCount = lifecyclePreferredReceivers.length ? preferredReadyReceiverCount : readyReceiverCount;
    const receiverTopFrameReady = receivers.some((receiver) => isOutermostReceiver(receiver) && receiver.receiverReady === true && isReceiverLifecyclePreferred(receiver));
    const receiverHasTopFrame = receivers.some((receiver) => isOutermostReceiver(receiver));
    const overrideReceiver = findOverrideReceiver(receivers, options.overrideKey);
    const receiverOverrideStatus = compactString(options.overrideKey) ? overrideReceiver ? "active" : "stale" : "none";
    let receiverSelectionPolicy = "none";
    if (receivers.length) {
      if (overrideReceiver) receiverSelectionPolicy = "operator_override";
      else if (receiverTopFrameReady) receiverSelectionPolicy = "top_frame";
      else if (effectiveReadyReceiverCount === 1) receiverSelectionPolicy = "single_ready";
      else if (effectiveReadyReceiverCount > 1) receiverSelectionPolicy = "latest_ready";
      else if (lifecyclePreferredReceivers.length === 1) receiverSelectionPolicy = "single_observed";
      else if (receivers.length === 1) receiverSelectionPolicy = "single_observed";
      else receiverSelectionPolicy = "latest_observed";
    }
    let receiverInventoryStatus = "none";
    if (receivers.length) {
      if (receivers.length === 1 && receiverHasTopFrame) receiverInventoryStatus = "single_top_frame";
      else if (receiverHasTopFrame) receiverInventoryStatus = "multi_frame_top_frame";
      else if (frameIds.length <= 1) receiverInventoryStatus = "single_subframe";
      else receiverInventoryStatus = "multi_frame_no_top_frame";
    }
    const selected = preferredContentReceiver(receivers, options);
    return {
      receiverCount: receivers.length,
      readyReceiverCount,
      receiverFrameIds: frameIds,
      receiverDocumentIds: documentIds,
      receiverSelectionPolicy,
      receiverInventoryStatus,
      receiverTopFrameReady,
      receiverOverrideStatus,
      ...selected ? {
        selectedReceiverKey: contentReceiverKey(selected) ?? void 0,
        selectedReceiverLabel: contentReceiverLabel(selected)
      } : {}
    };
  }
  function messageTargetForReceivers(receivers = [], options = {}) {
    const preferred = preferredContentReceiver(receivers, options);
    if (!preferred) return void 0;
    if (preferred.documentId) return { documentId: preferred.documentId };
    if (typeof preferred.frameId === "number") return { frameId: preferred.frameId };
    return void 0;
  }

  // src/shared/receiver-priming.ts
  function compactString2(value) {
    if (typeof value !== "string") return void 0;
    const trimmed = value.trim();
    return trimmed || void 0;
  }
  function uniqueStrings2(values) {
    const out = [];
    const seen = /* @__PURE__ */ new Set();
    for (const value of values) {
      const normalized = compactString2(value);
      if (!normalized || seen.has(normalized)) continue;
      seen.add(normalized);
      out.push(normalized);
    }
    return out;
  }
  function uniqueNumbers(values) {
    const out = [];
    const seen = /* @__PURE__ */ new Set();
    for (const value of values) {
      if (typeof value !== "number" || seen.has(value)) continue;
      seen.add(value);
      out.push(value);
    }
    return out;
  }
  function receiverPrimingKey(candidate) {
    return contentReceiverKey({ documentId: candidate.documentId, frameId: candidate.frameId });
  }
  function mergePrimedReceiverKeys(existing, incoming, limit = 64) {
    const merged = uniqueStrings2([...existing, ...incoming]);
    return merged.slice(Math.max(0, merged.length - Math.max(1, limit)));
  }
  function relatedFrameScheme(url) {
    const normalized = compactString2(url)?.toLowerCase();
    if (!normalized) return void 0;
    if (normalized.startsWith("about:")) return "about";
    if (normalized.startsWith("data:")) return "data";
    if (normalized.startsWith("blob:")) return "blob";
    if (normalized.startsWith("filesystem:")) return "filesystem";
    return void 0;
  }
  function isRelatedFrameUrl(url) {
    return relatedFrameScheme(url) !== void 0;
  }
  function primingSkipReason(frame, options) {
    const key = receiverPrimingKey(frame) ?? void 0;
    const documentId = compactString2(frame.documentId);
    const url = compactString2(frame.url);
    const frameId = typeof frame.frameId === "number" ? frame.frameId : void 0;
    if (isOutermostReceiver({ frameId, frameType: frame.frameType, parentFrameId: frame.parentFrameId })) return "top_frame";
    if (!options.isSupportedUrl(url)) return isRelatedFrameUrl(url) ? "related_frame_url" : "unsupported_url";
    if (!key) return "missing_target";
    if (options.observedKeys.has(key)) return "already_observed";
    if (options.primedKeys.has(key) || options.candidateKeys?.has(key)) return "already_primed";
    if (documentId || typeof frameId === "number") return null;
    return "missing_target";
  }
  function planReceiverPriming(frames = [], options) {
    const observedKeys = new Set((options.existingReceivers || []).map((receiver) => contentReceiverKey(receiver)).filter((value) => Boolean(value)));
    const primedKeys = new Set((options.primedKeys || []).map((value) => compactString2(value)).filter((value) => Boolean(value)));
    const candidates = [];
    const candidateKeys = /* @__PURE__ */ new Set();
    const skipped = [];
    for (const frame of frames) {
      const reason = primingSkipReason(frame, { observedKeys, primedKeys, candidateKeys, isSupportedUrl: options.isSupportedUrl });
      const key = receiverPrimingKey(frame) ?? void 0;
      const documentId = compactString2(frame.documentId);
      const url = compactString2(frame.url);
      const frameId = typeof frame.frameId === "number" ? frame.frameId : void 0;
      if (reason) {
        skipped.push({ key, frameId, documentId, url, reason });
        continue;
      }
      if (!key) {
        skipped.push({ frameId, documentId, url, reason: "missing_target" });
        continue;
      }
      candidateKeys.add(key);
      candidates.push({
        key,
        ...documentId ? { documentId } : {},
        ...typeof frameId === "number" ? { frameId } : {},
        ...compactString2(frame.frameType) ? { frameType: compactString2(frame.frameType) } : {},
        ...typeof frame.parentFrameId === "number" ? { parentFrameId: frame.parentFrameId } : {},
        ...url ? { url } : {}
      });
    }
    return {
      candidates,
      candidateKeys: candidates.map((candidate) => candidate.key),
      documentIds: uniqueStrings2(candidates.map((candidate) => candidate.documentId)),
      frameIds: uniqueNumbers(candidates.filter((candidate) => !candidate.documentId).map((candidate) => candidate.frameId)),
      skipped
    };
  }
  function describeReceiverPrimingAudit(frames = [], options) {
    const observedKeys = new Set((options.existingReceivers || []).map((receiver) => contentReceiverKey(receiver)).filter((value) => Boolean(value)));
    const primedKeys = new Set((options.primedKeys || []).map((value) => compactString2(value)).filter((value) => Boolean(value)));
    const plan = planReceiverPriming(frames, options);
    const candidateDocumentKeys = new Set(plan.candidates.filter((candidate) => candidate.documentId).map((candidate) => candidate.key));
    const candidateFrameKeys = new Set(plan.candidates.filter((candidate) => !candidate.documentId).map((candidate) => candidate.key));
    const skippedByKey = /* @__PURE__ */ new Map();
    const skippedByFrameId = /* @__PURE__ */ new Map();
    for (const entry of plan.skipped) {
      if (entry.key) skippedByKey.set(entry.key, entry.reason);
      if (typeof entry.frameId === "number") skippedByFrameId.set(entry.frameId, entry.reason);
    }
    const framesAudit = frames.map((frame) => {
      const key = receiverPrimingKey(frame) ?? void 0;
      const frameId = typeof frame.frameId === "number" ? frame.frameId : void 0;
      const documentId = compactString2(frame.documentId);
      const url = compactString2(frame.url);
      const relatedFrameUrl = isRelatedFrameUrl(url);
      const supportedUrl = options.isSupportedUrl(url);
      const observed = Boolean(key && observedKeys.has(key));
      const primed = Boolean(key && primedKeys.has(key));
      const status = key && candidateDocumentKeys.has(key) ? "candidate_document" : key && candidateFrameKeys.has(key) ? "candidate_frame" : (key ? skippedByKey.get(key) : void 0) ?? (typeof frameId === "number" ? skippedByFrameId.get(frameId) : void 0) ?? "missing_target";
      return {
        ...key ? { key } : {},
        ...typeof frameId === "number" ? { frameId } : {},
        ...documentId ? { documentId } : {},
        ...compactString2(frame.frameType) ? { frameType: compactString2(frame.frameType) } : {},
        ...typeof frame.parentFrameId === "number" ? { parentFrameId: frame.parentFrameId } : {},
        ...url ? { url } : {},
        relatedFrameUrl,
        supportedUrl,
        observed,
        primed,
        status
      };
    });
    const skippedReasonCounts = {
      top_frame: 0,
      unsupported_url: 0,
      related_frame_url: 0,
      already_observed: 0,
      already_primed: 0,
      missing_target: 0
    };
    for (const skipped of plan.skipped) skippedReasonCounts[skipped.reason] += 1;
    const topFrameCount = framesAudit.filter((frame) => frame.status === "top_frame").length;
    const relatedFrameUrlCount = framesAudit.filter((frame) => frame.relatedFrameUrl).length;
    const supportedUrlCount = framesAudit.filter((frame) => frame.supportedUrl).length;
    const observedCount = framesAudit.filter((frame) => frame.observed).length;
    const primedCount = framesAudit.filter((frame) => frame.primed).length;
    const gapCount = framesAudit.filter((frame) => ["candidate_document", "candidate_frame", "related_frame_url", "missing_target"].includes(frame.status)).length;
    return {
      plan,
      counts: {
        frameCount: framesAudit.length,
        supportedUrlCount,
        relatedFrameUrlCount,
        observedCount,
        primedCount,
        topFrameCount,
        candidateCount: plan.candidates.length,
        candidateDocumentCount: candidateDocumentKeys.size,
        candidateFrameCount: candidateFrameKeys.size,
        gapCount,
        skippedReasonCounts
      },
      frames: framesAudit
    };
  }
  function describeReceiverCoveragePolicyHints(audit, manifestPolicy) {
    const candidateFrames = audit.frames.filter((frame) => frame.status === "candidate_document" || frame.status === "candidate_frame");
    const relatedFrames = audit.frames.filter((frame) => frame.status === "related_frame_url");
    const aboutBlankFrames = relatedFrames.filter((frame) => relatedFrameScheme(frame.url) === "about");
    const opaqueRelatedFrames = relatedFrames.filter((frame) => {
      const scheme = relatedFrameScheme(frame.url);
      return scheme === "data" || scheme === "blob" || scheme === "filesystem";
    });
    const missingTargetFrames = audit.frames.filter((frame) => frame.status === "missing_target");
    const hints = [];
    if (candidateFrames.length) {
      hints.push({
        lever: "runtime_priming",
        rationale: "Supported subframes exist without observed receivers; runtime document/frame-targeted reinjection remains the lowest-surface recovery path.",
        frameCount: candidateFrames.length,
        frameIds: uniqueNumbers(candidateFrames.map((frame) => frame.frameId))
      });
    }
    if (relatedFrames.length && !manifestPolicy.allFrames) {
      hints.push({
        lever: "manifest_all_frames",
        rationale: "Static content scripts only auto-run in the top frame by default; reaching matching child frames declaratively would require all_frames.",
        frameCount: relatedFrames.length,
        frameIds: uniqueNumbers(relatedFrames.map((frame) => frame.frameId))
      });
    }
    if (aboutBlankFrames.length && !manifestPolicy.matchAboutBlank) {
      hints.push({
        lever: "manifest_match_about_blank",
        rationale: "Observed about:blank-related gaps match Chrome's dedicated related-frame hook; this is the focused declarative experiment for about:blank descendants.",
        frameCount: aboutBlankFrames.length,
        frameIds: uniqueNumbers(aboutBlankFrames.map((frame) => frame.frameId))
      });
    }
    if (relatedFrames.length && !manifestPolicy.matchOriginAsFallback) {
      hints.push({
        lever: "manifest_match_origin_as_fallback",
        rationale: "Observed about:/data:/blob:/filesystem: gaps match Chrome's initiator-origin fallback path; note that declarative patterns must use path * when this lever is enabled.",
        frameCount: relatedFrames.length,
        frameIds: uniqueNumbers(relatedFrames.map((frame) => frame.frameId))
      });
    }
    return {
      manifestPolicy,
      runtimePrimingCandidateCount: candidateFrames.length,
      relatedFrameGapCount: relatedFrames.length,
      aboutBlankGapCount: aboutBlankFrames.length,
      opaqueRelatedFrameGapCount: opaqueRelatedFrames.length,
      missingTargetGapCount: missingTargetFrames.length,
      hints
    };
  }
  function coverageGapFrames(audit) {
    return audit.frames.filter((frame) => frame.status === "candidate_document" || frame.status === "candidate_frame" || frame.status === "related_frame_url" || frame.status === "missing_target");
  }
  function uniqueFrameIds(frames) {
    return uniqueNumbers(frames.map((frame) => frame.frameId));
  }
  function experimentAddressesFrame(frame, manifestPolicy) {
    if (frame.status === "candidate_document" || frame.status === "candidate_frame") return true;
    if (frame.status === "missing_target") return false;
    if (frame.status !== "related_frame_url") return false;
    if (!manifestPolicy.allFrames) return false;
    const scheme = relatedFrameScheme(frame.url);
    if (manifestPolicy.matchOriginAsFallback) return scheme === "about" || scheme === "data" || scheme === "blob" || scheme === "filesystem";
    if (manifestPolicy.matchAboutBlank) return scheme === "about";
    return false;
  }
  function experimentNotes(experimentId, currentPolicy) {
    if (experimentId === "current_runtime_priming") {
      return [
        "Keeps GlassTTY on the conservative runtime-priming path for matching child frames.",
        "Related-frame gaps remain evidence for a later declarative manifest experiment rather than a default scope change."
      ];
    }
    if (experimentId === "manifest_all_frames") {
      return [
        "Matching child frames would receive declarative content scripts without waiting for runtime priming.",
        "Related about:/data:/blob:/filesystem: gaps would still remain unless a related-frame lever is added too."
      ];
    }
    if (experimentId === "manifest_match_about_blank") {
      return [
        "Models a narrower declarative experiment focused on about:blank descendants.",
        "Chrome only reaches child-frame about:blank documents declaratively when all_frames is also enabled."
      ];
    }
    return [
      "Models the broadest related-frame declarative experiment Chrome documents for about:/data:/blob:/filesystem: descendants.",
      currentPolicy.matchOriginAsFallback ? "match_origin_as_fallback is already enabled in the current policy, so this scenario mainly serves as a saved proof baseline." : "Chrome requires a * path when match_origin_as_fallback is enabled, and it takes priority over match_about_blank."
    ];
  }
  function describeReceiverCoverageExperimentPlan(audit, manifestPolicy) {
    const gaps = coverageGapFrames(audit);
    const candidateFrames = gaps.filter((frame) => frame.status === "candidate_document" || frame.status === "candidate_frame");
    const aboutBlankFrames = gaps.filter((frame) => frame.status === "related_frame_url" && relatedFrameScheme(frame.url) === "about");
    const opaqueRelatedFrames = gaps.filter((frame) => frame.status === "related_frame_url" && relatedFrameScheme(frame.url) !== "about");
    const missingTargetFrames = gaps.filter((frame) => frame.status === "missing_target");
    const proposals = [
      {
        id: "current_runtime_priming",
        label: "Current policy + runtime priming",
        manifestPolicy,
        rationale: "Use the current conservative manifest posture and let runtime priming recover matching child frames."
      },
      {
        id: "manifest_all_frames",
        label: "Declarative matching child frames",
        manifestPolicy: { ...manifestPolicy, allFrames: true },
        rationale: "Enable all_frames so matching child frames can receive the content script declaratively instead of waiting for runtime reinjection."
      },
      {
        id: "manifest_match_about_blank",
        label: "Declarative about:blank descendant experiment",
        manifestPolicy: { ...manifestPolicy, allFrames: true, matchAboutBlank: true },
        rationale: "Enable all_frames plus match_about_blank to test whether about:blank descendants are the missing reach."
      },
      {
        id: "manifest_match_origin_as_fallback",
        label: "Declarative related-frame fallback experiment",
        manifestPolicy: { ...manifestPolicy, allFrames: true, matchOriginAsFallback: true },
        rationale: "Enable all_frames plus match_origin_as_fallback to test Chrome's initiator-origin fallback for about:/data:/blob:/filesystem: descendants."
      }
    ];
    const currentAddressed = gaps.filter((frame) => experimentAddressesFrame(frame, manifestPolicy));
    const currentAddressedCount = currentAddressed.length;
    const seenPolicies = /* @__PURE__ */ new Set();
    const experiments = [];
    for (const proposal of proposals) {
      const policyKey = JSON.stringify(proposal.manifestPolicy);
      if (seenPolicies.has(policyKey)) continue;
      seenPolicies.add(policyKey);
      const addressed = gaps.filter((frame) => experimentAddressesFrame(frame, proposal.manifestPolicy));
      const remaining = gaps.filter((frame) => !experimentAddressesFrame(frame, proposal.manifestPolicy));
      experiments.push({
        id: proposal.id,
        label: proposal.label,
        manifestPolicy: proposal.manifestPolicy,
        rationale: proposal.rationale,
        addressedFrameCount: addressed.length,
        addressedFrameIds: uniqueFrameIds(addressed),
        remainingGapCount: remaining.length,
        remainingGapFrameIds: uniqueFrameIds(remaining),
        incrementalGapReduction: Math.max(0, addressed.length - currentAddressedCount),
        pathWildcardRequired: proposal.manifestPolicy.matchOriginAsFallback,
        notes: experimentNotes(proposal.id, manifestPolicy)
      });
    }
    let recommendedExperimentId;
    let recommendedRationale;
    const originFallback = experiments.find((experiment) => experiment.id === "manifest_match_origin_as_fallback");
    const aboutBlank = experiments.find((experiment) => experiment.id === "manifest_match_about_blank");
    const current = experiments.find((experiment) => experiment.id === "current_runtime_priming") ?? experiments[0];
    if (opaqueRelatedFrames.length && originFallback && originFallback.remainingGapCount < (current?.remainingGapCount ?? Number.MAX_SAFE_INTEGER)) {
      recommendedExperimentId = originFallback.id;
      recommendedRationale = "Opaque related-frame gaps are present; the next evidence-backed declarative experiment is all_frames plus match_origin_as_fallback.";
    } else if (aboutBlankFrames.length && aboutBlank && aboutBlank.remainingGapCount < (current?.remainingGapCount ?? Number.MAX_SAFE_INTEGER)) {
      recommendedExperimentId = aboutBlank.id;
      recommendedRationale = "Observed about:blank gaps suggest a narrower all_frames + match_about_blank experiment before broader related-frame fallback.";
    } else if (candidateFrames.length) {
      recommendedExperimentId = current?.id;
      recommendedRationale = "Matching child-frame gaps are already recoverable with runtime priming, so GlassTTY should stay conservative until a real related-frame artifact appears.";
    } else if (missingTargetFrames.length) {
      recommendedExperimentId = current?.id;
      recommendedRationale = "The remaining gaps are missing target identifiers, so better navigation/document evidence matters more than a manifest change.";
    }
    return {
      manifestPolicy,
      gapFrameCount: gaps.length,
      currentExperimentId: current?.id ?? "current_runtime_priming",
      ...recommendedExperimentId ? { recommendedExperimentId } : {},
      ...recommendedRationale ? { recommendedRationale } : {},
      experiments
    };
  }

  // src/shared/content-script-experiments.ts
  var EXPERIMENT_PREFIX = "glasstty-exp-";
  function compactString3(value) {
    if (typeof value !== "string") return void 0;
    const trimmed = value.trim();
    return trimmed || void 0;
  }
  function uniqueStrings3(values) {
    const out = [];
    const seen = /* @__PURE__ */ new Set();
    for (const value of values) {
      const normalized = compactString3(value);
      if (!normalized || seen.has(normalized)) continue;
      seen.add(normalized);
      out.push(normalized);
    }
    return out;
  }
  function scriptLabel(id) {
    if (id === "manifest_all_frames") return "Dynamic matching child-frame experiment";
    if (id === "manifest_match_about_blank") return "Dynamic about:blank descendant experiment";
    return "Dynamic related-frame fallback experiment";
  }
  function experimentNotes2(id) {
    if (id === "manifest_all_frames") {
      return [
        "Registers a non-persistent dynamic content script so matching child frames can receive the existing GlassTTY content runtime declaratively.",
        "Already-loaded documents may still need a reload or fresh navigation before the dynamic registration becomes observable in probes."
      ];
    }
    if (id === "manifest_match_about_blank") {
      return [
        "Registers a non-persistent dynamic content script with allFrames plus matchAboutBlank for about:blank descendant experiments.",
        "Chrome documents match_about_blank as the focused declarative lever for about:blank descendants; a reload or fresh navigation is still recommended for proof capture."
      ];
    }
    return [
      "Registers a non-persistent dynamic content script with allFrames plus matchOriginAsFallback for about:/data:/blob:/filesystem: descendant experiments.",
      "Chrome requires * paths when match_origin_as_fallback is enabled, so GlassTTY widens any narrower match-pattern paths in the experiment registration.",
      "A reload or fresh navigation is still recommended before comparing probe coverage against the experiment-plan prediction."
    ];
  }
  function normalizeMatchPatternForOriginFallback(match) {
    const trimmed = compactString3(match);
    if (!trimmed) return { match, widened: false, valid: false };
    if (trimmed === "<all_urls>") return { match: trimmed, widened: false, valid: true };
    const parsed = /^(\*|http|https|file|ftp):\/\/([^/]*)(\/.*)$/.exec(trimmed);
    if (!parsed) return { match: trimmed, widened: false, valid: false };
    const [, scheme, host, path] = parsed;
    if (path === "/*") return { match: trimmed, widened: false, valid: true };
    return { match: `${scheme}://${host}/*`, widened: true, valid: true };
  }
  function parseRule(source, script) {
    return {
      ...compactString3(script.id) ? { id: compactString3(script.id) } : {},
      source,
      matches: uniqueStrings3(Array.isArray(script.matches) ? script.matches : []),
      js: uniqueStrings3(Array.isArray(script.js) ? script.js : []),
      css: uniqueStrings3(Array.isArray(script.css) ? script.css : []),
      ...compactString3(script.run_at ?? script.runAt) ? { runAt: compactString3(script.run_at ?? script.runAt) } : {},
      allFrames: script.all_frames === true || script.allFrames === true,
      matchAboutBlank: script.match_about_blank === true || script.matchAboutBlank === true,
      matchOriginAsFallback: script.match_origin_as_fallback === true || script.matchOriginAsFallback === true,
      ...compactString3(script.world) ? { world: compactString3(script.world) } : {},
      ...typeof script.persistAcrossSessions === "boolean" ? { persistAcrossSessions: script.persistAcrossSessions } : {}
    };
  }
  function experimentRegistrationId(experimentId, index) {
    return `${EXPERIMENT_PREFIX}${experimentId}-${index + 1}`;
  }
  function glassTTYExperimentIdFromScriptId(id) {
    const normalized = compactString3(id);
    if (!normalized || !normalized.startsWith(EXPERIMENT_PREFIX)) return void 0;
    const body = normalized.slice(EXPERIMENT_PREFIX.length);
    if (body.startsWith("manifest_all_frames-")) return "manifest_all_frames";
    if (body.startsWith("manifest_match_about_blank-")) return "manifest_match_about_blank";
    if (body.startsWith("manifest_match_origin_as_fallback-")) return "manifest_match_origin_as_fallback";
    return void 0;
  }
  function staticContentScriptRulesFromManifest(manifest = {}) {
    const scripts = Array.isArray(manifest.content_scripts) ? manifest.content_scripts : [];
    return scripts.map((script) => parseRule("static", script));
  }
  function dynamicContentScriptRulesFromRegisteredScripts(scripts = []) {
    return scripts.filter((script) => glassTTYExperimentIdFromScriptId(compactString3(script.id)) !== void 0).map((script) => parseRule("dynamic", script));
  }
  function buildContentScriptExperimentRegistration(rules = [], experimentId) {
    const experimentRules = rules.filter((rule) => rule.source === "static" && (rule.js.length || rule.css.length));
    const invalidMatchPatterns = [];
    let widenedMatchPatterns = false;
    const registeredScripts = experimentRules.map((rule, index) => {
      const normalizedMatches = experimentId === "manifest_match_origin_as_fallback" ? rule.matches.map((match) => {
        const normalized = normalizeMatchPatternForOriginFallback(match);
        if (!normalized.valid) invalidMatchPatterns.push(match);
        widenedMatchPatterns ||= normalized.widened;
        return normalized.match;
      }) : [...rule.matches];
      return {
        id: experimentRegistrationId(experimentId, index),
        matches: uniqueStrings3(normalizedMatches),
        ...rule.js.length ? { js: [...rule.js] } : {},
        ...rule.css.length ? { css: [...rule.css] } : {},
        ...rule.runAt ? { runAt: rule.runAt } : {},
        ...rule.world ? { world: rule.world } : {},
        ...experimentId === "manifest_all_frames" || experimentId === "manifest_match_about_blank" || experimentId === "manifest_match_origin_as_fallback" ? { allFrames: true } : {},
        ...experimentId === "manifest_match_about_blank" ? { matchAboutBlank: true } : {},
        ...experimentId === "manifest_match_origin_as_fallback" ? { matchOriginAsFallback: true } : {},
        persistAcrossSessions: false
      };
    });
    return {
      experimentId,
      label: scriptLabel(experimentId),
      scriptIds: registeredScripts.map((script) => script.id),
      widenedMatchPatterns,
      invalidMatchPatterns: uniqueStrings3(invalidMatchPatterns),
      requiresNavigation: true,
      notes: experimentNotes2(experimentId),
      registeredScripts
    };
  }
  function summarizeContentScriptPolicy(staticRules = [], dynamicRules = []) {
    const allRules = [...staticRules, ...dynamicRules];
    const experimentIds = uniqueStrings3(dynamicRules.map((rule) => glassTTYExperimentIdFromScriptId(rule.id))).filter((value) => value === "manifest_all_frames" || value === "manifest_match_about_blank" || value === "manifest_match_origin_as_fallback");
    let activeExperiment;
    if (experimentIds.length === 1) {
      const experimentId = experimentIds[0];
      const registration = buildContentScriptExperimentRegistration(staticRules, experimentId);
      activeExperiment = {
        id: experimentId,
        label: scriptLabel(experimentId),
        registeredScriptCount: dynamicRules.length,
        scriptIds: uniqueStrings3(dynamicRules.map((rule) => rule.id)),
        matches: uniqueStrings3(dynamicRules.flatMap((rule) => rule.matches)),
        allFrames: dynamicRules.some((rule) => rule.allFrames),
        matchAboutBlank: dynamicRules.some((rule) => rule.matchAboutBlank),
        matchOriginAsFallback: dynamicRules.some((rule) => rule.matchOriginAsFallback),
        runAt: uniqueStrings3(dynamicRules.map((rule) => rule.runAt)),
        persistAcrossSessions: dynamicRules.every((rule) => rule.persistAcrossSessions !== false),
        widenedMatchPatterns: registration.widenedMatchPatterns,
        requiresNavigation: registration.requiresNavigation,
        notes: registration.notes
      };
    }
    return {
      staticContentScriptCount: staticRules.length,
      dynamicContentScriptCount: dynamicRules.length,
      matches: uniqueStrings3(allRules.flatMap((rule) => rule.matches)),
      allFrames: allRules.some((rule) => rule.allFrames),
      matchAboutBlank: allRules.some((rule) => rule.matchAboutBlank),
      matchOriginAsFallback: allRules.some((rule) => rule.matchOriginAsFallback),
      runAt: uniqueStrings3(allRules.map((rule) => rule.runAt)),
      ...activeExperiment ? { activeExperiment } : {}
    };
  }

  // src/background/main.ts
  var HOST_NAME = "com.glasstty.bridge";
  var STORAGE_KEY = "bridgeState";
  var PERSISTENT_HISTORY_KEY = "bridgePersistentHistory";
  var SESSION_TABS_KEY = "supportedTabs";
  var SESSION_PRIMED_RECEIVERS_KEY = "primedReceivers";
  var TRACE_KEY = "bridgeTrace";
  var TRACE_LIMIT = 160;
  var MENU_PATTERNS = supportedMatchPatterns();
  var MENU_OPEN_PANEL = "open-panel";
  var MENU_SET_TARGET = "set-target-tab";
  var MENU_READ_LATEST = "read-latest";
  var MENU_READ_PROMPT = "read-prompt";
  var MENU_WRITE_SELECTION = "write-selection-to-prompt";
  var MENU_CAPTURE_FIXTURE = "capture-fixture";
  var NATIVE_RECONNECT_ALARM = "native-reconnect";
  var NATIVE_RECONNECT_MINUTES = 0.5;
  var NATIVE_RECONNECT_MAX_MINUTES = 8;
  var MANIFEST_VERSION = chrome.runtime.getManifest().version;
  var BUNDLE_VERSION_IS_CURRENT = MANIFEST_VERSION === "0.1.126";
  var STALE_BUNDLE_RELOAD_KEY = "staleBundleReloadAttempt";
  var nativePort = null;
  var pendingNativeHealth = null;
  var WORKER_BOOT_ID = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `boot-${Date.now()}`;
  async function enforceCurrentBundle() {
    if (BUNDLE_VERSION_IS_CURRENT) {
      await chrome.storage.local.remove(STALE_BUNDLE_RELOAD_KEY);
      return true;
    }
    const expected = `${"0.1.126"}->${MANIFEST_VERSION}`;
    const stored = await chrome.storage.local.get(STALE_BUNDLE_RELOAD_KEY);
    if (stored[STALE_BUNDLE_RELOAD_KEY] === expected) {
      console.error(
        `GlassTTY worker bundle ${"0.1.126"} is still stale for manifest ${MANIFEST_VERSION} after one reload; rebuild and reload the unpacked extension`
      );
      return false;
    }
    await chrome.storage.local.set({ [STALE_BUNDLE_RELOAD_KEY]: expected });
    console.warn(
      `GlassTTY worker bundle ${"0.1.126"} is stale for manifest ${MANIFEST_VERSION}; reloading the unpacked extension once`
    );
    chrome.runtime.reload();
    return false;
  }
  var WORKER_BOOT_AT = (/* @__PURE__ */ new Date()).toISOString();
  var OFFSCREEN_DOCUMENT_PATH = "offscreen/index.html";
  var OFFSCREEN_JUSTIFICATION = "GlassTTY hidden diagnostics context for bridge proof and future headless lab work";
  var OFFSCREEN_REASONS = ["TESTING", "DOM_PARSER"];
  var creatingOffscreenDocument = null;
  function log(...args) {
    console.log("[GlassTTY background]", ...args);
  }
  function errorMessage(error) {
    return error instanceof Error ? error.message : String(error);
  }
  function sleep(ms) {
    return new Promise((resolve) => self.setTimeout(resolve, ms));
  }
  function originFromUrl2(url) {
    if (!url) return void 0;
    try {
      return new URL(url).origin;
    } catch {
      return void 0;
    }
  }
  function hostnameFromUrl2(url) {
    if (!url) return void 0;
    try {
      return new URL(url).hostname || void 0;
    } catch {
      return void 0;
    }
  }
  function compactString4(value) {
    if (typeof value !== "string") return void 0;
    const trimmed = value.trim();
    return trimmed || void 0;
  }
  function uniqueStrings4(values) {
    const out = [];
    const seen = /* @__PURE__ */ new Set();
    for (const value of values) {
      const normalized = compactString4(value);
      if (!normalized || seen.has(normalized)) continue;
      seen.add(normalized);
      out.push(normalized);
    }
    return out;
  }
  function dynamicScriptingApi() {
    return chrome.scripting;
  }
  async function glassTTYDynamicContentScripts() {
    const scripting = dynamicScriptingApi();
    if (!scripting.getRegisteredContentScripts) return [];
    try {
      const scripts = await scripting.getRegisteredContentScripts();
      return scripts.filter((script) => glassTTYExperimentIdFromScriptId(compactString4(script.id)) !== void 0);
    } catch (error) {
      await appendTrace("content_scripts.dynamic_inventory_failed", { error: errorMessage(error) }, "warn");
      return [];
    }
  }
  async function contentScriptPolicySummary(manifest = chrome.runtime.getManifest()) {
    const staticRules = staticContentScriptRulesFromManifest(manifest);
    const dynamicRules = dynamicContentScriptRulesFromRegisteredScripts(await glassTTYDynamicContentScripts());
    return summarizeContentScriptPolicy(staticRules, dynamicRules);
  }
  async function contentScriptExperimentStatus(manifest = chrome.runtime.getManifest()) {
    const dynamicScripts = await glassTTYDynamicContentScripts();
    const dynamicRules = dynamicContentScriptRulesFromRegisteredScripts(dynamicScripts);
    return {
      policy: summarizeContentScriptPolicy(staticContentScriptRulesFromManifest(manifest), dynamicRules),
      dynamicScriptCount: dynamicScripts.length
    };
  }
  async function clearContentScriptExperimentRegistration(options = {}) {
    const dynamicScripts = await glassTTYDynamicContentScripts();
    const ids = uniqueStrings4(dynamicScripts.map((script) => script.id));
    if (ids.length) {
      const scripting = dynamicScriptingApi();
      if (!scripting.unregisterContentScripts) throw new Error("chrome.scripting.unregisterContentScripts is unavailable in this Chrome build");
      await scripting.unregisterContentScripts({ ids });
    }
    const policy = await contentScriptPolicySummary();
    await appendTrace("content_scripts.experiment_cleared", { clearedIds: ids, traceReason: options.traceReason ?? null, activeExperiment: policy.activeExperiment?.id ?? null });
    return policy;
  }
  async function applyContentScriptExperiment(experimentId) {
    const manifest = chrome.runtime.getManifest();
    const registration = buildContentScriptExperimentRegistration(staticContentScriptRulesFromManifest(manifest), experimentId);
    const existing = await glassTTYDynamicContentScripts();
    const existingIds = uniqueStrings4(existing.map((script) => script.id));
    if (existingIds.length) {
      const scripting2 = dynamicScriptingApi();
      if (!scripting2.unregisterContentScripts) throw new Error("chrome.scripting.unregisterContentScripts is unavailable in this Chrome build");
      await scripting2.unregisterContentScripts({ ids: existingIds });
    }
    if (!registration.registeredScripts.length) {
      throw new Error(`no static GlassTTY content scripts were available to clone for ${experimentId}`);
    }
    const scripting = dynamicScriptingApi();
    if (!scripting.registerContentScripts) throw new Error("chrome.scripting.registerContentScripts is unavailable in this Chrome build");
    await scripting.registerContentScripts(registration.registeredScripts);
    const policy = await contentScriptPolicySummary(manifest);
    await appendTrace("content_scripts.experiment_set", {
      experimentId,
      scriptIds: registration.scriptIds,
      widenedMatchPatterns: registration.widenedMatchPatterns,
      invalidMatchPatterns: registration.invalidMatchPatterns,
      activeExperiment: policy.activeExperiment?.id ?? null
    });
    return { policy, registration };
  }
  function frameContextKey(details) {
    if (details.documentId) return `doc:${details.documentId}`;
    if (typeof details.frameId === "number") return `frame:${details.frameId}`;
    return null;
  }
  async function frameContextIndexForTab(tabId) {
    const index = /* @__PURE__ */ new Map();
    let frames;
    try {
      frames = await chrome.webNavigation.getAllFrames({ tabId });
    } catch (error) {
      await appendTrace("receivers.frame_context_failed", { tabId, error: errorMessage(error) }, "warn");
      return index;
    }
    const byFrameId = /* @__PURE__ */ new Map();
    for (const frame of frames || []) {
      if (typeof frame.frameId === "number") byFrameId.set(frame.frameId, frame);
    }
    function lineage(frame) {
      const seen = /* @__PURE__ */ new Set();
      const chain = [];
      let current = frame;
      while (current) {
        chain.push(current);
        if (typeof current.parentFrameId !== "number" || current.parentFrameId < 0 || seen.has(current.parentFrameId)) break;
        seen.add(current.frameId);
        current = byFrameId.get(current.parentFrameId);
      }
      return chain.reverse();
    }
    for (const frame of frames || []) {
      const key = frameContextKey({ documentId: frame.documentId, frameId: frame.frameId });
      if (!key) continue;
      const chain = lineage(frame);
      const framePathFrameIds = chain.map((entry) => entry.frameId).filter((value) => typeof value === "number");
      const framePathUrls = chain.map((entry) => entry.url).filter((value) => typeof value === "string" && value.length > 0);
      const framePathHosts = chain.map((entry) => hostnameFromUrl2(entry.url) ?? (entry.frameId === 0 ? "top-frame" : `frame:${entry.frameId}`));
      index.set(key, {
        documentId: frame.documentId,
        frameId: frame.frameId,
        documentLifecycle: frame.documentLifecycle,
        frameType: frame.frameType,
        parentFrameId: typeof frame.parentFrameId === "number" ? frame.parentFrameId : void 0,
        parentDocumentId: frame.parentDocumentId,
        frameUrl: frame.url,
        frameOrigin: originFromUrl2(frame.url),
        frameDepth: Math.max(0, chain.length - 1),
        framePathFrameIds,
        framePathUrls,
        framePathHosts,
        framePathLabel: framePathHosts.join(" \u2192 ")
      });
    }
    return index;
  }
  async function enrichReceiversWithFrameContext(tabId, receivers = []) {
    if (!receivers.length) return [];
    const frameIndex = await frameContextIndexForTab(tabId);
    if (!frameIndex.size) return receivers;
    return receivers.map((receiver) => {
      const key = frameContextKey(receiver);
      const context = key ? frameIndex.get(key) : void 0;
      return context ? { ...receiver, ...context } : receiver;
    });
  }
  function receiverKeysForFrames(frames = []) {
    return Array.from(new Set(frames.map((frame) => frameContextKey({ documentId: frame.documentId, frameId: frame.frameId })).filter((value) => Boolean(value))));
  }
  async function setPrimedReceiverKeys(tabId, keys) {
    const normalizedTabId = String(tabId);
    const state = await getPrimedReceivers();
    const nextKeys = mergePrimedReceiverKeys([], keys);
    await chrome.storage.session.set({
      [SESSION_PRIMED_RECEIVERS_KEY]: {
        ...state,
        [normalizedTabId]: nextKeys
      }
    });
    return nextKeys;
  }
  async function refreshSupportedTabReceiverContexts(tabId) {
    const existing = (await getSupportedTabs()).find((entry) => entry.tabId === tabId);
    if (!existing?.receivers?.length) return;
    const tab = await getTabById(tabId);
    if (!tab?.id || !isSupportedUrl(tab.url)) return;
    const frameIndex = await frameContextIndexForTab(tab.id);
    const reconciled = frameIndex.size ? reconcileContentReceivers(existing.receivers || [], Array.from(frameIndex.values())) : { receivers: existing.receivers || [], removed: [], removedKeys: [], retainedKeys: [] };
    if (reconciled.removedKeys.length) {
      await appendTrace("receivers.reconciled", { tabId: tab.id, removedKeys: reconciled.removedKeys, retainedKeys: reconciled.retainedKeys });
    }
    const supportedTabs = await rememberSupportedTab({
      ...existing,
      tabId: tab.id,
      windowId: tab.windowId,
      url: tab.url,
      title: tab.title,
      discarded: tab.discarded ?? existing.discarded,
      frozen: tab.frozen ?? existing.frozen,
      receivers: reconciled.receivers,
      lastSeenAt: (/* @__PURE__ */ new Date()).toISOString()
    });
    const state = await getBridgeState();
    await patchBridgeState({
      supportedTabs,
      targetTab: state.selectedTargetTabId === tab.id ? supportedTabs.find((entry) => entry.tabId === tab.id) ?? state.targetTab : state.targetTab
    });
  }
  async function primeSupportedSubframeReceivers(tab, knownState) {
    if (!tab?.id || !isSupportedUrl(tab.url)) return;
    if (tab.discarded || knownState?.discarded) return;
    if (tab.frozen || knownState?.frozen) return;
    let frames;
    try {
      frames = await chrome.webNavigation.getAllFrames({ tabId: tab.id });
    } catch (error) {
      await appendTrace("receivers.prime_inventory_failed", { tabId: tab.id, error: errorMessage(error) }, "warn");
      return;
    }
    const state = knownState ?? (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
    const liveReceiverKeys = new Set(receiverKeysForFrames(frames || []));
    const primedKeysBefore = await primedReceiverKeysForTab(tab.id);
    const primedKeys = liveReceiverKeys.size ? primedKeysBefore.filter((key) => liveReceiverKeys.has(key)) : primedKeysBefore;
    if (primedKeys.length !== primedKeysBefore.length) {
      await setPrimedReceiverKeys(tab.id, primedKeys);
      await appendTrace("receivers.primed_keys_reconciled", { tabId: tab.id, removedKeys: primedKeysBefore.filter((key) => !liveReceiverKeys.has(key)), retainedKeyCount: primedKeys.length });
    }
    const observedReceivers = liveReceiverKeys.size ? (state?.receivers || []).filter((receiver) => {
      const key = contentReceiverKey(receiver);
      return !key || liveReceiverKeys.has(key);
    }) : state?.receivers || [];
    const plan = planReceiverPriming(frames || [], {
      existingReceivers: observedReceivers,
      primedKeys,
      isSupportedUrl
    });
    if (!plan.candidates.length) return;
    await appendTrace("receivers.prime_planned", {
      tabId: tab.id,
      candidateCount: plan.candidates.length,
      documentIdCount: plan.documentIds.length,
      frameIdCount: plan.frameIds.length,
      candidateKeys: plan.candidateKeys
    });
    if (plan.documentIds.length) {
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id, documentIds: plan.documentIds },
          files: ["dist/content/main.js"]
        });
        await rememberPrimedReceiverKeys(tab.id, plan.candidates.filter((candidate) => candidate.documentId).map((candidate) => candidate.key));
        await appendTrace("receivers.prime_succeeded", { tabId: tab.id, mode: "documentIds", documentIds: plan.documentIds });
      } catch (error) {
        await appendTrace("receivers.prime_failed", { tabId: tab.id, mode: "documentIds", documentIds: plan.documentIds, error: errorMessage(error) }, "warn");
      }
    }
    if (plan.frameIds.length) {
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id, frameIds: plan.frameIds },
          files: ["dist/content/main.js"]
        });
        await rememberPrimedReceiverKeys(tab.id, plan.candidates.filter((candidate) => !candidate.documentId).map((candidate) => candidate.key));
        await appendTrace("receivers.prime_succeeded", { tabId: tab.id, mode: "frameIds", frameIds: plan.frameIds });
      } catch (error) {
        await appendTrace("receivers.prime_failed", { tabId: tab.id, mode: "frameIds", frameIds: plan.frameIds, error: errorMessage(error) }, "warn");
      }
    }
  }
  function reconnectDelayMinutes(attempt) {
    const boundedAttempt = Math.max(1, attempt);
    return Math.min(NATIVE_RECONNECT_MAX_MINUTES, NATIVE_RECONNECT_MINUTES * 2 ** (boundedAttempt - 1));
  }
  function defaultNativeConnectionState() {
    return {
      connected: false,
      reconnectAttempt: 0,
      reconnectScheduledFor: null,
      reconnectDelayMinutes: null
    };
  }
  function defaultRuntimeLaneState() {
    return {
      currentBootId: WORKER_BOOT_ID,
      currentBootAt: WORKER_BOOT_AT,
      bootCount: 0,
      lastBootstrapAt: WORKER_BOOT_AT
    };
  }
  function offscreenDocumentUrl() {
    return chrome.runtime.getURL(OFFSCREEN_DOCUMENT_PATH);
  }
  async function offscreenContexts() {
    if (typeof chrome.runtime.getContexts !== "function") return [];
    return chrome.runtime.getContexts({
      contextTypes: ["OFFSCREEN_DOCUMENT"],
      documentUrls: [offscreenDocumentUrl()]
    });
  }
  async function pingOffscreenDocument(timeoutMs = 1500) {
    const deadline = Date.now() + timeoutMs;
    let lastError;
    while (Date.now() < deadline) {
      try {
        const response = await chrome.runtime.sendMessage(makeEnvelope("offscreen.document_ping", { probeAt: (/* @__PURE__ */ new Date()).toISOString() }));
        if (response?.type === "offscreen.document_pong" && response.payload) {
          return { ok: true, payload: response.payload };
        }
        lastError = `unexpected offscreen ping response: ${String(response?.type ?? "missing")}`;
      } catch (error) {
        lastError = errorMessage(error);
      }
      await sleep(100);
    }
    return { ok: false, error: lastError ?? "offscreen ping timed out" };
  }
  async function requestOffscreenDomSummary(html, selectors, maxCandidates, baseUrl, timeoutMs = 2500) {
    const deadline = Date.now() + timeoutMs;
    let lastError;
    while (Date.now() < deadline) {
      try {
        const response = await chrome.runtime.sendMessage(
          makeEnvelope("offscreen.document_parse_html", {
            html,
            selectors,
            max_candidates: maxCandidates,
            ...baseUrl ? { base_url: baseUrl } : {}
          })
        );
        if (response?.type === "offscreen.document_parse_html_result" && response.payload?.ok && response.payload.summary) {
          return { ok: true, summary: response.payload.summary };
        }
        if (response?.payload?.error) {
          lastError = String(response.payload.error);
        } else {
          lastError = `unexpected offscreen parse response: ${String(response?.type ?? "missing")}`;
        }
      } catch (error) {
        lastError = errorMessage(error);
      }
      await sleep(100);
    }
    return { ok: false, error: lastError ?? "offscreen DOM parse timed out" };
  }
  async function requestOffscreenFixtureCapture(html, selectors, maxCandidates, baseUrl, timeoutMs = 2500) {
    const deadline = Date.now() + timeoutMs;
    let lastError;
    while (Date.now() < deadline) {
      try {
        const response = await chrome.runtime.sendMessage(
          makeEnvelope("offscreen.document_capture_fixture", {
            html,
            selectors,
            max_candidates: maxCandidates,
            ...baseUrl ? { base_url: baseUrl } : {}
          })
        );
        if (response?.type === "offscreen.document_capture_fixture_result" && response.payload?.ok && response.payload.summary && response.payload.fixture) {
          return { ok: true, summary: response.payload.summary, fixture: response.payload.fixture };
        }
        if (response?.payload?.error) {
          lastError = String(response.payload.error);
        } else {
          lastError = `unexpected offscreen fixture response: ${String(response?.type ?? "missing")}`;
        }
      } catch (error) {
        lastError = errorMessage(error);
      }
      await sleep(100);
    }
    return { ok: false, error: lastError ?? "offscreen fixture capture timed out" };
  }
  async function ensureOffscreenDocument(requested, opts = {}) {
    const url = offscreenDocumentUrl();
    const hasRuntimeGetContexts = typeof chrome.runtime.getContexts === "function";
    const offscreenApi = chrome.offscreen;
    const supported = Boolean(hasRuntimeGetContexts && typeof offscreenApi?.createDocument === "function");
    const existing = supported ? await offscreenContexts() : [];
    const base = {
      supported,
      requested,
      enabled: existing.length > 0,
      url,
      contextCount: existing.length,
      documentUrls: existing.map((context) => context.documentUrl).filter((value) => typeof value === "string"),
      runtimeGetContexts: hasRuntimeGetContexts,
      ...supported ? {} : { lastError: hasRuntimeGetContexts ? "offscreen API unavailable" : "runtime.getContexts unavailable" }
    };
    if (!requested || !supported) {
      if (opts.ping && base.enabled) {
        const ping = await pingOffscreenDocument(opts.pingTimeoutMs);
        return {
          ...base,
          responsive: ping.ok,
          lastReady: ping.payload,
          ...ping.ok ? {} : { lastError: ping.error ?? base.lastError }
        };
      }
      return base;
    }
    if (!existing.length) {
      if (creatingOffscreenDocument) {
        await creatingOffscreenDocument;
      } else {
        creatingOffscreenDocument = offscreenApi.createDocument({
          url: OFFSCREEN_DOCUMENT_PATH,
          reasons: OFFSCREEN_REASONS,
          justification: OFFSCREEN_JUSTIFICATION
        });
        try {
          await creatingOffscreenDocument;
          await appendTrace("offscreen.document_ensured", { url, reasons: OFFSCREEN_REASONS });
        } catch (error) {
          const failure = errorMessage(error);
          await appendTrace("offscreen.document_failed", { url, error: failure }, "warn");
          return {
            supported,
            requested,
            enabled: false,
            url,
            contextCount: 0,
            documentUrls: [],
            runtimeGetContexts: hasRuntimeGetContexts,
            responsive: false,
            lastError: failure
          };
        } finally {
          creatingOffscreenDocument = null;
        }
      }
    }
    const ensured = await offscreenContexts();
    const next = {
      supported,
      requested,
      enabled: ensured.length > 0,
      url,
      contextCount: ensured.length,
      documentUrls: ensured.map((context) => context.documentUrl).filter((value) => typeof value === "string"),
      runtimeGetContexts: hasRuntimeGetContexts
    };
    if (opts.ping && next.enabled) {
      const ping = await pingOffscreenDocument(opts.pingTimeoutMs);
      return {
        ...next,
        responsive: ping.ok,
        lastReady: ping.payload,
        ...ping.ok ? {} : { lastError: ping.error }
      };
    }
    return next;
  }
  async function patchRuntimeLane(patch) {
    const state = await getBridgeState();
    const next = {
      ...defaultRuntimeLaneState(),
      ...state.runtime ?? {},
      ...patch
    };
    return patchBridgeState({ runtime: next });
  }
  async function recordRuntimeBoot() {
    const state = await getBridgeState();
    const previous = state.runtime ?? defaultRuntimeLaneState();
    const bootCount = Math.max(1, Number(previous.bootCount ?? 0) + 1);
    const runtime = { ...previous, currentBootId: WORKER_BOOT_ID, currentBootAt: WORKER_BOOT_AT, bootCount, lastBootstrapAt: WORKER_BOOT_AT };
    await patchBridgeState({ runtime });
    await updatePersistentBridgeHistory((current) => recordPersistentWorkerBoot(current, { bootId: runtime.currentBootId, bootAt: runtime.currentBootAt, bootCount: runtime.bootCount }));
    await appendTrace("runtime.worker_boot", { bootId: WORKER_BOOT_ID, bootAt: WORKER_BOOT_AT, bootCount });
  }
  async function recordRuntimeSignal(signal) {
    const at = (/* @__PURE__ */ new Date()).toISOString();
    if (signal === "startup") {
      await patchRuntimeLane({ lastStartupSignalAt: at });
    } else if (signal === "installed") {
      await patchRuntimeLane({ lastInstalledAt: at });
    } else {
      await patchRuntimeLane({ lastSuspendSignalAt: at });
    }
    await appendTrace(`runtime.${signal}_signal`, { at, bootId: WORKER_BOOT_ID });
  }
  async function patchNativeConnection(patch) {
    const state = await getBridgeState();
    const next = {
      ...defaultNativeConnectionState(),
      ...state.nativeConnection ?? {},
      ...patch
    };
    return patchBridgeState({ nativeConnection: next });
  }
  async function markNativeConnected() {
    await chrome.alarms.clear(NATIVE_RECONNECT_ALARM).catch(console.error);
    await patchNativeConnection({
      connected: true,
      lastConnectedAt: (/* @__PURE__ */ new Date()).toISOString(),
      reconnectAttempt: 0,
      reconnectScheduledFor: null,
      reconnectDelayMinutes: null,
      lastHealthError: void 0
    });
  }
  async function markNativeDisconnected(reason) {
    await patchNativeConnection({
      connected: false,
      lastDisconnectedAt: (/* @__PURE__ */ new Date()).toISOString(),
      lastDisconnectReason: reason,
      lastHealthOk: false,
      lastHealthError: reason
    });
  }
  async function scheduleNativeReconnect(reason, attempt) {
    const delayInMinutes = reconnectDelayMinutes(attempt);
    const scheduledFor = new Date(Date.now() + delayInMinutes * 6e4).toISOString();
    await chrome.alarms.create(NATIVE_RECONNECT_ALARM, { delayInMinutes });
    await patchNativeConnection({
      connected: false,
      lastDisconnectReason: reason,
      reconnectAttempt: attempt,
      reconnectScheduledFor: scheduledFor,
      reconnectDelayMinutes: delayInMinutes
    });
    await appendTrace("native.reconnect_scheduled", { reason, attempt, delayInMinutes, scheduledFor }, "warn");
  }
  function clearPendingNativeHealth(reason) {
    if (!pendingNativeHealth) return;
    clearTimeout(pendingNativeHealth.timeoutId);
    pendingNativeHealth = null;
    void appendTrace("native.health_cancelled", { reason }, "warn").catch(console.error);
  }
  async function requestNativeHealth(trigger, timeoutMs = 1500) {
    if (!nativePort || pendingNativeHealth) return false;
    const requestId = `health-${Date.now()}`;
    const startedAt = Date.now();
    const healthRequest = makeEnvelope("health.ping", {
      requestId,
      trigger,
      sentAt: new Date(startedAt).toISOString(),
      broker_intent: "owner_candidate"
    });
    const timeoutId = self.setTimeout(() => {
      if (!pendingNativeHealth || pendingNativeHealth.requestId !== requestId) return;
      pendingNativeHealth = null;
      void patchNativeConnection({
        lastHealthPingAt: new Date(startedAt).toISOString(),
        lastHealthRequestId: requestId,
        lastHealthTrigger: trigger,
        lastHealthOk: false,
        lastHealthError: `timeout after ${timeoutMs}ms`
      }).catch(console.error);
      void appendTrace("native.health_timeout", { requestId, trigger, timeoutMs }, "warn").catch(console.error);
    }, timeoutMs);
    pendingNativeHealth = { requestId, envelopeRequestId: healthRequest.request_id, startedAt, timeoutId };
    await patchNativeConnection({
      lastHealthPingAt: new Date(startedAt).toISOString(),
      lastHealthRequestId: requestId,
      lastHealthTrigger: trigger,
      lastHealthOk: false,
      lastHealthError: void 0
    });
    await appendTrace("native.health_ping", { requestId, trigger }).catch(console.error);
    try {
      nativePort.postMessage(healthRequest);
      return true;
    } catch (error) {
      clearPendingNativeHealth("post_failed");
      await patchNativeConnection({
        lastHealthRequestId: requestId,
        lastHealthTrigger: trigger,
        lastHealthOk: false,
        lastHealthError: errorMessage(error)
      });
      await appendTrace("native.health_post_failed", { requestId, trigger, error: errorMessage(error) }, "warn");
      return false;
    }
  }
  function nativeHostIdentityFromRecord(record) {
    if (!record || typeof record !== "object") return void 0;
    return {
      pid: typeof record.pid === "number" ? record.pid : void 0,
      boot_id: typeof record.boot_id === "string" ? record.boot_id : void 0,
      started_at: typeof record.started_at === "string" ? record.started_at : void 0,
      message_count: typeof record.message_count === "number" ? record.message_count : void 0,
      first_message_at: typeof record.first_message_at === "string" ? record.first_message_at : void 0,
      first_message_type: typeof record.first_message_type === "string" ? record.first_message_type : void 0,
      last_message_at: typeof record.last_message_at === "string" ? record.last_message_at : void 0,
      last_message_type: typeof record.last_message_type === "string" ? record.last_message_type : void 0
    };
  }
  function nativeBrokerOwnerMetadataFromRecord(record) {
    if (!record || typeof record !== "object") return void 0;
    return {
      native_host: typeof record.native_host === "string" ? record.native_host : void 0,
      socket_path: typeof record.socket_path === "string" ? record.socket_path : void 0,
      lock_path: typeof record.lock_path === "string" ? record.lock_path : void 0,
      metadata_path: typeof record.metadata_path === "string" ? record.metadata_path : void 0,
      host_identity: nativeHostIdentityFromRecord(typeof record.host_identity === "object" && record.host_identity ? record.host_identity : void 0)
    };
  }
  function nativeBrokerSummaryFromPayload(payload) {
    if (!payload || typeof payload !== "object") return void 0;
    const broker = typeof payload.broker === "object" && payload.broker ? payload.broker : payload;
    return {
      role: typeof broker.role === "string" ? broker.role : void 0,
      lock_path: typeof broker.lock_path === "string" ? broker.lock_path : void 0,
      metadata_path: typeof broker.metadata_path === "string" ? broker.metadata_path : void 0,
      socket_path: typeof broker.socket_path === "string" ? broker.socket_path : void 0,
      socket_exists: typeof broker.socket_exists === "boolean" ? broker.socket_exists : void 0,
      connected_clients: typeof broker.connected_clients === "number" || broker.connected_clients === null ? broker.connected_clients : void 0,
      owner_metadata: nativeBrokerOwnerMetadataFromRecord(typeof broker.owner_metadata === "object" && broker.owner_metadata ? broker.owner_metadata : void 0)
    };
  }
  function nativeHostIdentitiesMatch(left, right) {
    if (!left || !right) return void 0;
    if (!left.boot_id || !right.boot_id) return void 0;
    if (typeof left.pid !== "number" || typeof right.pid !== "number") return void 0;
    return left.boot_id === right.boot_id && left.pid === right.pid;
  }
  function nativeOverflowSummaryFromPayload(payload) {
    if (!payload || typeof payload !== "object") return void 0;
    const overflow = typeof payload.last_oversized_host_message === "object" && payload.last_oversized_host_message ? payload.last_oversized_host_message : payload;
    return {
      kind: typeof overflow.kind === "string" ? overflow.kind : "oversized-host-outbound",
      artifact_path: typeof overflow.artifact_path === "string" ? overflow.artifact_path : void 0,
      original_type: typeof overflow.original_type === "string" ? overflow.original_type : void 0,
      message_size_bytes: typeof overflow.message_size_bytes === "number" ? overflow.message_size_bytes : void 0,
      limit_bytes: typeof overflow.limit_bytes === "number" ? overflow.limit_bytes : void 0,
      captured_at: typeof overflow.captured_at === "string" ? overflow.captured_at : void 0,
      request_id: typeof overflow.request_id === "string" ? overflow.request_id : void 0,
      tab_id: typeof overflow.tab_id === "number" ? overflow.tab_id : void 0,
      emitted_at: typeof overflow.emitted_at === "string" ? overflow.emitted_at : void 0
    };
  }
  function nativeOverflowInventoryDigestFromPayload(payload) {
    if (!payload || typeof payload !== "object") return void 0;
    const inventory = typeof payload.overflow_inventory === "object" && payload.overflow_inventory ? payload.overflow_inventory : payload;
    const recentArtifactsRaw = Array.isArray(inventory.recent_artifacts) ? inventory.recent_artifacts : [];
    return {
      latest_path: typeof inventory.latest_path === "string" ? inventory.latest_path : void 0,
      latest_exists: typeof inventory.latest_exists === "boolean" ? inventory.latest_exists : void 0,
      artifact_count: typeof inventory.artifact_count === "number" ? inventory.artifact_count : void 0,
      total_disk_bytes: typeof inventory.total_disk_bytes === "number" ? inventory.total_disk_bytes : void 0,
      total_reported_message_bytes: typeof inventory.total_reported_message_bytes === "number" ? inventory.total_reported_message_bytes : void 0,
      message_type_counts: typeof inventory.message_type_counts === "object" && inventory.message_type_counts ? inventory.message_type_counts : void 0,
      newest_captured_at: typeof inventory.newest_captured_at === "string" ? inventory.newest_captured_at : void 0,
      oldest_captured_at: typeof inventory.oldest_captured_at === "string" ? inventory.oldest_captured_at : void 0,
      latest_artifact_path: typeof inventory.latest_artifact_path === "string" ? inventory.latest_artifact_path : void 0,
      latest_artifact_exists: typeof inventory.latest_artifact_exists === "boolean" ? inventory.latest_artifact_exists : void 0,
      latest_artifact_in_inventory: typeof inventory.latest_artifact_in_inventory === "boolean" ? inventory.latest_artifact_in_inventory : void 0,
      recent_limit: typeof inventory.recent_limit === "number" ? inventory.recent_limit : void 0,
      recent_artifacts: recentArtifactsRaw.map((entry) => {
        const item = typeof entry === "object" && entry ? entry : {};
        return {
          path: typeof item.path === "string" ? item.path : void 0,
          name: typeof item.name === "string" ? item.name : void 0,
          captured_at: typeof item.captured_at === "string" ? item.captured_at : void 0,
          message_type: typeof item.message_type === "string" ? item.message_type : void 0,
          request_id: typeof item.request_id === "string" ? item.request_id : void 0,
          tab_id: typeof item.tab_id === "number" ? item.tab_id : void 0,
          reported_size_bytes: typeof item.reported_size_bytes === "number" ? item.reported_size_bytes : void 0,
          size_on_disk_bytes: typeof item.size_on_disk_bytes === "number" ? item.size_on_disk_bytes : void 0,
          parse_ok: typeof item.parse_ok === "boolean" ? item.parse_ok : void 0
        };
      })
    };
  }
  function nativeStatusSnapshotFromPayload(payload, trigger, capturedAt, persistentHostIdentity) {
    const hostIdentity = nativeHostIdentityFromRecord(typeof payload?.host_identity === "object" && payload?.host_identity ? payload.host_identity : void 0);
    return {
      capturedAt,
      trigger,
      native_host: typeof payload?.native_host === "string" ? payload.native_host : void 0,
      socket_path: typeof payload?.socket_path === "string" ? payload.socket_path : void 0,
      state_root: typeof payload?.state_root === "string" ? payload.state_root : void 0,
      events_path: typeof payload?.events_path === "string" ? payload.events_path : void 0,
      event_count: typeof payload?.event_count === "number" ? payload.event_count : void 0,
      latest_dir: typeof payload?.latest_dir === "string" ? payload.latest_dir : void 0,
      fixtures_dir: typeof payload?.fixtures_dir === "string" ? payload.fixtures_dir : void 0,
      run_dir: typeof payload?.run_dir === "string" ? payload.run_dir : void 0,
      host_identity: hostIdentity,
      broker: nativeBrokerSummaryFromPayload(payload),
      matches_persistent_host: nativeHostIdentitiesMatch(hostIdentity, persistentHostIdentity),
      last_oversized_host_message: nativeOverflowSummaryFromPayload(payload),
      overflow_inventory: nativeOverflowInventoryDigestFromPayload(payload)
    };
  }
  function nativeStatusSnapshotIsStale(state, maxAgeMs = 15e3) {
    const capturedAt = state.lastNativeStatusSnapshot?.capturedAt ? Date.parse(state.lastNativeStatusSnapshot.capturedAt) : Number.NaN;
    return !Number.isFinite(capturedAt) || Date.now() - capturedAt > maxAgeMs;
  }
  async function requestNativeStatusOneShot(trigger) {
    const requestId = `status-${Date.now()}`;
    const capturedAt = (/* @__PURE__ */ new Date()).toISOString();
    await appendTrace("native.status_snapshot_requested", { requestId, trigger }).catch(console.error);
    try {
      const response = await chrome.runtime.sendNativeMessage(HOST_NAME, makeEnvelope("bridge.status", { requestId, trigger, sentAt: capturedAt, broker_intent: "secondary_only" }));
      const payload = typeof response === "object" && response && "payload" in response ? response.payload : void 0;
      const stateBeforePatch = await getBridgeState();
      const snapshot = nativeStatusSnapshotFromPayload(payload ?? null, trigger, capturedAt, stateBeforePatch.nativeConnection?.persistentHostIdentity);
      await patchBridgeState({
        lastNativeStatusSnapshot: snapshot,
        lastNativeStatusError: void 0,
        lastOversizedHostMessage: snapshot.last_oversized_host_message ?? stateBeforePatch.lastOversizedHostMessage
      });
      await recordPersistentNativeEvent("native.oneshot_reachable", { trigger, at: capturedAt, nativeHost: snapshot.native_host, socketPath: snapshot.socket_path });
      await appendTrace("native.status_snapshot_result", {
        requestId,
        trigger,
        nativeHost: snapshot.native_host ?? null,
        brokerRole: snapshot.broker?.role ?? null,
        matchesPersistentHost: snapshot.matches_persistent_host ?? null,
        artifactCount: snapshot.overflow_inventory?.artifact_count ?? null
      }).catch(console.error);
      return snapshot;
    } catch (error) {
      const failure = errorMessage(error);
      await patchBridgeState({ lastNativeStatusError: failure });
      await appendTrace("native.status_snapshot_failed", { requestId, trigger, error: failure }, "warn").catch(console.error);
      return void 0;
    }
  }
  async function requestNativeHealthOneShot(trigger) {
    const requestId = `oneshot-${Date.now()}`;
    const startedAt = Date.now();
    const sentAt = new Date(startedAt).toISOString();
    await patchNativeConnection({
      lastOneShotProbeAt: sentAt,
      lastOneShotProbeRequestId: requestId,
      lastOneShotProbeTrigger: trigger,
      lastOneShotProbeOk: false,
      lastOneShotProbeError: void 0
    });
    await appendTrace("native.oneshot_probe", { requestId, trigger }).catch(console.error);
    try {
      const response = await chrome.runtime.sendNativeMessage(HOST_NAME, makeEnvelope("health.ping", { requestId, trigger, sentAt, broker_intent: "secondary_only" }));
      const payload = typeof response === "object" && response && "payload" in response ? response.payload : void 0;
      const host = typeof payload?.native_host === "string" ? payload.native_host : void 0;
      const socketPath = typeof payload?.socket_path === "string" ? payload.socket_path : void 0;
      const hostIdentity = nativeHostIdentityFromRecord(typeof payload?.host_identity === "object" && payload?.host_identity ? payload.host_identity : void 0);
      const broker = nativeBrokerSummaryFromPayload(payload ?? null);
      const ok = payload?.ok !== false;
      await patchNativeConnection({
        lastOneShotProbeAt: sentAt,
        lastOneShotProbeRequestId: requestId,
        lastOneShotProbeTrigger: trigger,
        lastOneShotProbeOk: ok,
        lastOneShotProbeError: ok ? void 0 : "native host response did not confirm ok=true",
        lastOneShotProbeRoundTripMs: Date.now() - startedAt,
        lastOneShotProbeHost: host,
        lastOneShotProbeSocketPath: socketPath,
        lastOneShotProbeHostIdentity: hostIdentity,
        lastOneShotProbeBroker: broker,
        nativeHost: host,
        socketPath
      });
      await appendTrace("native.oneshot_probe_result", { requestId, trigger, ok, host: host ?? null, socketPath: socketPath ?? null, brokerRole: broker?.role ?? null }).catch(console.error);
      if (ok) {
        await recordPersistentNativeEvent("native.oneshot_reachable", { trigger, at: sentAt, nativeHost: host, socketPath });
      }
      return ok;
    } catch (error) {
      await patchNativeConnection({
        lastOneShotProbeAt: sentAt,
        lastOneShotProbeRequestId: requestId,
        lastOneShotProbeTrigger: trigger,
        lastOneShotProbeOk: false,
        lastOneShotProbeError: errorMessage(error),
        lastOneShotProbeRoundTripMs: Date.now() - startedAt
      });
      await appendTrace("native.oneshot_probe_failed", { requestId, trigger, error: errorMessage(error) }, "warn").catch(console.error);
      return false;
    }
  }
  async function resumeNativeConnectionLane(trigger) {
    const state = await getBridgeState();
    const nativeConnection = state.nativeConnection ?? defaultNativeConnectionState();
    const scheduledFor = nativeConnection.reconnectScheduledFor ? Date.parse(nativeConnection.reconnectScheduledFor) : Number.NaN;
    const reconnectAlarm = await chrome.alarms.get(NATIVE_RECONNECT_ALARM).catch(() => void 0);
    if (nativeConnection.connected || !nativeConnection.reconnectScheduledFor) {
      await attemptNativeReconnect(trigger, `runtime.${trigger}`);
      return;
    }
    if (Number.isFinite(scheduledFor) && scheduledFor <= Date.now()) {
      await attemptNativeReconnect("alarm", `runtime.${trigger}.scheduled_due`);
      return;
    }
    if (reconnectAlarm) {
      await appendTrace("native.reconnect_alarm_preserved", { trigger, reconnectAlarm }, "warn");
      return;
    }
    const minutesUntil = Number.isFinite(scheduledFor) ? Math.max(NATIVE_RECONNECT_MINUTES, (scheduledFor - Date.now()) / 6e4) : nativeConnection.reconnectDelayMinutes ?? NATIVE_RECONNECT_MINUTES;
    await chrome.alarms.create(NATIVE_RECONNECT_ALARM, { delayInMinutes: minutesUntil });
    await appendTrace("native.reconnect_alarm_restored", { trigger, minutesUntil, scheduledFor: nativeConnection.reconnectScheduledFor }, "warn");
  }
  async function hardenStorageAccess() {
    try {
      await chrome.storage.local.setAccessLevel({ accessLevel: "TRUSTED_CONTEXTS" });
      await chrome.storage.session.setAccessLevel({ accessLevel: "TRUSTED_CONTEXTS" });
    } catch (error) {
      log("storage access hardening failed", error);
      await appendTrace("storage.hardening_failed", { error: errorMessage(error) }, "warn");
      return;
    }
    await appendTrace("storage.hardened");
  }
  async function getPersistentBridgeHistory() {
    const result = await chrome.storage.local.get(PERSISTENT_HISTORY_KEY);
    return normalizePersistentBridgeHistory(result[PERSISTENT_HISTORY_KEY]);
  }
  async function setPersistentBridgeHistory(next) {
    await chrome.storage.local.set({ [PERSISTENT_HISTORY_KEY]: next });
    return next;
  }
  async function updatePersistentBridgeHistory(mutator) {
    const current = await getPersistentBridgeHistory();
    return setPersistentBridgeHistory(mutator(current));
  }
  async function persistentDiagnosticsSnapshot(state) {
    const resolved = state ?? await getBridgeState();
    const rawHistory = (await chrome.storage.local.get(PERSISTENT_HISTORY_KEY))[PERSISTENT_HISTORY_KEY];
    return buildPersistentDiagnosticsSnapshot(rawHistory, resolved.runtime ?? defaultRuntimeLaneState(), resolved.nativeConnection?.laneDiagnosis);
  }
  async function bridgeStateWithPersistentDiagnostics(state) {
    const resolved = state ?? await getBridgeState();
    return { ...resolved, persistentDiagnostics: await persistentDiagnosticsSnapshot(resolved) };
  }
  function persistentEventHostIdentity(state) {
    return state.nativeConnection?.persistentHostIdentity ?? state.nativeConnection?.lastOneShotProbeHostIdentity ?? state.lastNativeStatusSnapshot?.host_identity;
  }
  async function recordPersistentNativeEvent(kind, extras = {}) {
    const state = await getBridgeState();
    const diagnosis = state.nativeConnection?.laneDiagnosis;
    const hostIdentity = persistentEventHostIdentity(state);
    const at = extras.at ?? (/* @__PURE__ */ new Date()).toISOString();
    await updatePersistentBridgeHistory((current) => appendPersistentNativeEvent(current, {
      at,
      bootId: state.runtime?.currentBootId ?? WORKER_BOOT_ID,
      kind,
      ...extras.trigger ? { trigger: extras.trigger } : {},
      ...extras.reason ? { reason: extras.reason } : {},
      ...diagnosis?.status ? { diagnosisStatus: diagnosis.status } : {},
      ...diagnosis?.summary ? { diagnosisSummary: diagnosis.summary } : {},
      ...state.nativeConnection?.persistentBroker?.role ? { persistentBrokerRole: state.nativeConnection.persistentBroker.role } : {},
      ...state.nativeConnection?.lastOneShotProbeBroker?.role ? { oneShotBrokerRole: state.nativeConnection.lastOneShotProbeBroker.role } : {},
      ...state.lastNativeStatusSnapshot?.broker?.role ? { snapshotBrokerRole: state.lastNativeStatusSnapshot.broker.role } : {},
      ...extras.nativeHost ?? state.nativeConnection?.nativeHost ?? state.lastNativeStatusSnapshot?.native_host ? { nativeHost: extras.nativeHost ?? state.nativeConnection?.nativeHost ?? state.lastNativeStatusSnapshot?.native_host } : {},
      ...extras.socketPath ?? state.nativeConnection?.socketPath ?? state.lastNativeStatusSnapshot?.socket_path ? { socketPath: extras.socketPath ?? state.nativeConnection?.socketPath ?? state.lastNativeStatusSnapshot?.socket_path } : {},
      ...hostIdentity?.boot_id ? { hostBootId: hostIdentity.boot_id } : {},
      ...typeof hostIdentity?.pid === "number" ? { hostPid: hostIdentity.pid } : {}
    }));
  }
  async function getSupportedTabs() {
    const result = await chrome.storage.session.get(SESSION_TABS_KEY);
    return result[SESSION_TABS_KEY] ?? [];
  }
  async function setSupportedTabs(next) {
    await chrome.storage.session.set({ [SESSION_TABS_KEY]: next });
  }
  async function getPrimedReceivers() {
    const result = await chrome.storage.session.get(SESSION_PRIMED_RECEIVERS_KEY);
    return result[SESSION_PRIMED_RECEIVERS_KEY] ?? {};
  }
  async function primedReceiverKeysForTab(tabId) {
    const state = await getPrimedReceivers();
    return Array.isArray(state[String(tabId)]) ? state[String(tabId)] : [];
  }
  async function rememberPrimedReceiverKeys(tabId, keys) {
    const normalizedTabId = String(tabId);
    const state = await getPrimedReceivers();
    const nextKeys = mergePrimedReceiverKeys(state[normalizedTabId] || [], keys);
    await chrome.storage.session.set({
      [SESSION_PRIMED_RECEIVERS_KEY]: {
        ...state,
        [normalizedTabId]: nextKeys
      }
    });
    return nextKeys;
  }
  async function forgetPrimedReceiverKeys(tabId) {
    const normalizedTabId = String(tabId);
    const state = await getPrimedReceivers();
    if (!(normalizedTabId in state)) return;
    const next = { ...state };
    delete next[normalizedTabId];
    await chrome.storage.session.set({ [SESSION_PRIMED_RECEIVERS_KEY]: next });
  }
  async function getTraceEntries() {
    const result = await chrome.storage.session.get(TRACE_KEY);
    return result[TRACE_KEY] ?? [];
  }
  async function appendTrace(kind, data, level = "info") {
    const entry = { at: (/* @__PURE__ */ new Date()).toISOString(), kind, level, ...data === void 0 ? {} : { data } };
    const next = [...await getTraceEntries(), entry].slice(-TRACE_LIMIT);
    await chrome.storage.session.set({ [TRACE_KEY]: next });
    return next;
  }
  async function recentTrace(limit = 40) {
    const entries = await getTraceEntries();
    return entries.slice(Math.max(0, entries.length - Math.max(1, limit)));
  }
  async function rememberSupportedTab(patch) {
    const existing = await getSupportedTabs();
    const current = existing.find((tab) => tab.tabId === patch.tabId);
    const merged = summarizeSupportedTabReceivers({
      ...current || {},
      ...patch,
      receivers: patch.receivers ?? current?.receivers,
      lastSeenAt: patch.lastSeenAt || current?.lastSeenAt || (/* @__PURE__ */ new Date()).toISOString()
    });
    const without = existing.filter((tab) => tab.tabId !== patch.tabId);
    const next = [merged, ...without].slice(0, 12);
    await setSupportedTabs(next);
    return next;
  }
  function summarizeSupportedTabReceivers(tab) {
    const summary = summarizeContentReceivers(tab.receivers || [], { overrideKey: tab.receiverOverrideKey });
    const preferred = preferredContentReceiver(tab.receivers || [], { overrideKey: tab.receiverOverrideKey });
    return {
      ...tab,
      ...preferred?.documentId ? { documentId: preferred.documentId } : {},
      ...typeof preferred?.frameId === "number" ? { frameId: preferred.frameId } : {},
      ...preferred?.documentLifecycle ? { documentLifecycle: preferred.documentLifecycle } : {},
      ...typeof preferred?.receiverReady === "boolean" ? { receiverReady: preferred.receiverReady } : {},
      receiverCount: summary.receiverCount,
      readyReceiverCount: summary.readyReceiverCount,
      receiverFrameIds: summary.receiverFrameIds,
      receiverDocumentIds: summary.receiverDocumentIds,
      receiverSelectionPolicy: summary.receiverSelectionPolicy,
      receiverInventoryStatus: summary.receiverInventoryStatus,
      receiverTopFrameReady: summary.receiverTopFrameReady,
      receiverOverrideStatus: summary.receiverOverrideStatus,
      selectedReceiverKey: summary.selectedReceiverKey,
      selectedReceiverLabel: summary.selectedReceiverLabel
    };
  }
  async function receiverCoverageAuditForTab(tab, manifestPolicy) {
    if (!tab?.tabId) return void 0;
    let frames;
    try {
      frames = await chrome.webNavigation.getAllFrames({ tabId: tab.tabId });
    } catch (error) {
      await appendTrace("receivers.coverage_inventory_failed", { tabId: tab.tabId, error: errorMessage(error) }, "warn");
      return void 0;
    }
    const primingAudit = describeReceiverPrimingAudit(frames || [], {
      existingReceivers: tab.receivers || [],
      primedKeys: await primedReceiverKeysForTab(tab.tabId),
      isSupportedUrl
    });
    const effectivePolicy = manifestPolicy ?? await contentScriptPolicySummary();
    return {
      frameCount: primingAudit.counts.frameCount,
      supportedUrlCount: primingAudit.counts.supportedUrlCount,
      relatedFrameUrlCount: primingAudit.counts.relatedFrameUrlCount,
      observedCount: primingAudit.counts.observedCount,
      primedCount: primingAudit.counts.primedCount,
      topFrameCount: primingAudit.counts.topFrameCount,
      candidateCount: primingAudit.counts.candidateCount,
      candidateDocumentCount: primingAudit.counts.candidateDocumentCount,
      candidateFrameCount: primingAudit.counts.candidateFrameCount,
      gapCount: primingAudit.counts.gapCount,
      skippedReasonCounts: primingAudit.counts.skippedReasonCounts,
      plan: primingAudit.plan,
      frames: primingAudit.frames,
      policyHints: { ...describeReceiverCoveragePolicyHints(primingAudit, effectivePolicy), manifestPolicy: effectivePolicy },
      experimentPlan: describeReceiverCoverageExperimentPlan(primingAudit, effectivePolicy)
    };
  }
  async function receiverAuditForTab(tab, state, manifestPolicy) {
    if (!tab) return void 0;
    const summarized = summarizeSupportedTabReceivers(tab);
    const resolverAudit = describeContentReceiverAudit(summarized.receivers || [], { overrideKey: summarized.receiverOverrideKey });
    const coverageAudit = await receiverCoverageAuditForTab(summarized, manifestPolicy);
    return {
      targetTabId: summarized.tabId,
      targetTabTitle: summarized.title,
      targetTabUrl: summarized.url,
      selectedTargetTabId: state?.selectedTargetTabId ?? null,
      receiverCount: summarized.receiverCount ?? 0,
      readyReceiverCount: summarized.readyReceiverCount ?? 0,
      receiverSelectionPolicy: summarized.receiverSelectionPolicy ?? "none",
      receiverInventoryStatus: summarized.receiverInventoryStatus ?? "none",
      receiverOverrideKey: summarized.receiverOverrideKey ?? null,
      receiverOverrideStatus: summarized.receiverOverrideStatus ?? "none",
      selectedReceiverKey: summarized.selectedReceiverKey,
      selectedReceiverLabel: summarized.selectedReceiverLabel,
      resolverPolicy: resolverAudit.resolverPolicy,
      receiverResolution: resolverAudit.receiverResolution,
      rankedMatches: resolverAudit.rankedMatches,
      coverageAudit,
      receivers: (summarized.receivers || []).map((receiver) => ({
        key: contentReceiverKey(receiver),
        label: contentReceiverLabel(receiver),
        frameId: receiver.frameId,
        documentId: receiver.documentId,
        adapter: receiver.adapter,
        documentLifecycle: receiver.documentLifecycle,
        frameType: receiver.frameType,
        parentFrameId: receiver.parentFrameId,
        parentDocumentId: receiver.parentDocumentId,
        frameUrl: receiver.frameUrl,
        frameOrigin: receiver.frameOrigin,
        frameDepth: receiver.frameDepth,
        framePathFrameIds: receiver.framePathFrameIds,
        framePathHosts: receiver.framePathHosts,
        framePathLabel: receiver.framePathLabel,
        receiverReady: receiver.receiverReady,
        lastSeenAt: receiver.lastSeenAt
      }))
    };
  }
  function receiverAuditTarget(state) {
    const selectedId = state.selectedTargetTabId;
    if (typeof selectedId === "number") {
      const selected = state.supportedTabs?.find((tab) => tab.tabId === selectedId);
      if (selected) return selected;
    }
    if (state.targetTab) return state.targetTab;
    if ((state.supportedTabs?.length ?? 0) === 1) return state.supportedTabs?.[0];
    return void 0;
  }
  async function forgetSupportedTab(tabId) {
    const next = (await getSupportedTabs()).filter((tab) => tab.tabId !== tabId);
    await setSupportedTabs(next);
    const state = await getBridgeState();
    if (state.selectedTargetTabId === tabId) {
      await patchBridgeState({ selectedTargetTabId: null, targetTab: null });
    }
    return next;
  }
  async function getBridgeState() {
    const result = await chrome.storage.session.get(STORAGE_KEY);
    return result[STORAGE_KEY] ?? {
      adapters: adapterDescriptors(),
      selectedTargetTabId: null,
      nativeConnection: defaultNativeConnectionState(),
      runtime: defaultRuntimeLaneState()
    };
  }
  async function patchBridgeState(patch) {
    const next = {
      ...await getBridgeState(),
      adapters: adapterDescriptors(),
      ...patch,
      updatedAt: (/* @__PURE__ */ new Date()).toISOString()
    };
    const resolvedNativeConnection = {
      ...defaultNativeConnectionState(),
      ...next.nativeConnection ?? {}
    };
    const nextWithDiagnosis = {
      ...next,
      nativeConnection: {
        ...resolvedNativeConnection,
        laneDiagnosis: deriveNativeLaneDiagnosis({
          nativeConnection: resolvedNativeConnection,
          lastNativeStatusSnapshot: next.lastNativeStatusSnapshot,
          lastNativeStatusError: next.lastNativeStatusError
        })
      }
    };
    await chrome.storage.session.set({ [STORAGE_KEY]: nextWithDiagnosis });
    return nextWithDiagnosis;
  }
  async function attemptNativeReconnect(trigger, reason) {
    try {
      ensureNativePort();
      await appendTrace(`native.reconnect_${trigger}_succeeded`, { reason });
      await recordPersistentNativeEvent("native.reconnect_succeeded", { trigger, reason });
      return true;
    } catch (error) {
      const nextAttempt = ((await getBridgeState()).nativeConnection?.reconnectAttempt ?? 0) + 1;
      const failureReason = errorMessage(error);
      await appendTrace(`native.reconnect_${trigger}_failed`, { reason, error: failureReason, attempt: nextAttempt }, "warn");
      await scheduleNativeReconnect(reason, nextAttempt);
      await recordPersistentNativeEvent("native.reconnect_failed", { trigger, reason: failureReason });
      return false;
    }
  }
  function messageTargetOptions(tab, state) {
    if (!tab.id) return void 0;
    const receiverTarget = messageTargetForReceivers(state?.receivers || [], { overrideKey: state?.receiverOverrideKey });
    if (receiverTarget?.documentId) return { documentId: receiverTarget.documentId };
    if (typeof receiverTarget?.frameId === "number") return { frameId: receiverTarget.frameId };
    if (state?.documentId) {
      return { documentId: state.documentId };
    }
    if (typeof state?.frameId === "number" && state.frameId >= 0) {
      return { frameId: state.frameId };
    }
    return void 0;
  }
  function isMissingReceiverError(error) {
    const message = String(error ?? "");
    return message.includes("Receiving end does not exist") || message.includes("Could not establish connection");
  }
  async function syncActionForTab(tab, state) {
    if (!tab?.id) return;
    const tabId = tab.id;
    const supported = isSupportedUrl(tab.url);
    let text = "";
    let color = "#5b6475";
    let title = "GlassTTY";
    if (!supported) {
      title = "GlassTTY: unsupported tab";
    } else if (tab.discarded) {
      text = "DISC";
      color = "#8b5a2b";
      title = "GlassTTY: supported tab is discarded and must be activated before messaging";
    } else if (tab.frozen) {
      text = "FRZ";
      color = "#6b46c1";
      title = "GlassTTY: supported tab is frozen and may not process messages until activated";
    } else if (state.selectedTargetTabId === tabId) {
      text = "TGT";
      color = "#1f6feb";
      title = "GlassTTY: selected target tab";
    } else {
      text = "OK";
      color = "#2f855a";
      title = "GlassTTY: supported tab observed";
    }
    await chrome.action.setBadgeBackgroundColor({ tabId, color }).catch(console.error);
    await chrome.action.setBadgeText({ tabId, text }).catch(console.error);
    await chrome.action.setTitle({ tabId, title }).catch(console.error);
  }
  async function tryInjectContentScript(tab, state) {
    if (!tab.id || !isSupportedUrl(tab.url)) return { ok: false, reason: "unsupported tab" };
    if (tab.discarded || state?.discarded) return { ok: false, reason: "tab is discarded" };
    if (tab.frozen || state?.frozen) return { ok: false, reason: "tab is frozen" };
    const target = { tabId: tab.id };
    const preferred = preferredContentReceiver(state?.receivers || [], { overrideKey: state?.receiverOverrideKey });
    if (preferred?.documentId) {
      target.documentIds = [preferred.documentId];
    } else if (typeof preferred?.frameId === "number" && preferred.frameId >= 0) {
      target.frameIds = [preferred.frameId];
    } else if (state?.documentId) {
      target.documentIds = [state.documentId];
    } else if (typeof state?.frameId === "number" && state.frameId >= 0) {
      target.frameIds = [state.frameId];
    }
    try {
      await chrome.scripting.executeScript({ target, files: ["dist/content/main.js"] });
      await appendTrace("content.reinject_succeeded", { tabId: tab.id, documentIds: target.documentIds, frameIds: target.frameIds });
      return { ok: true, injected: true };
    } catch (error) {
      await appendTrace("content.reinject_failed", { tabId: tab.id, error: errorMessage(error), documentIds: target.documentIds, frameIds: target.frameIds }, "warn");
      return { ok: false, reason: String(error) };
    }
  }
  async function selectedTargetTab() {
    const state = await getBridgeState();
    if (!state.selectedTargetTabId) return void 0;
    const tab = await getTabById(state.selectedTargetTabId);
    if (tab?.id && isSupportedUrl(tab.url)) return tab;
    await patchBridgeState({ selectedTargetTabId: null, targetTab: null });
    return void 0;
  }
  async function setSelectedTargetTab(tabId, hint) {
    if (!tabId) {
      return patchBridgeState({ selectedTargetTabId: null, targetTab: null });
    }
    const tab = hint?.id === tabId ? hint : await getTabById(tabId);
    if (!tab?.id || !isSupportedUrl(tab.url)) {
      throw new Error(`tab ${tabId} is not a supported GlassTTY tab`);
    }
    const supportedTabs = await rememberSupportedTab({
      tabId: tab.id,
      windowId: tab.windowId,
      url: tab.url,
      title: tab.title,
      lastSeenAt: (/* @__PURE__ */ new Date()).toISOString()
    });
    return patchBridgeState({
      supportedTabs,
      selectedTargetTabId: tab.id,
      targetTab: supportedTabs.find((entry) => entry.tabId === tab.id) ?? {
        tabId: tab.id,
        windowId: tab.windowId,
        url: tab.url,
        title: tab.title,
        lastSeenAt: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
  }
  async function setReceiverOverride(tabId, receiverKey) {
    const supportedTabs = await getSupportedTabs();
    const current = supportedTabs.find((entry) => entry.tabId === tabId);
    if (!current) {
      throw new Error(`tab ${tabId} has no observed GlassTTY receiver inventory`);
    }
    const nextTabs = await rememberSupportedTab({
      ...current,
      receiverOverrideKey: receiverKey,
      lastSeenAt: (/* @__PURE__ */ new Date()).toISOString()
    });
    const state = await getBridgeState();
    return patchBridgeState({
      supportedTabs: nextTabs,
      targetTab: state.selectedTargetTabId === tabId ? nextTabs.find((entry) => entry.tabId === tabId) ?? current : state.targetTab
    });
  }
  async function resolveTargetTab() {
    const pinned = await selectedTargetTab();
    if (pinned?.id) return pinned;
    const active = await getActiveTab();
    if (active?.id && isSupportedUrl(active.url)) return active;
    const supported = await getSupportedTabs();
    for (const entry of supported) {
      const tab = await getTabById(entry.tabId);
      if (tab?.id && isSupportedUrl(tab.url)) return tab;
    }
    return void 0;
  }
  async function chooseTargetTab(request) {
    const explicit = await getTabById(request?.tab_id);
    if (explicit?.id && isSupportedUrl(explicit.url)) return explicit;
    return resolveTargetTab();
  }
  async function syncSidePanelForTab(tab) {
    if (!tab?.id) return;
    const enabled = isSupportedUrl(tab.url);
    await chrome.sidePanel.setOptions({
      tabId: tab.id,
      path: "sidepanel/index.html",
      enabled
    }).catch(console.error);
  }
  async function refreshActiveTabState() {
    const tab = await getActiveTab();
    await syncSidePanelForTab(tab);
    const supportedTabs = await getSupportedTabs();
    const state = await getBridgeState();
    const targetTab = await resolveTargetTab();
    const nextState = await patchBridgeState({
      activeTab: {
        id: tab?.id,
        url: tab?.url,
        windowId: tab?.windowId,
        supported: isSupportedUrl(tab?.url),
        discarded: tab?.discarded,
        frozen: tab?.frozen
      },
      selectedTargetTabId: state.selectedTargetTabId ?? null,
      targetTab: targetTab?.id ? supportedTabs.find((entry) => entry.tabId === targetTab.id) ?? {
        tabId: targetTab.id,
        windowId: targetTab.windowId,
        url: targetTab.url,
        title: targetTab.title,
        discarded: targetTab.discarded,
        frozen: targetTab.frozen,
        lastSeenAt: (/* @__PURE__ */ new Date()).toISOString()
      } : null,
      supportedTabs
    });
    await syncActionForTab(tab, nextState);
    if (targetTab?.id && targetTab.id !== tab?.id) {
      await syncActionForTab(targetTab, nextState);
    }
  }
  async function recordTabObservation(tab, details = {}) {
    if (!tab?.id || !isSupportedUrl(tab.url)) return;
    const existing = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
    const observedAt = (/* @__PURE__ */ new Date()).toISOString();
    const shouldMergeReceiver = [details.documentId, details.frameId, details.documentLifecycle, details.adapter].some((value) => value !== void 0) || typeof details.receiverReady === "boolean";
    const mergedReceivers = shouldMergeReceiver ? mergeContentReceivers(existing?.receivers || [], {
      documentId: details.documentId,
      frameId: details.frameId,
      documentLifecycle: details.documentLifecycle,
      adapter: details.adapter,
      receiverReady: details.receiverReady,
      lastSeenAt: observedAt
    }) : existing?.receivers || [];
    const receivers = await enrichReceiversWithFrameContext(tab.id, mergedReceivers);
    const nextTab = summarizeSupportedTabReceivers({
      tabId: tab.id,
      windowId: tab.windowId,
      url: tab.url,
      title: tab.title,
      documentId: details.documentId ?? existing?.documentId,
      frameId: typeof details.frameId === "number" ? details.frameId : existing?.frameId,
      documentLifecycle: details.documentLifecycle ?? existing?.documentLifecycle,
      discarded: details.discarded ?? tab.discarded ?? existing?.discarded,
      frozen: details.frozen ?? tab.frozen ?? existing?.frozen,
      receiverReady: details.receiverReady ?? existing?.receiverReady,
      adapter: details.adapter ?? existing?.adapter,
      receiverOverrideKey: details.receiverOverrideKey ?? existing?.receiverOverrideKey,
      receivers,
      lastSeenAt: observedAt
    });
    const supportedTabs = await rememberSupportedTab(nextTab);
    await patchBridgeState({ supportedTabs });
  }
  async function recordSenderObservation(sender, message) {
    const senderTab = sender.tab;
    if (!senderTab?.id || !isSupportedUrl(senderTab.url)) return;
    await recordTabObservation(senderTab, {
      adapter: message.type === "adapter.detected" ? String(message.payload?.adapter ?? "") : void 0,
      documentId: sender.documentId,
      frameId: sender.frameId,
      documentLifecycle: sender.documentLifecycle,
      receiverReady: true
    });
    const observed = (await getSupportedTabs()).find((entry) => entry.tabId === senderTab.id);
    await appendTrace("content.sender_observed", { tabId: senderTab.id, messageType: message.type, documentId: sender.documentId, frameId: sender.frameId, documentLifecycle: sender.documentLifecycle, receiverCount: observed?.receiverCount, receiverInventoryStatus: observed?.receiverInventoryStatus, receiverSelectionPolicy: observed?.receiverSelectionPolicy, receiverOverrideStatus: observed?.receiverOverrideStatus, selectedReceiverKey: observed?.selectedReceiverKey });
    await primeSupportedSubframeReceivers(senderTab, observed);
  }
  async function annotateResponseWithReceiver(request, response, tab, knownState) {
    const selected = preferredContentReceiver(knownState?.receivers || [], { overrideKey: knownState?.receiverOverrideKey });
    const resolverAudit = describeContentReceiverAudit(knownState?.receivers || [], { overrideKey: knownState?.receiverOverrideKey });
    const coverageAudit = await receiverCoverageAuditForTab(knownState, await contentScriptPolicySummary());
    const selectedKey = selected ? contentReceiverKey(selected) : void 0;
    if (request.type !== "fixture.capture" || response.type !== "fixture.capture") {
      return response;
    }
    const payload = typeof response.payload === "object" && response.payload ? { ...response.payload } : {};
    const metadata = typeof payload.metadata === "object" && payload.metadata ? { ...payload.metadata } : {};
    metadata.receiver_target_policy = knownState?.receiverSelectionPolicy ?? "none";
    metadata.receiver_override_status = knownState?.receiverOverrideStatus ?? "none";
    metadata.receiver_target_key = selectedKey ?? null;
    metadata.receiver_target_label = selected ? contentReceiverLabel(selected) : null;
    metadata.receiver_target_frame_id = typeof selected?.frameId === "number" ? selected.frameId : null;
    metadata.receiver_target_document_id = selected?.documentId ?? null;
    metadata.receiver_target_frame_type = selected?.frameType ?? null;
    metadata.receiver_target_frame_url = selected?.frameUrl ?? null;
    metadata.receiver_target_frame_origin = selected?.frameOrigin ?? null;
    metadata.receiver_target_parent_frame_id = typeof selected?.parentFrameId === "number" ? selected.parentFrameId : null;
    metadata.receiver_target_frame_depth = typeof selected?.frameDepth === "number" ? selected.frameDepth : null;
    metadata.receiver_target_frame_path_frame_ids = Array.isArray(selected?.framePathFrameIds) ? selected?.framePathFrameIds : null;
    metadata.receiver_target_frame_path_hosts = Array.isArray(selected?.framePathHosts) ? selected?.framePathHosts : null;
    metadata.receiver_target_frame_path_label = selected?.framePathLabel ?? null;
    metadata.receiver_inventory_status = knownState?.receiverInventoryStatus ?? "none";
    metadata.receiver_resolver_policy = resolverAudit.resolverPolicy;
    metadata.receiver_resolution = resolverAudit.receiverResolution ?? null;
    metadata.receiver_ranked_matches = resolverAudit.rankedMatches;
    metadata.receiver_coverage_audit = coverageAudit ?? null;
    metadata.receiver_coverage_policy_hints = coverageAudit?.policyHints ?? null;
    metadata.receiver_coverage_experiment_plan = coverageAudit?.experimentPlan ?? null;
    metadata.receiver_coverage_gaps = coverageAudit?.frames.filter((frame) => ["candidate_document", "candidate_frame", "related_frame_url", "missing_target"].includes(frame.status)) ?? [];
    payload.metadata = metadata;
    return { ...response, payload };
  }
  async function sendToContentScript(tab, request) {
    const knownState = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
    const payload = { ...request, tab_id: tab.id };
    const targetOptions = messageTargetOptions(tab, knownState);
    await appendTrace("content.send_attempt", { requestType: request.type, tabId: tab.id, documentId: knownState?.documentId, frameId: knownState?.frameId, receiverCount: knownState?.receiverCount, receiverSelectionPolicy: knownState?.receiverSelectionPolicy, receiverOverrideStatus: knownState?.receiverOverrideStatus, receiverOverrideKey: knownState?.receiverOverrideKey ?? null, selectedReceiverKey: knownState?.selectedReceiverKey ?? null, targetOptions: targetOptions ?? null, discarded: tab.discarded ?? false, frozen: tab.frozen ?? false });
    try {
      const response = await annotateResponseWithReceiver(request, await chrome.tabs.sendMessage(tab.id, payload, targetOptions), tab, knownState);
      await recordTabObservation(tab, { receiverReady: true });
      await patchBridgeState({
        lastContentMessage: response,
        activeTab: { id: tab.id, url: tab.url, windowId: tab.windowId, supported: true, discarded: tab.discarded, frozen: tab.frozen }
      });
      await appendTrace("content.send_succeeded", { requestType: request.type, tabId: tab.id, responseType: response.type, selectedReceiverKey: knownState?.selectedReceiverKey ?? null, receiverSelectionPolicy: knownState?.receiverSelectionPolicy, receiverOverrideStatus: knownState?.receiverOverrideStatus });
      return response;
    } catch (error) {
      if (isMissingReceiverError(error)) {
        await appendTrace("content.missing_receiver", { requestType: request.type, tabId: tab.id, error: errorMessage(error) }, "warn");
        const reinjected = await tryInjectContentScript(tab, knownState);
        if (reinjected.ok) {
          try {
            const retried = await annotateResponseWithReceiver(request, await chrome.tabs.sendMessage(tab.id, payload, targetOptions), tab, knownState);
            await recordTabObservation(tab, { receiverReady: true, documentId: void 0, frameId: void 0, documentLifecycle: void 0 });
            await patchBridgeState({
              lastContentMessage: retried,
              activeTab: { id: tab.id, url: tab.url, windowId: tab.windowId, supported: true, discarded: tab.discarded, frozen: tab.frozen }
            });
            await appendTrace("content.retry_succeeded", { requestType: request.type, tabId: tab.id, responseType: retried.type, receiverOverrideStatus: knownState?.receiverOverrideStatus, receiverOverrideKey: knownState?.receiverOverrideKey ?? null });
            return retried;
          } catch (retryError) {
            const failure3 = replyTo(request, "error.report", {
              error: String(retryError),
              active_url: tab.url ?? null,
              recovery_attempted: true,
              injection_result: reinjected,
              tab_state: { discarded: tab.discarded ?? false, frozen: tab.frozen ?? false }
            }, tab.id);
            await recordTabObservation(tab, { receiverReady: false });
            await patchBridgeState({ lastError: failure3 });
            await appendTrace("content.retry_failed", { requestType: request.type, tabId: tab.id, error: errorMessage(retryError), injectionResult: reinjected }, "warn");
            return failure3;
          }
        }
        const failure2 = replyTo(request, "error.report", {
          error: reinjected.reason ?? String(error),
          active_url: tab.url ?? null,
          recovery_attempted: true,
          injection_result: reinjected,
          tab_state: { discarded: tab.discarded ?? false, frozen: tab.frozen ?? false }
        }, tab.id);
        await recordTabObservation(tab, { receiverReady: false });
        await patchBridgeState({ lastError: failure2 });
        await appendTrace("content.recovery_unavailable", { requestType: request.type, tabId: tab.id, injectionResult: reinjected }, "warn");
        return failure2;
      }
      const failure = replyTo(request, "error.report", {
        error: String(error),
        active_url: tab.url ?? null,
        tab_state: { discarded: tab.discarded ?? false, frozen: tab.frozen ?? false }
      }, tab.id);
      await recordTabObservation(tab, { receiverReady: false });
      await patchBridgeState({ lastError: failure });
      await appendTrace("content.send_failed", { requestType: request.type, tabId: tab.id, error: errorMessage(error) }, "warn");
      return failure;
    }
  }
  async function sendToTargetContentScript(request) {
    const tab = await chooseTargetTab(request);
    if (!tab?.id || !isSupportedUrl(tab.url)) {
      const error = replyTo(request, "error.report", {
        error: "no supported target tab",
        active_url: (await getActiveTab())?.url ?? null,
        known_supported_tabs: await getSupportedTabs()
      });
      await patchBridgeState({ lastError: error });
      return error;
    }
    return sendToContentScript(tab, request);
  }
  async function forwardResponseToNative(response) {
    const port = ensureNativePort();
    port.postMessage(response);
    await patchBridgeState({ lastContentMessage: response });
    await appendTrace("native.forward_response", { responseType: response.type, tabId: response.tab_id });
  }
  async function mirrorResponseToNativeIfAvailable(response) {
    try {
      await forwardResponseToNative(response);
      return { ok: true };
    } catch (error) {
      const failure = errorMessage(error);
      await patchBridgeState({ lastContentMessage: response });
      await appendTrace("native.forward_response_skipped", { responseType: response.type, tabId: response.tab_id, error: failure }, "warn");
      return { ok: false, error: failure };
    }
  }
  async function performAction(type, payload = {}, tabId) {
    const request = makeEnvelope(type, payload, tabId);
    const response = await sendToTargetContentScript(request);
    await mirrorResponseToNativeIfAvailable(response);
    return response;
  }
  async function openPanelForTab(tab) {
    if (!tab?.id || !tab.windowId) return;
    await chrome.sidePanel.open({ tabId: tab.id, windowId: tab.windowId }).catch(console.error);
  }
  async function openPanelForBestTab() {
    const tab = await resolveTargetTab();
    await openPanelForTab(tab);
  }
  async function extensionContextsSummary() {
    const runtimeVersion = chrome.runtime.getManifest().version;
    const hasRuntimeGetContexts = typeof chrome.runtime.getContexts === "function";
    const openContexts = hasRuntimeGetContexts ? (await chrome.runtime.getContexts({})).map((context) => ({
      contextId: context.contextId,
      contextType: context.contextType,
      documentId: context.documentId,
      documentUrl: context.documentUrl,
      documentOrigin: context.documentOrigin,
      tabId: context.tabId,
      windowId: context.windowId,
      frameId: context.frameId,
      incognito: context.incognito
    })) : [];
    return {
      runtimeId: chrome.runtime.id,
      runtimeVersion,
      hasRuntimeGetContexts,
      openContexts
    };
  }
  function nativeDiagnosticsShowReachability(state) {
    const nativeConnection = state.nativeConnection;
    if (nativeConnection?.connected) return false;
    if (nativeConnection?.lastOneShotProbeOk && !nativeConnection?.lastOneShotProbeError) return true;
    return Boolean(state.lastNativeStatusSnapshot && !state.lastNativeStatusError);
  }
  async function maybeReconnectNativeFromDiagnostics(trigger, waitForHealthMs = 0) {
    const state = await getBridgeState();
    if (!nativeDiagnosticsShowReachability(state)) return false;
    await appendTrace("native.opportunistic_reconnect", {
      trigger,
      diagnosis: state.nativeConnection?.laneDiagnosis?.status ?? null,
      lastOneShotProbeOk: state.nativeConnection?.lastOneShotProbeOk ?? null,
      snapshotCapturedAt: state.lastNativeStatusSnapshot?.capturedAt ?? null
    }, "warn");
    await recordPersistentNativeEvent("native.opportunistic_reconnect", { trigger });
    const reconnected = await attemptNativeReconnect(trigger === "bridge.status" ? "status" : "probe", `explicit ${trigger} confirmed one-shot native-host reachability`);
    if (!reconnected || waitForHealthMs <= 0) return reconnected;
    const requestId = (await getBridgeState()).nativeConnection?.lastHealthRequestId;
    await waitForNativeHealthResult(requestId, waitForHealthMs + 150);
    return (await getBridgeState()).nativeConnection?.connected === true;
  }
  async function currentBridgeStatus(request) {
    await refreshActiveTabState();
    const state = await getBridgeState();
    const nativeConnection = state.nativeConnection;
    const lastHealthPongAt = nativeConnection?.lastHealthPongAt ? Date.parse(nativeConnection.lastHealthPongAt) : Number.NaN;
    const healthIsStale = !Number.isFinite(lastHealthPongAt) || Date.now() - lastHealthPongAt > 1e4;
    if (nativeConnection?.connected && healthIsStale) {
      const requested = await requestNativeHealth("bridge.status");
      if (requested) {
        const requestId = (await getBridgeState()).nativeConnection?.lastHealthRequestId;
        await waitForNativeHealthResult(requestId, 1650);
      }
    }
    if (nativeStatusSnapshotIsStale(state)) {
      await requestNativeStatusOneShot("bridge.status");
    }
    await maybeReconnectNativeFromDiagnostics("bridge.status", 1200);
    return replyTo(request, "bridge.status", await bridgeStateWithPersistentDiagnostics());
  }
  async function waitForNativeHealthResult(requestId, timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const nativeConnection = (await getBridgeState()).nativeConnection;
      const requestMatches = !requestId || nativeConnection?.lastHealthRequestId === requestId;
      const healthSettled = requestMatches && (nativeConnection?.lastHealthOk === true || typeof nativeConnection?.lastHealthError === "string");
      if (healthSettled) return;
      await sleep(100);
    }
  }
  async function currentBridgeProbe(request) {
    await refreshActiveTabState();
    const payload = request.payload ?? {};
    const limitValue = Number(payload.limit ?? 40);
    const limit = Number.isFinite(limitValue) ? Math.max(1, Math.min(200, Math.trunc(limitValue))) : 40;
    const awaitHealthValue = Number(payload.await_health_ms ?? 1500);
    const awaitHealthMs = Number.isFinite(awaitHealthValue) ? Math.max(0, Math.min(5e3, Math.trunc(awaitHealthValue))) : 1500;
    const ensureOffscreenRequested = payload.ensure_offscreen === true || payload.ensure_offscreen === 1 || payload.ensure_offscreen === "1";
    const beforeHealth = (await getBridgeState()).nativeConnection;
    const shouldRefreshHealth = Boolean(beforeHealth?.connected && awaitHealthMs > 0);
    const lastOneShotAt = beforeHealth?.lastOneShotProbeAt ? Date.parse(beforeHealth.lastOneShotProbeAt) : Number.NaN;
    const oneShotIsStale = !Number.isFinite(lastOneShotAt) || Date.now() - lastOneShotAt > 1e4;
    const shouldRunOneShot = Boolean(!beforeHealth?.connected && awaitHealthMs > 0 && oneShotIsStale);
    if (shouldRefreshHealth) {
      const requested = await requestNativeHealth("bridge.probe", awaitHealthMs);
      if (requested) {
        const requestId = (await getBridgeState()).nativeConnection?.lastHealthRequestId;
        await waitForNativeHealthResult(requestId, awaitHealthMs + 150);
      }
    } else if (shouldRunOneShot) {
      await requestNativeHealthOneShot("bridge.probe");
    }
    const stateBeforeSnapshot = await getBridgeState();
    const nativeStatusSnapshot = nativeStatusSnapshotIsStale(stateBeforeSnapshot) ? await requestNativeStatusOneShot("bridge.probe") : stateBeforeSnapshot.lastNativeStatusSnapshot;
    await maybeReconnectNativeFromDiagnostics("bridge.probe", awaitHealthMs);
    const offscreen = await ensureOffscreenDocument(ensureOffscreenRequested, { ping: ensureOffscreenRequested });
    const session = await chrome.storage.session.get([STORAGE_KEY, TRACE_KEY, SESSION_TABS_KEY]);
    const manifest = chrome.runtime.getManifest();
    const effectiveContentScriptPolicy = await contentScriptPolicySummary(manifest);
    const status = await getBridgeState();
    return replyTo(request, "bridge.probe", {
      probeAt: (/* @__PURE__ */ new Date()).toISOString(),
      manifest: {
        version: manifest.version,
        minimumChromeVersion: manifest.minimum_chrome_version,
        permissions: manifest.permissions,
        hostPermissions: manifest.host_permissions,
        probeUrl: chrome.runtime.getURL("probe/index.html"),
        contentScriptPolicy: effectiveContentScriptPolicy
      },
      status: await bridgeStateWithPersistentDiagnostics(status),
      receiverAudit: await receiverAuditForTab(receiverAuditTarget(status), status, effectiveContentScriptPolicy),
      contexts: await extensionContextsSummary(),
      offscreen,
      nativeStatusSnapshot,
      trace: { events: await recentTrace(limit) },
      sessionMirror: {
        bridgeState: session[STORAGE_KEY],
        persistentDiagnostics: await persistentDiagnosticsSnapshot(status),
        bridgeTrace: session[TRACE_KEY],
        supportedTabs: session[SESSION_TABS_KEY]
      }
    });
  }
  async function handleBackgroundRequest(request) {
    if (request.type === "bridge.status") {
      return currentBridgeStatus(request);
    }
    if (request.type === "bridge.contexts") {
      const ensureOffscreenRequested = request.payload?.ensure_offscreen === true || request.payload?.ensure_offscreen === 1 || request.payload?.ensure_offscreen === "1";
      if (ensureOffscreenRequested) {
        await ensureOffscreenDocument(true);
      }
      return replyTo(request, "bridge.contexts", await extensionContextsSummary());
    }
    if (request.type === "bridge.trace") {
      const limitValue = Number(request.payload?.limit ?? 40);
      const limit = Number.isFinite(limitValue) ? Math.max(1, Math.min(200, Math.trunc(limitValue))) : 40;
      return replyTo(request, "bridge.trace", { events: await recentTrace(limit) });
    }
    if (request.type === "bridge.probe") {
      return currentBridgeProbe(request);
    }
    if (request.type === "bridge.content_script_experiment") {
      const status = await contentScriptExperimentStatus();
      return replyTo(request, "bridge.content_script_experiment", {
        ok: true,
        policy: status.policy,
        dynamicScriptCount: status.dynamicScriptCount,
        activeExperiment: status.policy.activeExperiment ?? null
      });
    }
    if (request.type === "bridge.set_content_script_experiment") {
      const experimentId = compactString4(request.payload?.experiment_id);
      if (!experimentId || !["manifest_all_frames", "manifest_match_about_blank", "manifest_match_origin_as_fallback"].includes(experimentId)) {
        return replyTo(request, "error.report", { error: "bridge.set_content_script_experiment requires experiment_id: manifest_all_frames | manifest_match_about_blank | manifest_match_origin_as_fallback" });
      }
      const applied = await applyContentScriptExperiment(experimentId);
      await refreshActiveTabState();
      return replyTo(request, "bridge.set_content_script_experiment", {
        ok: true,
        experimentId,
        policy: applied.policy,
        activeExperiment: applied.policy.activeExperiment ?? null,
        registration: applied.registration
      });
    }
    if (request.type === "bridge.clear_content_script_experiment") {
      const policy = await clearContentScriptExperimentRegistration({ traceReason: "bridge.clear_content_script_experiment" });
      await refreshActiveTabState();
      return replyTo(request, "bridge.clear_content_script_experiment", {
        ok: true,
        policy,
        activeExperiment: policy.activeExperiment ?? null
      });
    }
    if (request.type === "bridge.offscreen_dom") {
      const payload = request.payload ?? {};
      const html = typeof payload.html === "string" ? payload.html : "";
      const selectors = Array.isArray(payload.selectors) ? payload.selectors.filter((value) => typeof value === "string" && value.trim().length > 0) : [];
      const requestedMax = Number(payload.max_candidates ?? 8);
      const maxCandidates = Number.isFinite(requestedMax) ? Math.max(1, Math.min(24, Math.trunc(requestedMax))) : 8;
      const baseUrl = typeof payload.base_url === "string" && payload.base_url.trim().length > 0 ? payload.base_url.trim() : void 0;
      const offscreen = await ensureOffscreenDocument(true, { ping: true, pingTimeoutMs: 2e3 });
      if (!offscreen.enabled) {
        return replyTo(request, "error.report", { error: offscreen.lastError ?? "offscreen document unavailable", offscreen });
      }
      const parsed = await requestOffscreenDomSummary(html, selectors, maxCandidates, baseUrl);
      if (!parsed.ok || !parsed.summary) {
        return replyTo(request, "error.report", { error: parsed.error ?? "offscreen DOM parse failed", offscreen });
      }
      return replyTo(request, "bridge.offscreen_dom", {
        ok: true,
        offscreen: { ...offscreen, lastDomSummary: parsed.summary },
        summary: parsed.summary
      });
    }
    if (request.type === "bridge.offscreen_fixture") {
      const payload = request.payload ?? {};
      const html = typeof payload.html === "string" ? payload.html : "";
      const selectors = Array.isArray(payload.selectors) ? payload.selectors.filter((value) => typeof value === "string" && value.trim().length > 0) : [];
      const requestedMax = Number(payload.max_candidates ?? 8);
      const maxCandidates = Number.isFinite(requestedMax) ? Math.max(1, Math.min(24, Math.trunc(requestedMax))) : 8;
      const baseUrl = typeof payload.base_url === "string" && payload.base_url.trim().length > 0 ? payload.base_url.trim() : void 0;
      const offscreen = await ensureOffscreenDocument(true, { ping: true, pingTimeoutMs: 2e3 });
      if (!offscreen.enabled) {
        return replyTo(request, "error.report", { error: offscreen.lastError ?? "offscreen document unavailable", offscreen });
      }
      const captured = await requestOffscreenFixtureCapture(html, selectors, maxCandidates, baseUrl);
      if (!captured.ok || !captured.summary || !captured.fixture) {
        return replyTo(request, "error.report", { error: captured.error ?? "offscreen fixture capture failed", offscreen });
      }
      return replyTo(request, "bridge.offscreen_fixture", {
        ok: true,
        offscreen: { ...offscreen, lastDomSummary: captured.summary },
        summary: captured.summary,
        fixture: captured.fixture
      });
    }
    if (request.type === "bridge.set_target_tab") {
      const tabId = typeof request.payload?.tab_id === "number" ? Number(request.payload.tab_id) : request.tab_id;
      if (!tabId) {
        return replyTo(request, "error.report", { error: "bridge.set_target_tab requires tab_id" });
      }
      await setSelectedTargetTab(tabId);
      await appendTrace("bridge.target_selected", { tabId });
      await refreshActiveTabState();
      return replyTo(request, "bridge.set_target_tab", await getBridgeState(), tabId);
    }
    if (request.type === "bridge.clear_target_tab") {
      await setSelectedTargetTab(null);
      await appendTrace("bridge.target_cleared");
      await refreshActiveTabState();
      return replyTo(request, "bridge.clear_target_tab", await getBridgeState());
    }
    if (request.type === "bridge.set_receiver_override") {
      const payload = request.payload ?? {};
      const tabId = typeof payload.tab_id === "number" ? Number(payload.tab_id) : request.tab_id;
      const receiverKey = typeof payload.receiver_key === "string" && payload.receiver_key.trim().length > 0 ? payload.receiver_key.trim() : null;
      if (!tabId || !receiverKey) {
        return replyTo(request, "error.report", { error: "bridge.set_receiver_override requires tab_id and receiver_key" });
      }
      await setReceiverOverride(tabId, receiverKey);
      await appendTrace("bridge.receiver_override_set", { tabId, receiverKey });
      await refreshActiveTabState();
      return replyTo(request, "bridge.set_receiver_override", await getBridgeState(), tabId);
    }
    if (request.type === "bridge.clear_receiver_override") {
      const payload = request.payload ?? {};
      const tabId = typeof payload.tab_id === "number" ? Number(payload.tab_id) : request.tab_id;
      if (!tabId) {
        return replyTo(request, "error.report", { error: "bridge.clear_receiver_override requires tab_id" });
      }
      await setReceiverOverride(tabId, null);
      await appendTrace("bridge.receiver_override_cleared", { tabId });
      await refreshActiveTabState();
      return replyTo(request, "bridge.clear_receiver_override", await getBridgeState(), tabId);
    }
    return null;
  }
  function nativeOverflowSummaryFromMessage(message) {
    if (message.type !== "error.report") return void 0;
    const payload = typeof message.payload === "object" && message.payload ? message.payload : null;
    if (!payload || payload.overflow !== true) return void 0;
    return {
      ...nativeOverflowSummaryFromPayload(payload),
      request_id: typeof message.request_id === "string" ? message.request_id : void 0,
      tab_id: typeof message.tab_id === "number" ? message.tab_id : void 0
    };
  }
  async function handleNativeMessage(message) {
    log("native message", message);
    if (message.type === "bridge.forward_to_active_tab") {
      const forwarded = message.payload?.request;
      if (!forwarded) {
        const error = replyTo(message, "error.report", { error: "bridge.forward_to_active_tab missing payload.request" });
        ensureNativePort().postMessage(error);
        await patchBridgeState({ lastError: error });
        return;
      }
      const backgroundResponse = await handleBackgroundRequest(forwarded);
      const response = backgroundResponse ?? await sendToTargetContentScript(forwarded);
      await forwardResponseToNative(response);
      return;
    }
    if (message.type === "health.ping") {
      const payload = message.payload ?? {};
      const echo = typeof payload.echo === "object" && payload.echo ? payload.echo : {};
      const echoedRequestId = typeof payload.requestId === "string" ? payload.requestId : typeof echo.requestId === "string" ? echo.requestId : void 0;
      const pending = pendingNativeHealth && (pendingNativeHealth.requestId === echoedRequestId || pendingNativeHealth.envelopeRequestId === message.request_id) ? pendingNativeHealth : null;
      if (pendingNativeHealth && !pending) {
        await appendTrace("native.health_stale_pong", {
          responseRequestId: message.request_id,
          echoedRequestId: echoedRequestId ?? null,
          expectedRequestId: pendingNativeHealth.requestId,
          expectedEnvelopeRequestId: pendingNativeHealth.envelopeRequestId
        }, "warn").catch(console.error);
        return;
      }
      const requestId = echoedRequestId ?? pending?.requestId ?? message.request_id ?? "unknown";
      const trigger = typeof payload.trigger === "string" ? payload.trigger : typeof echo.trigger === "string" ? echo.trigger : "native.health";
      if (pending) {
        clearTimeout(pending.timeoutId);
        pendingNativeHealth = null;
      }
      const roundTripMs = pending ? Math.max(0, Date.now() - pending.startedAt) : void 0;
      const hostIdentity = nativeHostIdentityFromRecord(payload.host_identity ?? null);
      const broker = nativeBrokerSummaryFromPayload(payload.broker ?? null);
      const host = typeof payload.host === "string" ? payload.host : typeof payload.native_host === "string" ? payload.native_host : void 0;
      const stateBeforeHealthPatch = await getBridgeState();
      await patchNativeConnection({
        connected: true,
        lastHealthPongAt: (/* @__PURE__ */ new Date()).toISOString(),
        lastHealthRoundTripMs: roundTripMs,
        lastHealthRequestId: requestId,
        lastHealthTrigger: trigger,
        lastHealthOk: true,
        lastHealthError: void 0,
        persistentHostIdentity: hostIdentity,
        persistentBroker: broker,
        nativeHost: host,
        socketPath: payload.socket_path ? String(payload.socket_path) : void 0
      });
      await appendTrace("native.health_pong", { requestId, roundTripMs, trigger, host: host ?? null, socketPath: payload.socket_path ?? null, brokerRole: broker?.role ?? null, bootId: hostIdentity?.boot_id ?? null }).catch(console.error);
      if (!stateBeforeHealthPatch.nativeConnection?.connected || stateBeforeHealthPatch.nativeConnection?.lastHealthOk !== true) {
        await recordPersistentNativeEvent("native.connected", { trigger, reason: roundTripMs !== void 0 ? `health pong ${roundTripMs}ms` : "health pong" });
      }
      return;
    }
    if (message.type === "bridge.status") {
      await patchBridgeState({ lastNativeMessage: message });
      return;
    }
    if (message.type === "error.report") {
      const overflow = nativeOverflowSummaryFromMessage(message);
      await patchBridgeState({ lastError: message, lastOversizedHostMessage: overflow ?? void 0 });
      if (overflow) {
        await appendTrace("native.host_outbound_overflow", overflow, "warn").catch(console.error);
        return;
      }
      return;
    }
    log("unhandled native message type", message.type);
  }
  function ensureNativePort() {
    if (nativePort) return nativePort;
    try {
      nativePort = chrome.runtime.connectNative(HOST_NAME);
    } catch (error) {
      void patchBridgeState({ lastError: errorMessage(error) }).catch(console.error);
      void appendTrace("native.connect_failed", { error: errorMessage(error) }, "error").catch(console.error);
      throw error;
    }
    void appendTrace("native.connected").catch(console.error);
    void markNativeConnected().catch(console.error);
    void requestNativeHealth("native.connected").catch(console.error);
    nativePort.onMessage.addListener((msg) => {
      void patchBridgeState({ lastNativeMessage: msg }).catch(console.error);
      void appendTrace("native.message", { type: msg?.type ?? null }).catch(console.error);
      log("native message", msg);
      void handleNativeMessage(msg).catch(console.error);
    });
    nativePort.onDisconnect.addListener(() => {
      const reason = chrome.runtime.lastError?.message ?? "native port disconnected";
      log("native port disconnected", reason);
      nativePort = null;
      void (async () => {
        clearPendingNativeHealth("native.disconnect");
        await patchBridgeState({ lastError: reason });
        await markNativeDisconnected(reason);
        await appendTrace("native.disconnected", { reason }, "warn");
        await recordPersistentNativeEvent("native.disconnected", { trigger: "disconnect", reason });
        await attemptNativeReconnect("disconnect", reason);
      })().catch(console.error);
    });
    return nativePort;
  }
  function installContextMenus() {
    chrome.contextMenus.removeAll(() => {
      chrome.contextMenus.create({
        id: MENU_OPEN_PANEL,
        title: "Open GlassTTY side panel",
        contexts: ["page", "selection"],
        documentUrlPatterns: MENU_PATTERNS
      });
      chrome.contextMenus.create({
        id: MENU_SET_TARGET,
        title: "Target this tab with GlassTTY",
        contexts: ["page", "selection"],
        documentUrlPatterns: MENU_PATTERNS
      });
      chrome.contextMenus.create({
        id: MENU_READ_LATEST,
        title: "Read latest output into GlassTTY",
        contexts: ["page"],
        documentUrlPatterns: MENU_PATTERNS
      });
      chrome.contextMenus.create({
        id: MENU_READ_PROMPT,
        title: "Read prompt draft into GlassTTY",
        contexts: ["page"],
        documentUrlPatterns: MENU_PATTERNS
      });
      chrome.contextMenus.create({
        id: MENU_CAPTURE_FIXTURE,
        title: "Capture page fixture into GlassTTY",
        contexts: ["page"],
        documentUrlPatterns: MENU_PATTERNS
      });
      chrome.contextMenus.create({
        id: MENU_WRITE_SELECTION,
        title: "Write selected text into prompt draft",
        contexts: ["selection"],
        documentUrlPatterns: MENU_PATTERNS
      });
    });
  }
  chrome.runtime.onInstalled.addListener(() => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    void hardenStorageAccess();
    void chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(console.error);
    installContextMenus();
    void recordRuntimeSignal("installed").catch(console.error);
    void resumeNativeConnectionLane("installed");
    void refreshActiveTabState();
    void appendTrace("lifecycle.installed").catch(console.error);
    log("installed");
  });
  chrome.runtime.onStartup.addListener(() => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    void hardenStorageAccess();
    installContextMenus();
    void recordRuntimeSignal("startup").catch(console.error);
    void resumeNativeConnectionLane("startup");
    void appendTrace("lifecycle.startup").catch(console.error);
    void refreshActiveTabState();
  });
  chrome.tabs.onActivated.addListener((info) => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    void appendTrace("tabs.activated", { tabId: info.tabId, windowId: info.windowId }).catch(console.error);
    void refreshActiveTabState();
  });
  chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    if (changeInfo.url || changeInfo.status || typeof changeInfo.discarded === "boolean" || typeof changeInfo.frozen === "boolean") {
      await appendTrace("tabs.updated", { tabId, url: changeInfo.url ?? tab.url ?? null, status: changeInfo.status ?? tab.status ?? null, discarded: changeInfo.discarded ?? tab.discarded ?? null, frozen: changeInfo.frozen ?? tab.frozen ?? null });
    }
    await syncSidePanelForTab(tab);
    if (isSupportedUrl(tab.url)) {
      await recordTabObservation(tab);
      const observed = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
      await primeSupportedSubframeReceivers(tab, observed);
    }
    await refreshActiveTabState();
  });
  chrome.tabs.onRemoved.addListener((tabId) => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    void appendTrace("tabs.removed", { tabId }).catch(console.error);
    void forgetSupportedTab(tabId).then((supportedTabs) => patchBridgeState({ supportedTabs })).then(() => forgetPrimedReceiverKeys(tabId)).then(() => refreshActiveTabState()).catch(console.error);
  });
  for (const [eventName, listener] of [
    ["onCommitted", chrome.webNavigation.onCommitted],
    ["onHistoryStateUpdated", chrome.webNavigation.onHistoryStateUpdated],
    ["onReferenceFragmentUpdated", chrome.webNavigation.onReferenceFragmentUpdated]
  ]) {
    listener.addListener((details) => {
      if (!BUNDLE_VERSION_IS_CURRENT) return;
      void refreshSupportedTabReceiverContexts(details.tabId).catch(console.error);
      void (async () => {
        const tab = await getTabById(details.tabId);
        if (!tab?.id || !isSupportedUrl(tab.url)) return;
        const observed = (await getSupportedTabs()).find((entry) => entry.tabId === tab.id);
        await primeSupportedSubframeReceivers(tab, observed);
      })().catch(console.error);
      void appendTrace("receivers.frame_navigation", {
        event: eventName,
        tabId: details.tabId,
        frameId: details.frameId,
        documentId: details.documentId,
        documentLifecycle: details.documentLifecycle,
        parentFrameId: details.parentFrameId,
        frameType: details.frameType,
        url: details.url
      }).catch(console.error);
    });
  }
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    if (alarm.name !== NATIVE_RECONNECT_ALARM) return;
    void (async () => {
      await appendTrace("native.reconnect_alarm_fired", { scheduledTime: alarm.scheduledTime });
      const reason = (await getBridgeState()).nativeConnection?.lastDisconnectReason ?? "native reconnect alarm";
      await attemptNativeReconnect("alarm", reason);
    })().catch(console.error);
  });
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    if (!tab?.id || !isSupportedUrl(tab.url)) return;
    const tabId = tab.id;
    void (async () => {
      if (info.menuItemId === MENU_OPEN_PANEL) {
        await setSelectedTargetTab(tabId, tab);
        await openPanelForTab(tab);
        await refreshActiveTabState();
        return;
      }
      if (info.menuItemId === MENU_SET_TARGET) {
        await setSelectedTargetTab(tabId, tab);
        await openPanelForTab(tab);
        await refreshActiveTabState();
        return;
      }
      if (info.menuItemId === MENU_READ_LATEST) {
        await setSelectedTargetTab(tabId, tab);
        await performAction("transcript.latest", {}, tabId);
        return;
      }
      if (info.menuItemId === MENU_READ_PROMPT) {
        await setSelectedTargetTab(tabId, tab);
        await performAction("prompt.read", {}, tabId);
        return;
      }
      if (info.menuItemId === MENU_CAPTURE_FIXTURE) {
        await setSelectedTargetTab(tabId, tab);
        await performAction("fixture.capture", {}, tabId);
        return;
      }
      if (info.menuItemId === MENU_WRITE_SELECTION && info.selectionText) {
        await setSelectedTargetTab(tabId, tab);
        await performAction("prompt.write", { text: info.selectionText }, tabId);
        return;
      }
    })().catch(console.error);
  });
  chrome.commands.onCommand.addListener(async (command) => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    void appendTrace("command.invoked", { command }).catch(console.error);
    if (command === "pull-latest-output") {
      await performAction("transcript.latest");
    } else if (command === "pull-current-prompt") {
      await performAction("prompt.read");
    } else if (command === "debug-dom-candidates") {
      await performAction("debug.dom_candidates");
    } else if (command === "open-glasstty-side-panel") {
      await openPanelForBestTab();
    }
  });
  chrome.runtime.onSuspend.addListener(() => {
    if (!BUNDLE_VERSION_IS_CURRENT) return;
    void recordRuntimeSignal("suspend").catch(console.error);
  });
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!BUNDLE_VERSION_IS_CURRENT) {
      sendResponse(replyTo(message, "error.report", {
        error: `stale GlassTTY worker bundle ${"0.1.126"}; manifest requires ${MANIFEST_VERSION}`
      }));
      return false;
    }
    const fromExtensionPage = !sender.tab;
    const senderUrl = sender.url ?? sender.documentUrl;
    const fromOffscreenDocument = senderUrl === offscreenDocumentUrl();
    if (sender.tab) {
      void recordSenderObservation(sender, message).then(() => refreshActiveTabState()).catch(console.error);
    }
    if (fromOffscreenDocument && message.type === "offscreen.document_ready") {
      void appendTrace("offscreen.document_ready", { url: senderUrl, payload: message.payload ?? null }).catch(console.error);
      sendResponse(replyTo(message, "offscreen.document_ack", { ok: true, url: senderUrl }));
      return true;
    }
    if (fromExtensionPage && ["bridge.status", "bridge.contexts", "bridge.trace", "bridge.probe", "bridge.content_script_experiment", "bridge.set_content_script_experiment", "bridge.clear_content_script_experiment", "bridge.offscreen_dom", "bridge.offscreen_fixture", "bridge.set_target_tab", "bridge.clear_target_tab", "bridge.set_receiver_override", "bridge.clear_receiver_override"].includes(message.type)) {
      void handleBackgroundRequest(message).then((response) => sendResponse(response ?? replyTo(message, "error.report", { error: `no background handler for ${message.type}` }))).catch((error) => sendResponse(replyTo(message, "error.report", { error: String(error) })));
      return true;
    }
    if (fromExtensionPage && ["prompt.read", "prompt.write", "prompt.submit", "transcript.latest", "selection.read", "debug.dom_candidates", "state.snapshot", "fixture.capture"].includes(message.type)) {
      const tabId = typeof message.payload?.tab_id === "number" ? message.payload.tab_id : message.tab_id;
      const payload = typeof message.payload === "object" && message.payload ? { ...message.payload } : {};
      delete payload.tab_id;
      void performAction(message.type, payload, tabId).then((response) => sendResponse(response)).catch((error) => sendResponse(replyTo(message, "error.report", { error: String(error) })));
      return true;
    }
    void patchBridgeState({
      lastContentMessage: message,
      lastAdapterDetected: message.type === "adapter.detected" ? message : void 0,
      lastError: message.type === "error.report" ? message : void 0
    }).catch(console.error);
    try {
      const port = ensureNativePort();
      port.postMessage(message);
      sendResponse({ ok: true });
    } catch (error) {
      sendResponse({ ok: false, error: String(error) });
    }
    return true;
  });
  void enforceCurrentBundle().then((current) => {
    if (!current) return;
    void recordRuntimeBoot().catch(console.error);
    void hardenStorageAccess();
    void refreshActiveTabState();
    installContextMenus();
    void resumeNativeConnectionLane("bootstrap").catch(console.error);
  }).catch(console.error);
})();
